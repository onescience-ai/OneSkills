"""Fetch backends for the resource providers this skill can materialize from.

ModelScope is the primary provider (SDK -> CLI -> Git LFS degradation, see
:func:`fetch`). Two further providers share the same cache/lock/atomic
primitives so a hit lands identically regardless of source:

* :func:`fetch_hf`  -- a HuggingFace Hub repo (``huggingface_hub.snapshot_download``),
  preferred when a resource's canonical/latest home is HuggingFace rather than
  the ModelScope mirror;
* :func:`fetch_url` -- a single official direct download link (http(s) file or
  archive), used when neither the shared store, ModelScope nor HuggingFace has a
  usable copy and the caller has resolved an authoritative page link.

Public entry for ModelScope: :func:`fetch`. Behaviour contract (see
``references/download_workflow.md``):

* idempotent — a populated cache short-circuits to ``method=cache_hit``;
* atomic — payload is written into a ``.tmp.<pid>`` sibling and only moved into
  place after a non-empty check, so an interrupted run never leaves a
  directory that later looks like a usable cache;
* serialized per resource name through an exclusive lock file;
* failures carry a classified ``reason`` so the caller can decide between
  retry, credential guidance and hard ``blocked``.

Credentials are never handled here: public repos need none, and for gated
repos the ModelScope SDK/CLI resolves its own ``MODELSCOPE_API_TOKEN`` or
``~/.modelscope/credentials``. This module only recognizes the resulting
401/403/auth error and reports it.
"""

from __future__ import annotations

import contextlib
import json
import logging
import math
import os
import re
import shutil
import subprocess
import sys
import time
import tarfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

LOCK_NAME = ".fetch.lock"
LOCK_TIMEOUT_SECONDS = 30 * 60
DOWNLOAD_TIMEOUT_SECONDS = 3 * 60 * 60
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = (1, 4, 16)
RESERVED_REPO_PREFIX = "OneScience"

REASON_AUTH = "authentication_failed"
REASON_NETWORK = "network_error"
REASON_DISK = "insufficient_disk_space"
REASON_CHECKSUM = "checksum_mismatch"
REASON_REPO_NOT_FOUND = "repo_not_found"
REASON_AMBIGUOUS = "repo_ambiguous"
REASON_EMPTY = "empty_payload"
REASON_BACKEND_MISSING = "backend_unavailable"
REASON_FAILED = "fetch_failed"
REASON_NO_CANDIDATE = "no_selectable_repo"
REASON_SIZE = "over_max_bytes"
REASON_BAD_LINK = "invalid_source_link"

# Only http(s) links may be fetched directly; anything else is refused so a
# caller cannot smuggle file:// or shell-piped URIs into the download path.
URL_SCHEME_RE = re.compile(r"^https?://", re.IGNORECASE)
URL_CHUNK = 1 << 20
# Archive suffixes that are unpacked into the payload directory after download.
ARCHIVE_SUFFIXES = (".zip", ".tar", ".tar.gz", ".tgz", ".tar.bz2")

# Reasons that must not burn the retry budget on the SDK path.
NON_RETRYABLE = frozenset({REASON_REPO_NOT_FOUND, REASON_AUTH, REASON_DISK,
                           REASON_BACKEND_MISSING})


class FetchError(RuntimeError):
    def __init__(self, message: str, *, reason: str = REASON_FAILED,
                 details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.reason = reason
        self.details = details or {}


@dataclass
class FetchResult:
    repo_id: str
    repo_type: str
    local_path: str
    method: str                      # sdk | cli | git_lfs | cache_hit
    files: int = 0
    bytes: int = 0
    duration_seconds: float = 0.0
    retries: int = 0
    repo_id_source: str = "default_convention"
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repo_id": self.repo_id,
            "repo_type": self.repo_type,
            "local_path": self.local_path,
            "method": self.method,
            "files": self.files,
            "bytes": self.bytes,
            "duration_seconds": round(self.duration_seconds, 3),
            "retries": self.retries,
            "repo_id_source": self.repo_id_source,
            "warnings": self.warnings,
        }


def default_repo_id(name: str) -> str:
    """Fallback convention: the org every OneSkills-published repo lives under."""
    return f"{RESERVED_REPO_PREFIX}/{name}"


# ----------------------------------------------------------------------
# Name resolution through the public OpenAPI (stdlib only, SDK not required)
# ----------------------------------------------------------------------

