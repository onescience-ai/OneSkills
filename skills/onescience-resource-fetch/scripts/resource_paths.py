"""Local cache layout, probing and registry helpers for resource provisioning.

Everything this skill materializes lives under ``~/.onescience`` (user-space
cache) or a caller-supplied directory. The skill tree (``skills/**``) is a
read-only knowledge area and is never written here.

Layout:

    ~/.onescience/datasets/<name>/raw/   raw dataset payload
    ~/.onescience/models/<name>/         raw model / checkpoint payload
    ~/.onescience/resource_registry.json structured index of what is available

Environment knobs (all optional overrides of the defaults):

    ONESCIENCE_RESOURCE_HOME   relocate the cache root above (testing, or a
                               small system volume)
    ONESCIENCE_DATASETS_DIR    extra dataset probe root -- the same variable
                               ``onescience-data-standardizer`` resolves, so a
                               dataset already placed there is a hit for both
    ONESCIENCE_MODELS_DIR      extra model probe root

"Available" uses the same *visible file* criterion as the standardizer: a
file whose relative path contains no dot-prefixed segment. ModelScope leaves
bookkeeping residue (``.lock/``, ``._____temp/``, ``.mdl``/``.msc``) behind on
failed downloads, and counting that residue would turn a broken cache into a
false hit.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

ENV_CACHE_ROOT = "ONESCIENCE_RESOURCE_HOME"
ENV_DATASETS_DIR = "ONESCIENCE_DATASETS_DIR"
ENV_MODELS_DIR = "ONESCIENCE_MODELS_DIR"

# Read-only shared store some sites pre-seed datasets into; the standardizer
# probes it, so the candidate list keeps the same shape for consistency.
PUBLIC_DATASETS_ROOT = Path("/public/share/onestore/onedatasets")


def cache_root() -> Path:
    """Cache root, overridable for testing or when HOME lives on a small disk."""
    override = os.environ.get(ENV_CACHE_ROOT)
    if override:
        return Path(override).expanduser()
    return Path.home() / ".onescience"


REGISTRY_VERSION = 1

KIND_DATASET = "dataset"
KIND_MODEL = "model"
VALID_KINDS = (KIND_DATASET, KIND_MODEL)

# Refuse to even start a download when the target volume has less than this
# much free space; a half-written cache is worse than a clean BLOCKED.
MIN_FREE_BYTES = 2 * 1024 ** 3


# ----------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------

def dataset_cache_dir(name: str) -> Path:
    return cache_root() / "datasets" / name / "raw"


def model_cache_dir(name: str) -> Path:
    return cache_root() / "models" / name


def registry_path() -> Path:
    return cache_root() / "resource_registry.json"


def cache_dir_for(name: str, kind: str) -> Path:
    if kind == KIND_DATASET:
        return dataset_cache_dir(name)
    if kind == KIND_MODEL:
        return model_cache_dir(name)
    raise ValueError(f"unsupported kind: {kind}")


def work_dir_for(name: str, kind: str) -> Path:
    """Per-resource directory that holds the lock, temp payload and residue.

    Kept separate from the payload directory and always scoped to one resource
    name, so failure cleanup can never wipe a sibling resource: dataset uses
    ``datasets/<name>`` (payload lives in its ``raw`` child), model uses
    ``models/.state/<name>`` because its payload *is* ``models/<name>``.
    """
    if kind == KIND_DATASET:
        return dataset_cache_dir(name).parent
    if kind == KIND_MODEL:
        return cache_root() / "models" / ".state" / name
    raise ValueError(f"unsupported kind: {kind}")


# ----------------------------------------------------------------------
# Visible-file statistics
# ----------------------------------------------------------------------

def is_visible_file(path: Path, root: Path) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return False
    return not any(part.startswith(".") for part in parts)


def visible_files(root: Path) -> Iterable[Path]:
    if not root.is_dir():
        return []
    return (p for p in root.rglob("*") if p.is_file() and is_visible_file(p, root))


def dir_stats(root: Path) -> Dict[str, int]:
    total_bytes = 0
    files = 0
    for p in visible_files(root):
        files += 1
        try:
            total_bytes += p.stat().st_size
        except OSError:
            continue
    return {"files": files, "bytes": total_bytes}


def is_populated(root: Path) -> bool:
    return root.is_dir() and any(True for _ in visible_files(root))


def content_digest(root: Path) -> str:
    """Stable fingerprint of a materialized resource (relative path + size).

    Not a substitute for provider-side checksums; it lets callers detect that
    a cache directory changed between two runs without re-hashing gigabytes.
    """
    lines = []
    for p in sorted(visible_files(root), key=lambda x: str(x.relative_to(root))):
        try:
            size = p.stat().st_size
        except OSError:
            size = -1
        lines.append(f"{p.relative_to(root).as_posix()}:{size}")
    payload = "\n".join(lines).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


# ----------------------------------------------------------------------
# Probing
# ----------------------------------------------------------------------

def probe_candidates(name: str,
                     kind: str,
                     extra_paths: Optional[List[str]] = None,
                     domain: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return ordered local candidates with population status.

    Read-only: this function only stats and lists, never creates directories.
    The ordering follows ``onescience-data-standardizer`` (caller paths, env
    root, unified cache, shared store, workspace, registry record) so a
    resource resolved by one skill is not re-downloaded by the other.
    """
    workspace = Path(os.getcwd())
    candidates: List[Path] = []
    for raw in extra_paths or []:
        if raw:
            candidates.append(Path(raw).expanduser())

    env_root = os.environ.get(
        ENV_DATASETS_DIR if kind == KIND_DATASET else ENV_MODELS_DIR)
    if env_root:
        root = Path(env_root).expanduser()
        candidates.append(root / name)
        if domain:
            candidates.append(root / domain / name)

    candidates.append(cache_dir_for(name, kind))
    if kind == KIND_DATASET:
        # The standardizer also accepts the un-``raw``-nested layout.
        candidates.append(cache_root() / "datasets" / name)
        candidates.append(PUBLIC_DATASETS_ROOT / name)
        if domain:
            candidates.append(PUBLIC_DATASETS_ROOT / domain / name)
    candidates.append(workspace / "data" / name)
    candidates.append(workspace / ".onescience" / "data" / name)

    entry = registry_get(name, kind)
    if entry and entry.get("local_path"):
        candidates.append(Path(entry["local_path"]).expanduser())

    seen: set = set()
    out: List[Dict[str, Any]] = []
    for cand in candidates:
        try:
            key = str(cand.resolve())
        except OSError:
            key = str(cand)
        if key in seen:
            continue
        seen.add(key)
        exists = cand.is_dir()
        stats = dir_stats(cand) if exists else {"files": 0, "bytes": 0}
        out.append({
            "path": key,
            "exists": exists,
            "usable": exists and stats["files"] > 0,
            "files": stats["files"],
            "bytes": stats["bytes"],
        })
    return out


