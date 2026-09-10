"""
OpenAlex 检索脚本模板（命令块 A）
来源：onescience-live-literature SKILL.md

用法：python lit_search.py "<query>" <max_papers> <year_from> <pool_json路径>

示例：python lit_search.py "saffron crocin biosynthesis gene" 15 2018 pool.json
"""
import json, re, sys
from urllib.parse import quote
from urllib.request import urlopen, Request

q, n, year, out = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
url = ("https://api.openalex.org/works?search=" + quote(q)
       + f"&per-page={n}"
       + f"&filter=is_paratext:false,type:article,from_publication_date:{year}-01-01"
       + "&select=id,title,doi,publication_date,open_access,primary_location,"
         "authorships,cited_by_count,abstract_inverted_index")
req = Request(url, headers={"User-Agent": "OneSkills-harvester/0.1 (mailto:onetools@example.com)"})
data = json.loads(urlopen(req, timeout=30).read())

pool = json.load(open(out, encoding="utf-8")) if __import__("os").path.exists(out) else []
seen = {(p.get("doi") or p["title"].lower()) for p in pool}
base = len(pool)
skipped = 0
for w in data.get("results", []):
    key = (w.get("doi") or "").replace("https://doi.org/", "") or (w.get("title") or "").lower()
    if key in seen:
        skipped += 1
        continue
    seen.add(key)
    inv = w.get("abstract_inverted_index") or {}
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    abstract = " ".join(pos[i] for i in sorted(pos))[:400]
    loc = w.get("primary_location") or {}
    pool.append({
        "title": w.get("title") or "",
        "authors": [a.get("author", {}).get("display_name", "") for a in (w.get("authorships") or [])[:3]],
        "venue": ((loc.get("source") or {}).get("display_name")) or "",
        "year": (w.get("publication_date") or "")[:4],
        "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
        "oa_url": (w.get("open_access") or {}).get("oa_url") or "",
        "cited": w.get("cited_by_count") or 0,
        "abstract": abstract,
    })
json.dump(pool, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"== +{len(pool) - base} new, {skipped} dups skipped, pool={len(pool)} ==")
for i, p in enumerate(pool, 1):
    print(f"[{i}] {p['year']} {p['venue'][:38]} | cited={p['cited']} | "
          f"{'OA' if p['oa_url'] else '--'} | {p['title'][:80]}")
    print(f"    {p['abstract'][:220]}")