OPENAPI_BASE_ENV = "MODELSCOPE_OPENAPI_BASE"
OPENAPI_BASE_DEFAULT = "https://www.modelscope.cn/openapi/v1"
SEARCH_TIMEOUT_SECONDS = 15
SEARCH_PAGE_SIZE = 20
MAX_EXPANSION_QUERIES = 6
MAX_CANDIDATES = 8
MAX_RANKED = 8
USER_AGENT = "oneskills-resource-fetch"
# Ceiling for *auto-selected* candidates only. An explicit repo_id is what the
# caller asked for, so it is never swapped out on grounds of size.
AUTO_MAX_BYTES_ENV = "ONESCIENCE_RESOURCE_MAX_REPO_BYTES"
AUTO_MAX_BYTES_DEFAULT = 8 * 1024 ** 3
# Mirrors and personal re-uploads share names with canonical copies constantly,
# so namespace credibility breaks ties after exactness and popularity.
TRUSTED_ORGS = frozenset({
    "modelscope", "iic", "damo", "alibaba-nlp", "ai-modelscope",
    "qwen", "deepseek", "thudm", "opencsg", "infinity",
})


def openapi_base() -> str:
    return os.environ.get(OPENAPI_BASE_ENV, OPENAPI_BASE_DEFAULT).rstrip("/")


def _collection(repo_type: str) -> str:
    return "datasets" if repo_type == "dataset" else "models"


def _openapi_get(path: str) -> Dict[str, Any]:
    url = "%s%s" % (openapi_base(), path)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=SEARCH_TIMEOUT_SECONDS) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


def repo_exists(repo_id: str, repo_type: str) -> Optional[bool]:
    """True/False from the OpenAPI, ``None`` when the question could not be asked.

    ``None`` matters to the caller: an unreachable search endpoint must not be
    reported as "this repo does not exist", because then the download path never
    runs and its authoritative failure (auth, network) would be lost. A gated
    repo answers 401/403 rather than 404, so it is treated as existing and left
    to the credentialed SDK/CLI path.
    """
    if "/" not in repo_id:
        return None
    try:
        _openapi_get("/%s/%s" % (_collection(repo_type), urllib.parse.quote(repo_id)))
        return True
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            return True
        if exc.code == 404:
            return False
        return None
    except Exception:
        return None


_TOKEN_SPLIT = re.compile(r"[^0-9a-z\u4e00-\u9fff]+")
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def _tokens(text: str) -> List[str]:
    """Lowercased match tokens; CJK runs also contribute bigrams.

    CJK has no word separators, so a whole-run token rarely matches a search row
    verbatim. Bigrams make partial overlap detectable without a segmenter.
    """
    out: List[str] = []
    for run in _TOKEN_SPLIT.split((text or "").lower()):
        if len(run) < 2:
            continue
        out.append(run)
        if _CJK_RE.search(run):
            out.extend(run[i:i + 2] for i in range(len(run) - 1))
    return out


def auto_max_bytes(explicit: Optional[int]) -> int:
    """Size ceiling for auto-selection: explicit flag > env > 8 GiB default."""
    if explicit and explicit > 0:
        return int(explicit)
    raw = (os.environ.get(AUTO_MAX_BYTES_ENV) or "").strip()
    if raw.isdigit():
        return int(raw)
    return AUTO_MAX_BYTES_DEFAULT


def search_candidates(query: str, repo_type: str,
                      page_size: int = SEARCH_PAGE_SIZE) -> Dict[str, Any]:
    """Public OpenAPI search -> normalized candidate rows (stdlib only).

    Returns ``{"status": ok|unavailable, "candidates": [...], "error": ...}``.
    ``unavailable`` is never reported as "nothing exists": the caller keeps its
    own convention so the download backend stays the authority on existence.
    """
    try:
        payload = _openapi_get("/%s?%s" % (
            _collection(repo_type),
            urllib.parse.urlencode({"search": query, "page_size": page_size})))
    except Exception as exc:
        return {"status": "unavailable", "candidates": [],
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:180])}

    rows = (payload.get("data") or {}).get(_collection(repo_type)) or []
    query_l = (query or "").lower()
    cands: List[Dict[str, Any]] = []
    seen = set()
    for row in rows:
        rid = row.get("id") or row.get("RepoId")
        if not isinstance(rid, str) or "/" not in rid or rid in seen:
            continue
        seen.add(rid)
        org, _, tail = rid.partition("/")
        cands.append({
            "repo_id": rid,
            "org": org,
            "name": tail,
            "display_name": str(row.get("display_name") or ""),
            "description": str(row.get("description") or "")[:300],
            "file_size": int(row.get("file_size") or 0),
            "downloads": int(row.get("downloads") or 0),
            "likes": int(row.get("likes") or row.get("Likes") or 0),
            "license": str(row.get("license") or ""),
            "tasks": [str(t) for t in (row.get("tasks") or [])][:12],
            "tags": [str(t) for t in (row.get("tags") or [])][:12],
            "last_modified": str(row.get("last_modified") or ""),
            "name_exact": tail.lower() == query_l,
            "needs_auth": bool(row.get("gated") or row.get("login_required")
                               or row.get("private")),
        })
    return {"status": "ok", "candidates": cands, "error": None}


