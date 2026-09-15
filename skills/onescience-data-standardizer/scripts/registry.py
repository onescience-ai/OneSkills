"""Registry for ~/.onescience/data_management.json.

Implements the schema, merge-write semantics and file-locking contract
defined in references/data_management_registry.md.

The registry is a lightweight index over the per-dataset dataset_card.json
files that live inside each AI-Ready target directory. Only the minimum
queryable fields are stored here to keep the file small even when dozens
of datasets are registered.
"""

from __future__ import annotations

import contextlib
import json
import os
import shutil
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

SCHEMA_VERSION = 1
REGISTRY_FILENAME = "data_management.json"
LOCK_FILENAME = ".data_management.lock"
LOCK_TIMEOUT_SECONDS = 30.0
LOCK_POLL_INTERVAL = 0.2


class RegistryError(RuntimeError):
    pass


class RegistryLockTimeout(RegistryError):
    pass


class RegistryVersionError(RegistryError):
    pass


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def registry_root() -> Path:
    """Return the ~/.onescience directory, creating it if needed."""
    root = Path.home() / ".onescience"
    root.mkdir(parents=True, exist_ok=True)
    return root


def registry_path() -> Path:
    return registry_root() / REGISTRY_FILENAME


def lock_path() -> Path:
    return registry_root() / LOCK_FILENAME


# ----------------------------------------------------------------------
# Cross-platform advisory file lock
# ----------------------------------------------------------------------

