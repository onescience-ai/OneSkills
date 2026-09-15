"""ModelScope downloader with three-tier fallback.

Implements references/download_workflow.md:

    1. ModelScope Python SDK (snapshot_download)
    2. ModelScope CLI (`modelscope download`)
    3. Git LFS clone (opt-in via allow_git_lfs_fallback)

Cache directory is fixed at ~/.onescience/datasets/<name>/raw/ and the
download is idempotent (existing non-empty cache short-circuits).

The downloader never touches the standardization pipeline; it only produces
a local directory that resolve_source.py can subsequently point at.
"""

from __future__ import annotations

import contextlib
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

CACHE_ROOT = Path.home() / ".onescience" / "datasets"
DOWNLOAD_LOCK_NAME = ".download.lock"
LOCK_TIMEOUT_SECONDS = 30 * 60  # 30 minutes for large datasets
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = (1, 4, 16)


class DownloadError(RuntimeError):
    def __init__(self, message: str, *, reason: str = "download_failed",
                 details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.reason = reason
        self.details = details or {}


@dataclass
class DownloadResult:
    repo_id: str
    repo_type: str
    cache_dir: str
    method: str                       # sdk | cli | git_lfs | cache_hit
    bytes_downloaded: int = 0
    files_count: int = 0
    duration_seconds: float = 0.0
    retries: int = 0
    repo_id_source: str = "default_convention"
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repo_id": self.repo_id,
            "repo_type": self.repo_type,
            "cache_dir": self.cache_dir,
            "method": self.method,
            "bytes_downloaded": self.bytes_downloaded,
            "files_count": self.files_count,
            "duration_seconds": round(self.duration_seconds, 3),
            "retries": self.retries,
            "repo_id_source": self.repo_id_source,
            "warnings": self.warnings,
        }


# ----------------------------------------------------------------------
# Cache helpers
# ----------------------------------------------------------------------

def cache_dir_for(dataset_name: str) -> Path:
    return CACHE_ROOT / dataset_name / "raw"


def _dir_stats(root: Path) -> Dict[str, int]:
    total_bytes = 0
    files = 0
    for p in root.rglob("*"):
        if p.is_file():
            files += 1
            with contextlib.suppress(OSError):
                total_bytes += p.stat().st_size
    return {"bytes": total_bytes, "files": files}


def _cache_is_populated(cache_dir: Path) -> bool:
    return cache_dir.exists() and cache_dir.is_dir() and any(cache_dir.iterdir())


@contextlib.contextmanager
def _download_lock(dataset_name: str):
    """Exclusive per-dataset lock; blocks up to LOCK_TIMEOUT_SECONDS."""
    lock_dir = CACHE_ROOT / dataset_name
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_file = lock_dir / DOWNLOAD_LOCK_NAME
    deadline = time.time() + LOCK_TIMEOUT_SECONDS
    while True:
        try:
            fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            break
        except FileExistsError:
            # Steal stale locks (>1h old).
            try:
                age = time.time() - lock_file.stat().st_mtime
            except OSError:
                age = 0
            if age > 3600:
                with contextlib.suppress(OSError):
                    lock_file.unlink()
                continue
            if time.time() > deadline:
                raise DownloadError(
                    f"download lock held by another process for {dataset_name}",
                    reason="download_failed",
                    details={"lock_file": str(lock_file)},
                )
            time.sleep(2.0)
    try:
        yield
    finally:
        with contextlib.suppress(OSError):
            lock_file.unlink()


# ----------------------------------------------------------------------
# Three download paths
# ----------------------------------------------------------------------

def _download_via_sdk(repo_id: str, repo_type: str, cache_dir: Path,
                      revision: Optional[str] = None) -> Dict[str, Any]:
    try:
        from modelscope.hub.snapshot_download import snapshot_download  # type: ignore
    except ImportError as exc:
        raise DownloadError(
            "modelscope SDK not installed; install with: pip install modelscope",
            reason="download_failed",
            details={"import_error": str(exc)},
        ) from exc
    kwargs: Dict[str, Any] = {
        "repo_id": repo_id,
        "repo_type": repo_type,
        "cache_dir": str(cache_dir.parent),
    }
    if revision:
        kwargs["revision"] = revision
    try:
        local_path = snapshot_download(**kwargs)
    except Exception as exc:
        msg = str(exc)
        reason = _classify_error(msg)
        raise DownloadError(f"SDK download failed: {msg}",
                            reason=reason, details={"repo_id": repo_id}) from exc
    return {"local_path": str(local_path), "method": "sdk"}