_QUERY_SPLIT = re.compile(r"[\s,\uff0c\u3001;\uff1b/|+\u3002]+")


def query_variants(query: str) -> List[str]:
    """Whole phrase first, then its tokens.

    The OpenAPI ``search`` parameter matches substrings, so a multi-word phrase
    ("\u5ba0\u7269 \u732b\u72d7 \u56fe\u50cf\u5206\u7c7b") returns nothing while each part
    matches plenty. Expanding here is what keeps a task-level prompt down to one
    sentence: the caller does not have to hand-tune keywords.
    """
    phrase = (query or "").strip()
    if not phrase:
        return []
    out = [phrase]
    for part in _QUERY_SPLIT.split(phrase):
        part = part.strip()
        if len(part) >= 2 and part not in out:
            out.append(part)
    return out


def search_candidates_expanded(query: str, repo_type: str,
                               page_size: int = SEARCH_PAGE_SIZE,
                               max_queries: int = MAX_EXPANSION_QUERIES
                               ) -> Dict[str, Any]:
    """:func:`search_candidates` with token-level retry when the phrase misses.

    Returns ``{"status": ok|unavailable, "candidates": [...], "queries_tried":
    [...], "error": ...}``; it stops at the first variant that yields rows so a
    successful phrase costs one request, not one per token.
    """
    merged: List[Dict[str, Any]] = []
    seen = set()
    tried: List[Dict[str, Any]] = []
    last_error: Optional[str] = None
    for variant in query_variants(query)[:max_queries]:
        outcome = search_candidates(variant, repo_type, page_size=page_size)
        tried.append({"query": variant, "status": outcome["status"],
                      "hits": len(outcome["candidates"])})
        if outcome["status"] != "ok":
            last_error = outcome["error"]
            continue
        for cand in outcome["candidates"]:
            if cand["repo_id"] in seen:
                continue
            seen.add(cand["repo_id"])
            merged.append(cand)
        if merged:
            break
    return {"status": "ok" if merged or last_error is None else "unavailable",
            "candidates": merged, "queries_tried": tried, "error": last_error}


def rank_candidates(cands: List[Dict[str, Any]], query: str,
                    hints: Optional[List[str]] = None, max_bytes: int = 0,
                    keep_auth: bool = False) -> Dict[str, Any]:
    """Score candidates so a bare name *or* a bare task can pick one.

    Ranking is deterministic and every score ships its reasons, because choosing
    a repo on the caller's behalf is only honest if the caller can see why.
    ``max_bytes`` drops over-limit candidates from auto-selection (unknown size
    is kept and flagged, never assumed large); ``needs_auth`` rows are dropped
    unless the caller asks for credentialed repos.

    Weights: exact last-segment name 1000 > substring name 400 > title/desc
    token overlap 80 each (cap 240) > task-hint overlap 40 each (cap 240) >
    popularity 100*log10(downloads) (cap 400) > task/tag overlap 60 each
    (cap 180) > trusted org 150 > likes (cap 50) > size fit within ceiling
    (<=150). Ties break on downloads, then size, then repo_id.
    """
    q_tokens = set(_tokens(query or ""))
    hint_tokens = set()
    for hint in (hints or []):
        hint_tokens.update(_tokens(hint))
    hint_tokens -= q_tokens

    ranked: List[Dict[str, Any]] = []
    excluded: List[Dict[str, Any]] = []
    for cand in cands:
        if cand["needs_auth"] and not keep_auth:
            excluded.append({**cand, "excluded": "needs_auth"})
            continue
        size = cand["file_size"]
        if max_bytes and size and size > max_bytes:
            excluded.append({**cand, "excluded": "over_max_bytes",
                             "max_bytes": int(max_bytes)})
            continue

        score = 0.0
        reasons: List[str] = []
        name_l = cand["name"].lower()
        query_l = (query or "").lower()
        if cand["name_exact"]:
            score += 1000
            reasons.append("仓库名与请求名逐字同名")
        elif query_l and (name_l.startswith(query_l) or query_l in name_l
                          or name_l in query_l):
            score += 400
            reasons.append("仓库名与请求词互为前缀/包含")

        text_tokens = set(_tokens(" ".join([cand["repo_id"],
                                            cand["display_name"],
                                            cand["description"]])))
        overlap = len(q_tokens & text_tokens)
        if overlap:
            score += min(240, 80 * overlap)
            reasons.append("标题/描述与请求词有 %d 个共同词" % overlap)

        meta_tokens = text_tokens | set(_tokens(
            " ".join(cand["tasks"] + cand["tags"])))
        hint_overlap = len(hint_tokens & meta_tokens)
        if hint_overlap:
            score += min(240, 40 * hint_overlap)
            reasons.append("与任务描述有 %d 个共同词" % hint_overlap)
        tag_overlap = len(q_tokens & set(_tokens(
            " ".join(cand["tasks"] + cand["tags"]))))
        if tag_overlap:
            score += min(180, 60 * tag_overlap)
            reasons.append("任务标签与请求词命中 %d 项" % tag_overlap)

        if cand["downloads"]:
            score += min(400, 100 * math.log10(1 + cand["downloads"]))
            reasons.append("下载量 %d" % cand["downloads"])
        if cand["likes"]:
            score += min(50, cand["likes"])
        if cand["org"].lower() in TRUSTED_ORGS:
            score += 150
            reasons.append("来自可信机构命名空间 %s" % cand["org"])
        if max_bytes and size:
            score += 150 * (1 - size / float(max_bytes))
            reasons.append("体积 %d B 在上限内，越小越优先" % size)
        elif not size:
            reasons.append("检索接口未给出体积，未参与体积排序")

        ranked.append({**cand, "score": round(score, 1), "reasons": reasons})

    ranked.sort(key=lambda c: (-c["score"], -c["downloads"],
                               c["file_size"] or 0, c["repo_id"]))
    return {"ranked": ranked[:MAX_RANKED],
            "excluded": excluded[:MAX_CANDIDATES]}


