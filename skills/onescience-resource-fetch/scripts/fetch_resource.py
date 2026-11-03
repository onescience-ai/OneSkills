"""Resource provisioning entry point for ``onescience-resource-fetch``.

Resolves one logical resource (a dataset or a model/checkpoint bundle) to a
usable local directory through three ordered stages:

    1. explicit path   — caller gave ``--local-dir`` / ``source_dir``
    2. local probe     — unified cache, workspace data dirs, registry record
    3. ModelScope fetch— taken by default when stages 1-2 miss (缺即下)

Then the payload is verified (visible files / required patterns / size floor),
registered in ``~/.onescience/resource_registry.json``, and reported as a
``resource_retrieval_result`` with a ``provisioned_resources`` extension.

Usage:

    python scripts/fetch_resource.py provision --name <name> --kind dataset|model
    python scripts/fetch_resource.py search    --query <keyword> --kind dataset|model
    python scripts/fetch_resource.py probe     --name <name> --kind model
    python scripts/fetch_resource.py list

Callers should not have to know an organization name: a bare ``--name`` is
resolved through site search and *ranked* (name exactness, task-hint overlap,
popularity, trusted namespace, size), so the top candidate is fetched and the
runner-ups are retried in order. ``search`` exposes the same ranking for
task-level requests that name no resource at all.

Cache location honors ``ONESCIENCE_RESOURCE_HOME`` (default ``~/.onescience``);
``ONESCIENCE_DATASETS_DIR`` / ``ONESCIENCE_MODELS_DIR`` add probe roots, the same
variables ``onescience-data-standardizer`` looks at.

Exit codes: 0 = usable resource delivered; 1 = blocked/failed (reason in the
JSON); 2 = bad invocation.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

import modelscope_hub as hub          # noqa: E402
import resource_paths as rp           # noqa: E402

REPO_URL_RE = re.compile(r"modelscope\.cn/(datasets|models)/([\w.\-]+/[\w.\-]+)")
REPO_ID_RE = re.compile(r"repo[_-]?id\s*[:=]\s*[\"']?([\w.\-]+/[\w.\-]+)", re.IGNORECASE)

STATUS_SUCCESS = "success"
STATUS_PARTIAL = "partial"
STATUS_FAILED = "failed"

METHOD_EXPLICIT = "explicit_path"
METHOD_PROBE = "local_probe"
METHOD_CACHE_HIT = "cache_hit"
METHOD_FETCH = "modelscope_fetch"

SOURCE_NAME_SEARCH = "name_search"
SOURCE_SEARCH_RANKED = "name_search_ranked"

# A ranked plan is only useful if a miss moves on to the next candidate, so
# every reason that means "this repo will not hand over data" is retryable.
RETRYABLE_REASONS = frozenset({
    hub.REASON_REPO_NOT_FOUND, hub.REASON_FAILED, hub.REASON_NETWORK,
    hub.REASON_AUTH, hub.REASON_EMPTY, hub.REASON_CHECKSUM,
    "verification_failed",
})
METHOD_PROBE_ONLY = "probe_only_miss"

# Logical names double as cache directory names, so they must stay single-path
# segments: no separator, no traversal, no empty.
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")


class Blocked(Exception):
    """A provisioning failure that must be reported instead of papered over."""

    def __init__(self, message: str, reason: str,
                 details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.reason = reason
        self.details = details or {}


# ----------------------------------------------------------------------
# repo_id inference
# ----------------------------------------------------------------------

def infer_repo_id(name: str,
                  explicit: Optional[str],
                  hints: List[str]) -> tuple:
    """Return (repo_id, repo_id_source) by the documented precedence."""
    if explicit:
        return explicit, "explicit"
    for hint in hints:
        if not hint:
            continue
        m = REPO_URL_RE.search(hint)
        if m:
            return m.group(2), "card_extract"
        m = REPO_ID_RE.search(hint)
        if m:
            return m.group(1), "card_extract"
    return hub.default_repo_id(name), "default_convention"


def _brief(cands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Compact candidate summary: enough to audit a choice, small enough to ship."""
    return [{"repo_id": c["repo_id"], "file_size": c["file_size"],
             "downloads": c["downloads"], "name_exact": c["name_exact"],
             "score": c.get("score"), "excluded": c.get("excluded")}
            for c in cands]


