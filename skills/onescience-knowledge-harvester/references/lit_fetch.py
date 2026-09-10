"""
全文抓取脚本模板（命令块 B）
来源：onescience-live-literature SKILL.md
双通道实测：Europe PMC OA 子集 + NCBI BioC 兜底

用法：python lit_fetch.py <outdir> --keys "<关键词逗号分隔>" <doi1> <doi2> ...

示例：python lit_fetch.py fulltexts --keys "crocin,CCD2,biosynthesis" 10.1016/j.apsb.2023.12.013
"""
import json, os, re, sys, urllib.parse, urllib.request
from xml.etree import ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows GBK 控制台防崩
UA = {"User-Agent": "OneSkills-harvester/0.2"}

def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")

def norm_id(raw):
    # 防双重前缀坑：接受 "123"/"PMC123"/"PPR123"，统一规范化
    raw = str(raw or "").strip()
    if raw.isdigit():
        return "PMC" + raw
    return raw or None

def epmc_meta(doi):
    u = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:"
         + urllib.parse.quote('"' + doi + '"') + "&format=json&resultType=core")
    for r in json.loads(fetch(u, 30)).get("resultList", {}).get("result", []):
        fid = norm_id(r.get("pmcid")) or (r.get("id") if r.get("source") == "PPR" else None)
        return norm_id(fid), r.get("isOpenAccess")
    return None, None

def xml_to_text(xml):
    root, out = ET.fromstring(xml), []
    for sec in root.iter("sec"):
        title = " ".join(sec.findtext("title").split()) if sec.findtext("title") else ""
        if title:
            out.append("### " + title)
        for p in sec.findall("p"):
            t = " ".join("".join(p.itertext()).split())
            if t:
                out.append(t)
    return "\n".join(out)

def bioc_fallback(pmcid):
    u = ("https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/"
         + pmcid + "/unicode")
    d = json.loads(fetch(u, 90))
    out = []
    for doc in d.get("documents", []):
        for p in doc.get("passages", []):
            t = " ".join((p.get("text") or "").split())
            if t:
                out.append(("### " + t) if "title" in str(p.get("infon", {}).get("type", "")) else t)
    return "\n".join(out)

# 用法: python lit_fetch.py <outdir> --keys "<关键词逗号分隔>" <doi1> <doi2> ...
argv = sys.argv[1:]
outdir = argv[0]; argv = argv[1:]
keys = ["result", "discussion"]
if "--keys" in argv:
    i = argv.index("--keys")
    keys = [k.strip().lower() for k in argv[i + 1].split(",") if k.strip()] + keys
    argv = argv[:i] + argv[i + 2:]
os.makedirs(outdir, exist_ok=True)

for doi in argv:
    print("\n######## DOI:", doi)
    try:
        fid, oa = epmc_meta(doi)
        if not fid:
            print("STATUS abstract-only (Europe PMC 未收录或无全文ID)")
            continue
        text, src = "", ""
        try:
            text = xml_to_text(fetch("https://www.ebi.ac.uk/europepmc/webservices/rest/%s/fullTextXML" % fid))
            src = "europepmc:" + fid
        except Exception as e:
            print("europepmc fullTextXML 失败(%s)，试 NCBI BioC ..." % e)
            if fid.startswith("PMC"):
                try:
                    text = bioc_fallback(fid)
                    src = "ncbi-bioc:" + fid
                except Exception as e2:
                    print("NCBI BioC 亦失败:", e2)
        if not text or len(text) < 500:
            print("STATUS abstract-only (%s openaccess=%s，两条全文通道均失败)" % (fid, oa))
            continue
        slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", doi)
        path = os.path.join(outdir, slug + ".txt")
        open(path, "w", encoding="utf-8").write(text)
        secs = [ln[4:] for ln in text.splitlines() if ln.startswith("### ")]
        print("STATUS full-text OK via %s | %d chars | 已落盘: %s" % (src, len(text), path))
        print("章节索引:", " | ".join(s[:40] for s in secs[:20]))
        hits = [ln for ln in text.splitlines()
                if not ln.startswith("###") and any(k in ln.lower() for k in keys)]
        print("---- 关键词命中段落预览(前5条各<=400字; 完整内容必须用读文件工具读 %s) ----" % path)
        for ln in hits[:5]:
            print("*", ln[:400])
    except Exception as e:
        print("ERR:", type(e).__name__, e)