# ----------------------------------------------------------------------
# Cache helpers (shared visibility rule lives in resource_paths)
# ----------------------------------------------------------------------

def _visible_files(root: Path):
    for p in root.rglob("*"):
        if p.is_file() and not any(part.startswith(".")
                                   for part in p.relative_to(root).parts):
            yield p


def _is_populated(root: Path) -> bool:
    return root.is_dir() and any(True for _ in _visible_files(root))


def _drop_unusable_cache(cache_dir: Path) -> None:
    """Remove *this resource's* residue-only skeleton, never a sibling's.

    Cleanup is deliberately scoped to the payload directory of the resource
    being fetched: an interrupted run leaves ``.lock/`` / ``._____temp/`` /
    ``.mdl`` behind, and if that skeleton is left in place a later probe could
    treat the resource as available. A directory that holds any visible file is
    kept, because it may be a usable cache written by a concurrent fetch.
    """
    if cache_dir.is_dir() and not _is_populated(cache_dir):
        shutil.rmtree(cache_dir, ignore_errors=True)


def _prune_work_dir(work_dir: Path, payload: Path) -> None:
    """Drop the per-resource scratch directory once it holds nothing useful.

    Uses ``rmdir`` semantics only: a directory that still holds anything real is
    left alone, so cleanup can never cascade into a sibling resource or into a
    payload that a concurrent fetch just wrote.
    """
    if _is_populated(payload) or _is_populated(work_dir):
        return
    if not work_dir.is_dir():
        return
    for child in list(work_dir.iterdir()):
        if child.name.startswith("."):
            with contextlib.suppress(OSError):
                if child.is_dir():
                    shutil.rmtree(child, ignore_errors=True)
                else:
                    child.unlink()
    with contextlib.suppress(OSError):
        if not payload.exists():
            work_dir.rmdir()


