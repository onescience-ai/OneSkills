#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OneScience 远程工作台探测：枚举平台 SSH 连接、只读探测软件矩阵、输出推荐依据。

边界：只做 `command -v` / `module avail` / 加速器列表等只读探测；不安装、不提交作业、
不修改远端状态。私钥只按 ~/.ssh/config 中的路径引用，脚本不读取、不打印密钥内容。

用法：
  python probe_remote_env.py list-connections
  python probe_remote_env.py probe --needs vasp,lammps
  python probe_remote_env.py probe --needs vasp --conn xsl15389127580 --timeout 30
  python probe_remote_env.py probe --needs vasp,lammps --timeout 25 --retries 2
  python probe_remote_env.py probe --needs vasp --cache ./onescience.probe_cache.json
"""
import argparse
import glob
import json
import os
import re
import shlex
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

CONFIG_PATH = os.path.expanduser("~/.ssh/config")

# 软件名 -> 远端可探测的标志性命令/模块关键字
SOFTWARE_SIGNATURES = {
    "vasp": ["vasp_std", "vasp_gam", "vasp_ncl"],
    "qe": ["pw.x", "cp.x"],
    "cp2k": ["cp2k.popt", "cp2k.psmp"],
    "lammps": ["lmp", "lammps"],
    "gpaw": ["gpaw"],
    "abacus": ["abacus"],
    "vaspkit": ["vaspkit"],
}
# 模块名粗匹配（module avail 输出）
MODULE_PATTERNS = r"vasp[\w.-]*|lammps[\w.-]*|cp2k[\w.-]*|quantum[-\s]?espresso[\w.-]*|gpaw[\w.-]*|abacus[\w.-]*|openmpi[\w.-]*|dtk[\w.-]*|rocm[\w.-]*|cuda[\w.-]*"

# 探测失败分类：并发/负载下 SSH 握手易瞬时超时，这类是"未验证"而非"确认不可达"，
# 可重试；认证类失败是确定性的（重试也不会变），不重试、直接如实标注。
TRANSIENT_TOKENS = ("timed out", "timeout", "connection reset", "connection closed",
                    "connection refused", "no route to host", "broken pipe",
                    "kex_exchange_identification", "could not resolve", "temporary failure")
AUTHFAIL_TOKENS = ("permission denied", "publickey", "no such identity",
                   "too many authentication failures", "host key verification failed",
                   "authentication failed")


def classify_probe_failure(out):
    """把"远端命令没跑起来"的失败分成 auth_failed（确定性）与 timeout（可重试）。"""
    low = (out or "").lower()
    if any(t in low for t in AUTHFAIL_TOKENS):
        return "auth_failed"
    if any(t in low for t in TRANSIENT_TOKENS):
        return "timeout"
    # 无法归类时按可重试处理，避免把一次抖动误判成永久不可达。
    return "timeout"


def parse_platform_blocks(text):
    """解析平台写入的 `# >>> opencode ssh <name>` 块；同 Host 多连接靠块名区分。"""
    conns = []
    for m in re.finditer(r"# >>> opencode ssh (.+?)\n(.*?)# <<< opencode ssh", text, re.S):
        name, body = m.group(1).strip(), m.group(2)
        conn = {"name": name}
        for line in body.splitlines():
            line = line.strip()
            low = line.lower()
            if low.startswith("host ") and "hostname" not in low:
                conn.setdefault("host", line.split(None, 1)[1])
            elif low.startswith("hostname"):
                conn["host"] = line.split(None, 1)[1]
            elif low.startswith("user "):
                conn["user"] = line.split(None, 1)[1]
            elif low.startswith("port "):
                conn["port"] = line.split(None, 1)[1]
            elif low.startswith("identityfile"):
                conn["identity_file"] = os.path.expandvars(line.split(None, 1)[1])
            elif low.startswith("# remoteworkdir"):
                wps = line.split()
                if len(wps) > 2:
                    conn["remote_work_dir"] = " ".join(wps[2:])
        conn.setdefault("port", "22")
        conn.setdefault("host", conn.get("name"))
        if conn.get("user"):
            conns.append(conn)
    return conns


def parse_plain_hosts(text):
    """无平台标记时退回解析标准 Host 别名块（跳过通配）。"""
    conns, cur = [], None
    for line in text.splitlines():
        s = line.strip()
        if s.lower().startswith("host ") and "*" not in s:
            if cur:
                conns.append(cur)
            cur = {"name": s.split(None, 1)[1], "port": "22"}
        elif cur:
            low = s.lower()
            if low.startswith("hostname"):
                cur["host"] = s.split(None, 1)[1]
            elif low.startswith("user "):
                cur["user"] = s.split(None, 1)[1]
            elif low.startswith("port "):
                cur["port"] = s.split(None, 1)[1]
            elif low.startswith("identityfile"):
                cur["identity_file"] = os.path.expandvars(s.split(None, 1)[1])
    if cur:
        conns.append(cur)
    for c in conns:
        c.setdefault("host", c["name"])
    return [c for c in conns if c.get("user")]


def _read_config_text(path, seen_files):
    """读取一个 ssh config 文件文本；路径无效/已读过/非普通文件/读失败均返回 None。"""
    if not path:
        return None
    try:
        rp = os.path.realpath(os.path.expanduser(path))
    except (OSError, ValueError):
        return None
    if rp in seen_files or not os.path.isfile(rp):
        return None
    seen_files.add(rp)
    try:
        return open(rp, encoding="utf-8", errors="replace").read()
    except OSError:
        return None


def _include_targets(text, base_dir):
    """解析 ssh config 的 `Include` 指令，展开通配后返回被包含文件路径列表。"""
    out = []
    for line in (text or "").splitlines():
        s = line.strip()
        if s.lower().startswith("include ") or s.lower().startswith("include\t"):
            for token in s.split(None, 1)[1].split():
                token = os.path.expandvars(os.path.expanduser(token))
                if not os.path.isabs(token) and base_dir:
                    token = os.path.join(base_dir, token)
                out.extend(glob.glob(token))
    return out


def _platform_ssh_config_paths(conns):
    """定位账号隔离的平台 SSH 配置 `platform-ssh/<accountId>/config`：
    一是从已解析连接的 identity_file 路径反推其所在 acct 目录，二是扫描常见基路径
    （ONESCIENCE_PLATFORM_SSH_HOME、XDG_DATA_HOME/opencode/platform-ssh）。预置连接
    通常只写在这里，只读 ~/.ssh/config 会漏掉它们。"""
    dirs = set()
    for c in conns:
        idf = (c.get("identity_file") or "").replace("\\", "/")
        m = re.search(r"(.*platform-ssh/[^/]+)", idf)
        if m:
            dirs.add(m.group(1))
    bases = [os.environ.get("ONESCIENCE_PLATFORM_SSH_HOME"),
             os.path.join(os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share"),
                          "opencode", "platform-ssh")]
    for b in bases:
        if b and os.path.isdir(b):
            try:
                for acct in os.listdir(b):
                    dirs.add(os.path.join(b, acct))
            except OSError:
                pass
    return [os.path.join(d, "config") for d in sorted(dirs)]


def load_connections(path=CONFIG_PATH):
    """枚举所有平台 SSH 连接：`~/.ssh/config`（含其 `Include`）+ 账号隔离的
    `platform-ssh/<accountId>/config`，合并后按连接 name 去重。预置连接常只落在
    platform-ssh 目录，只读 ~/.ssh/config 会漏判，导致工作台弹窗少列候选连接。"""
    seen_files, conns, names = set(), [], set()

    def ingest(p):
        text = _read_config_text(p, seen_files)
        if text is None:
            return
        for c in (parse_platform_blocks(text) or parse_plain_hosts(text)):
            key = c.get("name") or (c.get("user"), c.get("host"), c.get("port"))
            if key in names:
                continue
            names.add(key)
            conns.append(c)
        base_dir = os.path.dirname(os.path.realpath(os.path.expanduser(p)))
        for inc in _include_targets(text, base_dir):
            ingest(inc)

    ingest(path)
    # 先按已解析连接的 identity_file 反推 acct 目录，再按常见基路径兜底；
    # 读入后可能带出新 acct，故做第二轮发现。
    for rnd in (1, 2):
        for cfg in _platform_ssh_config_paths(list(conns)):
            ingest(cfg)
    return conns


def build_remote_probe(needs):
    parts = ["echo ARCH=$(uname -m)"]
    safe = [n for n in needs if re.fullmatch(r"[a-z0-9._-]{1,32}", n)]
    for sw in sorted(set(safe)):
        for sig in SOFTWARE_SIGNATURES.get(sw, [sw]):
            parts.append(f"command -v {sig} >/dev/null 2>&1 && echo HIT:{sw}:{sig}")
    parts.append(f"module avail 2>&1 | grep -oiE '{MODULE_PATTERNS}' | sort -u | head -20 | sed 's/^/MOD:/'")
    parts.append("nvidia-smi -L 2>/dev/null | head -2 | sed 's/^/GPU:/'")
    parts.append("hy-smi 2>/dev/null | head -4 | sed 's/^/DCU:/'")
    parts.append("rocm-smi -i 2>/dev/null | head -4 | sed 's/^/DCU:/'")
    parts.append("command -v sbatch >/dev/null 2>&1 && echo SLURM:yes")
    parts.append("command -v conda >/dev/null 2>&1 && echo CONDA:yes")
    inner = "; ".join(parts)
    # HPC 上的 `module` 通常是登录 shell 里才定义的函数；非交互 ssh 直接跑拿不到
    # module，因此在远端用 `bash -lc` 走一次登录 shell 以初始化 Environment Modules。
    return "bash -lc " + shlex.quote(inner)


def resolve_identity(conn):
    """解析可用私钥：优先在 ~/.ssh/identities 真实密钥目录按 basename / 用户名匹配
    （平台 config 的 IdentityFile 常指向已失效的 .local 旧路径，那里即使存在也可能是
    坏密钥导致超时/拒绝）；identities 无匹配时才回退 config 的 IdentityFile。"""
    ident = conn.get("identity_file")
    iddir = os.path.join(os.path.expanduser("~"), ".ssh", "identities")
    if os.path.isdir(iddir):
        base = os.path.basename(ident) if ident else ""
        user = (conn.get("user") or "").lower()
        cands = sorted(os.path.join(iddir, f) for f in os.listdir(iddir))
        if base:
            for f in cands:
                if os.path.basename(f) == base:
                    return f
        if user:
            for f in cands:
                if user in os.path.basename(f).lower():
                    return f
    if ident and os.path.exists(ident):
        return ident
    return None


def probe_connection(conn, needs, timeout, retries=2):
    ident = resolve_identity(conn)
    argv = ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null", "-o", f"ConnectTimeout={min(15, timeout)}",
            "-p", str(conn.get("port", "22"))]
    if ident:
        argv += ["-i", ident]
    argv += [f"{conn['user']}@{conn['host']}", build_remote_probe(needs)]
    result = {"name": conn["name"], "user": conn["user"], "host": conn["host"],
              "port": conn["port"], "reachable": False, "state": "unknown",
              "unverified": False, "recommendable": False, "software": {},
              "accelerators": [], "modules": [], "evidence": [], "score": 0, "reason": ""}

    # 只有"远端命令真正跑起来"（首行回显 ARCH=）才算可达；瞬时超时可重试，
    # 认证失败为确定性错误不重试。单次超时不得直接判 unreachable。
    attempts, kind, lines, last_err = 0, "timeout", [], ""
    while True:
        attempts += 1
        try:
            p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        except (subprocess.TimeoutExpired, OSError) as e:
            kind, last_err, lines = "timeout", str(e)[:200], []
        else:
            out = (p.stdout or "") + "\n" + (p.stderr or "")
            lines = [l.strip() for l in out.splitlines() if l.strip()]
            if any(l.startswith("ARCH=") for l in lines):
                kind = "ok"
                break
            kind = classify_probe_failure(out)
            last_err = out.strip()[:200] or "ssh failed"
        if kind == "auth_failed":
            break  # 确定性失败，重试无意义
        if attempts <= retries:
            time.sleep(min(2 * attempts, 6))
            continue
        break
    result["attempts"] = attempts

    if kind != "ok":
        result["state"] = kind
        result["reachable"] = False
        result["unverified"] = (kind == "timeout")
        result["error"] = last_err
        if kind == "auth_failed":
            result["reason"] = "认证失败（确定性，需修复密钥/账号）"
        else:
            result["reason"] = f"探测超时/连接失败，未完成验证（已重试 {attempts} 次，不可断定为不可达）"
        return result

    hits, mods, accs = [], [], []
    for l in lines:
        if l.startswith("HIT:"):
            hits.append(l)
        elif l.startswith("MOD:"):
            mods.append(l[4:])
        elif l.startswith(("GPU:", "DCU:")):
            accs.append(l)
        elif l.startswith("ARCH="):
            result["arch"] = l.split("=", 1)[1]
        elif l.startswith(("SLURM:", "CONDA:")):
            accs.append(l)
    # reachable 必须以"远端命令真正执行"为准：probe 首行 echo ARCH=，只有认证通过、
    # 命令跑起来才会有 ARCH= 行。ssh 认证失败时只会吐 stderr 告警（no such identity /
    # Permission denied），绝不能把这些告警当成功，否则会把连不上的主机探成 reachable。
    result["reachable"] = True
    result["state"] = "ok"
    for h in hits:
        _, sw, sig = h.split(":", 2)
        result["software"].setdefault(sw, []).append(sig)
    result["modules"] = sorted(set(mods))[:20]
    result["accelerators"] = accs[:8]
    result["evidence"] = hits[:12]
    score = 1 if result["reachable"] else 0
    satisfied, missing = [], []
    for n in needs:
        found = bool(result["software"].get(n)) or any(
            n in m.lower() or n.replace("qe", "espresso") in m.lower() for m in result["modules"])
        (satisfied if found else missing).append(n)
        score += 10 if found else 0
    result["satisfied_needs"] = satisfied
    result["missing_needs"] = missing
    result["score"] = score
    # recommendable：只有确实可连通且满足至少一项目标商软需求的连接，才可被标为推荐；
    # "可达但未检到目标软件"的连接不具推荐资格，避免 fail-open 误导用户。
    result["recommendable"] = bool(result["reachable"] and satisfied)
    if satisfied:
        result["reason"] = "已具备 " + "、".join(satisfied)
        if missing:
            result["reason"] += "；缺 " + "、".join(missing)
    elif missing:
        result["reason"] = "可连通但未检到 " + "、".join(missing) + "（不具推荐资格，可能需安装）"
    else:
        result["reason"] = "可连通"
    if accs:
        result["reason"] += "；" + "; ".join(a.split(":", 1)[-1].strip() for a in accs[:2])
    return result


def main():
    ap = argparse.ArgumentParser(description="OneScience remote workbench probe")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list-connections", help="枚举 ~/.ssh/config 中的平台 SSH 连接")
    pp = sub.add_parser("probe", help="只读探测各连接软件矩阵并给出推荐")
    pp.add_argument("--needs", default="", help="逗号分隔的软件需求，如 vasp,lammps")
    pp.add_argument("--conn", action="append", default=[], help="只探测指定连接名（可多次）")
    pp.add_argument("--timeout", type=int, default=20, help="单连接探测超时秒数")
    pp.add_argument("--retries", type=int, default=2, help="瞬时超时/连接失败的额外重试次数（认证失败不重试）")
    pp.add_argument("--cache", default="", help="探测结果缓存 JSON 路径")
    pp.add_argument("--max-age", type=int, default=6 * 3600, help="缓存有效期秒数")
    args = ap.parse_args()

    if args.cmd == "list-connections":
        print(json.dumps(load_connections(), ensure_ascii=False, indent=2))
        return

    conns = load_connections()
    if args.conn:
        conns = [c for c in conns if c["name"] in args.conn]
    needs = [n.strip().lower() for n in args.needs.split(",") if n.strip()]
    for n in needs:
        if not re.fullmatch(r"[a-z0-9._-]{1,32}", n):
            sys.exit(f"非法需求标识: {n}")

    cache, cache_path = None, args.cache or None
    if cache_path and os.path.exists(cache_path):
        try:
            data = json.load(open(cache_path, encoding="utf-8"))
            fresh = time.time() - data.get("generated_at", 0) <= args.max_age
            same_needs = sorted(data.get("needs", [])) == sorted(needs)
            known = {c["name"] for c in conns}
            cached_names = {r["name"] for r in data.get("connections", [])}
            cached_incomplete = any(r.get("unverified") for r in data.get("connections", []))
            if fresh and same_needs and known <= cached_names and not cached_incomplete:
                cache = data
        except Exception:
            cache = None

    if cache:
        result = cache
        result["from_cache"] = True
    else:
        # 并发探测各连接，使总耗时≈单个最慢连接，避免多连接串行超过平台 bash 工具超时。
        with ThreadPoolExecutor(max_workers=max(1, min(6, len(conns) or 1))) as ex:
            results = list(ex.map(
                lambda c: probe_connection(c, needs, args.timeout, args.retries), conns))
        results.sort(key=lambda r: (r["recommendable"], r["score"]), reverse=True)
        result = {"generated_at": int(time.time()), "needs": needs,
                  "connections": results, "from_cache": False}
        # 推荐只给"确实满足目标商软需求"的连接；禁止 fail-open：
        # 若没有任何可推荐连接、但存在因超时未完成验证的连接，宁可留空推荐
        # 并标注"需重试"，也绝不把"可达但无商软"的连接标成推荐去误导用户。
        recommendable = [r for r in results if r.get("recommendable")]
        unverified = [r for r in results if r.get("unverified")]
        if recommendable:
            result["recommended"] = recommendable[0]["name"]
        elif unverified:
            result["recommended"] = None
            result["probe_incomplete"] = True
            result["no_recommend_reason"] = (
                "存在因超时未完成验证的连接（%s），不能断定其不具备目标商软；"
                "暂不给出推荐，请重试探测，不要改而推荐'可达但无商软'的连接。"
                % "、".join(r["name"] for r in unverified))
        else:
            result["recommended"] = None
            result["no_recommend_reason"] = "已验证的所有连接均未检到目标商软，无推荐项（可能需安装）。"
        if cache_path and not result.get("probe_incomplete"):
            # 探测不完整（含未验证连接）的结果不写缓存，下次重新探测。
            try:
                json.dump(result, open(cache_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            except Exception:
                pass
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