def _selection(cand: Dict[str, Any], ranking: Dict[str, Any]) -> Dict[str, Any]:
    """Why this repo was picked, plus what was passed over."""
    return {
        "chosen": cand["repo_id"],
        "score": cand["score"],
        "reasons": cand["reasons"],
        "name_exact": cand["name_exact"],
        "file_size": cand["file_size"],
        "downloads": cand["downloads"],
        "license": cand["license"],
        "display_name": cand["display_name"],
        "searched": ranking["queries"],
        "max_repo_bytes": ranking["max_bytes"],
        "alternatives": _brief([c for c in ranking["ranked"]
                                if c["repo_id"] != cand["repo_id"]]),
        "excluded": _brief(ranking["excluded"]),
    }


def collect_candidates(name: str, kind: str, args: argparse.Namespace,
                       warnings: List[str]) -> Dict[str, Any]:
    """Site search over the bare name plus any task-level queries, then rank.

    Merging queries is what lets a task description ("猫狗图像分类") resolve a
    repo sharing no literal with the requested logical name.
    """
    queries: List[str] = [name]
    for extra in (getattr(args, "search_query", None) or []):
        if extra and extra not in queries:
            queries.append(extra)

    merged: List[Dict[str, Any]] = []
    seen = set()
    errors: List[str] = []
    trace: List[Dict[str, Any]] = []
    for query in queries:
        outcome = hub.search_candidates_expanded(
            query, kind, page_size=args.search_page_size)
        trace.extend(outcome["queries_tried"])
        if outcome["status"] != "ok":
            errors.append("%s: %s" % (query, outcome["error"]))
            continue
        for cand in outcome["candidates"]:
            if cand["repo_id"] in seen:
                continue
            seen.add(cand["repo_id"])
            merged.append(cand)

    hints = list(getattr(args, "task_hint", None) or []) + queries[1:]
    max_bytes = hub.auto_max_bytes(getattr(args, "max_repo_bytes", None))
    ranking = hub.rank_candidates(
        merged, name, hints=hints, max_bytes=max_bytes,
        keep_auth=bool(getattr(args, "allow_gated", False)))
    ranking["queries"] = queries
    ranking["search_trace"] = trace
    ranking["search_errors"] = errors
    ranking["max_bytes"] = max_bytes
    return ranking


def plan_repos(name: str, kind: str, args: argparse.Namespace,
               warnings: List[str]) -> List[Dict[str, Any]]:
    """Ordered stage-3 attempts: ``[{repo_id, repo_id_source, selection}]``.

    Precedence stays documented — explicit, resource-card extraction, the
    OneScience/<name> convention — and when the convention does not exist the
    bare name gets a ranked site search instead of a refusal. Several same-named
    repos no longer block: the best-scoring one is tried first and the rest are
    kept as fallbacks, with the scoring reasons reported. ``--strict-name``
    restores the old "unique exact match or repo_ambiguous" behaviour for
    callers who want to choose themselves.
    """
    repo_id, source = infer_repo_id(name, args.repo_id, args.repo_hint)
    if source != "default_convention" or args.no_name_search:
        return [{"repo_id": repo_id, "repo_id_source": source, "selection": None}]

    exists = hub.repo_exists(repo_id, kind)
    if exists is True:
        return [{"repo_id": repo_id, "repo_id_source": source, "selection": None}]
    if exists is None:
        warnings.append("默认仓库 %s 的存在性未能确认（接口不可达或超时），直接按该 repo_id 尝试下载" % repo_id)
        return [{"repo_id": repo_id, "repo_id_source": source, "selection": None}]

    ranking = collect_candidates(name, kind, args, warnings)
    ranked, excluded = ranking["ranked"], ranking["excluded"]
    if ranking["search_errors"]:
        warnings.append("站内检索不可用（%s），仍按 %s 尝试下载"
                        % ("; ".join(ranking["search_errors"])[:160], repo_id))
    if not ranked:
        if excluded:
            raise Blocked(
                "'%s' 检索到候选但都不可自动选用（%s）"
                % (name, "/".join(sorted({c["excluded"] for c in excluded}))),
                hub.REASON_NO_CANDIDATE,
                {"tried_repo_id": repo_id, "searched": ranking["queries"],
                 "candidates": _brief(excluded)},
            )
        return [{"repo_id": repo_id, "repo_id_source": source, "selection": None}]

    exact = [c for c in ranked if c["name_exact"]]
    limit = max(1, int(args.candidate_attempts))

    if args.strict_name:
        if len(exact) == 1:
            warnings.append("默认仓库 %s 不存在，按站内检索改用 %s"
                            % (repo_id, exact[0]["repo_id"]))
            return [{"repo_id": exact[0]["repo_id"],
                     "repo_id_source": SOURCE_NAME_SEARCH,
                     "selection": _selection(exact[0], ranking)}]
        if len(exact) > 1:
            raise Blocked(
                "'%s' 在 ModelScope 上匹配到多个同名仓库，--strict-name 下不代作选择" % name,
                hub.REASON_AMBIGUOUS,
                {"tried_repo_id": repo_id, "candidates": _brief(exact),
                 "default_repo_id_missing": True},
            )
        warnings.append("站内检索没有逐字同名仓库，仍按 %s 尝试下载" % repo_id)
        return [{"repo_id": repo_id, "repo_id_source": source, "selection": None}]

    plan: List[Dict[str, Any]] = []
    for cand in ranked[:limit]:
        plan.append({
            "repo_id": cand["repo_id"],
            "repo_id_source": (SOURCE_NAME_SEARCH if cand["name_exact"]
                               else SOURCE_SEARCH_RANKED),
            "selection": _selection(cand, ranking),
        })
    if len(ranked) > limit:
        warnings.append("检索到 %d 个可选候选，按打分只试前 %d 个；要放宽用 --candidate-attempts"
                        % (len(ranked), limit))
    if exact:
        warnings.append("默认仓库 %s 不存在，按站内检索择优改用 %s"
                        % (repo_id, plan[0]["repo_id"]))
    else:
        warnings.append("没有逐字同名仓库，按任务语义与热度择优选用 %s" % plan[0]["repo_id"])
    return plan