@contextlib.contextmanager
def _fetch_lock(lock_dir: Path):
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_file = lock_dir / LOCK_NAME
    deadline = time.time() + LOCK_TIMEOUT_SECONDS
    while True:
        try:
            fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            break
        except FileExistsError:
            with contextlib.suppress(OSError):
                if time.time() - lock_file.stat().st_mtime > 3600:
                    lock_file.unlink()
                    continue
            if time.time() > deadline:
                raise FetchError(
                    f"another fetch holds the lock for {lock_dir.name}",
                    reason=REASON_FAILED,
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

@contextlib.contextmanager
def _quiet_sdk_streams():
    """Keep backend chatter off the stdout channel that carries our JSON.

    ``snapshot_download`` writes INFO logs through the ``modelscope`` logger,
    whose handler is bound to ``sys.stdout`` at import time, so an in-process
    download interleaves plain text with the result envelope the caller parses.
    Re-point any stdout-bound handler at stderr and swap ``sys.stdout`` for the
    duration of the call; tqdm already defaults to stderr.
    """
    real = sys.stdout
    rehosted = []
    loggers = [logging.getLogger()]
    for obj in list(logging.root.manager.loggerDict.values()):
        if isinstance(obj, logging.Logger):
            loggers.append(obj)
    for logger in loggers:
        for handler in logger.handlers:
            if getattr(handler, "stream", None) is real:
                with contextlib.suppress(Exception):
                    handler.setStream(sys.stderr)
                    rehosted.append(handler)
    try:
        with contextlib.redirect_stdout(sys.stderr):
            yield
    finally:
        for handler in rehosted:
            with contextlib.suppress(Exception):
                handler.setStream(real)


def _via_sdk(repo_id: str, repo_type: str, dest: Path,
             revision: Optional[str]) -> Dict[str, Any]:
    try:
        from modelscope.hub.snapshot_download import snapshot_download  # type: ignore
    except ImportError as exc:
        raise FetchError(
            "modelscope SDK not importable; install with: pip install modelscope",
            reason=REASON_BACKEND_MISSING,
            details={"import_error": str(exc)},
        ) from exc
    kwargs: Dict[str, Any] = {
        "repo_id": repo_id,
        "repo_type": repo_type,
        "cache_dir": str(dest),
    }
    if revision:
        kwargs["revision"] = revision
    try:
        with _quiet_sdk_streams():
            local_path = snapshot_download(**kwargs)
    except FetchError:
        raise
    except Exception as exc:  # modelscope raises a grab-bag of exception types
        raise FetchError(f"SDK fetch failed: {exc}",
                         reason=classify_error(str(exc)),
                         details={"repo_id": repo_id}) from exc
    return {"local_path": str(local_path), "method": "sdk"}


def _via_cli(repo_id: str, repo_type: str, dest: Path,
             revision: Optional[str]) -> Dict[str, Any]:
    exe = shutil.which("modelscope")
    if not exe:
        raise FetchError(
            "modelscope CLI not found on PATH; install with: pip install modelscope",
            reason=REASON_BACKEND_MISSING,
        )
    # CLI v1.37+ has no --repo-id flag: the repo goes through --dataset/--model.
    flag = "--dataset" if repo_type == "dataset" else "--model"
    cmd = [exe, "download", flag, repo_id, "--repo-type", repo_type,
           "--local_dir", str(dest)]
    if revision:
        cmd += ["--revision", revision]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=DOWNLOAD_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as exc:
        raise FetchError("modelscope CLI timed out",
                         reason=REASON_NETWORK) from exc
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "")[-1024:]
        raise FetchError(f"modelscope CLI failed (rc={proc.returncode}): {tail}",
                         reason=classify_error(tail),
                         details={"returncode": proc.returncode})
    return {"local_path": str(dest), "method": "cli"}


def _via_git_lfs(repo_id: str, repo_type: str, dest: Path) -> Dict[str, Any]:
    git = shutil.which("git")
    if not git:
        raise FetchError("git not found on PATH", reason=REASON_BACKEND_MISSING)
    if not shutil.which("git-lfs"):
        raise FetchError("git-lfs not installed; required for the LFS fallback",
                         reason=REASON_BACKEND_MISSING)
    url = f"https://www.modelscope.cn/{repo_type}s/{repo_id}.git"
    if dest.exists():
        shutil.rmtree(dest, ignore_errors=True)
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run([git, "lfs", "install"], check=True,
                       capture_output=True, text=True, timeout=60)
        subprocess.run([git, "clone", url, str(dest)], check=True,
                       capture_output=True, text=True,
                       timeout=DOWNLOAD_TIMEOUT_SECONDS)
    except subprocess.CalledProcessError as exc:
        raise FetchError(f"git clone failed: {(exc.stderr or '')[-1024:]}",
                         reason=classify_error(exc.stderr or "")) from exc
    except subprocess.TimeoutExpired as exc:
        raise FetchError("git clone timed out", reason=REASON_NETWORK) from exc
    return {"local_path": str(dest), "method": "git_lfs"}


def classify_error(msg: str) -> str:
    low = (msg or "").lower()
    if "401" in low or "403" in low or "token" in low or "auth" in low:
        return REASON_AUTH
    # Network signals are checked before repo phrasing: DNS/outage tracebacks
    # from modelscope's wrapper often mention a repo "not exist", and treating
    # those as repo_not_found would skip a retryable failure.
    if re.search(r"connection|\btimeout\b|timed out|\bnetwork\b|name resolution"
                 r"|gaierror|unreachable|temporarily unavailable|max retries", low):
        return REASON_NETWORK
    if "space" in low or "quota" in low or "disk" in low:
        return REASON_DISK
    if "checksum" in low or "hash" in low or "corrupt" in low:
        return REASON_CHECKSUM
    if ("404" in low or "not found" in low or "does not exist" in low
            or "not exist" in low or ("repo" in low and "exist" in low)):
        return REASON_REPO_NOT_FOUND
    return REASON_FAILED


