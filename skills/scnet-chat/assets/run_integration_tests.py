# -*- coding: utf-8 -*-
"""
SCNet Chat 集成测试：使用 ~/.scnet-chat.env 与真实 API（可能产生计费/机时消耗）。

运行（在技能根目录）:
  python assets/run_integration_tests.py

日志写入本目录下 test_integration_log.txt 与 test_integration_results.json
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

try:
    import aiohttp  # noqa: F401
except ImportError:
    print("请先执行: pip install aiohttp", file=sys.stderr)
    sys.exit(1)

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
SCNET_PY = SCRIPTS / "scnet.py"
CACHE_PY = SCRIPTS / "cache.py"
CONFIG_PATH = Path.home() / ".scnet-chat.env"
ASSETS_DIR = Path(__file__).resolve().parent
LOG_PATH = ASSETS_DIR / "test_integration_log.txt"
RESULTS_PATH = ASSETS_DIR / "test_integration_results.json"


def _console_safe(s: str) -> str:
    """Windows 控制台常为 GBK，避免打印子进程输出中的 emoji 时崩溃。"""
    enc = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        return s.encode(enc, errors="replace").decode(enc, errors="replace")
    except (LookupError, TypeError, UnicodeError):
        return s.encode("ascii", errors="replace").decode("ascii")


def _log(msg: str) -> None:
    line = f"[{datetime.now(timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(_console_safe(line))
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def _run_scnet(nl: str, timeout: int) -> tuple[int, str]:
    """调用自然语言入口 scnet.py。"""
    proc = subprocess.run(
        [sys.executable, str(SCNET_PY), nl],
        cwd=str(SKILL_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    out = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    return proc.returncode, out.strip()


def _run_cache_init(timeout: int = 120) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(CACHE_PY)],
        cwd=str(SKILL_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    out = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    return proc.returncode, out.strip()


def _cache_path_from_config() -> Path | None:
    if not CONFIG_PATH.exists():
        return None
    user = None
    try:
        for line in CONFIG_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() == "SCNET_USER":
                user = v.strip()
                break
    except OSError:
        return None
    if user:
        return Path.home() / f".scnet-chat-cache-{user}.json"
    return Path.home() / ".scnet-chat-cache.json"


def _output_looks_ok(output: str) -> bool:
    """scnet.py 正常退出时未必区分业务失败，用语义标记判断。"""
    bad = (
        "配置文件不存在",
        "未能理解",
        "缓存刷新失败",
        "AC 认证 token 不可用",
        "配置错误",
        "读取配置文件失败",
        "查询失败",
        "作业提交失败",
    )
    return not any(m in output for m in bad)


def _parse_submitted_job_id(output: str) -> str | None:
    m = re.search(r"作业提交成功[^\d]*(\d{3,})", output)
    if m:
        return m.group(1)
    m2 = re.search(r"作业ID[：:]\s*\S*?(\d{3,})", output)
    if m2:
        return m2.group(1)
    return None


def main() -> int:
    LOG_PATH.write_text("", encoding="utf-8")
    results: list[dict] = []

    def record(name: str, ok: bool, detail: str = "", extra: dict | None = None):
        entry = {"name": name, "ok": ok, "detail": (detail or "")[:8000]}
        if extra:
            entry.update(extra)
        results.append(entry)
        _log(f"{'PASS' if ok else 'FAIL'} | {name} | {detail[:200]!r}")

    if not CONFIG_PATH.exists():
        record("config_exists", False, f"缺少配置文件: {CONFIG_PATH}")
        RESULTS_PATH.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        return 1

    record("config_exists", True, str(CONFIG_PATH))

    cache_path = _cache_path_from_config()
    if cache_path and not cache_path.exists():
        _log("缓存不存在，执行 cache.py 初始化…")
        code, out = _run_cache_init(120)
        record("cache_init", code == 0, out[:4000] if out else "(无输出)", {"returncode": code})
        if code != 0:
            RESULTS_PATH.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
            return 1
    else:
        record("cache_file", True, str(cache_path) if cache_path else "default path")

    try:
        out = ""
        rc = 1
        for attempt in range(3):
            proc = subprocess.run(
                [sys.executable, str(SCRIPTS / "job.py"), "--queues"],
                cwd=str(SKILL_ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60,
            )
            out = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
            rc = proc.returncode
            if rc == 0 and "NullPointerException" not in out and '"code": "0"' in out:
                break
            time.sleep(3)
        record("job_py_queues", rc == 0 and "NullPointerException" not in out, out[:6000], {"returncode": rc})
    except Exception as e:  # noqa: BLE001
        record("job_py_queues", False, f"{e}\n{traceback.format_exc()}")

    cases: list[tuple[str, str, int]] = [
        ("nl_user", "查询用户", 45),
        ("nl_walltime", "机时", 45),
        ("nl_queues", "查询队列", 60),
        ("nl_cluster", "集群信息", 45),
        ("nl_jobs", "查询作业", 90),
        ("nl_history", "历史作业 最近1天", 120),
        ("nl_help", "帮助", 30),
    ]

    for key, nl, timeout in cases:
        try:
            code, out = _run_scnet(nl, timeout)
            ok = code == 0 and _output_looks_ok(out) and len(out.strip()) > 2
            record(key, ok, f"rc={code}\n{out}", {"returncode": code})
        except Exception as e:  # noqa: BLE001
            record(key, False, f"{e}\n{traceback.format_exc()}")

    # 使用较长 sleep、默认墙钟（与显式「运行时间」组合在部分区域会触发平台错误/权限拒绝）
    job_id: str | None = None
    try:
        code, out = _run_scnet("提交作业 sleep 120", 120)
        job_id = _parse_submitted_job_id(out)
        blocked = "Access/permission denied" in out or "access restricted" in out
        ok_submit = (
            code == 0
            and job_id is not None
            and "作业提交失败" not in out
            and "提交失败" not in out
        )
        if blocked:
            record(
                "nl_submit_sleep",
                True,
                f"SKIP（平台侧限制或并发）\nrc={code}\n{out}",
                {"returncode": code, "job_id": job_id, "skipped": True},
            )
        else:
            record("nl_submit_sleep", ok_submit, f"rc={code}\n{out}", {"returncode": code, "job_id": job_id})
    except Exception as e:  # noqa: BLE001
        record("nl_submit_sleep", False, f"{e}\n{traceback.format_exc()}")

    if job_id:
        # 实时详情 API 偶有几秒延迟，立即删除会报「未找到作业」
        time.sleep(8)
        try:
            code, out = _run_scnet(f"删除作业 {job_id}", 90)
            ok_del = code == 0 and "删除成功" in out and job_id in out
            record("nl_delete_job", ok_del, f"rc={code}\n{out}", {"returncode": code, "job_id": job_id})
        except Exception as e:  # noqa: BLE001
            record("nl_delete_job", False, f"{e}\n{traceback.format_exc()}")

    RESULTS_PATH.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    failed = [r for r in results if not r.get("ok")]
    _log(f"完成: {len(results) - len(failed)}/{len(results)} 通过")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