# ----------------------------------------------------------------------
# Stage 1 / 2: resolution without network
# ----------------------------------------------------------------------

def resolve_local(name: str,
                  kind: str,
                  local_dir: Optional[str],
                  extra_probe_paths: List[str],
                  domain: Optional[str] = None) -> Optional[Dict[str, Any]]:
    if local_dir:
        cand = Path(local_dir).expanduser()
        stats = rp.dir_stats(cand) if cand.is_dir() else {"files": 0, "bytes": 0}
        if stats["files"] == 0:
            raise Blocked(
                f"explicit source_dir has no visible file: {cand}",
                "explicit_path_empty",
                {"path": str(cand)},
            )
        return {"path": str(cand), "method": METHOD_EXPLICIT, **stats}

    for probe in rp.probe_candidates(name, kind, extra_probe_paths, domain):
        if probe["usable"]:
            # A hit on the unified cache directory is a cache hit, not just some
            # local file: callers use that label to decide whether a refresh or a
            # re-download is warranted.
            hit_cache = probe["path"] == str(rp.cache_dir_for(name, kind).resolve())
            return {"path": probe["path"],
                    "method": METHOD_CACHE_HIT if hit_cache else METHOD_PROBE,
                    "files": probe["files"], "bytes": probe["bytes"]}
    return None


# ----------------------------------------------------------------------
# Verification
# ----------------------------------------------------------------------

def verify(path: str,
           required_patterns: List[str],
           min_files: int,
           min_bytes: int) -> Dict[str, Any]:
    root = Path(path)
    files = list(rp.visible_files(root))
    names = {p.relative_to(root).as_posix() for p in files}
    basenames = {p.name for p in files}
    total_bytes = sum(p.stat().st_size for p in files if p.is_file())

    checks: List[Dict[str, Any]] = []
    checks.append({
        "check": "populated",
        "passed": len(files) >= max(min_files, 1),
        "detail": f"{len(files)} visible file(s), >= {max(min_files, 1)} required",
    })
    if min_bytes > 0:
        checks.append({
            "check": "size_floor",
            "passed": total_bytes >= min_bytes,
            "detail": f"{total_bytes} bytes, floor {min_bytes}",
        })
    for pattern in required_patterns:
        hit = any(fnmatch.fnmatch(n, pattern)
                  or fnmatch.fnmatch(n.split("/")[-1], pattern) for n in names)
        checks.append({
            "check": f"required_file:{pattern}",
            "passed": hit,
            "detail": "matched" if hit else f"no visible file matches {pattern}",
        })

    passed = all(c["passed"] for c in checks)
    return {
        "passed": passed,
        "files": len(files),
        "bytes": total_bytes,
        "checks": checks,
        "failures": [c["check"] for c in checks if not c["passed"]],
    }