def _download_via_cli(repo_id: str, repo_type: str, cache_dir: Path,
                      revision: Optional[str] = None) -> Dict[str, Any]:
    exe = shutil.which("modelscope")
    if not exe:
        raise DownloadError(
            "modelscope CLI not found on PATH; install with: pip install modelscope",
            reason="download_failed",
        )
    # modelscope CLI v1.37+ signature:
    #   modelscope download [--model X | --dataset X] [--repo-type T]
    #                       [--local_dir D] [--revision R]
    # repo_id is passed via --model/--dataset (NOT --repo-id, which does
    # not exist and causes "unrecognized arguments").
    if repo_type == "dataset":
        cmd = [exe, "download", "--dataset", repo_id,
               "--repo-type", "dataset", "--local_dir", str(cache_dir)]
    else:
        cmd = [exe, "download", "--model", repo_id,
               "--repo-type", "model", "--local_dir", str(cache_dir)]
    if revision:
        cmd += ["--revision", revision]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=LOCK_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as exc:
        raise DownloadError("modelscope CLI timed out",
                            reason="download_failed") from exc
    if proc.returncode != 0:
        reason = _classify_error(proc.stderr or proc.stdout or "")
        raise DownloadError(
            f"modelscope CLI failed (rc={proc.returncode}): "
            f"{(proc.stderr or proc.stdout or '')[:1024]}",
            reason=reason,
            details={"returncode": proc.returncode},
        )
    return {"local_path": str(cache_dir), "method": "cli"}


