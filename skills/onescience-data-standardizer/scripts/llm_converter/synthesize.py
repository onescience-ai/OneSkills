"""Tier2 LLM-synthesized converter orchestrator.

Pipeline:
    1. probe_raw(source_dir) -> raw_probe_report.json
    2. Load primitives spec.md / usage.md (already fetched by main flow and
       passed via --spec-json) and the AI-Ready contract from
       references/ai_ready_contract.md
    3. Render prompts/system.md + prompts/user.md.j2 with all context
    4. Dispatch to an LLM backend:
         - host    : read prompt from stdin, write script to stdout
                     (used when the enclosing Agent acts as the LLM)
         - file    : read a pre-generated script from --generated-script
                     (used when orchestrator delegates to onescience-coder
                      and hands back the artifact path)
         - none    : abort with a diagnostic telling the caller to supply
                     --generated-script or run in `host` mode
    5. Statically validate the script; on failure, retry up to --max-retries
       times by re-emitting the prompt with the validation report appended
    6. Persist to <target_dir>/_converter/convert_<name>.py plus
       prompt_snapshot.md and raw_probe_report.json for audit
    7. Execute the script via subprocess and stream stderr through

This module never talks to a remote LLM API directly; the host Agent (or
onescience-coder via orchestrator handoff) is the LLM. That keeps the
skill runtime-agnostic and avoids embedding credentials.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent.parent
REFERENCES_DIR = SKILL_ROOT / "references"
ADAPTERS_DIR = SCRIPT_DIR.parent / "adapters"

sys.path.insert(0, str(SCRIPT_DIR))
import validate_generated  # noqa: E402

MAX_PROBE_FILES = 200
MAX_PROBE_DEPTH = 4
SAMPLE_HEADER_BYTES = 4096

FORMAT_BY_EXT: Dict[str, str] = {
    ".nc": "netcdf", ".nc4": "netcdf", ".netcdf": "netcdf",
    ".h5": "hdf5", ".hdf5": "hdf5", ".hdf": "hdf5",
    ".pkl": "pickle", ".pickle": "pickle",
    ".npz": "npz", ".npy": "npy",
    ".pdb": "pdb", ".ent": "pdb",
    ".cif": "mmcif", ".mmcif": "mmcif",
    ".sdf": "sdf", ".mol": "mol", ".mol2": "mol2",
    ".csv": "csv", ".tsv": "tsv",
    ".lmdb": "lmdb", ".mdb": "lmdb", ".aselmdb": "aselmdb",
    ".extxyz": "extxyz", ".xyz": "xyz",
    ".h5ad": "h5ad",
    ".zarr": "zarr",
    ".fasta": "fasta", ".fa": "fasta", ".faa": "fasta", ".fna": "fasta",
    ".json": "json", ".yaml": "yaml", ".yml": "yaml",
    ".grib": "grib", ".grib2": "grib", ".grb": "grib", ".grb2": "grib",
    ".parquet": "parquet",
    ".txt": "text", ".md": "markdown",
    ".png": "image", ".jpg": "image", ".jpeg": "image", ".tif": "image",
    ".tiff": "image",
}

# Domain -> few-shot adapter preference (same-domain first).
FEW_SHOT_BY_DOMAIN: Dict[str, List[Tuple[str, str]]] = {
    "climate": [("climate", "era5"), ("cfd", "deepcfd"),
                ("matchem", "oc20"), ("bio", "targetdiff")],
    "cfd":     [("cfd", "deepcfd"), ("climate", "era5"),
                ("matchem", "oc20"), ("bio", "targetdiff")],
    "bio":     [("bio", "targetdiff"), ("matchem", "oc20"),
                ("climate", "era5"), ("cfd", "deepcfd")],
    "matchem": [("matchem", "oc20"), ("bio", "targetdiff"),
                ("climate", "era5"), ("cfd", "deepcfd")],
}


class SynthesisError(RuntimeError):
    def __init__(self, message: str, *, reason: str = "converter_failed",
                 details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.reason = reason
        self.details = details or {}


# ----------------------------------------------------------------------
# Stage 1: raw probing
# ----------------------------------------------------------------------

def _magic_format(path: Path) -> Optional[str]:
    try:
        with open(path, "rb") as fh:
            head = fh.read(8)
    except OSError:
        return None
    if head.startswith(b"\x89HDF\r\n\x1a\n"):
        return "hdf5"
    if head[:3] == b"CDF":
        return "netcdf"
    if head[:4] == b"\x50\x4b\x03\x04":
        return "zip_or_npz"
    if head[:5] == b"HEADER":
        return "grib"
    if head[:4] == b"GRIB":
        return "grib"
    return None


def probe_raw(source_dir: Path) -> Dict[str, Any]:
    source_dir = Path(source_dir).expanduser().resolve()
    if not source_dir.exists():
        raise SynthesisError(f"source_dir does not exist: {source_dir}",
                             reason="source_dir_invalid")

    entries: List[Dict[str, Any]] = []
    format_hist: Dict[str, int] = {}
    total_bytes = 0
    total_files = 0
    ext_by_depth: Dict[int, Dict[str, int]] = {}

    root_depth = len(source_dir.parts)
    for path in sorted(source_dir.rglob("*")):
        depth = len(path.parts) - root_depth
        if depth > MAX_PROBE_DEPTH:
            continue
        rel = path.relative_to(source_dir).as_posix()
        if path.is_dir():
            try:
                children = sum(1 for _ in path.iterdir())
            except OSError:
                children = 0
            entries.append({"path": rel + "/", "type": "dir",
                            "depth": depth, "children_count": children})
            continue
        try:
            size = path.stat().st_size
        except OSError:
            size = 0
        total_files += 1
        total_bytes += size
        ext = path.suffix.lower()
        fmt = FORMAT_BY_EXT.get(ext) or _magic_format(path) or "unknown"
        format_hist[fmt] = format_hist.get(fmt, 0) + 1
        ext_by_depth.setdefault(depth, {})
        ext_by_depth[depth][ext] = ext_by_depth[depth].get(ext, 0) + 1
        if len(entries) < MAX_PROBE_FILES:
            entries.append({
                "path": rel, "type": "file", "depth": depth,
                "size": size, "ext": ext, "format": fmt,
            })

    samples = _sample_files(source_dir, entries, format_hist)
    detected_patterns = _detect_patterns(format_hist, entries, samples)

    return {
        "source_dir": str(source_dir),
        "total_files": total_files,
        "total_bytes": total_bytes,
        "max_depth_scanned": MAX_PROBE_DEPTH,
        "truncated": total_files > MAX_PROBE_FILES,
        "directory_tree": entries,
        "format_histogram": format_hist,
        "ext_by_depth": {str(k): v for k, v in sorted(ext_by_depth.items())},
        "samples": samples,
        "detected_patterns": detected_patterns,
        "summary": {
            "dominant_format": max(format_hist.items(),
                                   key=lambda kv: kv[1])[0]
                               if format_hist else "unknown",
            "n_formats": len(format_hist),
        },
    }


def _sample_files(source_dir: Path, entries: List[Dict[str, Any]],
                  format_hist: Dict[str, int]) -> List[Dict[str, Any]]:
    """Pick up to one representative file per detected format and inspect it."""
    chosen: Dict[str, Dict[str, Any]] = {}
    for e in entries:
        if e.get("type") != "file":
            continue
        fmt = e.get("format")
        if not fmt or fmt in chosen:
            continue
        chosen[fmt] = e
        if len(chosen) >= max(6, len(format_hist)):
            break

    samples: List[Dict[str, Any]] = []
    for fmt, entry in chosen.items():
        info: Dict[str, Any] = {
            "path": entry["path"],
            "format": fmt,
            "size": entry.get("size", 0),
        }
        full = source_dir / entry["path"]
        try:
            with open(full, "rb") as fh:
                head = fh.read(SAMPLE_HEADER_BYTES)
            info["head_hex"] = head[:32].hex()
            info["head_ascii"] = head[:256].decode("utf-8", errors="replace")
        except OSError as exc:
            info["read_error"] = str(exc)
        parsed = _try_parse_sample(full, fmt)
        if parsed:
            info["parsed"] = parsed
        samples.append(info)
    return samples


def _try_parse_sample(path: Path, fmt: str) -> Optional[Dict[str, Any]]:
    """Best-effort structured peek; never raises."""
    try:
        if fmt == "hdf5":
            import h5py  # type: ignore
            with h5py.File(path, "r") as fh:
                keys = list(fh.keys())
                shapes = {}
                for k in keys[:8]:
                    obj = fh[k]
                    if hasattr(obj, "shape"):
                        shapes[k] = list(obj.shape)
                        shapes[k + "_dtype"] = str(obj.dtype)
                    if hasattr(obj, "attrs"):
                        shapes[k + "_attrs"] = {
                            a: (str(obj.attrs[a])[:120])
                            for a in list(obj.attrs.keys())[:6]
                        }
                return {"keys": keys, "datasets": shapes}
        if fmt == "netcdf":
            import netCDF4  # type: ignore
            with netCDF4.Dataset(str(path), "r") as ds:
                return {
                    "variables": list(ds.variables.keys())[:20],
                    "dimensions": {k: len(v) for k, v in ds.dimensions.items()},
                    "global_attrs": {a: str(ds.getncattr(a))[:120]
                                     for a in ds.ncattrs()[:10]},
                }
        if fmt == "npz":
            import numpy as np  # type: ignore
            with np.load(path, allow_pickle=False) as z:
                return {"keys": list(z.keys())[:20],
                        "shapes": {k: list(z[k].shape) for k in list(z.keys())[:8]}}
        if fmt == "npy":
            import numpy as np  # type: ignore
            arr = np.load(path, allow_pickle=False, mmap_mode="r")
            return {"shape": list(arr.shape), "dtype": str(arr.dtype)}
        if fmt == "json":
            data = json.loads(path.read_text(encoding="utf-8")[:65536])
            if isinstance(data, dict):
                return {"top_keys": list(data.keys())[:20]}
            if isinstance(data, list):
                return {"length": len(data),
                        "first_item_keys": list(data[0].keys())[:20]
                        if data and isinstance(data[0], dict) else None}
        if fmt in ("csv", "tsv"):
            sep = "," if fmt == "csv" else "\t"
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                header = fh.readline().rstrip("\n").split(sep)
                first = fh.readline().rstrip("\n").split(sep)
            return {"columns": header[:30], "first_row": first[:30]}
        if fmt == "pdb":
            atoms = 0
            hetatm = 0
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if line.startswith("ATOM"):
                        atoms += 1
                    elif line.startswith("HETATM"):
                        hetatm += 1
            return {"atom_records": atoms, "hetatm_records": hetatm}
        if fmt == "extxyz":
            frames = 0
            first_natoms: Optional[int] = None
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                line = fh.readline()
                while line:
                    try:
                        n = int(line.strip())
                    except ValueError:
                        line = fh.readline()
                        continue
                    if first_natoms is None:
                        first_natoms = n
                    frames += 1
                    # Skip comment + n atom lines
                    fh.readline()
                    for _ in range(n):
                        fh.readline()
                    line = fh.readline()
            return {"frames": frames, "first_natoms": first_natoms}
    except Exception as exc:
        return {"parse_error": f"{type(exc).__name__}: {exc}"}
    return None


def _detect_patterns(format_hist: Dict[str, int],
                     entries: List[Dict[str, Any]],
                     samples: List[Dict[str, Any]]) -> List[str]:
    patterns: List[str] = []
    if not format_hist:
        return patterns
    dominant = max(format_hist.items(), key=lambda kv: kv[1])
    patterns.append(f"dominant format: {dominant[0]} ({dominant[1]} files)")
    dir_names = {e["path"].rstrip("/").split("/")[-1]
                 for e in entries if e.get("type") == "dir"}
    for split in ("train", "val", "test", "s2ef_200k_uncompressed",
                  "s2ef_val_id_uncompressed"):
        if split in dir_names:
            patterns.append(f"detected split directory: {split}")
    for s in samples:
        parsed = s.get("parsed") or {}
        if "variables" in parsed:
            patterns.append(
                f"netcdf variables detected in {s['path']}: "
                f"{parsed['variables'][:6]}...")
        if "keys" in parsed and s["format"] == "hdf5":
            patterns.append(
                f"hdf5 datasets detected in {s['path']}: {parsed['keys'][:6]}")
        if "frames" in parsed:
            patterns.append(
                f"extxyz multi-frame file {s['path']}: {parsed['frames']} frames")
    return patterns


# ----------------------------------------------------------------------
# Stage 2/3: context assembly + prompt rendering
# ----------------------------------------------------------------------

def load_ai_ready_contract() -> str:
    path = REFERENCES_DIR / "ai_ready_contract.md"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_prompt_templates() -> Tuple[str, str]:
    sys_path = SCRIPT_DIR / "prompts" / "system.md"
    usr_path = SCRIPT_DIR / "prompts" / "user.md.j2"
    system = sys_path.read_text(encoding="utf-8") if sys_path.exists() else ""
    user = usr_path.read_text(encoding="utf-8") if usr_path.exists() else ""
    return system, user


def pick_few_shot(domain: str) -> Tuple[str, str, str]:
    """Return (domain, dataset, source_code) of the best available adapter."""
    candidates = FEW_SHOT_BY_DOMAIN.get(
        domain, [("climate", "era5"), ("cfd", "deepcfd"),
                 ("bio", "targetdiff"), ("matchem", "oc20")])
    for cand_domain, cand_name in candidates:
        path = ADAPTERS_DIR / cand_domain / f"{cand_name}.py"
        if path.exists():
            return cand_domain, cand_name, path.read_text(encoding="utf-8")
    return "", "", ""


def render_user_prompt(template: str, context: Dict[str, Any]) -> str:
    """Minimal Jinja-like {{ var }} substitution (avoids jinja2 dependency)."""
    def repl(match: re.Match) -> str:
        key = match.group(1).strip()
        val = context.get(key, "")
        if isinstance(val, (dict, list)):
            return json.dumps(val, indent=2, ensure_ascii=False)
        return str(val)
    return re.sub(r"\{\{\s*([^}]+?)\s*\}\}", repl, template)


# ----------------------------------------------------------------------
# Stage 4: LLM backend dispatch
# ----------------------------------------------------------------------

def _backend_host(system_prompt: str, user_prompt: str,
                  feedback: Optional[str]) -> str:
    """Host backend: emit prompt to stderr, read script from stdin.

    This is the contract used when the enclosing Agent (Claude Code /
    Codex / OpenCode / Qoder / etc.) acts as the LLM: the skill prints
    the prompt and expects the Agent to pipe the generated script back
    through stdin. Orchestrators that cannot satisfy this contract should
    use `--llm-backend file --generated-script <path>` instead.
    """
    sys.stderr.write("=" * 72 + "\n")
    sys.stderr.write("TIER2 CONVERTER SYNTHESIS PROMPT\n")
    sys.stderr.write("=" * 72 + "\n\n")
    sys.stderr.write("---- SYSTEM ----\n")
    sys.stderr.write(system_prompt + "\n\n")
    sys.stderr.write("---- USER ----\n")
    sys.stderr.write(user_prompt + "\n\n")
    if feedback:
        sys.stderr.write("---- RETRY FEEDBACK ----\n")
        sys.stderr.write(feedback + "\n\n")
    sys.stderr.write("=" * 72 + "\n")
    sys.stderr.write(
        "Paste the generated Python script below, then send EOF "
        "(Ctrl+D on POSIX, Ctrl+Z then Enter on Windows):\n"
    )
    sys.stderr.flush()
    script = sys.stdin.read()
    if not script.strip():
        raise SynthesisError(
            "host backend produced empty script on stdin",
            reason="converter_failed")
    return script


def _backend_file(generated_script: Path) -> str:
    if not generated_script.exists():
        raise SynthesisError(
            f"--generated-script not found: {generated_script}",
            reason="converter_failed")
    return generated_script.read_text(encoding="utf-8")


def _backend_openai(system_prompt: str, user_prompt: str,
                    feedback: Optional[str],
                    api_key: str, base_url: str, model: str,
                    timeout: int = 300) -> str:
    """Call an OpenAI-compatible /chat/completions endpoint.

    Uses only ``urllib`` from the stdlib so the skill stays dependency-free.
    Works with any OpenAI-compatible gateway (OpenAI, Azure, vLLM, Ollama,
    Xiaomi MiMo, DeepSeek, Moonshot, etc.).

    ``feedback`` from a previous failed validation is appended to the user
    prompt so the model can self-correct on retry.
    """
    import urllib.request
    import urllib.error

    if feedback:
        user_prompt = (
            user_prompt
            + "\n\n## Retry feedback (previous attempt failed validation)\n\n"
            + "Fix ALL the issues below and regenerate the complete script:\n\n"
            + feedback
        )

    url = base_url.rstrip("/") + "/chat/completions"
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "stream": False,
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8", errors="replace")[:1024]
        except Exception:
            pass
        raise SynthesisError(
            f"OpenAI-compatible API HTTP {exc.code}: {detail}",
            reason="llm_backend_error",
            details={"status": exc.code, "url": url, "model": model},
        ) from exc
    except urllib.error.URLError as exc:
        raise SynthesisError(
            f"OpenAI-compatible API network error: {exc.reason}",
            reason="llm_backend_error",
            details={"url": url, "model": model},
        ) from exc
    except Exception as exc:
        raise SynthesisError(
            f"OpenAI-compatible API call failed: {type(exc).__name__}: {exc}",
            reason="llm_backend_error",
            details={"url": url, "model": model},
        ) from exc

    try:
        parsed = json.loads(raw)
        content = parsed["choices"][0]["message"]["content"]
    except (json.JSONDecodeError, KeyError, IndexError) as exc:
        raise SynthesisError(
            f"malformed API response: {raw[:512]}",
            reason="llm_backend_error",
            details={"url": url, "model": model},
        ) from exc
    if not content or not content.strip():
        raise SynthesisError(
            "API returned empty content",
            reason="llm_backend_error",
            details={"url": url, "model": model},
        )
    return content


def _strip_code_fences(text: str) -> str:
    """Remove ```python ... ``` fences if the LLM wrapped the output."""
    stripped = text.strip()
    if stripped.startswith("```"):
        first_nl = stripped.find("\n")
        if first_nl != -1:
            stripped = stripped[first_nl + 1:]
        if stripped.rstrip().endswith("```"):
            stripped = stripped.rstrip()[:-3]
    return stripped.strip() + "\n"


# ----------------------------------------------------------------------
# Stage 5-7: synthesis loop + execution
# ----------------------------------------------------------------------

@dataclass
class SynthesisResult:
    ok: bool
    tier: int = 2
    handler: str = "llm_synth:v1"
    script_path: Optional[str] = None
    prompt_snapshot_path: Optional[str] = None
    probe_report_path: Optional[str] = None
    attempts: int = 0
    validation_reports: List[Dict[str, Any]] = None  # type: ignore[assignment]
    execution: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0

    def __post_init__(self) -> None:
        if self.validation_reports is None:
            self.validation_reports = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "tier": self.tier,
            "handler": self.handler,
            "script_path": self.script_path,
            "prompt_snapshot_path": self.prompt_snapshot_path,
            "probe_report_path": self.probe_report_path,
            "attempts": self.attempts,
            "validation_reports": self.validation_reports,
            "execution": self.execution,
            "error": self.error,
            "duration_seconds": round(self.duration_seconds, 3),
        }


def synthesize(dataset_name: str, domain: str, source_dir: Path,
               target_dir: Path, spec: Dict[str, Any],
               llm_backend: str = "host",
               generated_script: Optional[Path] = None,
               max_retries: int = 2,
               dry_run: bool = False,
               openai_api_key: Optional[str] = None,
               openai_base_url: Optional[str] = None,
               openai_model: Optional[str] = None) -> SynthesisResult:
    started = time.time()
    result = SynthesisResult(ok=False)

    # ---- 1. Probe raw ----
    probe_report = probe_raw(source_dir)

    # ---- 2. Assemble context ----
    fs_domain, fs_dataset, fs_source = pick_few_shot(domain)
    spec_md = spec.get("spec_md") or spec.get("spec_md_full") or ""
    usage_md = spec.get("usage_md") or spec.get("usage_md_full") or ""
    if not spec_md:
        # Fall back to serializing whatever spec fields we do have.
        spec_md = json.dumps(
            {k: v for k, v in spec.items() if not k.startswith("_")},
            indent=2, ensure_ascii=False)

    system_prompt, user_template = load_prompt_templates()
    if not system_prompt or not user_template:
        raise SynthesisError(
            "prompt templates missing under scripts/llm_converter/prompts/",
            reason="converter_failed")

    context = {
        "dataset_name": dataset_name,
        "domain": domain,
        "few_shot_domain": fs_domain,
        "few_shot_dataset": fs_dataset,
        "spec_md_full": spec_md,
        "usage_md_full": usage_md,
        "raw_probe_report_json": json.dumps(probe_report, indent=2,
                                            ensure_ascii=False),
        "ai_ready_contract_md": load_ai_ready_contract(),
        "few_shot_adapter_source": fs_source,
    }
    user_prompt = render_user_prompt(user_template, context)

    # ---- 3. Persist audit artifacts ----
    converter_dir = target_dir / "_converter"
    converter_dir.mkdir(parents=True, exist_ok=True)
    script_path = converter_dir / f"convert_{dataset_name.lower().replace('-', '_')}.py"
    prompt_path = converter_dir / "prompt_snapshot.md"
    probe_path = converter_dir / "raw_probe_report.json"
    probe_path.write_text(json.dumps(probe_report, indent=2, ensure_ascii=False),
                          encoding="utf-8")
    prompt_path.write_text(
        "# SYSTEM\n\n" + system_prompt +
        "\n\n# USER\n\n" + user_prompt + "\n",
        encoding="utf-8")
    result.prompt_snapshot_path = str(prompt_path)
    result.probe_report_path = str(probe_path)

    if dry_run:
        result.ok = True
        result.error = None
        result.duration_seconds = time.time() - started
        result.script_path = str(script_path) + " (dry-run: not generated)"
        return result

    # ---- 4. Synthesis loop with validation ----
    # Resolve OpenAI-compatible backend params from args or env.
    oa_key = openai_api_key or os.environ.get("ONESCIENCE_LLM_API_KEY") \
        or os.environ.get("OPENAI_API_KEY")
    oa_url = openai_base_url or os.environ.get("ONESCIENCE_LLM_BASE_URL") \
        or os.environ.get("OPENAI_BASE_URL")
    oa_model = openai_model or os.environ.get("ONESCIENCE_LLM_MODEL") \
        or os.environ.get("OPENAI_MODEL")
    openai_ready = bool(oa_key and oa_url and oa_model)

    feedback: Optional[str] = None
    for attempt in range(1, max_retries + 2):
        result.attempts = attempt
        try:
            if llm_backend == "file":
                if generated_script is None:
                    raise SynthesisError(
                        "--llm-backend file requires --generated-script",
                        reason="converter_failed")
                raw_script = _backend_file(generated_script)
            elif llm_backend == "openai":
                if not openai_ready:
                    raise SynthesisError(
                        "--llm-backend openai requires api_key + base_url + "
                        "model (via --openai-* args or ONESCIENCE_LLM_* / "
                        "OPENAI_* env vars)",
                        reason="converter_failed")
                raw_script = _backend_openai(
                    system_prompt, user_prompt, feedback,
                    api_key=oa_key, base_url=oa_url, model=oa_model)
            elif llm_backend == "host":
                raw_script = _backend_host(system_prompt, user_prompt, feedback)
            elif llm_backend == "none":
                raise SynthesisError(
                    "Tier2 synthesis requires an LLM backend; pass "
                    "--llm-backend openai (with ONESCIENCE_LLM_* env), "
                    "--llm-backend host (interactive) or "
                    "--llm-backend file --generated-script <path> "
                    "(when orchestrator delegates to onescience-coder)",
                    reason="converter_failed")
            elif llm_backend == "auto":
                # Auto priority: pre-generated file > openai (if configured)
                # > host (interactive).
                if generated_script and Path(generated_script).exists():
                    raw_script = _backend_file(Path(generated_script))
                elif openai_ready:
                    raw_script = _backend_openai(
                        system_prompt, user_prompt, feedback,
                        api_key=oa_key, base_url=oa_url, model=oa_model)
                else:
                    raw_script = _backend_host(system_prompt, user_prompt,
                                               feedback)
            else:
                raise SynthesisError(
                    f"unknown llm_backend: {llm_backend}",
                    reason="converter_failed")
        except SynthesisError as exc:
            result.error = str(exc)
            result.duration_seconds = time.time() - started
            return result

        script_source = _strip_code_fences(raw_script)
        report = validate_generated.validate(script_source)
        result.validation_reports.append({
            "attempt": attempt, "ok": report.ok,
            "errors": [i.to_dict() for i in report.errors()],
            "warnings": [i.to_dict() for i in report.warnings()],
            "stats": report.stats,
        })
        if not report.ok:
            # Build retry feedback from the static-validation error list.
            err_lines = "\n".join(
                f"  - line {i.lineno}: [{i.code}] {i.message}"
                for i in report.errors())
            feedback = (
                "Your previous output failed static validation with the "
                f"following errors:\n{err_lines}\n\n"
                "Regenerate the script fixing all listed errors. Do not "
                "introduce new hardcoded paths, network imports, or writes "
                "to source_dir."
            )
            continue

        # Static validation passed — persist and execute.
        script_path.write_text(script_source, encoding="utf-8")
        result.script_path = str(script_path)
        exec_result = _execute_script(script_path, source_dir, target_dir, spec)
        result.execution = exec_result
        if exec_result.get("ok"):
            result.ok = True
            result.error = None
            break
        # Execution failed at runtime: feed the traceback back to the LLM so
        # the next attempt can self-correct (e.g. SameFileError from copying
        # its own script, missing optional dep, array shape mismatch).
        stderr_tail = (exec_result.get("stderr_tail") or "")[-2000:]
        stdout_tail = (exec_result.get("stdout_tail") or "")[-500:]
        feedback = (
            "Your previous script passed static validation but FAILED AT "
            f"RUNTIME (exit code {exec_result.get('returncode')}).\n\n"
            f"stderr:\n{stderr_tail}\n\n"
            f"stdout:\n{stdout_tail}\n\n"
            "Regenerate the COMPLETE script fixing this runtime error. "
            "Common causes: copying/moving your own script file (__file__) "
            "into a path where it already exists (SameFileError), missing "
            "optional dependencies, array shape mismatches, or writing into "
            "--source-dir. Do NOT copy, move, or re-save your own script "
            "file; the orchestrator already persists it to _converter/."
        )
    else:
        # Exhausted all attempts without a successful execution.
        result.ok = False
        if result.execution and not result.execution.get("ok"):
            result.error = (
                f"converter failed at runtime after {result.attempts} "
                f"attempts: {result.execution.get('error')}"
            )
        else:
            result.error = (
                f"script failed static validation after {result.attempts} "
                f"attempts; last errors: "
                f"{[i.to_dict() for i in report.errors()]}"
            )
    result.duration_seconds = time.time() - started
    return result


def _execute_script(script_path: Path, source_dir: Path, target_dir: Path,
                    spec: Dict[str, Any]) -> Dict[str, Any]:
    spec_file = target_dir / "_converter" / "spec_input.json"
    spec_file.parent.mkdir(parents=True, exist_ok=True)
    spec_file.write_text(json.dumps(spec, indent=2, ensure_ascii=False),
                         encoding="utf-8")
    cmd = [sys.executable, str(script_path),
           "--source-dir", str(source_dir),
           "--target-dir", str(target_dir),
           "--spec-json", str(spec_file)]
    if "--seed" in script_path.read_text(encoding="utf-8"):
        cmd += ["--seed", str(int(spec.get("seed", 42)))]
    started = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=int(os.environ.get(
                                  "ONESCIENCE_STANDARDIZER_TIMEOUT", "7200")))
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "converter execution timed out",
                "duration_seconds": time.time() - started}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}",
                "duration_seconds": time.time() - started}
    stdout_summary: Optional[Dict[str, Any]] = None
    for line in reversed((proc.stdout or "").strip().splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                stdout_summary = json.loads(line)
                break
            except json.JSONDecodeError:
                continue
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-2048:],
        "stderr_tail": (proc.stderr or "")[-2048:],
        "summary": stdout_summary,
        "duration_seconds": round(time.time() - started, 3),
        "error": None if proc.returncode == 0 else
                 f"converter exited with rc={proc.returncode}",
    }


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def _cli() -> int:
    parser = argparse.ArgumentParser(
        description="Tier2 LLM-synthesized converter orchestrator")
    parser.add_argument("--dataset-name", required=True)
    parser.add_argument("--domain", required=True)
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--target-dir", required=True)
    parser.add_argument("--spec-json", default=None,
                        help="Path to serialized primitives spec JSON")
    parser.add_argument("--llm-backend", default="auto",
                        choices=["auto", "host", "file", "openai", "none"])
    parser.add_argument("--generated-script", default=None,
                        help="Pre-generated script path (for backend=file)")
    parser.add_argument("--openai-api-key", default=None,
                        help="OpenAI-compatible API key (or ONESCIENCE_LLM_API_KEY / OPENAI_API_KEY env)")
    parser.add_argument("--openai-base-url", default=None,
                        help="OpenAI-compatible base URL (or ONESCIENCE_LLM_BASE_URL / OPENAI_BASE_URL env)")
    parser.add_argument("--openai-model", default=None,
                        help="Model name (or ONESCIENCE_LLM_MODEL / OPENAI_MODEL env)")
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    spec: Dict[str, Any] = {}
    if args.spec_json:
        p = Path(args.spec_json).expanduser()
        if p.exists():
            spec = json.loads(p.read_text(encoding="utf-8"))

    try:
        result = synthesize(
            dataset_name=args.dataset_name,
            domain=args.domain,
            source_dir=Path(args.source_dir),
            target_dir=Path(args.target_dir),
            spec=spec,
            llm_backend=args.llm_backend,
            generated_script=Path(args.generated_script)
                              if args.generated_script else None,
            max_retries=args.max_retries,
            dry_run=args.dry_run,
            openai_api_key=args.openai_api_key,
            openai_base_url=args.openai_base_url,
            openai_model=args.openai_model,
        )
    except SynthesisError as exc:
        print(json.dumps({"ok": False, "reason": exc.reason,
                          "message": str(exc), "details": exc.details},
                         indent=2, ensure_ascii=False), file=sys.stderr)
        return 1

    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(_cli())