# ----------------------------------------------------------------------
# Provisioning
# ----------------------------------------------------------------------

def validate_name(name: str) -> str:
    if not NAME_RE.match(name):
        raise Blocked(
            f"unsafe resource name '{name}': use a single path segment matching "
            "[A-Za-z0-9][A-Za-z0-9._-] (no '/', '\\', or '..')",
            "invalid_resource_name",
        )
    return name


def provision_one(name: str,
                  kind: str,
                  args: argparse.Namespace) -> Dict[str, Any]:
    """Resolve one resource end to end; raises Blocked on unrecoverable misses."""
    name = validate_name(name)
    cache_dir = rp.cache_dir_for(name, kind)
    _, registry_warning = rp.registry_status()
    warnings: List[str] = []
    if registry_warning:
        warnings.append(registry_warning)
    resolved = resolve_local(name, kind, args.local_dir,
                             args.extra_probe_path, args.domain)

    if resolved is None and args.probe_only:
        raise Blocked(
            f"{kind} '{name}' not found locally and probe-only mode forbids download",
            "resource_missing",
            {"probed": rp.probe_candidates(name, kind, args.extra_probe_path,
                                           args.domain)},
        )

    fetch_details: Optional[Dict[str, Any]] = None
    selection: Optional[Dict[str, Any]] = None
    attempts: List[Dict[str, Any]] = []
    report: Optional[Dict[str, Any]] = None
    if resolved is None:
        free = rp.free_bytes(cache_dir)
        if free is not None and free < rp.MIN_FREE_BYTES:
            raise Blocked(
                f"insufficient free space on the cache volume: {free} bytes free",
                hub.REASON_DISK,
                {"free_bytes": free, "required_bytes": rp.MIN_FREE_BYTES},
            )
        plan = plan_repos(name, kind, args, warnings)
        last: Optional[Blocked] = None
        for idx, step in enumerate(plan):
            try:
                result = hub.fetch(
                    name=name,
                    cache_dir=cache_dir,
                    repo_id=step["repo_id"],
                    repo_type=kind,
                    revision=args.revision,
                    allow_git_lfs_fallback=args.allow_git_lfs_fallback,
                    repo_id_source=step["repo_id_source"],
                    work_dir=rp.work_dir_for(name, kind),
                )
            except hub.FetchError as exc:
                last = Blocked(str(exc), exc.reason, dict(exc.details or {}))
                attempts.append({"repo_id": step["repo_id"],
                                 "repo_id_source": step["repo_id_source"],
                                 "outcome": exc.reason})
                if exc.reason not in RETRYABLE_REASONS or idx + 1 >= len(plan):
                    last.details["fetch_attempts"] = attempts
                    if step["selection"]:
                        last.details["selection"] = step["selection"]
                    raise last from exc
                warnings.append("候选 %s 取不到（%s），按打分顺序改试下一个"
                                % (step["repo_id"], exc.reason))
                continue

            method = METHOD_CACHE_HIT if result.method == "cache_hit" else METHOD_FETCH
            fetch_details = result.to_dict()
            warnings.extend(result.warnings)
            report = verify(result.local_path, args.required_file,
                            args.min_files, args.min_bytes)
            attempts.append({"repo_id": step["repo_id"],
                             "repo_id_source": step["repo_id_source"],
                             "outcome": "ok" if report["passed"]
                             else "verification_failed",
                             "files": report["files"], "bytes": report["bytes"]})
            if not report["passed"] and idx + 1 < len(plan):
                warnings.append("候选 %s 落盘但未通过完整性校验（%s），改试下一个候选"
                                % (step["repo_id"], ", ".join(report["failures"])))
                fetch_details, report = None, None
                continue

            selection = step["selection"]
            resolved = {"path": result.local_path, "method": method,
                        "files": result.files, "bytes": result.bytes}
            if not args.revision and result.method != "cache_hit":
                warnings.append("未固定 revision，取的是仓库默认版本，严格复现需显式指定")
            break

        if resolved is None:
            raise Blocked(
                f"{kind} '{name}' could not be materialized from ModelScope",
                (last or Blocked("no candidate", hub.REASON_FAILED)).reason,
                {"fetch_attempts": attempts, "selection": selection},
            )

    root = Path(resolved["path"])
    if report is None:
        report = verify(resolved["path"], args.required_file,
                        args.min_files, args.min_bytes)
    digest = rp.content_digest(root)

    if not report["passed"]:
        raise Blocked(
            f"{kind} '{name}' landed at {resolved['path']} but failed verification: "
            f"{', '.join(report['failures'])}",
            "verification_failed",
            {"local_path": resolved["path"], "verification": report,
             "fetch_attempts": attempts},
        )

    entry = {
        "repo_id": (fetch_details or {}).get("repo_id") or registry_repo_id(name),
        "repo_id_source": (fetch_details or {}).get("repo_id_source", "registry_or_unknown"),
        "fetch_method": (fetch_details or {}).get("method", resolved["method"]),
        "local_path": resolved["path"],
        "files": report["files"],
        "bytes": report["bytes"],
        "content_digest": digest,
        "verified": True,
        "domain": args.domain or None,
    }
    registry_key = None
    if not args.no_register:
        registry_key, _ = rp.registry_upsert(name, kind, entry)

    return {
        "type": f"{kind}_resource",
        "name": name,
        "kind": kind,
        "domain": args.domain or "general",
        "path": resolved["path"],
        "local_path": resolved["path"],
        "resolution_method": resolved["method"],
        "registry_key": registry_key,
        "repo_id": entry["repo_id"],
        "repo_id_source": entry["repo_id_source"],
        "selection": selection,
        "fetch_attempts": attempts or None,
        "fetch": fetch_details or {"method": resolved["method"],
                                   "note": "resolved locally, no provider call"},
        "content_digest": digest,
        "files": report["files"],
        "bytes": report["bytes"],
        "verification": report,
        "warnings": warnings,
        "why_matched": f"resolved by {resolved['method']}",
        "limitations": _limitations(resolved["method"], fetch_details),
    }