def _download_via_git_lfs(repo_id: str, repo_type: str,
                          cache_dir: Path) -> Dict[str, Any]:
    git = shutil.which("git")
    if not git:
        raise DownloadError("git not found on PATH", reason="download_failed")
    lfs = shutil.which("git-lfs")
    if not lfs:
        raise DownloadError(
            "git-lfs not installed; required for git_lfs fallback",
            reason="download_failed",
        )
    url = f"https://www.modelscope.cn/{repo_type}s/{repo_id}.git"
    if cache_dir.exists():
        shutil.rmtree(cache_dir, ignore_errors=True)
    cache_dir.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run([git, "lfs", "install"], check=True,
                       capture_output=True, text=True, timeout=60)
        subprocess.run([git, "clone", url, str(cache_dir)], check=True,
                       capture_output=True, text=True,
                       timeout=LOCK_TIMEOUT_SECONDS)
    except subprocess.CalledProcessError as exc:
        raise DownloadError(
            f"git clone failed: {(exc.stderr or '')[:1024]}",
            reason=_classify_error(exc.stderr or ""),
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise DownloadError("git clone timed out",
                            reason="download_failed") from exc
    return {"local_path": str(cache_dir), "method": "git_lfs"}


def _classify_error(msg: str) -> str:
    low = msg.lower()
    # repo-not-found: cover both "does not exist" and modelscope's
    # "not exists" / "not exist" phrasing, plus HTTP 404.
    if ("404" in low or "not found" in low or "does not exist" in low
            or "not exists" in low or "not exist" in low
            or "repo" in low and "exist" in low):
        return "repo_not_found"
    if "401" in low or "403" in low or "auth" in low or "token" in low:
        return "authentication_failed"
    if "space" in low or "quota" in low or "disk" in low:
        return "insufficient_disk_space"
    if "timeout" in low or "connection" in low or "network" in low:
        return "network_error"
    if "checksum" in low or "hash" in low or "corrupt" in low:
        return "checksum_mismatch"
    return "download_failed"


# ----------------------------------------------------------------------
# Public entry
# ----------------------------------------------------------------------

def download(dataset_name: str,
             repo_id: Optional[str] = None,
             repo_type: str = "dataset",
             revision: Optional[str] = None,
             allow_git_lfs_fallback: bool = False,
             repo_id_source: str = "default_convention") -> DownloadResult:
    """Idempotent download to ~/.onescience/datasets/<name>/raw/.

    Raises DownloadError with a classified reason on unrecoverable failure.
    """
    cache_dir = cache_dir_for(dataset_name)
    effective_repo_id = repo_id or f"OneScience/{dataset_name}"

    # Fast path: cache already populated.
    if _cache_is_populated(cache_dir):
        stats = _dir_stats(cache_dir)
        return DownloadResult(
            repo_id=effective_repo_id,
            repo_type=repo_type,
            cache_dir=str(cache_dir),
            method="cache_hit",
            bytes_downloaded=stats["bytes"],
            files_count=stats["files"],
            repo_id_source=repo_id_source,
            warnings=["cache hit; skipping download"],
        )

    # Clean empty cache dir before download.
    if cache_dir.exists() and not any(cache_dir.iterdir()):
        with contextlib.suppress(OSError):
            cache_dir.rmdir()

    with _download_lock(dataset_name):
        started = time.time()
        tmp_dir = CACHE_ROOT / dataset_name / f".raw.tmp.{os.getpid()}"
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir, ignore_errors=True)
        tmp_dir.mkdir(parents=True, exist_ok=True)

        last_error: Optional[DownloadError] = None
        retries = 0
        chosen: Optional[Dict[str, Any]] = None

        for attempt in range(MAX_RETRIES):
            retries = attempt
            try:
                chosen = _download_via_sdk(effective_repo_id, repo_type,
                                           tmp_dir, revision)
                break
            except DownloadError as exc:
                last_error = exc
                # Non-retryable reasons short-circuit to CLI immediately.
                if exc.reason in ("repo_not_found", "authentication_failed",
                                  "insufficient_disk_space"):
                    break
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BACKOFF_SECONDS[attempt])

        if chosen is None:
            # Fallback to CLI.
            try:
                chosen = _download_via_cli(effective_repo_id, repo_type,
                                           tmp_dir, revision)
            except DownloadError as exc:
                last_error = exc

        if chosen is None and allow_git_lfs_fallback:
            try:
                chosen = _download_via_git_lfs(effective_repo_id, repo_type,
                                               tmp_dir)
            except DownloadError as exc:
                last_error = exc

        if chosen is None:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            raise last_error or DownloadError("download failed",
                                              reason="download_failed")

        # SDK may have written into cache_dir.parent/<something>; normalize
        # by moving tmp_dir contents into cache_dir.
        downloaded_root = Path(chosen["local_path"])
        cache_dir.parent.mkdir(parents=True, exist_ok=True)
        if downloaded_root.resolve() != cache_dir.resolve():
            if cache_dir.exists():
                shutil.rmtree(cache_dir, ignore_errors=True)
            # If SDK put files under tmp_dir/<repo_name>, lift them up.
            children = list(downloaded_root.iterdir())
            if len(children) == 1 and children[0].is_dir() and \
                    children[0].name.lower() in (
                        effective_repo_id.split("/")[-1].lower(),
                        dataset_name.lower()):
                shutil.move(str(children[0]), str(cache_dir))
                shutil.rmtree(downloaded_root, ignore_errors=True)
            else:
                shutil.move(str(downloaded_root), str(cache_dir))
            if tmp_dir.exists() and tmp_dir != downloaded_root:
                shutil.rmtree(tmp_dir, ignore_errors=True)

        stats = _dir_stats(cache_dir)
        if stats["files"] == 0:
            raise DownloadError(
                f"download produced empty cache: {cache_dir}",
                reason="download_failed",
            )
        return DownloadResult(
            repo_id=effective_repo_id,
            repo_type=repo_type,
            cache_dir=str(cache_dir),
            method=chosen["method"],
            bytes_downloaded=stats["bytes"],
            files_count=stats["files"],
            duration_seconds=time.time() - started,
            retries=retries,
            repo_id_source=repo_id_source,
        )


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def _cli() -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Download a dataset from ModelScope")
    parser.add_argument("--dataset-name", required=True)
    parser.add_argument("--repo-id", default=None)
    parser.add_argument("--repo-type", default="dataset",
                        choices=["dataset", "model"])
    parser.add_argument("--revision", default=None)
    parser.add_argument("--allow-git-lfs-fallback", action="store_true")
    args = parser.parse_args()

    try:
        result = download(
            dataset_name=args.dataset_name,
            repo_id=args.repo_id,
            repo_type=args.repo_type,
            revision=args.revision,
            allow_git_lfs_fallback=args.allow_git_lfs_fallback,
            repo_id_source="explicit" if args.repo_id else "default_convention",
        )
    except DownloadError as exc:
        print(json.dumps({"ok": False, "reason": exc.reason,
                          "message": str(exc), "details": exc.details},
                         indent=2, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps({"ok": True, **result.to_dict()},
                     indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
