#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""onescience-online-knowledge · 引用溯源自检（provenance-by-copy）。

用途：把**终稿里出现的具体标识符**（DOI / COD 号 / arXiv 号 / PDB / UniProt）与本轮
**工具真实产出**的证据文件做集合差，逐条判定：
  grounded   —— 标识符逐字见于工具证据（lit_result.json / structure_result.json /
                param_result.json / cod_*.cif，或 --evidence 显式传入的工具输出转储）；
  disclosed  —— 未见于工具证据，但**同一行**已明确标注为模型先验/未经在线核实/仅abstract（诚实降级，合规）；
  violation  —— 未见于工具证据、且未作任何先验标注 —— 即「把记忆包装成检索所得」，必须修。

纪律要点：**agent 自己写的 online_knowledge.json 默认不作为证据源**（循环论证：那份文件
里的 DOI 本来就是 agent 抄写/生成的）；确需纳入时用 --allow-selfauthored 显式声明。

退出码：0=无 violation；2=存在 violation（可被 CI/上层直接卡住）；3=用法错误。
纯标准库、不联网，兼容 Python 3.6。

用法：
  python check_provenance.py --answer answer.md --workdir ./online_kb
  python check_provenance.py --answer answer.md --evidence tool_out.log --json-out prov.json
"""
import argparse, io, json, os, re, sys

try:
    sys.stdout.reconfigure(encoding="utf-8")  # 避免 Windows GBK 控制台打印 ⚠/中文崩道
except Exception:
    pass

# ---------- 标识符抽取 ----------
DOI_RE = re.compile(r"10\.\d{4,9}/[0-9A-Za-z._\-<>\/]+")
COD_RE = re.compile(r"(?:COD\s*[:#]?\s*|cod\.?crystallography\.net/cod/|crystallography\.net/cod/)(\d{6,8})", re.I)
ARXIV_RE = re.compile(r"arXiv[:\s]*(\d{4}\.\d{4,5}(?:v\d+)?)", re.I)
PDB_RE = re.compile(r"(?:PDB\s*[:#]?\s*|rcsb\.org/pdb/entry/)([0-9A-Za-z]{4})\b", re.I)
UNIPROT_RE = re.compile(r"(?:UniProt\s*[:#]?\s*|uniprot\.org/b/?)([A-NR-Z][0-9][A-Z][0-9][0-9][0-9][0-9]|[A-Z][P-Q][0-9][A-Z][0-9][0-9][0-9][0-9])\b", re.I)

TRAIL = ".,;:)]}>`\"'\\|（）()，。；、】 \u3000<"

# 诚实披露标记：未接地但已在**同一行**声明为先验/未核实 => 合规降级，不算 violation
DISCLOSE_RE = re.compile(
    u"模型先验|未经在线核实|未经核实|未核实|待核实|待核|先验区|凭先验|未检索到|检索未命中|"
    u"无出处|存疑|疑似|不可采信|未验证|unverified|not\\s+verified|model\\s+prior|hallucinat|"
    u"abstract-only|abstract\\s*级|无全文回执|no\\s+source", re.I)

# agent 自写产物：默认排除出证据源（循环论证）
SELF_AUTHORED = ("online_knowledge.json",)
TOOL_EVIDENCE = ("lit_result.json", "structure_result.json", "param_result.json")


def trim_token(t):
    while t and t[-1] in TRAIL:
        t = t[:-1]
    return t


def extract_identifiers(text):
    """返回 [(kind, token, pos), ...]，同一 token 只留首次出现位置。"""
    found, seen = [], set()

    def push(kind, tok, pos):
        key = (kind, tok.lower())
        if key in seen:
            return
        seen.add(key)
        found.append((kind, tok, pos))

    for m in DOI_RE.finditer(text):
        tok = trim_token(m.group(0))
        if tok.count("/") > 0 and len(tok) >= 8:
            push("doi", tok, m.start())
    for rx, kind in ((COD_RE, "cod"), (ARXIV_RE, "arxiv"), (PDB_RE, "pdb"), (UNIPROT_RE, "uniprot")):
        for m in rx.finditer(text):
            push(kind, m.group(1), m.start())
    return found


def collect_evidence(workdirs, extra_paths, allow_self=False):
    """把工具真实产出的证据文件内容拼成一个语料串；返回 (blob, 纳入文件列表, 被排除文件列表)。"""
    files, skipped = [], []
    for wd in [d for d in workdirs if d]:
        if not os.path.isdir(wd):
            continue
        for root, _dirs, names in os.walk(wd):
            for n in names:
                low = n.lower()
                if low in SELF_AUTHORED:
                    # 自写产物：仅在显式允许时计入证据源，否则登记为已排除
                    if allow_self:
                        files.append(os.path.join(root, n))
                    else:
                        skipped.append(os.path.join(root, n))
                    continue
                if low in TOOL_EVIDENCE or low.endswith("_result.json") or low.endswith(".cif"):
                    files.append(os.path.join(root, n))
    for p in extra_paths:
        if os.path.isdir(p):
            for root, _dirs, names in os.walk(p):
                for n in names:
                    if n.lower() in SELF_AUTHORED and not allow_self:
                        skipped.append(os.path.join(root, n))
                    else:
                        files.append(os.path.join(root, n))
        elif os.path.isfile(p):
            files.append(p)

    blob_parts = []
    used = []
    for f in dict.fromkeys(files):
        try:
            blob_parts.append(io.open(f, encoding="utf-8", errors="replace").read())
            used.append(f)
        except Exception as e:
            print("[WARN] 证据文件读失败 %s: %s" % (f, e))
    return "\n".join(blob_parts), used, skipped


def disclosed_same_line(text, pos):
    """披露标注必须与标识符**同行**才算数。
    不用固定字符窗口：窗口会让相邻表行的“abstract-only”串到本行，把无回执引用洗白。"""
    lo = text.rfind("\n", 0, pos) + 1
    hi = text.find("\n", pos)
    if hi < 0:
        hi = len(text)
    return bool(DISCLOSE_RE.search(text[lo:hi]))


def main():
    ap = argparse.ArgumentParser(description="终稿引用与工具证据的溯源自检（provenance-by-copy）")
    ap.add_argument("--answer", required=True, help="终稿文本文件（md/txt）")
    ap.add_argument("--workdir", default="./online_kb", help="在线兜底产物目录（自动发现 *result.json / *.cif）")
    ap.add_argument("--evidence", action="append", default=[], help="额外证据文件或目录，可重复传")
    ap.add_argument("--extra-workdir", action="append", default=[], help="额外扫描目录，可重复传")
    ap.add_argument("--allow-selfauthored", action="store_true",
                    help="允许把 online_knowledge.json（agent 自写）计入证据源；默认禁止，避免循环论证")
    ap.add_argument("--strict", action="store_true", help="已标注先验的未接地标识符也计为 violation")
    ap.add_argument("--json-out", help="结果落盘路径，默认 <workdir>/provenance_result.json")
    args = ap.parse_args()

    if not os.path.isfile(args.answer):
        print("[ERR] 终稿文件不存在: %s" % args.answer)
        return 3

    text = io.open(args.answer, encoding="utf-8", errors="replace").read()
    ids = extract_identifiers(text)
    blob, used, skipped = collect_evidence([args.workdir] + list(args.extra_workdir),
                                           list(args.evidence), args.allow_selfauthored)
    blob_l = blob.lower()

    out = {"answer": args.answer, "evidence_files": used, "evidence_excluded_selfauthored": skipped,
           "strict": args.strict, "counts": {}, "items": []}
    g = d = v = 0
    print("=== 引用溯源自检 · %s ===" % os.path.basename(args.answer))
    print("证据源=工具产出 %d 个文件%s；标识符 %d 个" % (
        len(used), ("（已排除 agent 自写 %d 个）" % len(skipped)) if skipped else "", len(ids)))
    for kind, tok, pos in ids:
        base = tok.lower().replace("https://doi.org/", "").replace("http://dx.doi.org/", "")
        grounded = base in blob_l or tok.lower() in blob_l
        if grounded:
            g += 1
            verdict = "接地✓"
        else:
            disc = disclosed_same_line(text, pos)
            if disc:
                d += 1
                if args.strict:
                    v += 1  # 严格模式：已标注先验也计 violation
                verdict = "violation(严格)" if args.strict else "已标注先验(合规)"
            else:
                v += 1
                verdict = "⚠violation：无检索回执且未标注先验"
        if not grounded:
            ctx = text[max(0, pos - 70):pos + 10].replace("\n", " ")
            print("   [%-6s] %-46s %s" % (kind, tok[:46], verdict))
            print("            上下文: ...%s" % ctx[-78:])
            out["items"].append({"kind": kind, "token": tok, "grounded": False,
                                 "disclosed": disc, "violation": (not disc) or args.strict,
                                 "context": ctx[-80:]})
    out["counts"] = {"total": len(ids), "grounded": g, "disclosed_ungrounded": d, "violations": v}
    rate = (100.0 * g / len(ids)) if ids else 100.0
    print("接地率 %d/%d (%.0f%%) · 合规先验 %d · violation %d" % (g, len(ids), rate, d, v))
    if v:
        print("→ 处置：把这些标识符改成「模型先验·未经在线核实」措辞，或补一轮针对性检索取回真实回执后再引用。")

    jp = args.json_out or (os.path.join(args.workdir, "provenance_result.json")
                           if args.workdir else "provenance_result.json")
    try:
        os.makedirs(os.path.dirname(jp) or ".", exist_ok=True)
        with io.open(jp, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print("[OUT] %s" % jp)
    except Exception as e:
        print("[WARN] 结果落盘失败: %s" % e)
    return 2 if v else 0


if __name__ == "__main__":
    sys.exit(main())