def registry_repo_id(name: str) -> Optional[str]:
    """repo_id recorded by an earlier fetch; never guessed for a local hit.

    A directory found by probing proves only that data exists locally, so the
    provenance stays whatever the registry recorded (or null) instead of being
    back-filled with the default OneScience/<name> convention.
    """
    for entry in rp.registry_load()["resources"].values():
        if entry.get("name") == name and entry.get("repo_id"):
            return entry["repo_id"]
    return None


def _limitations(method: str, fetch_details: Optional[Dict[str, Any]]) -> str:
    if method == METHOD_EXPLICIT:
        return "调用方显式指定路径，未校验其与 ModelScope 仓库的一致性。"
    if method == METHOD_PROBE:
        return "命中本地已有缓存，未核对版本/修订是否与需求一致。"
    if method == METHOD_CACHE_HIT:
        return "缓存命中直接复用；如需强制更新请清理缓存目录或指定 --revision。"
    if fetch_details and fetch_details.get("method") == "git_lfs":
        return "经 Git LFS 兜底获取，未走 SDK 校验链路；完整性仅按可见文件/必需文件判定。"
    return ("内容来自 ModelScope 公开仓库；完整性仅校验可见文件数、必需文件通配与大小下界，"
            "未做语义级（字段/形状/物理量）校验。")


# ----------------------------------------------------------------------
# Result envelope
# ----------------------------------------------------------------------

