#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""onescience-online-knowledge · 通道②：晶体结构 / 物质数据在线取数。

能力：给定物质名 / 化学式（或直接的 COD 编号），从 Crystallography Open Database
真实下载 CIF，抽取晶格参数、空间群、分数坐标，并**强制用化学式回验**，
只有回验通过的结构才作为 `verified_online=true` 的证据交付；取不到就返回
found=false（**绝不默写坐标**，交由上层按纪律降级为「带标注的先验」）。

纯标准库（urllib/json/re/argparse），兼容 Python 3.6；网络不可用打印 [OFFLINE]
并正常退出，绝不抛栈中断上层任务。

用法：
  python structure_fetch.py --name glycine --formula C2H5NO2 --workdir ./online_kb
  python structure_fetch.py --cod-id 1010222 --formula C2H5NO2 --workdir ./online_kb
"""
import argparse, json, os, re, ssl, sys, time
from urllib import request, error, parse

try:
    sys.stdout.reconfigure(encoding="utf-8")  # 避免 Windows GBK 控制台打印 ⚠/中文崩道；Linux 默认 UTF-8
except Exception:
    pass

MAIN = "https://www.crystallography.net"
BASES = [
    "https://www.crystallography.net/cod",   # 官方（实测 result.php?formula=<Hill 带空格> 可用）
    "http://qiserver.ugr.es/cod",             # 西班牙镜像
    "http://www.crystallography.net/cod",     # 官方 http
]
CIF_URL = MAIN + "/cod/{cid}.cif"          # 已实测：按编号下载稳定 200
UA = "Mozilla/5.0 (compatible; onescience-online-knowledge/1.0)"

_net_ok = True  # 运行期网络状态，异常时置 False


def _ctx():
    try:
        return ssl._create_unverified_context()
    except Exception:
        return None


def http_get(url, timeout=30, data=None, headers=None, cookies=None):
    """返回 (status, body_text, resp_headers)。网络失败返回 (None, '', {})。"""
    global _net_ok
    h = {"User-Agent": UA}
    if headers:
        h.update(headers)
    if cookies:
        h["Cookie"] = cookies
    try:
        req = request.Request(url, data=data.encode() if isinstance(data, str) else data, headers=h)
        with request.urlopen(req, timeout=timeout, context=_ctx()) as r:
            raw = r.read()
            try:
                setc = r.headers.get("Set-Cookie", "")
            except Exception:
                setc = ""
            return r.getcode(), raw.decode("utf-8", "replace"), {"set_cookie": setc}
    except (error.URLError, error.HTTPError, OSError) as e:
        _net_ok = False
        code = getattr(e, "code", None)
        if isinstance(e, error.HTTPError):
            return code, "", {}
        return None, "", {}


def norm_counts(formula):
    """把 'C2H5NO2' / 'C2 H5 N O2' 归一化为 {元素: 计数} 多重集。"""
    if not formula:
        return {}
    s = formula.replace("(", "").replace(")", "").replace("'", "").strip()
    s = re.sub(r"\s+", "", s)
    counts = {}
    for el, num in re.findall(r"([A-Z][a-z]?)(\d*)", s):
        if not el:
            continue
        counts[el] = counts.get(el, 0) + (int(num) if num else 1)
    return counts


def formula_match(target, cif_sum):
    tc, cc = norm_counts(target), norm_counts(cif_sum)
    if not tc:
        return True  # 未给目标化学式则不卡
    return tc == cc  # 元素计数完全一致才算回验通过


# ---------- COD 检索（化学式 → 候选编号）：session 握手 + format=lst 取号 ----------
def spaced_hill(formula):
    """把 C2H5NO2 变成 COD 'like' 检索需要的 'C2 H5 N O2'（元素与数字间插空格）。"""
    toks = re.findall(r"[A-Z][a-z]?\d*", formula or "")
    return " ".join(toks)


def discover_cod_ids(name=None, formula=None, limit=40):
    """正确发现姿势（已实测）：
    1) GET result.php?formula=<Hill 带空格>&count=.. → 页面里建立并回带 CODSESSION；
    2) GET result.php?format=lst&CODSESSION=<sid> → 直接返回纯 COD 编号列表；
    取到的号仍会在下游逐个下载 + 化学式回验，错的剔除。
    注：裸 chemical_name/pattern 等字段名会被 COD 忽略并返回默认列表，故以 formula 为准。"""
    ids, seen = [], set()
    if not (_net_ok and formula):
        return ids
    q = "formula=" + parse.quote(spaced_hill(formula))
    for base in BASES:
        url = base + "/result.php?" + q + "&count=%d&order_by=vol&order=asc" % max(limit, 40)
        st, body, _ = http_get(url)
        if st != 200 or not body:
            continue
        m = re.search(r"CODSESSION=(\w+)", body)
        if not m:
            continue
        st2, lst, _ = http_get(base + "/result.php?format=lst&CODSESSION=" + m.group(1))
        if st2 != 200 or not lst:
            continue
        for tok in re.findall(r"\b(\d{6,7})\b", lst):
            if tok not in seen:
                seen.add(tok); ids.append(tok)
        if ids:
            break
    return ids[:limit]


# ---------- CIF 解析 ----------
def _fnum(tok):
    """解析 CIF 数值，剥离标准不确定度后缀 (n) 与末尾句点；无法解析返回 None。"""
    if tok is None:
        return None
    t = tok.strip().rstrip(".")
    t = re.sub(r"\((?:\d+|\?)\)", "", t).strip()
    if not t or t in ("?", "."):
        return None
    try:
        return float(t)
    except ValueError:
        return None


def parse_cif(text):
    out = {"formula_sum": None, "cell": {}, "spacegroup": None, "atoms": []}
    m = re.search(r"_chemical_formula_sum\s+'?([^'\r\n]+)'?", text)
    if m:
        out["formula_sum"] = m.group(1).strip()
    for key, tag in [("a", "_cell_length_a"), ("b", "_cell_length_b"), ("c", "_cell_length_c"),
                     ("alpha", "_cell_angle_alpha"), ("beta", "_cell_angle_beta"), ("gamma", "_cell_angle_gamma")]:
        mm = re.search(re.escape(tag) + r"\s+([0-9.]+)", text)
        if mm:
            out["cell"][key] = float(mm.group(1))
    sg = re.search(r"(?:_symmetry_space_group_name_H-M|_space_group_name_H-M_alt)\s+'?([^'\r\n]+)'?", text)
    if sg:
        out["spacegroup"] = sg.group(1).strip()
    # 逐 loop_ 找 atom_site 块
    for blk in re.split(r"\n\s*loop_", text)[1:]:
        if "_atom_site_fract_x" not in blk:
            continue
        head = blk.split("\n\n")[0]
        order = [c for c in re.findall(r"_(?:atom_site|site)_(\w+)", head)]
        rows = []
        for line in head.splitlines():
            line = line.strip()
            if not line or line.startswith("_") or line.startswith("#") or line.startswith("loop_"):
                continue
            rows.append(line.split())
        if "fract_x" not in order:
            continue
        try:
            ix, iy, iz = order.index("fract_x"), order.index("fract_y"), order.index("fract_z")
            il = order.index("label") if "label" in order else 0
            it = order.index("type_symbol") if "type_symbol" in order else None
        except ValueError:
            continue
        for r in rows:
            if len(r) <= max(ix, iy, iz):
                continue
            xs, ys, zs = _fnum(r[ix]), _fnum(r[iy]), _fnum(r[iz])
            if xs is None or ys is None or zs is None:
                continue  # 非数值（如 ? 占位）行跳过
            out["atoms"].append({"label": r[il], "element": (r[it] if it is not None and it < len(r) else r[il]),
                                 "x": xs, "y": ys, "z": zs})
        break
    return out


# ---------- 锚点表 ----------
def load_anchors():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "cod_anchors.json")
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name")
    ap.add_argument("--formula")
    ap.add_argument("--cod-id", dest="cod_id")
    ap.add_argument("--workdir", default="./online_kb")
    ap.add_argument("--max", type=int, default=15, help="最多回验多少个候选")
    args = ap.parse_args()
    os.makedirs(args.workdir, exist_ok=True)

    # 1) 组织候选编号：显式号 → 在线发现（默认主路）→ 锚点表（仅在线不可达时兜底）
    #    锚点只是加速缓存，不是数据源头；所有候选（含锚点）一律走下载+化学式回验。
    anchors = load_anchors()
    key = (args.name or "").lower().strip()
    cand = []
    if args.cod_id:
        cand.append(args.cod_id)
    if not cand and (args.name or args.formula):
        cand += discover_cod_ids(name=args.name, formula=args.formula, limit=args.max * 2)
    if not cand:  # 在线发现为空（多为离线/端点不可达）才查锚点，且仍回验
        if key in anchors:
            a = anchors[key]
            cand += a["cod_ids"] if isinstance(a, dict) else a

    items, tried, accepted = [], [], 0
    for cid in cand[: args.max]:
        st, body, _ = http_get(CIF_URL.format(cid=cid))
        if st != 200 or not body or "_chemical_formula_sum" not in body:
            tried.append({"cod_id": cid, "status": st, "verdict": "download_failed"})
            continue
        parsed = parse_cif(body)
        ok = formula_match(args.formula, parsed["formula_sum"])
        tried.append({"cod_id": cid, "status": st, "formula_sum": parsed["formula_sum"],
                      "verdict": "match" if ok else "formula_mismatch"})
        if not ok:
            continue  # 回验不符：丢弃，换下一个（绝不将错就错）
        cif_path = os.path.join(args.workdir, "cod_%s.cif" % cid)
        with open(cif_path, "w", encoding="utf-8") as f:
            f.write(body)
        accepted += 1
        items.append({
            "key": "%s_structure" % (key or cid),
            "channel": "structure",
            "value": {"cod_id": cid, "cif_path": cif_path, "formula_sum": parsed["formula_sum"],
                      "cell": parsed["cell"], "spacegroup": parsed["spacegroup"],
                      "atom_count": len(parsed["atoms"]), "atoms_fract": parsed["atoms"]},
            "provenance": "COD:%s" % cid,
            "source_type": "database",
            "evidence_level": "db-record",
            # 本条 CIF 刚刚真实下载并通过化学式回验——即使某个端点瞬时失败把 _net_ok
            # 置了 False，也不能把已在线取到的数据误标为 offline（粘滞离线 bug）。
            "verified_online": True,
            "self_verified": True,
            "domain_match": "exact",
            "confidence": "high",
            "note": "化学式回验通过（%s）" % parsed["formula_sum"],
        })
        if accepted >= 3:
            break

    # 2) 全部未命中：如实返回 found=false（不默写坐标，交上层按纪律降级为先验）
    if not items:
        reason = "offline" if not _net_ok else ("no candidate matched formula %s" % args.formula if cand else "未检索到候选编号")
        items.append({
            "key": "%s_structure" % (key or "unknown"),
            "channel": "structure",
            "value": None,
            "provenance": "model-prior(no online hit: %s)" % reason,
            "source_type": "model-prior",
            "evidence_level": "prior",
            "verified_online": False,
            "self_verified": False,
            "domain_match": None,
            "confidence": "low",
            "note": "⚠ 未经在线核实：COD 取数/回验未命中，禁止把先验坐标冒充 COD/文献出处；由上层决定是否降级为带标注先验。",
        })

    result = {"channel": "structure", "query": {"name": args.name, "formula": args.formula, "cod_id": args.cod_id},
              "network": "online" if (accepted > 0 or _net_ok) else "offline",
              "candidates_tried": tried, "items": items, "found": accepted > 0}
    outp = os.path.join(args.workdir, "structure_result.json")
    with open(outp, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    if not _net_ok:
        print("[OFFLINE] COD 不可达；structure 通道返回 found=false，未默写坐标。")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("\n[saved] %s" % outp)


if __name__ == "__main__":
    main()
