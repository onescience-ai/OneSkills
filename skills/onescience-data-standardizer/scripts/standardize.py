"""Main CLI entrypoint for onescience-data-standardizer.

Subcommands:
    run       - full six-stage standardization pipeline
    registry  - manage ~/.onescience/data_management.json (delegates to registry.py)
    probe     - probe source resolution without executing conversion
    report    - probe / call dataset_report tool

The `run` subcommand implements the six-stage flow described in SKILL.md:
    1. input parsing + domain normalization
    2. three-stage source resolution
    3. target spec fetch (via onescience-primitives)
    4. converter selection (Tier1 adapter or Tier2 LLM synth) + execution
    5. validation + registration + dataset_report
    6. execution_result emission

Stage 3 (primitives fetch) is delegated to the caller in normal skill mode:
the orchestrator / host Agent performs `resource_retrieval_request` and
passes the spec content via --spec-json. When invoked as a standalone CLI
without a spec, we fall back to a minimal default spec so Tier1 adapters can
still run against well-known datasets.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import registry as registry_mod           # noqa: E402
import report_probe as report_mod         # noqa: E402
import resolve_source as resolver_mod     # noqa: E402
import download_modelscope as dl_mod      # noqa: E402

VALID_DOMAINS = resolver_mod.VALID_DOMAINS


class StandardizerError(RuntimeError):
    def __init__(self, message: str, *, reason: str,
                 details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.reason = reason
        self.details = details or {}


# ----------------------------------------------------------------------
# Stage 4 helpers: Tier selection + adapter loading
# ----------------------------------------------------------------------

# Domain alias map — mirrors resolve_source.DOMAIN_ALIASES. Kept as a local
# constant so this module has no hard import dependency on resolve_source
# (which in turn imports modelscope lazily).
DOMAIN_CANONICAL = {
    "earth": "climate", "climate": "climate",
    "materials": "matchem", "matchem": "matchem",
    "biology": "bio", "bio": "bio",
    "fluid": "cfd", "cfd": "cfd",
}


def _canonical_domain(domain: str) -> str:
    return DOMAIN_CANONICAL.get((domain or "").strip().lower(), (domain or "").strip().lower())


def _adapter_path(domain: str, dataset_name: str) -> Path:
    canonical = _canonical_domain(domain)
    normalized = dataset_name.lower().replace("-", "_")
    return SCRIPT_DIR / "adapters" / canonical / f"{normalized}.py"


def select_tier(domain: str, dataset_name: str) -> Tuple[int, str, Optional[Path]]:
    canonical = _canonical_domain(domain)
    adapter = _adapter_path(canonical, dataset_name)
    if adapter.exists():
        return 1, f"adapter:{canonical}/{dataset_name.lower()}", adapter
    return 2, "llm_synth:v1", None


def _ensure_adapters_package() -> type:
    """Register ``adapters`` and ``adapters._base`` in sys.modules.

    Adapters do ``from adapters._base import BaseAdapter, ...`` after
    inserting ``scripts/`` into sys.path themselves. When loaded via
    ``importlib.util.spec_from_file_location`` from this parent process,
    we must pre-register the same module objects so ``issubclass`` checks
    compare against the identical ``BaseAdapter`` class.
    """
    if SCRIPT_DIR not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))

    if "adapters" not in sys.modules:
        pkg_spec = importlib.util.spec_from_file_location(
            "adapters",
            SCRIPT_DIR / "adapters" / "__init__.py"
            if (SCRIPT_DIR / "adapters" / "__init__.py").exists()
            else None,
            submodule_search_locations=[str(SCRIPT_DIR / "adapters")],
        )
        if pkg_spec is None or pkg_spec.loader is None:
            # Synthesize a namespace package manually.
            import types
            pkg = types.ModuleType("adapters")
            pkg.__path__ = [str(SCRIPT_DIR / "adapters")]  # type: ignore[attr-defined]
            sys.modules["adapters"] = pkg
        else:
            pkg = importlib.util.module_from_spec(pkg_spec)
            sys.modules["adapters"] = pkg
            pkg_spec.loader.exec_module(pkg)  # type: ignore[union-attr]

    if "adapters._base" not in sys.modules:
        base_spec = importlib.util.spec_from_file_location(
            "adapters._base", SCRIPT_DIR / "adapters" / "_base.py")
        if base_spec is None or base_spec.loader is None:
            raise StandardizerError(
                f"cannot import adapters._base from {SCRIPT_DIR}",
                reason="converter_failed",
            )
        base_mod = importlib.util.module_from_spec(base_spec)
        sys.modules["adapters._base"] = base_mod
        base_spec.loader.exec_module(base_mod)  # type: ignore[union-attr]

    return sys.modules["adapters._base"].BaseAdapter  # type: ignore[attr-defined]


def _load_adapter_class(adapter_file: Path) -> type:
    """Import an adapter module by path and locate its BaseAdapter subclass."""
    BaseAdapter = _ensure_adapters_package()

    # Register the adapter's own domain package (e.g. ``adapters.cfd``) so
    # relative-style imports inside the adapter resolve consistently.
    domain_pkg_name = adapter_file.parent.name
    full_pkg = f"adapters.{domain_pkg_name}"
    if full_pkg not in sys.modules:
        import types
        pkg = types.ModuleType(full_pkg)
        pkg.__path__ = [str(adapter_file.parent)]  # type: ignore[attr-defined]
        sys.modules[full_pkg] = pkg

    mod_name = f"{full_pkg}.{adapter_file.stem}"
    spec = importlib.util.spec_from_file_location(mod_name, adapter_file)
    if spec is None or spec.loader is None:
        raise StandardizerError(
            f"cannot import adapter: {adapter_file}",
            reason="converter_failed",
        )
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    try:
        spec.loader.exec_module(module)  # type: ignore[union-attr]
    except Exception as exc:
        sys.modules.pop(mod_name, None)
        raise StandardizerError(
            f"adapter import error: {exc}",
            reason="converter_failed",
            details={"traceback": traceback.format_exc()},
        ) from exc

    candidates = [
        obj for name, obj in vars(module).items()
        if isinstance(obj, type) and issubclass(obj, BaseAdapter)
        and obj is not BaseAdapter
    ]
    if not candidates:
        raise StandardizerError(
            f"no BaseAdapter subclass found in {adapter_file}",
            reason="converter_failed",
        )
    # Prefer the class whose dataset_name matches the requested one.
    return candidates[0]


def run_tier1(adapter_file: Path, source_dir: Path, target_dir: Path,
              spec: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a Tier1 adapter in-process (preferred) or via subprocess."""
    try:
        adapter_cls = _load_adapter_class(adapter_file)
    except StandardizerError:
        raise
    adapter = adapter_cls(source_dir=source_dir, target_dir=target_dir,
                          spec=spec, dry_run=False)
    return adapter.run()