def build_result(items: List[Dict[str, Any]],
                 missing: List[Dict[str, Any]],
                 query_summary: str,
                 domain: Optional[str]) -> Dict[str, Any]:
    if items and not missing:
        status = STATUS_SUCCESS
    elif items:
        status = STATUS_PARTIAL
    else:
        status = STATUS_FAILED
    result: Dict[str, Any] = {
        "status": status,
        "query_summary": query_summary,
        "detected_domain": domain or (items[0].get("domain") if items else None) or "general",
        "task_intent": "resource_provision",
        "provisioned_resources": items,
        "matched_resources": items,
        "missing_resources": missing,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    if missing:
        result["blocked_reason"] = missing[0]["reason"]
        result["next_recommendation"] = missing[0]["next_recommendation"]
    return {"resource_retrieval_result": result}


RECOMMENDATIONS = {
    hub.REASON_REPO_NOT_FOUND:
        "核对 repo_id（默认约定 OneScience/<name> 未命中，站内检索也没有同名仓库），或显式提供 --repo-id / source_dir。",
    hub.REASON_AMBIGUOUS:
        "已开 --strict-name 且同名仓库不止一个：从 details.candidates 里选定后以 --repo-id 重发；去掉 --strict-name 则按打分自动择优。",
    hub.REASON_NO_CANDIDATE:
        "检索到候选但都不可自动选用（needs_auth / over_max_bytes）：配好凭据后加 --allow-gated，或放宽 --max-repo-bytes，或从 details.candidates 显式指定 --repo-id。",
    hub.REASON_AUTH:
        "该仓库需要凭据：配置 MODELSCOPE_API_TOKEN 或 ~/.modelscope/credentials 后重试（本技能不代管凭据）。",
    hub.REASON_NETWORK:
        "网络或镜像不可达：确认出网策略/代理后重试；离线环境可先 --probe-only 只做本地判定。",
    hub.REASON_DISK:
        "缓存所在卷空间不足：清理缓存，或用 ONESCIENCE_RESOURCE_HOME 把缓存根换到大盘后重试。",
    hub.REASON_CHECKSUM:
        "下载内容校验失败：删除对应缓存目录后重新拉取。",
    hub.REASON_EMPTY:
        "仓库为空或仅含元数据：确认该 repo_id 是否真的发布了数据/权重。",
    hub.REASON_BACKEND_MISSING:
        "执行环境缺少 modelscope 后端：pip install modelscope（Git LFS 兜底需另装 git-lfs）。",
    hub.REASON_FAILED:
        "按 details 定位后重试；持续失败则如实报告 blocked，不得改用占位数据继续。",
    "resource_missing":
        "只探测未下载：确认允许联网后去掉 --probe-only 重新 provision。",
    "explicit_path_empty":
        "用户显式给出的目录里没有可见数据文件：核对路径或改由本地探测/ModelScope 获取。",
    "verification_failed":
        "资源已落盘但完整性未达标：检查必需文件是否随仓库发布，必要时换 repo_id 或修订版本。",
    "invalid_resource_name":
        "资源名不合法（含路径分隔符或相对路径片段）：改为单个安全目录名后重试。",
}


def missing_item(name: str, kind: str, exc: Blocked) -> Dict[str, Any]:
    return {
        "name": name,
        "kind": kind,
        "reason": exc.reason,
        "message": str(exc),
        "details": exc.details,
        "suggested_repo_id": hub.default_repo_id(name),
        "next_recommendation": RECOMMENDATIONS.get(
            exc.reason, RECOMMENDATIONS[hub.REASON_FAILED]),
    }


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def _add_common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--name", action="append", required=True,
                   help="逻辑资源名（可重复，用于一次准备多个资源）")
    p.add_argument("--kind", default=rp.KIND_DATASET, choices=list(rp.VALID_KINDS),
                   help="资源类型，对本次调用中每个 --name 都生效")
    p.add_argument("--domain", default=None)
    p.add_argument("--query-summary", dest="query_summary", default=None)


def _add_provision(p: argparse.ArgumentParser) -> None:
    p.add_argument("--repo-id", dest="repo_id", default=None,
                   help="显式 ModelScope repo_id（最高优先级）")
    p.add_argument("--repo-hint", dest="repo_hint", action="append", default=[],
                   help="来自资源卡/论文的文本，从中抽取 repo_id（可重复）")
    p.add_argument("--no-name-search", dest="no_name_search", action="store_true",
                   help="禁用按名检索：仅当默认约定 OneScience/<name> 命中时才下载")
    p.add_argument("--search-query", dest="search_query", action="append", default=[],
                   help="额外检索词（可重复）：资源名与仓库名不一致、或只给了任务描述时用来扩大命中面")
    p.add_argument("--task-hint", dest="task_hint", action="append", default=[],
                   help="任务描述片段（可重复）：参与候选打分，让只给任务的请求也能定向选仓")
    p.add_argument("--max-repo-bytes", dest="max_repo_bytes", type=int, default=None,
                   help="自动择优的仓库体积上限（字节）；缺省读 ONESCIENCE_RESOURCE_MAX_REPO_BYTES，再缺省 8 GiB；显式 --repo-id 不受此限")
    p.add_argument("--candidate-attempts", dest="candidate_attempts", type=int, default=3,
                   help="按打分顺序最多尝试几个候选（默认 3）")
    p.add_argument("--strict-name", dest="strict_name", action="store_true",
                   help="保守模式：只采纳逐字同名且唯一的命中，多命中报 repo_ambiguous 不代作选择")
    p.add_argument("--allow-gated", dest="allow_gated", action="store_true",
                   help="允许 gated/login_required/private 仓库进入自动择优（凭据需自备）")
    p.add_argument("--search-page-size", dest="search_page_size", type=int,
                   default=hub.SEARCH_PAGE_SIZE, help="检索接口每页条数（默认 20）")
    p.add_argument("--revision", default=None)
    p.add_argument("--local-dir", dest="local_dir", default=None,
                   help="段1：调用方显式指定的本地数据目录")
    p.add_argument("--extra-probe-path", dest="extra_probe_path", action="append",
                   default=[], help="额外的本地探测目录（可重复）")
    p.add_argument("--required-file", dest="required_file", action="append",
                   default=[], help="下载后必须存在的文件通配式（可重复）")
    p.add_argument("--min-files", dest="min_files", type=int, default=1)
    p.add_argument("--min-bytes", dest="min_bytes", type=int, default=0)
    p.add_argument("--probe-only", dest="probe_only", action="store_true",
                   help="只探测不下载（只读校测/离线受限环境）")
    p.add_argument("--allow-git-lfs-fallback", dest="allow_git_lfs_fallback",
                   action="store_true")
    p.add_argument("--no-register", dest="no_register", action="store_true",
                   help="不写入 ~/.onescience/resource_registry.json")


