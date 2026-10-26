#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""onescience-online-knowledge · 通道③：软件级计算参数查询（静态表 + 在线核对）。

基线来自 assets/param_reference.json（按软件栈 + 计算类型组织的推荐参数与出处），
产出统一 schema 的 items[]（channel=software-param、source_type=software-doc）。
--live 时逐个标签实时抓取 VASP 官方 wiki 对应页面并摘录定义段，把该项升级为
verified_online=true 且附 wiki URL 出处；抓不到（离线/页面改版）自动退回静态表
并如实标注。这些值来自软件文档/惯例，不写 DOI；存疑项以 confidence=low + note
『⚠』如实标出，供上层核对，绝不升格为已核实事实。纯标准库，网络不可用不崩溃。

用法：
  python param_lookup.py --software VASP --calc NMR-GIPAW --live
  python param_lookup.py --software VASP --calc opt --workdir ./online_kb
"""
import argparse, json, os, re, ssl, sys
from urllib import request, error, parse

try:
    sys.stdout.reconfigure(encoding="utf-8")  # py3.7+；3.6/Linux 下默认即 UTF-8，异常忽略
except Exception:
    pass

ASSET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "param_reference.json")
WIKI_BASES = [
    "https://wiki.vasp.at/index.php/",           # VASP 新 wiki（2024+）
    "https://www.vasp.at/wiki/index.php/",       # 旧地址（多数仍跳转/可用）
]
UA = "Mozilla/5.0 (compatible; onescience-online-knowledge/1.0)"


def _ctx():
    try:
        return ssl._create_unverified_context()
    except Exception:
        return None


def fetch_wiki(tag, timeout=20):
    """实时抓 VASP wiki 标签页，返回 (url, 摘录文本) 或 (None, None)。"""
    tag = re.sub(r"[^A-Za-z0-9_\-]", "", str(tag or ""))
    if not tag:
        return None, None
    for base in WIKI_BASES:
        url = base + tag
        try:
            req = request.Request(url, headers={"User-Agent": UA})
            with request.urlopen(req, timeout=timeout, context=_ctx()) as r:
                html = r.read().decode("utf-8", "replace")
        except (error.URLError, error.HTTPError, OSError):
            continue
        if "wiki" not in html.lower():
            continue
        # 去脚本/样式/标签，取正文前段作为定义摘录
        body = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html)
        m = re.search(r"(?is)<div[^>]*id=.mw-content-text.(.*?)(<h2|<footer|$)", body)
        text = re.sub(r"(?s)<[^>]+>", " ", m.group(1) if m else body)
        text = re.sub(r"\[\d+\]|\s+", " ", text).strip()
        # 截到第一个较完整段落（~900 字符），避免整页噪声
        excerpt = text[:900]
        if len(excerpt) > 80 and tag.lower() in excerpt.lower():
            return r.geturl(), excerpt
        if len(excerpt) > 80:
            return r.geturl(), excerpt
    return None, None


def load():
    try:
        with open(ASSET, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"_error": "无法读取参数表: %s" % e}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--software", required=True, help="VASP / QuantumESPRESSO / CASTEP ...")
    ap.add_argument("--calc", required=True, help="opt / NMR-GIPAW / ... 计算类型")
    ap.add_argument("--workdir", default="./online_kb")
    ap.add_argument("--live", action="store_true", help="实时抓 VASP wiki 核对每个标签（失败自动退静态表）")
    args = ap.parse_args()
    os.makedirs(args.workdir, exist_ok=True)

    db = load()
    sw = db.get(args.software, {})
    rows = sw.get(args.calc, [])
    if not isinstance(db, dict) or "_error" in db:
        print(json.dumps(db, ensure_ascii=False))
        return

    items, live_ok_count = [], 0
    for r in rows:
        conf = r.get("confidence", "medium")
        item = {
            "key": "%s" % r.get("name"),
            "channel": "software-param",
            "value": r.get("value"),
            "provenance": "software-doc:%s" % r.get("source", "curated"),
            "source_type": "software-doc",
            "evidence_level": "curated-ref",
            "verified_online": False,     # 基线：内置参考表，非本次联网取
            "self_verified": False,
            "domain_match": None,
            "confidence": conf,
            "applies": r.get("applies", ""),
            "note": ("⚠ 存疑项，须核对官方 wiki/实测确认，不得当已核实事实" if conf == "low" else r.get("note", "")),
        }
        if args.live and args.software.upper() == "VASP":
            url, excerpt = fetch_wiki(r.get("name"))
            if url and excerpt:
                item["verified_online"] = True
                item["self_verified"] = True   # 标签存在性与描述已在官方 wiki 实页核对
                item["provenance"] = "software-doc:vasp-wiki:%s" % r.get("name")
                item["wiki_url"] = url
                item["wiki_excerpt"] = excerpt
                item["note"] = ("已在线核对 VASP wiki（值仍为推荐惯例，具体体系须按 ENMAX/测试实定）。"
                                + ("⚠ 原存疑标记保留：wiki 页未直接给出推荐值。" if conf == "low" else "")).strip()
                live_ok_count += 1
            else:
                item["note"] = (item["note"] + " | --live 抓取 wiki 失败，退回静态表").strip(" |")
        items.append(item)

    result = {
        "channel": "software-param",
        "query": {"software": args.software, "calc": args.calc, "live": bool(args.live)},
        "found": len(items) > 0,
        "live_verified": live_ok_count,
        "note": ("命中参数表" if items else "本表未收录 %s/%s；请先核对官方 wiki，缺失项按带标注先验处理，不 blocked 任务" % (args.software, args.calc)),
        "items": items,
    }
    outp = os.path.join(args.workdir, "param_result.json")
    with open(outp, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("\n[saved] %s" % outp)


if __name__ == "__main__":
    main()
