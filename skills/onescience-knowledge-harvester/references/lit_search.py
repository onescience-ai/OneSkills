"""
多源学术检索脚本模板（命令块 A · 六级降级链版）
来源：onescience-live-literature SKILL.md + 429 限流兜底扩展

用法：python lit_search.py "<query>" <max_papers> <year_from> <pool_json路径>
示例：python lit_search.py "saffron crocin biosynthesis gene" 15 2018 pool.json

降级链（命中即停，全失败优雅 exit 0）：
  L1 OpenAlex          polite-pool mailto + 指数退避 3 次
  L2 Semantic Scholar  Graph API 免费层（可选 S2_API_KEY 环境变量提额）
  L3 CrossRef          polite pool（mailto header）
  L4 领域专用          arXiv / bioRxiv / chemRxiv / PMC OA（按 query 关键词路由）
  L5 Europe PMC        REST search
  L6 SQLite 缓存       命中过的 query 直接返回（_lit_cache.sqlite，与 pool.json 同目录）

输出契约（与旧版兼容，harvester 会解析）：
  == +N new, M dups skipped, pool=K ==
  [i] <year> <venue> | cited=<n> | OA/-- | <title>
      <abstract 前 220 字>
"""
import json, os, re, sys, time, sqlite3, hashlib
from urllib.parse import quote, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

# ---------- CLI ----------
if len(sys.argv) < 5:
    print("usage: lit_search.py <query> <max_papers> <year_from> <pool_json>", file=sys.stderr)
    sys.exit(2)
QUERY, N, YEAR, OUT = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
MAILTO = os.environ.get("LIT_MAILTO", "onetools@example.com")
S2_KEY = os.environ.get("S2_API_KEY", "")
UA = f"OneSkills-harvester/0.2 (mailto:{MAILTO})"
TIMEOUT = int(os.environ.get("LIT_TIMEOUT", "30"))

# ---------- SQLite 缓存 ----------
CACHE_DB = os.path.join(os.path.dirname(os.path.abspath(OUT)) or ".", "_lit_cache.sqlite")

def _cache_init():
    try:
        con = sqlite3.connect(CACHE_DB, timeout=5)
        con.execute("CREATE TABLE IF NOT EXISTS q ("
                    "k TEXT PRIMARY KEY, v TEXT, ts INTEGER, src TEXT)")
        con.commit()
        return con
    except Exception:
        return None

def _cache_key(q, n, y):
    return hashlib.sha1(f"{q}|{n}|{y}".encode("utf-8")).hexdigest()

def cache_get(con, q, n, y):
    if con is None: return None
    try:
        row = con.execute("SELECT v FROM q WHERE k=?", (_cache_key(q, n, y),)).fetchone()
        return json.loads(row[0]) if row else None
    except Exception:
        return None

def cache_put(con, q, n, y, items, src):
    if con is None or not items: return
    try:
        con.execute("INSERT OR REPLACE INTO q(k,v,ts,src) VALUES(?,?,?,?)",
                    (_cache_key(q, n, y), json.dumps(items, ensure_ascii=False),
                     int(time.time()), src))
        con.commit()
    except Exception:
        pass

# ---------- 通用 HTTP ----------
def http_json(url, headers=None, retries=3, backoff=(1, 4, 16)):
    hdrs = {"User-Agent": UA}
    if headers: hdrs.update(headers)
    last = None
    for i in range(retries):
        try:
            req = Request(url, headers=hdrs)
            return json.loads(urlopen(req, timeout=TIMEOUT).read())
        except HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code in (429, 500, 502, 503, 504) and i < retries - 1:
                time.sleep(backoff[i]); continue
            break
        except (URLError, TimeoutError, OSError) as e:
            last = f"NET {type(e).__name__}"
            if i < retries - 1:
                time.sleep(backoff[i]); continue
            break
        except Exception as e:
            last = f"PARSE {type(e).__name__}"
            break
    print(f"  [http_json] fail: {url[:80]}... -> {last}", file=sys.stderr)
    return None

def http_text(url, headers=None, retries=3, backoff=(2, 8, 20)):
    """与 http_json 同款退避: 429/5xx 时指数等待重试(arXiv 实测会 429)"""
    hdrs = {"User-Agent": UA}
    if headers: hdrs.update(headers)
    last = None
    for i in range(retries):
        try:
            req = Request(url, headers=hdrs)
            return urlopen(req, timeout=TIMEOUT).read().decode("utf-8", errors="replace")
        except HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code in (429, 500, 502, 503, 504) and i < retries - 1:
                time.sleep(backoff[i]); continue
            break
        except (URLError, TimeoutError, OSError) as e:
            last = f"NET {type(e).__name__}"
            if i < retries - 1:
                time.sleep(backoff[i]); continue
            break
        except Exception as e:
            last = f"{type(e).__name__}"
            break
    print(f"  [http_text] fail: {url[:80]}... -> {last}", file=sys.stderr)
    return None