def _emit(payload: Dict[str, Any], output: Optional[str]) -> None:
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if output:
        Path(output).write_text(text, encoding="utf-8")
    try:
        print(text)
    except UnicodeEncodeError:
        # Windows consoles may sit on a code page that cannot carry every
        # Chinese message; escaping keeps the JSON contract machine-readable
        # instead of crashing the run at the reporting step.
        print(json.dumps(payload, indent=2, ensure_ascii=True))


def cmd_provision(args: argparse.Namespace) -> int:
    conflict = _single_shot_args(args)
    if conflict:
        print(json.dumps({"error": conflict}, ensure_ascii=False), file=sys.stderr)
        return 2
    items: List[Dict[str, Any]] = []
    missing: List[Dict[str, Any]] = []
    for name in args.name:
        try:
            items.append(provision_one(name, args.kind, args))
        except Blocked as exc:
            missing.append(missing_item(name, args.kind, exc))
        except OSError as exc:
            missing.append(missing_item(
                name, args.kind,
                Blocked(f"io error while provisioning {name}: {exc}", "fetch_failed")))
    payload = build_result(items, missing,
                           args.query_summary or f"provision {args.kind}: {args.name}",
                           args.domain)
    _emit(payload, args.output)
    return 0 if items and not missing else 1


def _single_shot_args(args: argparse.Namespace) -> Optional[str]:
    """Refuse per-resource arguments when several resources are requested.

    ``--local-dir`` and ``--repo-id`` name one concrete path/repository. Reusing
    them for a second ``--name`` would silently hand that resource someone
    else's data, which is worse than refusing to run.
    """
    if len(args.name) < 2:
        return None
    given = [flag for flag, value in (("--local-dir", args.local_dir),
                                      ("--repo-id", args.repo_id)) if value]
    if given:
        return (f"{given[0]} identifies a single resource; drop it or pass one "
                f"--name at a time (got {len(args.name)})")
    return None


def cmd_probe(args: argparse.Namespace) -> int:
    items: List[Dict[str, Any]] = []
    missing: List[Dict[str, Any]] = []
    for name in args.name:
        try:
            name = validate_name(name)
        except Blocked as exc:
            missing.append(missing_item(name, args.kind, exc))
            continue
        resolved = resolve_local(name, args.kind, None,
                                 args.extra_probe_path, args.domain)
        if resolved:
            items.append({
                "type": f"{args.kind}_resource",
                "name": name,
                "kind": args.kind,
                "domain": args.domain or "general",
                "path": resolved["path"],
                "local_path": resolved["path"],
                "resolution_method": resolved["method"],
                "files": resolved["files"],
                "bytes": resolved["bytes"],
                "limitations": _limitations(resolved["method"], None),
                "details": {"probed": rp.probe_candidates(
                    name, args.kind, args.extra_probe_path, args.domain)},
            })
        else:
            missing.append({
                "name": name,
                "kind": args.kind,
                "reason": "resource_missing",
                "message": f"{args.kind} '{name}' not found locally",
                "suggested_repo_id": hub.default_repo_id(name),
                "details": {"probed": rp.probe_candidates(
                    name, args.kind, args.extra_probe_path, args.domain)},
                "next_recommendation": RECOMMENDATIONS["resource_missing"],
            })
    payload = build_result(items, missing,
                           args.query_summary or f"probe {args.kind}: {args.name}",
                           args.domain)
    _emit(payload, args.output)
    return 0 if items and not missing else 1