def _select_error(errors: List[FetchError]) -> FetchError:
    """Report the reason that actually explains the failure.

    A missing fallback backend (no SDK *and* no CLI on PATH) must not mask a
    concrete cause such as ``repo_not_found`` or ``network_error``; conversely,
    when every attempt only said "backend unavailable" then that is the truthful
    answer. The first specific error wins, in attempt order.
    """
    for err in errors:
        if err.reason != REASON_BACKEND_MISSING:
            return err
    return errors[-1] if errors else FetchError("fetch failed", reason=REASON_FAILED)


# ----------------------------------------------------------------------
# Shared atomic materialization (used by the non-ModelScope providers)
# ----------------------------------------------------------------------

def _cache_hit_result(cache_dir: Path, repo_id: str, repo_type: str,
                      repo_id_source: str) -> FetchResult:
    files = list(_visible_files(cache_dir))
    return FetchResult(
        repo_id=repo_id, repo_type=repo_type, local_path=str(cache_dir),
        method="cache_hit", files=len(files),
        bytes=sum(_size(f) for f in files), repo_id_source=repo_id_source,
        warnings=["cache already populated; fetch skipped"],
    )


def _atomic_fetch(name: str, cache_dir: Path, scope: Path, repo_id: str,
                  repo_type: str, repo_id_source: str, produce) -> FetchResult:
    """Run ``produce(tmp_dir)`` under the resource lock, then move + verify.

    Mirrors :func:`fetch`'s post-download discipline (isolated temp dir, atomic
    normalize into the canonical cache path, non-empty check, cleanup that only
    touches this resource) so HF/URL payloads are indistinguishable downstream.
    """
    with _fetch_lock(scope):
        started = time.time()
        tmp_dir = scope / f".{cache_dir.name}.tmp.{os.getpid()}"
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir, ignore_errors=True)
        tmp_dir.mkdir(parents=True, exist_ok=True)
        try:
            chosen = produce(tmp_dir)
        except FetchError:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            _drop_unusable_cache(cache_dir)
            _prune_work_dir(scope, cache_dir)
            raise
        landed = _normalize(chosen["local_path"], tmp_dir, cache_dir,
                            repo_id, name)
        files = list(_visible_files(landed))
        if not files:
            shutil.rmtree(landed, ignore_errors=True)
            _prune_work_dir(scope, cache_dir)
            raise FetchError(
                f"fetch reported success but no visible file landed in {landed}",
                reason=REASON_EMPTY, details={"repo_id": repo_id})
        return FetchResult(
            repo_id=repo_id, repo_type=repo_type, local_path=str(landed),
            method=chosen["method"], files=len(files),
            bytes=sum(_size(f) for f in files),
            duration_seconds=time.time() - started, retries=0,
            repo_id_source=repo_id_source)


# ----------------------------------------------------------------------
# HuggingFace provider
# ----------------------------------------------------------------------

def _via_hf(repo_id: str, repo_type: str, dest: Path,
            revision: Optional[str], endpoint: Optional[str]) -> Dict[str, Any]:
    try:
        from huggingface_hub import snapshot_download  # type: ignore
    except ImportError as exc:
        raise FetchError(
            "huggingface_hub not importable; install with: pip install huggingface_hub",
            reason=REASON_BACKEND_MISSING, details={"import_error": str(exc)}) from exc
    kwargs: Dict[str, Any] = {
        "repo_id": repo_id,
        "local_dir": str(dest),
        "repo_type": "dataset" if repo_type == "dataset" else "model",
    }
    if revision:
        kwargs["revision"] = revision
    ep = endpoint or os.environ.get("HF_ENDPOINT")
    if ep:
        kwargs["endpoint"] = ep
    try:
        with _quiet_sdk_streams():
            local_path = snapshot_download(**kwargs)
    except FetchError:
        raise
    except Exception as exc:
        raise FetchError(f"HuggingFace fetch failed: {exc}",
                         reason=classify_error(str(exc)),
                         details={"repo_id": repo_id}) from exc
    return {"local_path": str(local_path), "method": "hf"}


def fetch_hf(name: str, cache_dir: Path, repo_id: str, work_dir: Path,
             repo_type: str = "dataset", revision: Optional[str] = None,
             repo_id_source: str = "explicit",
             endpoint: Optional[str] = None) -> FetchResult:
    """Materialize a HuggingFace Hub repo into ``cache_dir`` (idempotent).

    ``repo_id`` must be a HuggingFace ``org/name`` (or ``dataset`` namespace);
    a bare name with no ``/`` is refused because HuggingFace has no implicit
    single-namespace convention the way ModelScope's OneScience/ fallback does.
    """
    if not repo_id or "/" not in repo_id:
        raise FetchError(
            "HuggingFace repo_id must be org/name; got %r" % (repo_id,),
            reason=REASON_REPO_NOT_FOUND, details={"repo_id": repo_id})
    scope = Path(work_dir) if work_dir else cache_dir.parent
    scope.mkdir(parents=True, exist_ok=True)
    if _is_populated(cache_dir):
        return _cache_hit_result(cache_dir, repo_id, repo_type, repo_id_source)
    if cache_dir.exists() and not any(cache_dir.iterdir()):
        with contextlib.suppress(OSError):
            cache_dir.rmdir()
    return _atomic_fetch(
        name, cache_dir, scope, repo_id, repo_type, repo_id_source,
        lambda tmp: _via_hf(repo_id, repo_type, tmp, revision, endpoint))