# ---------- 条目归一 ----------
def norm_item(title, authors, venue, year, doi, oa_url, cited, abstract):
    return {
        "title": (title or "").strip(),
        "authors": [a for a in (authors or []) if a][:3],
        "venue": (venue or "").strip(),
        "year": str(year or "")[:4],
        "doi": (doi or "").replace("https://doi.org/", "").strip(),
        "oa_url": oa_url or "",
        "cited": int(cited or 0),
        "abstract": (abstract or "")[:400],
    }

def inv_to_abstract(inv):
    """OpenAlex abstract_inverted_index -> plain text"""
    if not inv: return ""
    pos = {}
    for w, idxs in inv.items():
        for i in idxs: pos[i] = w
    return " ".join(pos[i] for i in sorted(pos))[:400]

# ---------- L1 OpenAlex ----------
def l1_openalex():
    url = ("https://api.openalex.org/works?search=" + quote(QUERY)
           + f"&per-page={N}"
           + f"&filter=is_paratext:false,type:article,from_publication_date:{YEAR}-01-01"
           + "&select=id,title,doi,publication_date,open_access,primary_location,"
             "authorships,cited_by_count,abstract_inverted_index"
           + f"&mailto={MAILTO}")
    data = http_json(url)
    if not data or "results" not in data: return None
    out = []
    for w in data["results"]:
        loc = w.get("primary_location") or {}
        out.append(norm_item(
            w.get("title"),
            [a.get("author", {}).get("display_name", "") for a in (w.get("authorships") or [])],
            ((loc.get("source") or {}).get("display_name")),
            (w.get("publication_date") or "")[:4],
            w.get("doi"),
            (w.get("open_access") or {}).get("oa_url"),
            w.get("cited_by_count"),
            inv_to_abstract(w.get("abstract_inverted_index")),
        ))
    return out or None

# ---------- L2 Semantic Scholar ----------
def l2_semantic_scholar():
    hdrs = {}
    if S2_KEY: hdrs["x-api-key"] = S2_KEY
    url = ("https://api.semanticscholar.org/graph/v1/paper/search?"
           + urlencode({"query": QUERY, "limit": min(N, 100), "year": f"{YEAR}-",
                        "fields": "title,authors,venue,year,externalIds,openAccessPdf,"
                                  "citationCount,abstract"}))
    data = http_json(url, headers=hdrs)
    if not data or "data" not in data: return None
    out = []
    for p in data["data"]:
        ext = p.get("externalIds") or {}
        oa = p.get("openAccessPdf") or {}
        out.append(norm_item(
            p.get("title"),
            [a.get("name", "") for a in (p.get("authors") or [])],
            p.get("venue"),
            p.get("year"),
            ext.get("DOI"),
            oa.get("url"),
            p.get("citationCount"),
            p.get("abstract"),
        ))
    return out or None

# ---------- L3 CrossRef ----------
def l3_crossref():
    url = ("https://api.crossref.org/works?"
           + urlencode({"query": QUERY, "rows": N,
                        "filter": f"from-pub-date:{YEAR}-01-01,type:journal-article",
                        "select": "title,author,container-title,issued,DOI,URL,"
                                  "is-referenced-by-count,abstract"}))
    data = http_json(url, headers={"Mailto": MAILTO})
    if not data or "message" not in data: return None
    out = []
    for w in data["message"].get("items", []):
        title = (w.get("title") or [""])[0]
        venue = (w.get("container-title") or [""])[0]
        year = ((w.get("issued") or {}).get("date-parts") or [[""]])[0][0]
        authors = [f"{a.get('given','')} {a.get('family','')}".strip()
                   for a in (w.get("author") or [])]
        abst = re.sub(r"<[^>]+>", "", w.get("abstract") or "")[:400]
        out.append(norm_item(title, authors, venue, year, w.get("DOI"),
                             w.get("URL"), w.get("is-referenced-by-count"), abst))
    return out or None

