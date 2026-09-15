"""Three-stage raw dataset source resolution.

Implements references/source_resolution.md:

    stage 1 - explicit path from task_context.source_dir
    stage 2 - local probe across a fixed list of candidate directories
    stage 3 - ModelScope download (gated by allow_download / autonomous_mode)

The resolver never downloads by itself; it returns a decision object that
scripts/standardize.py acts upon. This keeps side effects out of the
resolution logic and makes the module trivially testable.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

DOMAIN_ALIASES: Dict[str, str] = {
    "earth": "climate",
    "materials": "matchem",
    "material": "matchem",
    "biology": "bio",
    "bioinformatics": "bio",
    "fluid": "cfd",
    "fluids": "cfd",
    "climate": "climate",
    "cfd": "cfd",
    "bio": "bio",
    "matchem": "matchem",
}

VALID_DOMAINS = ("cfd", "bio", "climate", "matchem")


class SourceResolutionError(RuntimeError):
    pass


@dataclass
class ProbeEntry:
    path: str
    exists: bool = False
    is_dir: bool = False
    non_empty: bool = False
    readable: bool = False
    hit: bool = False
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "exists": self.exists,
            "is_dir": self.is_dir,
            "non_empty": self.non_empty,
            "readable": self.readable,
            "hit": self.hit,
            "reason": self.reason,
        }


@dataclass
class ResolutionDecision:
    method: str                              # explicit | local_probe | modelscope_download | none
    resolved_path: Optional[str] = None
    probed_paths: List[ProbeEntry] = field(default_factory=list)
    blocked_reason: Optional[str] = None
    blocked_details: Optional[str] = None
    suggested_repo_id: Optional[str] = None
    needs_download: bool = False
    domain: Optional[str] = None
    dataset_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "method": self.method,
            "resolved_path": self.resolved_path,
            "probed_paths": [p.to_dict() for p in self.probed_paths],
            "needs_download": self.needs_download,
            "domain": self.domain,
            "dataset_name": self.dataset_name,
        }
        if self.blocked_reason:
            out["blocked_reason"] = self.blocked_reason
            out["blocked_details"] = self.blocked_details
        if self.suggested_repo_id:
            out["suggested_repo_id"] = self.suggested_repo_id
        return out


def normalize_domain(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    key = raw.strip().lower()
    return DOMAIN_ALIASES.get(key, key if key in VALID_DOMAINS else None)


def _dir_ok(path: Path) -> ProbeEntry:
    entry = ProbeEntry(path=str(path))
    try:
        entry.exists = path.exists()
    except OSError as exc:
        entry.reason = f"stat failed: {exc}"
        return entry
    if not entry.exists:
        entry.reason = "does not exist"
        return entry
    entry.is_dir = path.is_dir()
    if not entry.is_dir:
        entry.reason = "not a directory"
        return entry
    try:
        entry.readable = os.access(path, os.R_OK)
    except OSError:
        entry.readable = False
    if not entry.readable:
        entry.reason = "permission denied"
        return entry
    try:
        entry.non_empty = any(path.iterdir())
    except OSError as exc:
        entry.reason = f"list failed: {exc}"
        return entry
    if not entry.non_empty:
        entry.reason = "empty directory"
        return entry
    entry.hit = True
    return entry


def _candidate_paths(dataset_name: str, domain: Optional[str]) -> List[Path]:
    """Ordered list of local probe candidates (stage 2)."""
    candidates: List[Path] = []
    name_lower = dataset_name.lower()
    env_root = os.environ.get("ONESCIENCE_DATASETS_DIR")
    if env_root:
        root = Path(env_root).expanduser()
        candidates.append(root / dataset_name)
        if domain:
            candidates.append(root / domain / dataset_name)
            candidates.append(root / domain / name_lower)
    home_cache = Path.home() / ".onescience" / "datasets"
    candidates.append(home_cache / dataset_name / "raw")
    candidates.append(home_cache / dataset_name)
    public_root = Path("/public/share/onestore/onedatasets")
    candidates.append(public_root / dataset_name)
    if domain:
        candidates.append(public_root / domain / dataset_name)
        candidates.append(public_root / domain / name_lower)
    cwd = Path.cwd()
    candidates.append(cwd / dataset_name)
    candidates.append(cwd / "data" / dataset_name)
    # Deduplicate while preserving order.
    seen: set = set()
    unique: List[Path] = []
    for p in candidates:
        key = str(p)
        if key not in seen:
            seen.add(key)
            unique.append(p)
    return unique


def _suggest_repo_id(dataset_name: str, domain: Optional[str],
                     explicit: Optional[str] = None) -> str:
    if explicit:
        return explicit
    # Default convention: OneScience/<dataset_name>. Domain prefix is added
    # only when the plain name is ambiguous, which we cannot detect here, so
    # we keep the simple form and let the downloader fall back if 404.
    return f"OneScience/{dataset_name}"


def resolve(dataset_name: str,
            domain: Optional[str] = None,
            source_dir: Optional[str] = None,
            allow_download: bool = False,
            autonomous_mode: bool = False,
            modelscope_repo_id: Optional[str] = None) -> ResolutionDecision:
    """Run the three-stage resolution and return a decision.

    Never performs IO beyond stat/listdir; never downloads.
    """
    if not dataset_name:
        raise SourceResolutionError("dataset_name is required")

    normalized_domain = normalize_domain(domain)
    decision = ResolutionDecision(
        method="none",
        domain=normalized_domain,
        dataset_name=dataset_name,
        suggested_repo_id=_suggest_repo_id(dataset_name, normalized_domain,
                                           modelscope_repo_id),
    )

    # ---- Stage 1: explicit path ----
    if source_dir:
        explicit = Path(source_dir).expanduser()
        entry = _dir_ok(explicit)
        decision.probed_paths.append(entry)
        if entry.hit:
            decision.method = "explicit"
            decision.resolved_path = str(explicit.resolve())
            return decision
        # Explicit path was provided but invalid -> hard fail, do NOT fall
        # through to probe/download. The user asked for a specific location.
        decision.blocked_reason = "source_dir_invalid"
        decision.blocked_details = (
            f"provided source_dir failed validation: {entry.reason} "
            f"(path={entry.path})"
        )
        return decision

    # ---- Stage 2: local probe ----
    for candidate in _candidate_paths(dataset_name, normalized_domain):
        entry = _dir_ok(candidate)
        decision.probed_paths.append(entry)
        if entry.hit:
            decision.method = "local_probe"
            decision.resolved_path = str(candidate.resolve())
            return decision

    # ---- Stage 3: ModelScope download gate ----
    if allow_download or autonomous_mode:
        decision.method = "modelscope_download"
        decision.needs_download = True
        return decision

    probed_list = "\n".join(f"  - {p.path} ({p.reason or 'hit'})"
                            for p in decision.probed_paths)
    decision.blocked_reason = "raw_dataset_not_found"
    decision.blocked_details = (
        f"raw dataset '{dataset_name}' not found locally. Probed paths:\n"
        f"{probed_list}\n"
        f"Suggested ModelScope repo: {decision.suggested_repo_id}\n"
        f"To proceed: set allow_download=true (or run in autonomous_mode), "
        f"or provide source_dir explicitly."
    )
    return decision


def default_target_dir(dataset_name: str, domain: Optional[str]) -> Path:
    """Compute the default AI-Ready target directory.

    Priority:
      1. ${ONESCIENCE_DATASETS_DIR}/<name>-ai-ready
      2. ~/.onescience/datasets/<name>-ai-ready
    """
    suffix = f"{dataset_name}-ai-ready"
    env_root = os.environ.get("ONESCIENCE_DATASETS_DIR")
    if env_root:
        return Path(env_root).expanduser() / suffix
    return Path.home() / ".onescience" / "datasets" / suffix


# ----------------------------------------------------------------------
# CLI (for manual probing / debugging)
# ----------------------------------------------------------------------

def _cli() -> int:
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(description="Probe raw dataset source")
    parser.add_argument("--dataset-name", required=True)
    parser.add_argument("--domain", default=None)
    parser.add_argument("--source-dir", default=None)
    parser.add_argument("--allow-download", action="store_true")
    parser.add_argument("--autonomous-mode", action="store_true")
    parser.add_argument("--modelscope-repo-id", default=None)
    args = parser.parse_args()

    decision = resolve(
        dataset_name=args.dataset_name,
        domain=args.domain,
        source_dir=args.source_dir,
        allow_download=args.allow_download,
        autonomous_mode=args.autonomous_mode,
        modelscope_repo_id=args.modelscope_repo_id,
    )
    print(json.dumps(decision.to_dict(), indent=2, ensure_ascii=False))
    return 0 if decision.method != "none" else 1


if __name__ == "__main__":
    import sys
    sys.exit(_cli())