def cmd_search(args: argparse.Namespace) -> int:
    """Rank ModelScope candidates for a keyword; no download, no cache write.

    This is the discovery half for task-level requests that name no resource:
    the caller reads the ranking, picks a repo (or accepts the top one), then
    runs ``provision --repo-id`` — or simply lets ``provision`` rank for it.
    """
    queries: List[Dict[str, Any]] = []
    for query in args.query:
        outcome = hub.search_candidates_expanded(
            query, args.kind, page_size=args.page_size)
        if outcome["status"] != "ok":
            queries.append({"query": query, "kind": args.kind,
                            "status": "unavailable", "candidates": [],
                            "excluded": [], "queries_tried":
                                outcome["queries_tried"],
                            "error": outcome["error"]})
            continue
        ranking = hub.rank_candidates(
            outcome["candidates"], query, hints=list(args.task_hint or []),
            max_bytes=hub.auto_max_bytes(args.max_repo_bytes),
            keep_auth=bool(args.allow_gated))
        queries.append({
            "query": query, "kind": args.kind, "status": "ok",
            "candidates": ranking["ranked"][:max(1, args.top)],
            "excluded": ranking["excluded"],
            "queries_tried": outcome["queries_tried"],
            "error": None,
        })

    hit = any(q["candidates"] for q in queries)
    all_ok = all(q["status"] == "ok" for q in queries)
    payload = {
        "status": STATUS_SUCCESS if hit and all_ok else (STATUS_PARTIAL if hit
                                                        else STATUS_FAILED),
        "task_intent": "resource_search",
        "query_summary": "search %s candidates for %s" % (args.kind, args.query),
        "queries": queries,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "next_recommendation": (
            "选定候选后用 provision --name <逻辑名> --repo-id <repo_id> 物化；"
            "或直接把该关键词交给 provision --name/--search-query 让其自动择优。"
            if hit else
            "检索接口对长句只按子串匹配，脚本已自动拆词重试；仍无命中就换更短的"
            "关键词（2-6 字中文词或单个英文词）或改用 --kind 重试；"
            "两轮都无命中时如实报告 resource_plan_empty，不得改用占位数据。"),
    }
    _emit(payload, args.output)
    return 0 if hit else 1


def cmd_list(_: argparse.Namespace) -> int:
    data = rp.registry_load()
    print(json.dumps({"registry_path": str(rp.registry_path()), **data},
                     indent=2, ensure_ascii=False))
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_prov = sub.add_parser("provision", help="三段式解析并在缺资源时从 ModelScope 下载")
    _add_common(p_prov)
    _add_provision(p_prov)
    p_prov.add_argument("--output", default=None, help="把结果 JSON 另存到该路径")
    p_prov.set_defaults(func=cmd_provision)

    p_probe = sub.add_parser("probe", help="只读探测本地是否已有该资源")
    _add_common(p_probe)
    p_probe.add_argument("--extra-probe-path", dest="extra_probe_path",
                         action="append", default=[])
    p_probe.add_argument("--output", default=None)
    p_probe.set_defaults(func=cmd_probe)

    p_search = sub.add_parser(
        "search", help="按关键词检索 ModelScope 候选并打分排序（只读，不下载）")
    p_search.add_argument("--query", action="append", required=True,
                          help="检索词（可重复）：裸资源名或任务关键词均可")
    p_search.add_argument("--kind", default=rp.KIND_DATASET,
                          choices=list(rp.VALID_KINDS))
    p_search.add_argument("--task-hint", dest="task_hint", action="append",
                          default=[], help="任务描述片段（可重复），参与打分")
    p_search.add_argument("--top", type=int, default=8, help="返回前 N 个候选")
    p_search.add_argument("--max-repo-bytes", dest="max_repo_bytes", type=int,
                          default=None, help="体积上限；超出者列入 excluded")
    p_search.add_argument("--allow-gated", dest="allow_gated", action="store_true",
                          help="把需凭据的仓库也纳入排序")
    p_search.add_argument("--page-size", dest="page_size", type=int,
                          default=hub.SEARCH_PAGE_SIZE)
    p_search.add_argument("--output", default=None)
    p_search.set_defaults(func=cmd_search)

    p_list = sub.add_parser("list", help="打印资源注册表")
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