def run_tier2(source_dir: Path, target_dir: Path, spec: Dict[str, Any],
              dataset_name: str, domain: str,
              llm_backend: str = "auto",
              generated_script: Optional[Path] = None,
              max_retries: int = 2,
              openai_api_key: Optional[str] = None,
              openai_base_url: Optional[str] = None,
              openai_model: Optional[str] = None) -> Dict[str, Any]:
    """Delegate to llm_converter/synthesize.py.

    Valid ``llm_backend`` values (aligned with synthesize.py):
      - ``auto``: prefer ``file`` when --generated-script is provided,
                  otherwise fall back to ``host``
      - ``host``: interactive stdin/stdout protocol with the enclosing Agent
      - ``file``: read a pre-generated converter script from disk
      - ``none``: abort with a diagnostic
    """
    synth = SCRIPT_DIR / "llm_converter" / "synthesize.py"
    if not synth.exists():
        raise StandardizerError(
            f"Tier2 synthesizer missing: {synth}",
            reason="converter_failed",
        )
    cmd = [
        sys.executable, str(synth),
        "--dataset-name", dataset_name,
        "--domain", domain,
        "--source-dir", str(source_dir),
        "--target-dir", str(target_dir),
        "--llm-backend", llm_backend,
        "--max-retries", str(int(max_retries)),
    ]
    if generated_script:
        cmd += ["--generated-script", str(generated_script)]
    if openai_api_key:
        cmd += ["--openai-api-key", openai_api_key]
    if openai_base_url:
        cmd += ["--openai-base-url", openai_base_url]
    if openai_model:
        cmd += ["--openai-model", openai_model]
    spec_file = target_dir / "_converter" / "spec_input.json"
    spec_file.parent.mkdir(parents=True, exist_ok=True)
    spec_file.write_text(json.dumps(spec, indent=2, ensure_ascii=False),
                         encoding="utf-8")
    cmd += ["--spec-json", str(spec_file)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise StandardizerError(
            f"Tier2 synthesizer failed (rc={proc.returncode}): "
            f"{(proc.stderr or proc.stdout or '')[:2048]}",
            reason="converter_failed",
            details={"returncode": proc.returncode,
                     "stderr": proc.stderr[-2048:] if proc.stderr else ""},
        )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"tier": 2, "handler": "llm_synth:v1",
                "target_dir": str(target_dir),
                "raw_stdout": proc.stdout[-2048:]}