# ----------------------------------------------------------------------
# Official direct-link provider
# ----------------------------------------------------------------------

def _looks_like_archive(path: Path) -> bool:
    low = path.name.lower()
    return any(low.endswith(sfx) for sfx in ARCHIVE_SUFFIXES)


def _extract_archive(archive: Path, dest: Path) -> None:
    low = archive.name.lower()
    if low.endswith(".zip"):
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(dest)
    else:
        mode = "r:*" if (low.endswith(".gz") or low.endswith(".tgz")) else "r"
        if low.endswith(".bz2"):
            mode = "r:bz2"
        with tarfile.open(archive, mode) as tf:
            tf.extractall(dest)
    with contextlib.suppress(OSError):
        archive.unlink()


def _via_url(url: str, dest: Path, name: str,
             max_bytes: int) -> Dict[str, Any]:
    if not URL_SCHEME_RE.match(url or ""):
        raise FetchError(
            "only http(s) direct links may be fetched: %r" % (url,),
            reason=REASON_BAD_LINK, details={"url": url})
    base = urllib.parse.unquote(urlparse_path(url)) or name
    base = os.path.basename(base) or name
    target = dest / base
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    cap = max_bytes if max_bytes and max_bytes > 0 else AUTO_MAX_BYTES_DEFAULT
    total = 0
    try:
        with urllib.request.urlopen(req, timeout=DOWNLOAD_TIMEOUT_SECONDS) as resp, \
                open(target, "wb") as fh:
            while True:
                chunk = resp.read(URL_CHUNK)
                if not chunk:
                    break
                total += len(chunk)
                if total > cap:
                    raise FetchError(
                        "direct download exceeded size ceiling (%d > %d bytes)"
                        % (total, cap), reason=REASON_SIZE,
                        details={"url": url, "max_bytes": cap})
                fh.write(chunk)
    except FetchError:
        with contextlib.suppress(OSError):
            target.unlink()
        raise
    except (urllib.error.URLError, OSError) as exc:
        with contextlib.suppress(OSError):
            target.unlink()
        reason = classify_error(str(exc))
        if reason == REASON_FAILED:
            reason = REASON_NETWORK
        raise FetchError("direct link fetch failed: %s" % exc,
                         reason=reason, details={"url": url}) from exc
    if _looks_like_archive(target):
        try:
            _extract_archive(target, dest)
        except (tarfile.TarError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
            raise FetchError("archive could not be unpacked: %s" % exc,
                           reason=REASON_CHECKSUM, details={"url": url}) from exc
    return {"local_path": str(dest), "method": "url"}


def urlparse_path(url: str) -> str:
    return urllib.parse.urlparse(url).path


def fetch_url(name: str, cache_dir: Path, url: str, work_dir: Path,
              repo_type: str = "dataset", max_bytes: int = 0,
              repo_id_source: str = "explicit") -> FetchResult:
    """Download one official direct link (file or archive) into ``cache_dir``.

    The link is treated as an authoritative source the caller resolved; it must
    be http(s) and is size-capped exactly like an auto-selected repo, so a wrong
    URL cannot pull an unbounded payload onto the cache volume.
    """
    scope = Path(work_dir) if work_dir else cache_dir.parent
    scope.mkdir(parents=True, exist_ok=True)
    if _is_populated(cache_dir):
        return _cache_hit_result(cache_dir, url, repo_type, repo_id_source)
    if cache_dir.exists() and not any(cache_dir.iterdir()):
        with contextlib.suppress(OSError):
            cache_dir.rmdir()
    return _atomic_fetch(
        name, cache_dir, scope, url, repo_type, repo_id_source,
        lambda tmp: _via_url(url, tmp, name, max_bytes))


# ----------------------------------------------------------------------
# Public entry
# ----------------------------------------------------------------------

def fetch(name: str,
          cache_dir: Path,
          repo_id: Optional[str] = None,
          repo_type: str = "dataset",
          revision: Optional[str] = None,
          allow_git_lfs_fallback: bool = False,
          repo_id_source: str = "default_convention",
          work_dir: Optional[Path] = None) -> FetchResult:
    """Materialize a ModelScope repo into ``cache_dir`` (idempotent).

    ``work_dir`` scopes the lock and the temporary payload to one resource name.
    Without it, model fetches would serialize on ``models/.fetch.lock`` (all
    models at once) and litter the shared ``models/`` tree with temp dirs.
    """
    effective_repo_id = repo_id or default_repo_id(name)
    scope = Path(work_dir) if work_dir else cache_dir.parent
    scope.mkdir(parents=True, exist_ok=True)

    if _is_populated(cache_dir):
        files = list(_visible_files(cache_dir))
        return FetchResult(
            repo_id=effective_repo_id,
            repo_type=repo_type,
            local_path=str(cache_dir),
            method="cache_hit",
            files=len(files),
            bytes=sum(_size(f) for f in files),
            repo_id_source=repo_id_source,
            warnings=["cache already populated; fetch skipped"],
        )

    if cache_dir.exists() and not any(cache_dir.iterdir()):
        with contextlib.suppress(OSError):
            cache_dir.rmdir()

    with _fetch_lock(scope):
        started = time.time()
        tmp_dir = scope / f".{cache_dir.name}.tmp.{os.getpid()}"
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir, ignore_errors=True)
        tmp_dir.mkdir(parents=True, exist_ok=True)

        chosen: Optional[Dict[str, Any]] = None
        last_error: Optional[FetchError] = None
        errors: List[FetchError] = []
        retries = 0
        for attempt in range(MAX_RETRIES):
            retries = attempt
            try:
                chosen = _via_sdk(effective_repo_id, repo_type, tmp_dir, revision)
                break
            except FetchError as exc:
                last_error = exc
                errors.append(exc)
                if exc.reason in NON_RETRYABLE:
                    break
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BACKOFF_SECONDS[attempt])

        if chosen is None:
            try:
                chosen = _via_cli(effective_repo_id, repo_type, tmp_dir, revision)
            except FetchError as exc:
                last_error = exc
                errors.append(exc)

        if chosen is None and allow_git_lfs_fallback:
            try:
                chosen = _via_git_lfs(effective_repo_id, repo_type, tmp_dir)
            except FetchError as exc:
                last_error = exc
                errors.append(exc)

        if chosen is None:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            _drop_unusable_cache(cache_dir)
            _prune_work_dir(scope, cache_dir)
            reported = _select_error(errors) or last_error
            if len(errors) > 1:
                reported = FetchError(
                    str(reported), reason=reported.reason,
                    details=dict(reported.details,
                                 fallback_errors=[
                                     {"reason": e.reason, "message": str(e)}
                                     for e in errors if e is not reported][:4]))
            raise reported or FetchError("fetch failed", reason=REASON_FAILED)

        landed = _normalize(chosen["local_path"], tmp_dir, cache_dir,
                            effective_repo_id, name)

        files = list(_visible_files(landed))
        if not files:
            shutil.rmtree(landed, ignore_errors=True)
            _prune_work_dir(scope, cache_dir)
            raise FetchError(
                f"fetch reported success but no visible file landed in {landed}",
                reason=REASON_EMPTY,
                details={"repo_id": effective_repo_id},
            )
        return FetchResult(
            repo_id=effective_repo_id,
            repo_type=repo_type,
            local_path=str(landed),
            method=chosen["method"],
            files=len(files),
            bytes=sum(_size(f) for f in files),
            duration_seconds=time.time() - started,
            retries=retries,
            repo_id_source=repo_id_source,
        )


def _size(path: Path) -> int:
    with contextlib.suppress(OSError):
        return path.stat().st_size
    return 0


def _normalize(landed_raw: str, tmp_dir: Path, cache_dir: Path,
               repo_id: str, name: str) -> Path:
    """Move whatever the backend produced into the canonical cache location.

    The SDK may write under ``cache_dir`` itself, under a repo-name subfolder,
    or into the temp dir; the CLI writes straight into the target. Normalize so
    downstream probing and the registry always see one path.
    """
    landed = Path(landed_raw)
    cache_dir.parent.mkdir(parents=True, exist_ok=True)
    if landed.resolve() == cache_dir.resolve():
        return cache_dir
    children = [c for c in landed.iterdir()] if landed.is_dir() else []
    single_repo_child = (len(children) == 1 and children[0].is_dir()
                         and children[0].name.lower() in
                         (repo_id.split("/")[-1].lower(), name.lower()))
    source = children[0] if single_repo_child else landed
    if cache_dir.exists():
        shutil.rmtree(cache_dir, ignore_errors=True)
    shutil.move(str(source), str(cache_dir))
    if tmp_dir.exists() and tmp_dir != landed:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    return cache_dir