@contextlib.contextmanager
def _file_lock(timeout: float = LOCK_TIMEOUT_SECONDS) -> Iterator[None]:
    """Best-effort exclusive lock; falls back to no-op on unsupported OS."""
    lock_file = lock_path()
    deadline = time.time() + timeout
    fd: Optional[int] = None
    try:
        while True:
            try:
                fd = os.open(str(lock_file),
                             os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
                os.write(fd, str(os.getpid()).encode())
                break
            except FileExistsError:
                # Stale-lock detection: if the lock file is older than 10 min
                # and the owning pid is gone, steal it.
                try:
                    age = time.time() - lock_file.stat().st_mtime
                    owner_pid = int(lock_file.read_text().strip() or "0")
                    stale = age > 600 or not _pid_alive(owner_pid)
                except (OSError, ValueError):
                    stale = True
                if stale:
                    with contextlib.suppress(OSError):
                        lock_file.unlink()
                    continue
                if time.time() > deadline:
                    raise RegistryLockTimeout(
                        f"could not acquire {lock_file} within {timeout}s"
                    )
                time.sleep(LOCK_POLL_INTERVAL)
        yield
    finally:
        if fd is not None:
            with contextlib.suppress(OSError):
                os.close(fd)
        with contextlib.suppress(OSError):
            lock_file.unlink()


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        # Best-effort on Windows: use OpenProcess via ctypes if available.
        try:
            import ctypes
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
            handle = kernel32.OpenProcess(
                PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
            if not handle:
                return False
            kernel32.CloseHandle(handle)
            return True
        except Exception:
            return True  # assume alive when we cannot tell
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


# ----------------------------------------------------------------------
# Read / write primitives
# ----------------------------------------------------------------------

def _default_state() -> Dict[str, Any]:
    return {"version": SCHEMA_VERSION, "datasets": []}


def _read_state() -> Dict[str, Any]:
    path = registry_path()
    if not path.exists():
        return _default_state()
    try:
        raw = path.read_text(encoding="utf-8")
        state = json.loads(raw) if raw.strip() else _default_state()
    except (OSError, json.JSONDecodeError) as exc:
        # Corrupt file: back it up and start fresh.
        backup = path.with_suffix(f".corrupt.{int(time.time())}.json")
        with contextlib.suppress(OSError):
            shutil.copy2(path, backup)
        print(f"[registry] corrupted registry backed up to {backup}: {exc}",
              file=sys.stderr)
        return _default_state()
    if not isinstance(state, dict):
        return _default_state()
    version = int(state.get("version", SCHEMA_VERSION))
    if version > SCHEMA_VERSION:
        raise RegistryVersionError(
            f"registry version {version} > supported {SCHEMA_VERSION}; "
            f"please upgrade onescience-data-standardizer"
        )
    state = _migrate(state)
    state.setdefault("datasets", [])
    if not isinstance(state["datasets"], list):
        state["datasets"] = []
    return state


def _migrate(state: Dict[str, Any]) -> Dict[str, Any]:
    """Forward-migration hook. Currently a no-op at version=1."""
    state.setdefault("version", SCHEMA_VERSION)
    return state


def _atomic_write(state: Dict[str, Any]) -> None:
    path = registry_path()
    tmp_fd, tmp_name = tempfile.mkstemp(
        prefix=f".{REGISTRY_FILENAME}.tmp.", suffix=".json",
        dir=str(path.parent),
    )
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as fh:
            json.dump(state, fh, indent=2, ensure_ascii=False)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_name, path)
    except Exception:
        with contextlib.suppress(OSError):
            os.unlink(tmp_name)
        raise


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------

REQUIRED_FIELDS = ("name", "domain", "source_dir", "target_dir", "handler",
                   "source_resolution_method", "dataset_card_path")
MUTABLE_FIELDS = ("source_dir", "target_dir", "handler", "checksum",
                  "source_resolution_method", "modelscope_repo_id",
                  "dataset_card_path", "dataset_report_called", "domain")


def list_datasets() -> List[Dict[str, Any]]:
    with _file_lock():
        return list(_read_state()["datasets"])


def get_dataset(name: str) -> Optional[Dict[str, Any]]:
    for entry in list_datasets():
        if entry.get("name") == name:
            return entry
    return None


def upsert(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Merge-write a single dataset entry keyed by `name`.

    - Missing required fields raise RegistryError.
    - Existing entries keep their `created_at` and `notes`.
    - New entries get `created_at == updated_at == now()`.
    """
    missing = [f for f in REQUIRED_FIELDS if f not in entry or entry[f] in (None, "")]
    if missing:
        raise RegistryError(f"missing required fields: {missing}")

    now = _utcnow_iso()
    with _file_lock():
        state = _read_state()
        datasets: List[Dict[str, Any]] = state["datasets"]
        existing_idx = next(
            (i for i, d in enumerate(datasets) if d.get("name") == entry["name"]),
            None,
        )
        if existing_idx is None:
            new_entry = dict(entry)
            new_entry.setdefault("checksum", None)
            new_entry.setdefault("modelscope_repo_id", None)
            new_entry.setdefault("dataset_report_called", False)
            new_entry.setdefault("notes", None)
            new_entry["created_at"] = now
            new_entry["updated_at"] = now
            datasets.append(new_entry)
            written = new_entry
        else:
            existing = datasets[existing_idx]
            for field in MUTABLE_FIELDS:
                if field in entry:
                    existing[field] = entry[field]
            existing["updated_at"] = now
            # Preserve created_at and notes from existing record.
            datasets[existing_idx] = existing
            written = existing
        state["datasets"] = datasets
        _atomic_write(state)
    return written


def remove(name: str) -> bool:
    with _file_lock():
        state = _read_state()
        before = len(state["datasets"])
        state["datasets"] = [d for d in state["datasets"] if d.get("name") != name]
        if len(state["datasets"]) == before:
            return False
        _atomic_write(state)
        return True


def verify() -> Dict[str, Any]:
    """Sanity-check every registered entry.

    Returns a report dict; does not mutate the registry.
    """
    report: Dict[str, Any] = {"checked": 0, "ok": 0, "issues": []}
    for entry in list_datasets():
        report["checked"] += 1
        problems: List[str] = []
        target = entry.get("target_dir")
        if not target or not Path(target).exists():
            problems.append(f"target_dir missing: {target}")
        card = entry.get("dataset_card_path")
        if card and not Path(card).exists():
            problems.append(f"dataset_card missing: {card}")
        source = entry.get("source_dir")
        if source and not Path(source).exists():
            problems.append(f"source_dir missing (may be transient): {source}")
        if problems:
            report["issues"].append({"name": entry.get("name"), "problems": problems})
        else:
            report["ok"] += 1
    return report


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def _cli(argv: Optional[List[str]] = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Manage ~/.onescience/data_management.json"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List all registered datasets")

    p_get = sub.add_parser("get", help="Get one dataset by name")
    p_get.add_argument("--name", required=True)

    p_rm = sub.add_parser("remove", help="Remove one dataset by name")
    p_rm.add_argument("--name", required=True)

    sub.add_parser("verify", help="Verify registry integrity")

    p_path = sub.add_parser("path", help="Print registry file path")
    p_path.set_defaults(cmd="path")

    args = parser.parse_args(argv)

    if args.cmd == "list":
        print(json.dumps(list_datasets(), indent=2, ensure_ascii=False))
    elif args.cmd == "get":
        entry = get_dataset(args.name)
        if entry is None:
            print(f"dataset not found: {args.name}", file=sys.stderr)
            return 1
        print(json.dumps(entry, indent=2, ensure_ascii=False))
    elif args.cmd == "remove":
        ok = remove(args.name)
        print(json.dumps({"removed": ok, "name": args.name}))
        return 0 if ok else 1
    elif args.cmd == "verify":
        print(json.dumps(verify(), indent=2, ensure_ascii=False))
    elif args.cmd == "path":
        print(str(registry_path()))
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