# ----------------------------------------------------------------------
# Stage 5 helpers: validation + registration + report
# ----------------------------------------------------------------------

REQUIRED_CARD_FIELDS = ("schema_version", "name", "domain", "handler",
                        "source", "target", "target_schema", "quality_checks")


def validate_output(target_dir: Path, dataset_name: str,
                    domain: str) -> Dict[str, Any]:
    """Lightweight built-in validation (fallback for onescience-dataset-builder)."""
    result: Dict[str, Any] = {
        "format_valid": False,
        "required_files_present": [],
        "warnings": [],
        "errors": [],
    }
    card_path = target_dir / "dataset_card.json"
    data_dir = target_dir / "data"
    readme_path = target_dir / "README.md"

    present: List[str] = []
    if card_path.exists():
        present.append("dataset_card.json")
    else:
        result["errors"].append("dataset_card.json missing")
    if data_dir.exists() and data_dir.is_dir() and any(data_dir.iterdir()):
        present.append("data/")
    else:
        result["errors"].append("data/ missing or empty")
    if readme_path.exists() and readme_path.stat().st_size > 0:
        present.append("README.md")
    else:
        result["errors"].append("README.md missing or empty")
    result["required_files_present"] = present

    if card_path.exists():
        try:
            card = json.loads(card_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            result["errors"].append(f"dataset_card.json unreadable: {exc}")
            card = None
        if isinstance(card, dict):
            missing = [f for f in REQUIRED_CARD_FIELDS if f not in card]
            if missing:
                result["errors"].append(
                    f"dataset_card.json missing fields: {missing}")
            card_name = str(card.get("name") or "")
            # Case-insensitive + separator-tolerant comparison: adapters may
            # canonicalize (DeepCFD vs deepcfd, ERA5 vs era5, OC20 vs oc20).
            def _norm(s: str) -> str:
                return s.lower().replace("-", "_").replace(" ", "_")
            if _norm(card_name) != _norm(dataset_name):
                result["errors"].append(
                    f"card.name={card_name!r} != expected {dataset_name!r} "
                    f"(after case/separator normalization)")
            card_domain = str(card.get("domain") or "")
            domain_aliases = {domain, domain.lower()}
            # Accept earth<->climate, materials<->matchem, biology<->bio, fluid<->cfd
            alias_map = {
                "earth": "climate", "climate": "climate",
                "materials": "matchem", "matchem": "matchem",
                "biology": "bio", "bio": "bio",
                "fluid": "cfd", "cfd": "cfd",
            }
            canonical_expected = alias_map.get(domain.lower())
            canonical_card = alias_map.get(card_domain.lower())
            if canonical_card is None:
                result["errors"].append(
                    f"card.domain={card_domain!r} not in {VALID_DOMAINS}")
            elif canonical_expected and canonical_card != canonical_expected:
                result["errors"].append(
                    f"card.domain={card_domain!r} != expected {domain!r} "
                    f"(canonical: {canonical_card} vs {canonical_expected})")
            target_in_card = card.get("target", {}).get("dir")
            if target_in_card and \
                    Path(target_in_card).resolve() != target_dir.resolve():
                result["warnings"].append(
                    f"card.target.dir={target_in_card!r} differs from {target_dir}")

    result["format_valid"] = not result["errors"]
    return result


def register(name: str, domain: str, source_dir: str, target_dir: str,
             handler: str, resolution_method: str,
             modelscope_repo_id: Optional[str],
             dataset_report_called: bool) -> Dict[str, Any]:
    entry = {
        "name": name,
        "domain": domain,
        "source_dir": source_dir,
        "target_dir": target_dir,
        "handler": handler,
        "source_resolution_method": resolution_method,
        "modelscope_repo_id": modelscope_repo_id,
        "dataset_card_path": str(Path(target_dir) / "dataset_card.json"),
        "dataset_report_called": dataset_report_called,
    }
    return registry_mod.upsert(entry)


# ----------------------------------------------------------------------
# Stage 3 helper: default spec fallback
# ----------------------------------------------------------------------

def _default_spec(dataset_name: str, domain: str) -> Dict[str, Any]:
    """Minimal spec used when the caller did not supply --spec-json.

    Real skill invocations must pass the primitives-provided spec; this
    fallback only exists so Tier1 adapters can be exercised from a bare CLI.
    """
    return {
        "version": "1.0.0",
        "_spec_source": f"onescience-primitives:{domain}/datasets/{dataset_name}/spec.md",
        "_default_fallback": True,
        "data_schema": {},
        "storage_format": "",
        "scale_spec": "",
        "label_spec": "",
        "split_strategy": "",
    }


# ----------------------------------------------------------------------
# `run` subcommand: the full pipeline
# ----------------------------------------------------------------------

def cmd_run(args: argparse.Namespace) -> int:
    started = time.time()
    execution_result: Dict[str, Any] = {
        "skill": "onescience-data-standardizer",
        "status": "failed",
        "artifacts": {},
        "observation": {
            "summary": "",
            "completed": [],
            "tier": None,
            "validation": {},
            "source_resolution": {},
            "dataset_report": {},
            "risks": [],
            "next_recommendation": "",
        },
    }

    dataset_name = args.dataset_name
    domain_input = args.domain

    # ---- Stage 1: input parsing + domain normalization ----
    domain = resolver_mod.normalize_domain(domain_input)
    if domain_input and not domain:
        execution_result["status"] = "blocked"
        execution_result["blocked_reason"] = "invalid_domain"
        execution_result["blocked_details"] = (
            f"domain={domain_input!r} not in {VALID_DOMAINS} (aliases accepted)"
        )
        _emit(execution_result, args.output)
        return 2
    execution_result["observation"]["completed"].append("parse_input")

    # ---- Stage 2: source resolution ----
    decision = resolver_mod.resolve(
        dataset_name=dataset_name,
        domain=domain,
        source_dir=args.source_dir,
        allow_download=args.allow_download,
        autonomous_mode=args.autonomous_mode,
        modelscope_repo_id=args.modelscope_repo_id,
    )
    execution_result["observation"]["source_resolution"] = decision.to_dict()
    if decision.blocked_reason:
        execution_result["status"] = "blocked"
        execution_result["blocked_reason"] = decision.blocked_reason
        execution_result["blocked_details"] = decision.blocked_details
        _emit(execution_result, args.output)
        return 2

    # Domain may be inferred during resolution when absent.
    domain = decision.domain or domain
    if not domain:
        execution_result["status"] = "blocked"
        execution_result["blocked_reason"] = "domain_unresolved"
        execution_result["blocked_details"] = (
            "domain could not be inferred; pass --domain explicitly or ensure "
            "primitives returns detected_domain"
        )
        _emit(execution_result, args.output)
        return 2

    # ---- Stage 3 (optional): ModelScope download ----
    modelscope_repo_id: Optional[str] = None
    if decision.needs_download:
        try:
            dl_result = dl_mod.download(
                dataset_name=dataset_name,
                repo_id=args.modelscope_repo_id,
                repo_type=args.repo_type,
                revision=args.revision,
                allow_git_lfs_fallback=args.allow_git_lfs_fallback,
                repo_id_source="explicit" if args.modelscope_repo_id
                else "default_convention",
            )
        except dl_mod.DownloadError as exc:
            execution_result["status"] = "blocked"
            execution_result["blocked_reason"] = exc.reason
            execution_result["blocked_details"] = str(exc)
            execution_result["observation"]["source_resolution"][
                "download_details"] = exc.details
            _emit(execution_result, args.output)
            return 2
        decision.resolved_path = dl_result.cache_dir
        decision.method = "modelscope_download"
        modelscope_repo_id = dl_result.repo_id
        execution_result["observation"]["source_resolution"][
            "download_details"] = dl_result.to_dict()
        execution_result["observation"]["completed"].append("download_raw")

    source_dir = Path(decision.resolved_path)  # type: ignore[arg-type]
    execution_result["observation"]["completed"].append("resolve_source")

    # ---- Target dir ----
    target_dir = Path(args.target_dir).expanduser() if args.target_dir \
        else resolver_mod.default_target_dir(dataset_name, domain)
    target_dir = target_dir.resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    # ---- Stage 3b: target spec fetch ----
    spec: Dict[str, Any]
    if args.spec_json:
        spec_path = Path(args.spec_json).expanduser()
        if not spec_path.exists():
            execution_result["status"] = "blocked"
            execution_result["blocked_reason"] = "target_spec_missing"
            execution_result["blocked_details"] = (
                f"--spec-json path does not exist: {spec_path}"
            )
            _emit(execution_result, args.output)
            return 2
        try:
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            execution_result["status"] = "blocked"
            execution_result["blocked_reason"] = "target_spec_missing"
            execution_result["blocked_details"] = f"cannot read spec: {exc}"
            _emit(execution_result, args.output)
            return 2
    else:
        spec = _default_spec(dataset_name, domain)
        execution_result["observation"]["risks"].append(
            "using default spec fallback; real skill invocations should pass "
            "--spec-json sourced from onescience-primitives"
        )
    spec["_source_resolution_method"] = decision.method
    spec["_modelscope_repo_id"] = modelscope_repo_id
    execution_result["observation"]["completed"].append("fetch_target_spec")

    # ---- Stage 4: converter selection + execution ----
    tier, handler, adapter_file = select_tier(domain, dataset_name)
    execution_result["observation"]["tier"] = tier
    execution_result["observation"]["completed"].append("select_converter")

    try:
        if tier == 1:
            assert adapter_file is not None
            summary = run_tier1(adapter_file, source_dir, target_dir, spec)
        else:
            summary = run_tier2(source_dir, target_dir, spec,
                                dataset_name, domain,
                                llm_backend=args.llm_backend,
                                generated_script=(
                                    Path(args.generated_script).expanduser()
                                    if args.generated_script else None),
                                max_retries=args.max_retries,
                                openai_api_key=args.openai_api_key,
                                openai_base_url=args.openai_base_url,
                                openai_model=args.openai_model)
    except StandardizerError as exc:
        execution_result["status"] = "failed"
        execution_result["blocked_reason"] = exc.reason
        execution_result["blocked_details"] = str(exc)
        _emit(execution_result, args.output)
        return 1
    except Exception as exc:
        execution_result["status"] = "failed"
        execution_result["blocked_reason"] = "converter_failed"
        execution_result["blocked_details"] = (
            f"{type(exc).__name__}: {exc}\n{traceback.format_exc()[-2048:]}"
        )
        _emit(execution_result, args.output)
        return 1
    execution_result["observation"]["completed"].append("convert")

    # ---- Stage 5: validate + register + report ----
    validation = validate_output(target_dir, dataset_name, domain)
    execution_result["observation"]["validation"] = validation
    if not validation["format_valid"]:
        execution_result["status"] = "partial"
        execution_result["observation"]["risks"].extend(validation["errors"])
    else:
        execution_result["status"] = "success"
    execution_result["observation"]["completed"].append("validate")

    payload = report_mod.build_payload(dataset_name, str(target_dir),
                                       str(source_dir))
    report_result = report_mod.call(payload)
    execution_result["observation"]["dataset_report"] = report_result
    execution_result["observation"]["completed"].append("report")

    try:
        registry_entry = register(
            name=dataset_name,
            domain=domain,
            source_dir=str(source_dir),
            target_dir=str(target_dir),
            handler=handler,
            resolution_method=decision.method,
            modelscope_repo_id=modelscope_repo_id,
            dataset_report_called=bool(report_result.get("called")),
        )
    except registry_mod.RegistryError as exc:
        execution_result["status"] = "partial"
        execution_result["observation"]["risks"].append(
            f"registry write failed: {exc}")
        registry_entry = None
    execution_result["observation"]["completed"].append("register")

    execution_result["artifacts"] = {
        "name": dataset_name,
        "domain": domain,
        "source_dir": str(source_dir),
        "target_dir": str(target_dir),
        "handler": handler,
        "dataset_card": str(target_dir / "dataset_card.json"),
        "registry_path": str(registry_mod.registry_path()),
        "registry_entry": registry_entry,
        "dataset_report_called": bool(report_result.get("called")),
        "dataset_report_payload": payload,
        "converter_summary": summary,
    }
    execution_result["observation"]["summary"] = (
        f"{dataset_name} ({domain}) standardized to {target_dir} "
        f"via tier={tier} handler={handler}"
    )
    execution_result["observation"]["duration_seconds"] = round(
        time.time() - started, 3)
    if tier == 2:
        execution_result["observation"]["next_recommendation"] = (
            "if this dataset is used repeatedly, promote "
            f"{target_dir}/_converter/convert_*.py to "
            f"scripts/adapters/{domain}/{dataset_name.lower()}.py after review"
        )
    else:
        execution_result["observation"]["next_recommendation"] = (
            "ready for downstream training/datapipe consumption; optionally "
            "invoke onescience-dataset-builder task 2 for deeper validation"
        )

    _emit(execution_result, args.output)
    return 0 if execution_result["status"] == "success" else 1


def _emit(result: Dict[str, Any], output: Optional[str]) -> None:
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if output:
        Path(output).expanduser().parent.mkdir(parents=True, exist_ok=True)
        Path(output).expanduser().write_text(text, encoding="utf-8")
        print(f"execution_result written to {output}", file=sys.stderr)
    print(text)


# ----------------------------------------------------------------------
# Subcommand plumbing
# ----------------------------------------------------------------------

def cmd_probe(args: argparse.Namespace) -> int:
    decision = resolver_mod.resolve(
        dataset_name=args.dataset_name,
        domain=args.domain,
        source_dir=args.source_dir,
        allow_download=args.allow_download,
        autonomous_mode=args.autonomous_mode,
        modelscope_repo_id=args.modelscope_repo_id,
    )
    print(json.dumps(decision.to_dict(), indent=2, ensure_ascii=False))
    return 0 if decision.method != "none" else 1


def cmd_report(args: argparse.Namespace) -> int:
    return report_mod._cli(
        ["probe"] if args.probe_only else
        ["call", "--name", args.name, "--target-dir", args.target_dir] +
        (["--source-dir", args.source_dir] if args.source_dir else [])
    )


def cmd_registry(args: argparse.Namespace) -> int:
    return registry_mod._cli(args.registry_args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="standardize.py",
        description="OneScience data standardizer: raw dataset -> AI-Ready",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="Run the full six-stage pipeline")
    p_run.add_argument("--dataset-name", required=True)
    p_run.add_argument("--domain", default=None,
                       help="cfd|bio|climate|earth|matchem (aliases accepted)")
    p_run.add_argument("--source-dir", default=None)
    p_run.add_argument("--target-dir", default=None)
    p_run.add_argument("--spec-json", default=None,
                       help="Path to primitives-provided spec JSON")
    p_run.add_argument("--allow-download", action="store_true")
    p_run.add_argument("--autonomous-mode", action="store_true")
    p_run.add_argument("--modelscope-repo-id", default=None)
    p_run.add_argument("--repo-type", default="dataset",
                       choices=["dataset", "model"])
    p_run.add_argument("--revision", default=None)
    p_run.add_argument("--allow-git-lfs-fallback", action="store_true")
    p_run.add_argument("--llm-backend", default="auto",
                       choices=["auto", "host", "file", "openai", "none"],
                       help="Tier2 backend: auto|host|file|openai|none "
                            "(must match synthesize.py)")
    p_run.add_argument("--generated-script", default=None,
                       help="Pre-generated Tier2 converter path "
                            "(required when --llm-backend=file)")
    p_run.add_argument("--openai-api-key", default=None,
                       help="OpenAI-compatible API key (or ONESCIENCE_LLM_API_KEY env)")
    p_run.add_argument("--openai-base-url", default=None,
                       help="OpenAI-compatible base URL (or ONESCIENCE_LLM_BASE_URL env)")
    p_run.add_argument("--openai-model", default=None,
                       help="Model name (or ONESCIENCE_LLM_MODEL env)")
    p_run.add_argument("--max-retries", type=int, default=2,
                       help="Tier2 validation retry budget")
    p_run.add_argument("--output", default=None,
                       help="Optional path to also write execution_result JSON")
    p_run.set_defaults(func=cmd_run)

    p_probe = sub.add_parser("probe", help="Probe source resolution only")
    p_probe.add_argument("--dataset-name", required=True)
    p_probe.add_argument("--domain", default=None)
    p_probe.add_argument("--source-dir", default=None)
    p_probe.add_argument("--allow-download", action="store_true")
    p_probe.add_argument("--autonomous-mode", action="store_true")
    p_probe.add_argument("--modelscope-repo-id", default=None)
    p_probe.set_defaults(func=cmd_probe)

    p_rep = sub.add_parser("report", help="Probe/call dataset_report tool")
    p_rep.add_argument("--probe-only", action="store_true")
    p_rep.add_argument("--name", default=None)
    p_rep.add_argument("--target-dir", default=None)
    p_rep.add_argument("--source-dir", default=None)
    p_rep.set_defaults(func=cmd_report)

    p_reg = sub.add_parser("registry", help="Manage data_management.json")
    p_reg.add_argument("registry_args", nargs=argparse.REMAINDER)
    p_reg.set_defaults(func=cmd_registry)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.cmd == "report" and not args.probe_only:
        if not args.name or not args.target_dir:
            parser.error("report requires --name and --target-dir "
                         "(or use --probe-only)")
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
