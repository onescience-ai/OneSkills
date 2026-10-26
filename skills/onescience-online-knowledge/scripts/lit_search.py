#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""onescience-online-knowledge · 通道①：文献检索（题录 + 摘要 + 免费全文线索）。

OpenAlex works 相关性检索为主（同时抓取 is_oa / best_oa_location 免费全文直链，
不再浪费 OA 信息），Europe PMC search 兜底；对命中 DOI 逐条查 Unpaywall 找合法
OA 版（机构库/预印本 PDF）；另设 arXiv API 通道（cond-mat 等计算领域论文大量
免费全文）。--fetch-oa 时会把 OA PDF 下载落盘并尽力用 pymupdf 抽取全文文本。
产出统一 schema 的 items[]（channel=literature、source_type=literature、
evidence_level=abstract|full-text-oa）。付费墙仍然成立：拿不到合法 OA 版的就
如实停在 abstract，绝不绕墙。纯标准库，网络不可用打印 [OFFLINE] 并正常退出。

用法：
  python lit_search.py "glycine 13C 15N chemical shift GIPAW" --max 15 --workdir ./online_kb
  python lit_search.py "glycine GIPAW NMR" --max 10 --fetch-oa --oa-limit 5 --workdir ./online_kb
"""
import argparse, json, os, re, ssl, sys
from urllib import request, error, parse

try:
    sys.stdout.reconfigure(encoding="utf-8")  # 避免 Windows GBK 控制台打印 ⚠/特殊字符崩道；Linux 默认 UTF-8
except Exception:
    pass

OA = "https://api.openalex.org/works"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
UNPAYWALL = "https://api.unpaywall.org/v2/"
ARXIV = "http://export.arxiv.org/api/query"
UA = "onescience-online-knowledge/1.0 (mailto:research@example.org)"
_net_ok = True


def _ctx():
    try:
        return ssl._create_unverified_context()
    except Exception:
        return None


def get_json(url, timeout=30):
    global _net_ok
    try:
        req = request.Request(url, headers={"User-Agent": UA})
        with request.urlopen(req, timeout=timeout, context=_ctx()) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except (error.URLError, error.HTTPError, OSError, ValueError) as e:
        _net_ok = False
        sys.stderr.write("net err: %s: %s\n" % (type(e).__name__, e))
        return None


def reconstruct_abstract(inv):
    if not inv:
        return ""
    pos = {}
    for w, idxs in inv.items():
        for i in idxs:
            pos[i] = w
    return " ".join(pos[k] for k in sorted(pos))[:1200]


def get_text(url, timeout=40, binary=False):
    """GET 文本/二进制；失败返回 None（不翻转 _net_ok 之外的状态）。"""
    global _net_ok
    try:
        req = request.Request(url, headers={"User-Agent": UA})
        with request.urlopen(req, timeout=timeout, context=_ctx()) as r:
            raw = r.read()
            return raw if binary else raw.decode("utf-8", "replace")
    except (error.URLError, error.HTTPError, OSError) as e:
        _net_ok = False
        sys.stderr.write("net err: %s: %s\n" % (type(e).__name__, e))
        return None


def openalex(query, maxn):
    url = OA + "?" + parse.urlencode({
        "search": query, "per-page": maxn,
        "select": "id,doi,title,publication_year,authorships,abstract_inverted_index,cited_by_count,"
                  "open_access,best_oa_location",
        "filter": "type:article",
    })
    d = get_json(url)
    if not d:
        return []
    out = []
    for w in d.get("results", [])[:maxn]:
        auths = [a.get("author", {}).get("display_name", "") for a in w.get("authorships", [])][:3]
        oa = w.get("open_access") or {}
        bol = w.get("best_oa_location") or {}
        out.append({
            "title": w.get("title"),
            "year": w.get("publication_year"),
            "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
            "authors": auths,
            "cited_by": w.get("cited_by_count"),
            "abstract": reconstruct_abstract(w.get("abstract_inverted_index")),
            "is_oa": bool(oa.get("is_oa")),
            "oa_pdf_url": bol.get("pdf_url"),
            "oa_url": bol.get("landing_page_url") or oa.get("oa_url"),
        })
    return out


def unpaywall_lookup(doi):
    """查 DOI 的合法 OA 版（Unpaywall 聚合机构库/预印本）。返回 (is_oa, pdf_url) 或 (None, None)。"""
    if not doi:
        return None, None
    d = get_json(UNPAYWALL + parse.quote(doi, "") + "?" + parse.urlencode({"email": "research@example.org"}), timeout=20)
    if not d or not isinstance(d, dict):
        return None, None
    loc = d.get("best_oa_location") or {}
    return bool(d.get("is_oa")), loc.get("url_for_pdf")


def arxiv_search(query, maxn):
    """arXiv API：cond-mat/物理/CS 计算类论文多在这里，全部免费全文。"""
    xml = get_text(ARXIV + "?" + parse.urlencode({"search_query": "all:" + query,
                                                  "max_results": maxn, "sortBy": "relevance"}), timeout=30)
    if not xml:
        return []
    out = []
    for entry in re.findall(r"<entry>([\s\S]*?)</entry>", xml)[:maxn]:
        def tag(t):
            m = re.search(r"<%s[^>]*>([\s\S]*?)</%s>" % (t, t), entry)
            return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
        aid_url = tag("id")
        m = re.search(r"arxiv\.org/abs/([\w.\-/]+)", aid_url)
        aid = m.group(1) if m else ""
        out.append({
            "title": tag("title"),
            "year": tag("published")[:4],
            "doi": "",
            "authors": re.findall(r"<name>([^<]+)</name>", entry)[:3],
            "cited_by": None,
            "abstract": tag("summary")[:1200],
            "is_oa": True,
            "oa_pdf_url": ("https://arxiv.org/pdf/%s" % aid) if aid else None,
            "oa_url": aid_url,
        })
    return out


def try_extract_pdf(pdf_path):
    """尽力抽 PDF 全文文本：优先 pymupdf，备选 pdfminer.six；都没有返回 None。"""
    try:
        import fitz  # pymupdf
        doc = fitz.open(pdf_path)
        return "\n".join(page.get_text() for page in doc)[:400000]
    except Exception:
        pass
    try:
        from pdfminer.high_level import extract_text
        return extract_text(pdf_path)[:400000]
    except Exception:
        return None


def fetch_oa_pdf(rec, workdir):
    """下载 OA PDF 并尝试抽取全文。返回 (pdf_path, fulltext_path or None)。"""
    url = rec.get("oa_pdf_url")
    if not url:
        return None, None
    slug = re.sub(r"[^\w.\-]+", "_", (rec.get("doi") or rec.get("title") or "lit")[:60])
    pdf_path = os.path.join(workdir, "%s.pdf" % slug)
    data = get_text(url, timeout=60, binary=True)
    if not data or not data[:5].startswith(b"%PDF"):
        return None, None  # 非 PDF（登录页/HTML），如实放弃
    with open(pdf_path, "wb") as f:
        f.write(data)
    text = try_extract_pdf(pdf_path)
    if not text:
        return pdf_path, None
    txt_path = os.path.join(workdir, "%s_fulltext.txt" % slug)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    return pdf_path, txt_path


def europepmc(query, maxn):
    url = EPMC + "?" + parse.urlencode({"query": query, "format": "json", "pageSize": maxn,
                                          "resultType": "core"})
    d = get_json(url)
    if not d:
        return []
    out = []
    for r in d.get("resultList", {}).get("result", [])[:maxn]:
        out.append({
            "title": r.get("title"),
            "year": (r.get("pubdate") or "")[:4],
            "doi": r.get("doi", ""),
            "authors": [x.get("name", "") for x in []][:3],
            "cited_by": r.get("citedByCount"),
            "abstract": r.get("abstractText", "")[:1200],
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--max", type=int, default=15)
    ap.add_argument("--workdir", default="./online_kb")
    ap.add_argument("--fetch-oa", dest="fetch_oa", action="store_true",
                    help="对带合法 OA 直链的条目下载 PDF 并尽力抽取全文")
    ap.add_argument("--oa-limit", dest="oa_limit", type=int, default=5, help="最多下载几篇 OA 全文")
    ap.add_argument("--with-arxiv", dest="with_arxiv", action="store_true",
                    help="附加 arXiv API 通道（计算领域免费全文）并做 Unpaywall OA 补查")
    args = ap.parse_args()
    os.makedirs(args.workdir, exist_ok=True)

    recs = openalex(args.query, args.max)
    src = "OpenAlex"
    if not recs:
        recs = europepmc(args.query, args.max)
        src = "EuropePMC"
    online = len(recs) > 0  # 只要有任一端点拿到结果就算在线命中（不因首选端点瞬时失败而误标 offline）

    # Unpaywall 补查：给没有 OA 线索的 DOI 找合法免费版（机构库/预印本）
    def abs_hash(t):
        return re.sub(r"[^\w]+", "", (t or "").lower())[:60]

    if args.with_arxiv or args.fetch_oa:
        for r in recs:
            if r.get("doi") and not r.get("oa_pdf_url"):
                is_oa, pdf = unpaywall_lookup(r["doi"])
                if is_oa and pdf:
                    r["is_oa"], r["oa_pdf_url"] = True, pdf
                    r["oa_source"] = "unpaywall"
        # arXiv 通道：独立命中，全部自带免费 PDF
        for r in arxiv_search(args.query, max(5, args.max // 3)):
            if not any(abs_hash(x["title"]) == abs_hash(r["title"]) for x in recs):
                r["oa_source"] = "arxiv"
                recs.append(r)

    items, oa_fetched = [], 0
    for i, r in enumerate(recs, 1):
        ev = "abstract"
        note_txt = "abstract-only；引用其全文数值前须先取全文并核对"
        pdf_path = txt_path = None
        if r.get("is_oa"):
            note_txt = "有合法 OA 免费版：%s" % (r.get("oa_pdf_url") or r.get("oa_url") or "")
            if args.fetch_oa and oa_fetched < args.oa_limit and r.get("oa_pdf_url"):
                pdf_path, txt_path = fetch_oa_pdf(r, args.workdir)
                if pdf_path:
                    oa_fetched += 1
                    if txt_path:
                        ev = "full-text-oa"
                        note_txt = "OA 全文已抽取：%s" % txt_path
                    else:
                        note_txt = "OA PDF 已下载但本机缺 pymupdf/pdfminer，未能抽文本：%s" % pdf_path
        items.append({
            "key": "lit_%02d" % i,
            "channel": "literature",
            "value": dict(r, pdf_path=pdf_path, fulltext_path=txt_path),
            "provenance": ("DOI:%s" % r["doi"]) if r.get("doi") else ("title:%s" % (r.get("title") or "")[:60]),
            "source_type": "literature",
            "evidence_level": ev,
            "verified_online": online,
            "self_verified": False,
            "domain_match": None,           # 由上层按 exact/adjacent/cross_domain 逐条打标
            "confidence": "medium" if online else "low",
            "note": note_txt if online else "OFFLINE",
        })

    result = {"channel": "literature", "query": args.query, "source": src,
              "network": "online" if online else "offline",
              "oa_fulltext_count": sum(1 for x in items if x["evidence_level"] == "full-text-oa"),
              "found": len(items) > 0, "count": len(items), "items": items}
    outp = os.path.join(args.workdir, "lit_result.json")
    with open(outp, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    if not online:
        print("[OFFLINE] OpenAlex/Europe PMC 均不可达；文献通道返回空，上层如实标注离线缺口。")
    print(json.dumps({"source": src, "network": result["network"], "count": len(items),
                      "oa_fulltext": result["oa_fulltext_count"],
                      "top": [{"title": x["value"]["title"], "year": x["value"]["year"], "doi": x["value"]["doi"],
                               "is_oa": x["value"].get("is_oa"), "ev": x["evidence_level"]}
                              for x in items[:8]]}, ensure_ascii=False, indent=2))
    print("\n[saved] %s" % outp)


if __name__ == "__main__":
    main()