def free_bytes(path: Path) -> Optional[int]:
    """Free space on the volume that ``path`` lives on (or will live on)."""
    target = path
    while not target.exists() and target.parent != target:
        target = target.parent
    try:
        usage = shutil.disk_usage(str(target))
    except OSError:
        return None
    return int(usage.free)


# ----------------------------------------------------------------------
# Registry
# ----------------------------------------------------------------------

def registry_load() -> Dict[str, Any]:
    """Read the registry, silently rebuilding it when the file is unusable.

    A broken registry must not stop provisioning, but the caller is told about
    it through :func:`registry_status` so the repair is reported instead of
    happening invisibly.
    """
    data, _ = _registry_load_with_flag()
    return data


def registry_status() -> Tuple[Dict[str, Any], Optional[str]]:
    """Return (registry, warning_or_None) for callers that must report repair."""
    return _registry_load_with_flag()


def _registry_load_with_flag() -> Tuple[Dict[str, Any], Optional[str]]:
    path = registry_path()
    if not path.is_file():
        return {"version": REGISTRY_VERSION, "resources": {}}, None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return ({"version": REGISTRY_VERSION, "resources": {}},
                f"resource_registry.json was unreadable ({exc.__class__.__name__}) "
                f"and has been rebuilt empty: {path}")
    if not isinstance(data, dict) or not isinstance(data.get("resources"), dict):
        return ({"version": REGISTRY_VERSION, "resources": {}},
                f"resource_registry.json had an unexpected shape and has been "
                f"rebuilt empty: {path}")
    return data, None


def registry_get(name: str, kind: str) -> Optional[Dict[str, Any]]:
    return registry_load()["resources"].get(f"{kind}:{name}")


def registry_upsert(name: str, kind: str, entry: Dict[str, Any]) -> Tuple[str, bool]:
    """Insert or refresh one entry; returns (registry_key, created)."""
    data = registry_load()
    key = f"{kind}:{name}"
    created = key not in data["resources"]
    merged = dict(data["resources"].get(key, {}))
    merged.update(entry)
    merged["name"] = name
    merged["kind"] = kind
    merged["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    data["resources"][key] = merged
    _atomic_write_json(registry_path(), data)
    return key, created


def _atomic_write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(str(tmp), str(path))