# ---------- L4 arXiv（唯一有真正 search API 的预印本库；bioRxiv/chemRxiv 无关键词搜索 API，其预印本覆盖交给 L5 Europe PMC） ----------
def l4_domain():
    # 注意: (1) arXiv API 要求 search_query 里的 'all:' 前缀不能被 URL 转义成 'all%3A',
    # 故手动拼 URL, 只对 query 本体做 quote, 不用 urlencode 整体处理;
    # (2) 必须用 https, http 端点实测返回 502 Bad Gateway
    url = ("https://export.arxiv.org/api/query?search_query=all:"
           + quote(QUERY) + f"&max_results={N}&sortBy=relevance")
    txt = http_text(url)
    if not txt: return None
    return _parse_arxiv_atom(txt)

def _parse_arxiv_atom(txt):
    entries = re.findall(r"<entry>(.*?)</entry>", txt, re.S)
    out = []
    for e in entries[:N]:
        title = re.search(r"<title>(.*?)</title>", e, re.S)
        summ = re.search(r"<summary>(.*?)</summary>", e, re.S)
        doi = re.search(r"<arxiv:doi[^>]*>(.*?)</arxiv:doi>", e, re.S)
        pdf = re.search(r'<link[^>]+title="pdf"[^>]+href="([^"]+)"', e)
        pub = re.search(r"<published>(.*?)</published>", e)
        authors = re.findall(r"<name>(.*?)</name>", e)
        out.append(norm_item(
            (title.group(1).strip().replace("\n", " ") if title else ""),
            authors, "arXiv",
            (pub.group(1)[:4] if pub else ""),
            (doi.group(1) if doi else ""),
            (pdf.group(1) if pdf else ""),
            0,
            (summ.group(1).strip().replace("\n", " ")[:400] if summ else ""),
        ))
    return out or None

# ---------- L5 Europe PMC ----------
def l5_europepmc():
    url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
           + urlencode({"query": QUERY, "format": "json", "pageSize": N,
                        "resultType": "core"}))
    data = http_json(url)
    if not data or "resultList" not in data: return None
    out = []
    for p in data["resultList"].get("result", []):
        oa = ""
        if p.get("isOpenAccess") == "Y" and p.get("pmcid"):
            oa = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{p['pmcid']}/fullTextXML"
        out.append(norm_item(
            p.get("title"), (p.get("authorString") or "").split(", "),
            p.get("journalInfo", {}).get("journal", {}).get("title") if isinstance(p.get("journalInfo"), dict) else "",
            p.get("pubYear"),
            p.get("doi"),
            oa,
            p.get("citedByCount"),
            p.get("abstractText"),
        ))
    return out or None

# ---------- 主流程 ----------
def main():
    con = _cache_init()
    # L6 缓存优先（命中过的 query 秒回，节省 API 配额）
    cached = cache_get(con, QUERY, N, YEAR)
    if cached:
        print(f"  [cache hit] {len(cached)} items from _lit_cache.sqlite", file=sys.stderr)
        _merge_and_emit(cached, "cache")
        return

    chain = [("L1_openalex", l1_openalex),
             ("L2_semantic_scholar", l2_semantic_scholar),
             ("L3_crossref", l3_crossref),
             ("L4_domain", l4_domain),
             ("L5_europepmc", l5_europepmc)]
    for name, fn in chain:
        try:
            items = fn()
        except Exception as e:
            print(f"  [{name}] exception: {type(e).__name__}: {e}", file=sys.stderr)
            items = None
        if items:
            print(f"  [{name}] hit: {len(items)} items", file=sys.stderr)
            cache_put(con, QUERY, N, YEAR, items, name)
            _merge_and_emit(items, name)
            return
        print(f"  [{name}] miss, degrade...", file=sys.stderr)

    print("== all sources failed, pool unchanged ==", file=sys.stderr)
    sys.exit(0)

def _merge_and_emit(items, src):
    pool = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else []
    seen = {(p.get("doi") or p["title"].lower()) for p in pool}
    base = len(pool); skipped = 0
    for it in items:
        key = it.get("doi") or it["title"].lower()
        if not key or key in seen:
            skipped += 1; continue
        seen.add(key)
        it["_src"] = src
        pool.append(it)
    json.dump(pool, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"== +{len(pool) - base} new, {skipped} dups skipped, pool={len(pool)} == (src={src})")
    for i, p in enumerate(pool, 1):
        print(f"[{i}] {p.get('year','')} {p.get('venue','')[:38]} | cited={p.get('cited',0)} | "
              f"{'OA' if p.get('oa_url') else '--'} | {p.get('title','')[:80]}")
        print(f"    {p.get('abstract','')[:220]}")

if __name__ == "__main__":
    main()
