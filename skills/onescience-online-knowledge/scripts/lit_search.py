#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""onescience-online-knowledge · 通道①：文献检索（题录 + 摘要 + 免费全文降级链）。

v2 重构要点 —— 每条都对应一次实测归因，勿回退：

1) 弃用 OpenAlex `search=<长串>`。`search=` 是全字段（含全文）逐词 AND，14 词长串实测
   count=2 且头部全不对题（返回催化材料核磁综述、药物盐/共晶综述）；改
   `filter=title_and_abstract.search:<≤4 词子查询>` 后同一语料 count=370，头部即靶心。
   查询串会被自动分解为多条子查询并行打，再合并去重。
2) arXiv 禁用 `all:<裸串>`。实测裸串返回「NMR Quantum Computation」「Quantum Computing
   with NMR」「Underground Water Cherenkov Muon Detector…Tibet」等噪声，曾直接污染
   online_kb 下载队列；改 `abs:"X" AND abs:"Y" AND (cat:… OR cat:…)` 后 5/5 全对题。
3) Europe PMC 从「OpenAlex 返回空才兜底」的死代码改为并行主源。OpenAlex 几乎从不返回空
   （哪怕全是垃圾），旧兜底分支永不触发；而 EPMC 字段布尔
   `TITLE:"glycine" AND TITLE:"polymorphs" AND TITLE:"NMR"` 实测直出 α/γ 甘氨酸原始文献，
   且能给 pmcid → 免费全文。
4) 客户端相关性门：目标实体词必须出现在 title/abstract 才进池，且**未过门者永不进下载
   队列**——旧逻辑「只要 is_oa 就下」会让噪声抢占 --oa-limit 名额、挤掉对题文献。
5) `domain_match` 由脚本按客观规则先打（看实体/方法词落在 title 还是 abstract），并给出
   `domain_match_basis` 依据串。上层只能改严不能改松，杜绝自封 exact。
6) 免费全文降级链：Unpaywall → OpenAlex 施引反查（`filter=cites:W…,is_oa:true`）→
   EPMC pmcid 全文 → 仍无则标 `abstract-only` 且禁止作数值来源。实测两篇靶心文献
   Unpaywall is_oa=False/pdf=None（付费墙成立），但施引反查给出 8 + 17 篇开放获取下游
   载体（含 ¹³C shielding tensors、NMR crystallography 专题），是可行的免费替代路径。
   **付费墙仍然成立：绝不绕墙。**
7) HTTP 层统一指数退避（429/5xx），OpenAlex 带 mailto 进 polite pool。

纯标准库。网络不可用时打印 [OFFLINE] 并正常退出。

用法：
  # 基本快查（自动分解子查询 + 三源并行 + 相关性门）
  python lit_search.py "glycine 13C 15N chemical shift GIPAW" --max 15 --workdir ./online_kb

  # 推荐：显式给出目标实体与方法词（相关性门与 domain_match 的客观依据），
  # 并开启 arXiv 布尔通道、OA 全文下载、施引反查
  python lit_search.py "glycine polymorph alpha gamma 13C 15N solid-state NMR chemical shift GIPAW DFT" \
      --entities "glycine,polymorph" --methods "GIPAW,chemical shift,magnetic shielding,DFT" \
      --with-arxiv --fetch-oa --citing-oa --max 15 --workdir ./online_kb
"""
import argparse, http.client, json, os, re, ssl, sys, time
from urllib import request, error, parse

try:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows GBK 控制台打印 α/γ/⚠ 会崩；Linux 默认 UTF-8
except Exception:
    pass

OA = "https://api.openalex.org/works"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
UNPAYWALL = "https://api.unpaywall.org/v2/"
ARXIV = "https://export.arxiv.org/api/query"   # 实测 http:// 会 502，必须 https
# 联系邮箱 / API key 一律只从环境读，**绝不硬编占位符**。理由是按实测纠偏过的认知：
#  · OpenAlex 的 mailto 只决定能否进 polite pool（官方：响应时间更稳定）以及"出事能联系到人"，
#    它**不提高配额**。配额现在是 credits 制：list 检索每次 10 credits，免费 100k credits/天
#    + 100 req/s，超出即 HTTP 429。无 API key 时额度按**出口 IP** 归属，HPC 共享 NAT 出口下
#    同 IP 用户互相耗尽——实测同一台机器相隔 3 小时从 0 次 429 变成连续 429，与检索式无关。
#  · 真正的额度杠杆是免费 API key（官方：日额度 10 倍），故一并支持。
#  · Unpaywall 与 OpenAlex 相反，它**必须带一个 email 参数**：实测 email="" 直接
#    HTTP 422 "Email address required"，而 research@example.org / a@b.co 都返回 200
#    ——它只校验"有没有这个参数"，不校验域名归属。所以这里**必须有非空兜底值**，
#    "没配置就跳过 Unpaywall"是回归（会关掉一条本来可用的降级链），已按实测改回。
DEFAULT_MAILTO = os.environ.get("ONESCIENCE_CONTACT_EMAIL", "").strip()
# OpenAlex 侧：为空就不带 mailto（实测匿名照样出数），不冒充 polite pool。
# Unpaywall 侧：为空时用中性占位，保证这条链始终可用。
UNPAYWALL_EMAIL = DEFAULT_MAILTO or "onescience-online-knowledge@example.org"
# key 只走环境变量、不做命令行参数：命令行会进 ps 与 shell 历史，凭证不得明文出现在进程列表。
OA_API_KEY = os.environ.get("OPENALEX_API_KEY", "").strip()
CROSSREF = "https://api.crossref.org/works"   # 备用摘要层：独立基础设施/限流池，免 key
DEFAULT_ARXIV_CATS = "cond-mat.mtrl-sci,physics.chem-ph,physics.comp-ph"
OA_SELECT = ("id,doi,title,publication_year,publication_date,authorships,abstract_inverted_index,"
             "cited_by_count,open_access,best_oa_location,primary_location")

# 方法/技术词白名单：用户未显式给 --entities/--methods 时用于自动切分查询串。
# 命中的归「方法词」，其余实义词归「实体词」。可按领域扩展，扩展后相关性门会更准。
METHOD_LEXICON = {
    "dft", "gipaw", "paw", "vasp", "castep", "quantum espresso", "ab initio", "first-principles",
    "first principles", "chemical shift", "chemical shifts", "shielding", "magnetic shielding",
    "nmr", "ssnmr", "solid-state nmr", "magres", "quadrupolar", "spin-spin coupling", "j coupling",
    "hybrid functional", "pbe", "b3lyp", "hse06", "scan", "rscan", "r2scan", "lda", "gga", "zora",
    "spin-orbit", "dispersion", "d3-bj", "ivdw", "phonon", "phonons", "molecular dynamics", "mlmd",
    "machine learning", "deep learning", "neural network", "mace", "lammps", "gromacs", "slurm",
    "encut", "kpoints", "incar", "poscar", "potcar", "pseudopotential", "basis set", "plane wave",
    "convergence", "geometry optimization", "band structure", "density of states", "adsorption",
    "catalysis", "co2rr", "xrd", "x-ray diffraction", "spectroscopy", "tensor", "tensors",
    "nuclear quantum effects", "path integral", "electric field gradient", "cpmg", "mas",
}
# 弱词：不参与实体/方法识别与相关性门计分（但在检索串里原样保留）
STOPWORDS = {
    "for", "of", "the", "and", "in", "on", "with", "a", "an", "to", "using", "use", "via", "from",
    "by", "its", "their", "this", "that", "are", "is", "was", "were", "be", "been", "study",
    "studies", "calculation", "calculations", "analysis", "review", "based", "effect", "effects",
    "some", "new", "novel", "towards", "toward", "case", "influence", "results",
}
# 宽泛方法词：参与检索式构造与 domain_match，但**不参与相关性门计分**。
# 否则「NMR Quantum Computation」会因命中 NMR 被误放行（单测实测验证过这一失效模式）。
WEAK_METHODS = {
    "nmr", "dft", "md", "molecular dynamics", "xrd", "spectroscopy", "convergence", "ab initio",
    "first-principles", "first principles", "machine learning", "deep learning", "neural network",
    "relaxation", "tensor", "tensors", "basis set", "plane wave", "density of states",
}
# 泛修饰实体词：单独命中不足以证明相关（如 alpha/beta/gamma 晶型标识、solid-state）。
GENERIC_MODIFIERS = {
    "alpha", "beta", "gamma", "delta", "low", "high", "solid", "solid-state", "liquid", "gas",
    "single", "poly", "nano", "bulk", "thin", "film", "13c", "15n", "17o", "27al", "1h",
}
BACKOFF = (1, 3, 8)          # 429/5xx 指数退避（秒）
RETRYABLE = (429, 500, 502, 503, 504)
GATE_THRESHOLD = 2           # 相关性门及格线（加权分）

# 方法词别名：同一概念在文献里的多种表述。不做归一会使「magnetic shielding」
# 匹配不上文中的「chemical shielding」，真正相关的方法学文献会被相关性门误杀。
# **别名不得放裸词**：实测把 "shielding" 当 "magnetic shielding" 的别名时，
# 「Rapid fabrication, magnetic, and radiation shielding characteristics of NiFe2O4
# nanoparticles」(cited=35) 会因「radiation shielding」命中而被误判为 anchor 档、
# dm=adjacent，挤进 top 14。别名必须是能锁定 NMR 语境的复合短语。
METHOD_ALIASES = {
    "magnetic shielding": ["chemical shielding", "nuclear magnetic shielding", "magnetic-shielding",
                           "shielding tensor", "shielding tensors", "shielding scale",
                           "isotropic shielding", "anisotropic shielding", "shielding surface",
                           "13c shielding", "15n shielding", "17o shielding", "29si shielding"],
    "chemical shift": ["chemical shifts", "shift tensor", "shift tensors"],
    "solid-state nmr": ["solid state nmr", "ssnmr", "mas nmr", "solid-state nuclear magnetic resonance"],
    "gipaw": ["gauge including projector augmented wave"],
    "electric field gradient": ["efg", "quadrupolar coupling"],
    "nuclear quantum effects": ["nqe", "path integral molecular dynamics"],
    "x-ray diffraction": ["xrd"],
    "density of states": ["dos"],
    "molecular dynamics": ["md simulation", "md simulations"],
    "geometry optimization": ["structural optimization", "geometry optimisation",
                              "structural relaxation"],
    # ---- 第二轮（MOF-5/MLMD 探针实测补入，均为同一方法的不同写法=真同义词，非放宽门槛）----
    # 证据：唯一真靶心 "Neural Network Potential for MOF-5"(cited=133) 曾被判 strong=[]，
    # "active learning" 命中的 3 篇全部被 drop。补别名把它们救回正确档位。
    # 刻意不含裸 "gap"/"snap"/"mace"：实测 "gap" 会命中 "band gap" 造成假阳性。
    "machine learning interatomic potential": [
        "machine learned potential", "machine learning potential",
        "machine-learned potential", "ml potential",
        "neural network potential", "neural network potentials",
        "high-dimensional neural network potential",
        "message passing neural network", "deep potential", "deeppmd",
        "behler-parrinello", "spectral neighbor analysis potential",
        "gaussian approximation potential"],
    "active learning": ["on-the-fly learning", "on the fly learning",
                        "query by committee", "active-learning"],
    # 与现有表同风格的标准缩写对（xrd/dos/efg/ssnmr 已在表内）
    "nudged elastic band": ["neb", "climbing image neb"],
    "ab initio molecular dynamics": ["aimd"],
    "density functional theory": ["dft"],
}

_net_ok = True
_MAILTO = DEFAULT_MAILTO


def _ctx():
    try:
        return ssl._create_unverified_context()
    except Exception:
        return None


def _oa_auth_params():
    """只在真的有值时才附加 mailto / api_key。

    空串拼进 querystring 会得到 `mailto=`——形式上带了参数、实质上仍是无身份请求，
    还可能被服务端判为非法输入；宁可不带。
    """
    p = {}
    if _MAILTO:
        p["mailto"] = _MAILTO
    if OA_API_KEY:
        p["api_key"] = OA_API_KEY
    return p


def _user_agent():
    """OpenAlex 也接受在 User-Agent 里给 mailto；无邮箱时只报身份，不冒充 polite pool。"""
    base = "onescience-online-knowledge/2.0"
    return "%s (mailto:%s)" % (base, _MAILTO) if _MAILTO else base


def http_get(url, timeout=30, mode="json", retries=3):
    """统一 GET：429/5xx 指数退避重试。mode ∈ {json, text, binary}。

    彻底失败才翻转 _net_ok，以区分「网络不可达」与「查询本身无果」——旧版把两者混为一谈，
    导致检索式写错时也会误报 offline。
    """
    global _net_ok
    last = None
    for i in range(retries):
        try:
            req = request.Request(url, headers={"User-Agent": _user_agent()})
            with request.urlopen(req, timeout=timeout, context=_ctx()) as r:
                raw = r.read()
            if mode == "binary":
                return raw
            txt = raw.decode("utf-8", "replace")
            return json.loads(txt) if mode == "json" else txt
        except error.HTTPError as e:
            last = "HTTP %s" % e.code
            if e.code in RETRYABLE and i < retries - 1:
                time.sleep(BACKOFF[i]); continue
            break
        except (error.URLError, TimeoutError, OSError, http.client.HTTPException) as e:
            # 必须包含 http.client.HTTPException：IncompleteRead / BadStatusLine 等属于它，
            # **不是** URLError 的子类。实测 OpenAlex 的 chunked 响应被截断时抛
            # http.client.IncompleteRead(8181 bytes read)，旧写法没捕获它，
            # 整个脚本直接崩退出——本轮所有子查询的检索成果全部丢失，
            # 上层只看到 traceback 而不是「某个源无果」。
            last = "%s" % type(e).__name__
            if i < retries - 1:
                time.sleep(BACKOFF[i]); continue
            break
        except ValueError as e:                      # JSON 解析失败，重试无意义
            last = "PARSE %s" % type(e).__name__
            break
    _net_ok = False
    sys.stderr.write("net err: %s -> %s\n" % (url[:100], last))
    return None


def get_json(url, timeout=30):
    return http_get(url, timeout=timeout, mode="json")


def get_text(url, timeout=40, binary=False):
    """binary=True 取原始字节（PDF），否则取文本（arXiv Atom XML）。"""
    return http_get(url, timeout=timeout, mode="binary" if binary else "text")


# ---------------------------------------------------------------- 查询构造
def _norm(t):
    return re.sub(r"[^\w]+", "", (t or "").lower())


# 排版连字符归一：文献标题/摘要里的 "metal–organic"(U+2013)、"13C–13C"、"Ti–O"、
# 以及 U+2212 数学减号 常是排版连字符，而查询词与别名写的是 ASCII hyphen，
# re.escape 后两者不相等 -> 系统性漏匹配（全域通用缺陷，非某一领域专属）。
# 归一为 ASCII '-' 后再匹配；两侧（候选词与 blob）都要归一，否则任一侧带连字符仍漏。
_DASH_RE = re.compile("[\u2010\u2011\u2012\u2013\u2014\u2015\u2212\u2043\u00ad]")


def term_hit(term, blob):
    """词/短语是否命中 blob（已 lower）。先整体匹配，再试 METHOD_ALIASES 别名。

    用 `(?<!\w)…(?!\w)` 边界而非裸子串包含：裸子串会让缩写词误命中——
    实测 "dos"（density of states 的别名）会命中 "dosage"/"dosimetry"，
    "md" 会命中任何含该字母串的词，把跟目标方法无关的文献抬进相关性门。
    用 lookaround 而非 `\b`：`\b` 要求词自身首尾就是 \w，遇到 "13C"、"α-glycine"
    这类以数字/希腊字母开头的词会漏匹配。
    """
    t = (term or "").lower().strip()
    if not t:
        return False
    blob = _DASH_RE.sub("-", blob)
    for c in [t] + list(METHOD_ALIASES.get(t, [])):
        c = _DASH_RE.sub("-", (c or "").lower().strip())
        if c and re.search(r"(?<!\w)%s(?!\w)" % re.escape(c), blob):
            return True
    return False


def split_terms(query):
    """把查询串切成实义词。先把 METHOD_LEXICON 里的多词短语整体抽出（否则
    "chemical shift" 会被空格拆成 chemical / shift，导致方法词识别失败），再切单词。"""
    q = query or ""
    low = q.lower()
    phrases = []
    for ph in sorted((p for p in METHOD_LEXICON if " " in p), key=len, reverse=True):
        if re.search(r"\b%s\b" % re.escape(ph), low):
            phrases.append(ph)
            q = re.sub(r"(?i)\b%s\b" % re.escape(ph), " ", q)
    quoted = re.findall(r'"([^"]+)"', q)
    bare = re.sub(r'"[^"]*"', " ", q)
    words = [w.strip(".,;()") for w in re.split(r"[\s,;]+", bare)]
    words = [w for w in words if w and w.lower() not in STOPWORDS]
    return phrases + quoted + words


def is_method(term):
    t = (term or "").lower().strip()
    return t in METHOD_LEXICON or any(m in t for m in METHOD_LEXICON if len(m) > 4)


def auto_split(query, entities, methods):
    """自动区分实体词/方法词。显式传参优先，缺失部分用白名单推断。"""
    ents = [x.strip() for x in (entities or "").split(",") if x.strip()]
    meths = [x.strip() for x in (methods or "").split(",") if x.strip()]
    if ents and meths:
        return ents, meths
    terms = split_terms(query)
    if not ents:
        ents = [t for t in terms if not is_method(t)]
    if not meths:
        meths = [t for t in terms if is_method(t)]
    return ents[:4], meths[:6]


def build_subqueries(query, entities, methods, explicit, limit=6):
    """生成本轮要打的全部子查询。

    两条实测教训：
    a) 一条长串打天下会把 OpenAlex `search=` 压到 count=2；拆成多条 ≤4 词的精确
       子查询分别打、再合并去重，召回从 2 → 370，头部即靶心。
    b) 子查询必须以**锚定实体**（entities[0]）开头。实测把次要实体词单独当检索词
       （如 `polymorph GIPAW`）会召回大量跳领域高被引噪声，把真靶心挤出 top。
    """
    subs = []
    if explicit:
        for q in [x.strip() for x in explicit.split("|") if x.strip()]:
            subs.append(("explicit", q))
        return subs[:limit]
    anchor = entities[0] if entities else ""
    if anchor:
        for m in methods[:3]:
            subs.append(("anchor+method", "%s %s" % (anchor, m)))
        for e in entities[1:3]:
            subs.append(("anchor+entity", "%s %s" % (anchor, e)))
        if len(methods) >= 2:
            subs.append(("anchor+methods", "%s %s" % (anchor, " ".join(methods[:2]))))
        subs.append(("anchor", anchor))
    else:
        for m in methods[:3]:
            subs.append(("method", m))
    # 兜底：原始整串也打一次（走 search=），排最后，靠相关性门过滤
    subs.append(("raw", query.strip()))
    # 去重保序，并限流：子查询越多请求越多（每源每条约 1s），默认封顶 6 条
    seen, out = set(), []
    for kind, q in subs:
        k = _norm(q)
        if q and k and k not in seen:
            seen.add(k); out.append((kind, q))
        if len(out) >= limit:
            break
    return out


def epmc_query(entities, methods, raw):
    """EPMC 字段布尔检索。实测 TITLE/ABSTRACT 字段限定比全字段宽松串精准得多。"""
    parts = []
    for e in entities[:2]:
        parts.append('(TITLE:"%s" OR ABSTRACT:"%s")' % (e, e))
    for m in methods[:2]:
        parts.append('(TITLE:"%s" OR ABSTRACT:"%s")' % (m, m))
    if len(parts) < 2:
        return raw
    return " AND ".join(parts)


def arxiv_query(entities, methods, cats, raw, rescue=False):
    """arXiv 布尔检索。绝不使用 `all:<裸串>`——实测会返回量子计算/绢子探测器级噪声。

    rescue=True（OpenAlex 被限流取空时的降级救援）刻意放宽：只 AND 首个实体+首个方法两条
    abs 子句、且**不加 cat: 过滤**——实测 `(cat:X OR cat:Y) AND abs:"…"` 会被 arXiv API 判成
    0 命中（cat 组与 abs 布尔式合取失效），而纯 abs 布尔式能正常回血（TBG 热输返 4 条、
    甘氨酸 chemical shift 3 条）。常规 --with-arxiv 仍走严格式保精度，不改既有行为。
    """
    if rescue:
        terms = ([entities[0]] if entities else []) + (
            [methods[0]] if methods else ([entities[1]] if len(entities) > 1 else []))
        cap = 2
        cat_list = []
    else:
        terms = (entities[:1] + methods[:2]) or split_terms(raw)[:3]
        cap = 3
        cat_list = [c.strip() for c in (cats or "").split(",") if c.strip()]
    clauses = ["abs:\"%s\"" % t.strip('"') for t in terms if t.strip()]
    if not clauses:
        return None
    q = " AND ".join(clauses[:cap])
    if cat_list:
        q = "(%s) AND %s" % (" OR ".join("cat:%s" % c for c in cat_list), q)
    return q


# ---------------------------------------------------------------- 数据源
def reconstruct_abstract(inv):
    if not inv:
        return ""
    pos = {}
    for w, idxs in inv.items():
        for i in idxs:
            pos[i] = w
    return " ".join(pos[k] for k in sorted(pos))[:1200]


def openalex(query, maxn, year_from=None, sort="cited", field="title_and_abstract"):
    """OpenAlex 字段级检索。field ∈ {title_and_abstract, title, fulltext, search}。

    `search=` 保留为最后兜底手段（field="search"）；默认走 filter 字段级检索，
    并显式带 is_paratext:false + 年份下限 + 排序 + mailto（polite pool）。
    """
    if field == "search":
        params = {"search": query, "filter": "type:article,is_paratext:false"}
    else:
        filt = "type:article,is_paratext:false,%s.search:%s" % (field, query)
        if year_from:
            filt += ",from_publication_date:%s-01-01" % year_from
        params = {"filter": filt}
    params.update({"per-page": maxn, "select": OA_SELECT})
    params.update(_oa_auth_params())
    params["sort"] = "cited_by_count:desc" if sort == "cited" else "relevance_score:desc"
    d = get_json(OA + "?" + parse.urlencode(params))
    if not d or "results" not in d:
        return []
    out = []
    for w in d.get("results", [])[:maxn]:
        oaw = w.get("open_access") or {}
        bol = w.get("best_oa_location") or {}
        loc = w.get("primary_location") or {}
        src = (loc.get("source") or {})
        out.append({
            "title": w.get("title") or w.get("display_name"),
            "year": w.get("publication_year"),
            "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
            "authors": [a.get("author", {}).get("display_name", "") for a in w.get("authorships", [])][:3],
            "venue": src.get("display_name") or "",
            "cited_by": w.get("cited_by_count"),
            "abstract": reconstruct_abstract(w.get("abstract_inverted_index")),
            "is_oa": bool(oaw.get("is_oa")),
            "oa_status": oaw.get("oa_status") or ("closed" if not oaw.get("is_oa") else ""),
            "oa_pdf_url": bol.get("pdf_url"),
            "oa_url": bol.get("landing_page_url") or oaw.get("oa_url"),
            "openalex_id": (w.get("id") or "").split("/")[-1],
            "source": "OpenAlex",
        })
    return out


def europepmc(query, maxn):
    d = get_json(EPMC + "?" + parse.urlencode(
        {"query": query, "format": "json", "pageSize": maxn, "resultType": "core"}))
    if not d:
        return []
    out = []
    for r in d.get("resultList", {}).get("result", [])[:maxn]:
        pdf = ""
        for u in (r.get("fullTextUrlList") or {}).get("fullTextUrl", []):
            if u.get("documentStyle") == "pdf" and u.get("url"):
                pdf = u["url"]; break
        is_oa = (r.get("isOpenAccess") or "").upper() == "Y"
        pmcid = r.get("pmcid") or ""
        out.append({
            "title": (r.get("title") or "").rstrip("."),
            "year": (r.get("pubdate") or r.get("firstPublicationDate") or "")[:4],
            "doi": r.get("doi", "") or "",
            "authors": [a.get("fullName", "") for a in (r.get("authorList") or {}).get("author", [])][:3],
            "venue": r.get("journalTitle", "") or "",
            "cited_by": _to_int(r.get("citedByCount")),
            "abstract": re.sub(r"<[^>]+>", "", r.get("abstractText", "") or "")[:1200],
            "is_oa": is_oa,
            "oa_status": "green" if (is_oa and pmcid) else ("closed" if not is_oa else ""),
            "oa_pdf_url": pdf or None,
            # PMC 系有免费全文 XML 入口，是付费墙外最稳的全文来源
            "oa_url": ("https://www.ebi.ac.uk/europepmc/webservices/rest/%s/fullTextXML" % pmcid) if pmcid else None,
            "pmcid": pmcid,
            "source": "EuropePMC",
        })
    return out


def crossref(query, maxn, year_from=None):
    """Crossref REST 备用摘要源：独立于 OpenAlex/EPMC 的限流池，免 key、限额宽松。
    当 OpenAlex 被 IP 级 429、EPMC 亦无果时，本层仍可交付候选，避免
    「单源限流 → 整个在线兜底清零」（全域通用健壮性，非某领域专属）。
    Crossref abstract 字段稀疏且常缺，本层主要贡献 title 匹配 + DOI/元数据；
    abstract 缺失时 relevance_gate 仍按 title 判定，语义与其它源一致。
    用 query.bibliographic（短语感知），不加 select 以免字段名触发 400；
    逐条 try/except，单条畸形绝不崩全局（沿用 OpenAlex IncompleteRead 教训）。
    """
    params = {"query.bibliographic": query, "rows": max(1, min(maxn, 30)), "mailto": _MAILTO}
    if year_from:
        params["filter"] = "from-pub-date:%s-01-01" % year_from
    d = get_json(CROSSREF + "?" + parse.urlencode(params))
    if not d:
        return []
    out = []
    for it in (d.get("message") or {}).get("items", [])[:maxn]:
        try:
            titles = it.get("title") or []
            title = titles[0] if titles else ""
            sub = it.get("subtitle") or []
            if not title and sub:
                title = sub[0]
            if not title:                     # 无题条目不能贡献 title 匹配、只会污染统计，直接跳过
                continue
            authors = [(a.get("given", "") + " " + a.get("family", "")).strip()
                       for a in (it.get("author") or [])][:3]
            ct = it.get("container-title") or []
            venue = ct[0] if ct else ""
            dp = ((it.get("issued") or {}).get("date-parts") or [[None]])[0]
            year = dp[0] if dp else None
            abstract = re.sub(r"<[^>]+>", " ", it.get("abstract") or "")
            abstract = re.sub(r"\s+", " ", abstract).strip()[:1200]
            oa_pdf = ""
            for lk in (it.get("link") or []):
                if "pdf" in (lk.get("content-type") or "").lower() and lk.get("URL"):
                    oa_pdf = lk["URL"]; break
            res = ((it.get("resource") or {}).get("primary") or {}).get("URL") or ""
            out.append({
                "title": title,
                "year": year,
                "doi": (it.get("DOI") or "").lower(),
                "authors": [a for a in authors if a],
                "venue": venue,
                "cited_by": it.get("is-referenced-by-count"),
                "abstract": abstract,
                "is_oa": bool(oa_pdf),
                "oa_status": "green" if oa_pdf else "",
                "oa_pdf_url": oa_pdf or None,
                "oa_url": oa_pdf or res or None,
                "source": "Crossref",
            })
        except Exception:
            continue
    return out


def _to_int(v):
    try:
        return int(v)
    except Exception:
        return None


def arxiv_search(sq, maxn):
    """arXiv API：cond-mat/physics 计算类论文大量免费全文。sq 必须是布尔表达式。"""
    if not sq:
        return []
    xml = get_text(ARXIV + "?" + parse.urlencode(
        {"search_query": sq, "max_results": maxn, "sortBy": "relevance"}), timeout=40)
    if not xml or isinstance(xml, dict):
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
            "venue": "arXiv",
            "cited_by": None,
            "abstract": tag("summary")[:1200],
            "is_oa": True,
            "oa_status": "green",
            "oa_pdf_url": ("https://arxiv.org/pdf/%s" % aid) if aid else None,
            "oa_url": aid_url,
            "source": "arXiv",
        })
    return out


def citing_oa(openalex_id, maxn=5):
    """施引反查：靶心文献被付费墙挡住时，用开放获取的下游文献承载其数值。

    实测对两篇 closed 靶心文献分别得到 8 / 17 篇 OA 施引文献，含
    「The accuracy of carbon-13 NMR magnetic-shielding tensors…」（RSC，直链 PDF）
    与 「Uniform chi-squared model probabilities in NMR crystallography」（PMC11710992）。
    """
    if not openalex_id:
        return []
    qparams = {"filter": "cites:%s,is_oa:true,type:article" % openalex_id,
               "sort": "publication_date:desc", "per-page": maxn, "select": OA_SELECT}
    qparams.update(_oa_auth_params())
    d = get_json(OA + "?" + parse.urlencode(qparams))
    if not d or "results" not in d:
        return []
    out = []
    for w in d.get("results", [])[:maxn]:
        oaw = w.get("open_access") or {}
        bol = w.get("best_oa_location") or {}
        loc = ((w.get("primary_location") or {}).get("source") or {})
        out.append({
            "title": w.get("title") or w.get("display_name"),
            "year": w.get("publication_year"),
            "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
            "authors": [a.get("author", {}).get("display_name", "") for a in w.get("authorships", [])][:3],
            "venue": loc.get("display_name") or "",
            "cited_by": w.get("cited_by_count"),
            "abstract": reconstruct_abstract(w.get("abstract_inverted_index")),
            "is_oa": True,
            "oa_status": oaw.get("oa_status") or "green",
            "oa_pdf_url": bol.get("pdf_url"),
            "oa_url": bol.get("landing_page_url") or oaw.get("oa_url"),
            "openalex_id": (w.get("id") or "").split("/")[-1],
            "source": "OpenAlex-citing",
            "cites": openalex_id,
        })
    return out


def unpaywall_lookup(doi):
    """查 DOI 的合法 OA 版（Unpaywall 聚合机构库/预印本）。返回 (is_oa, pdf_url)。"""
    if not doi:
        return None, None
    # 用 UNPAYWALL_EMAIL 而非 _MAILTO：_MAILTO 允许为空（OpenAlex 侧匿名可用），
    # 但 Unpaywall 空值会被 422 拒掉。占位值实测 200，能力不丢。
    d = get_json(UNPAYWALL + parse.quote(doi, "") + "?" + parse.urlencode({"email": UNPAYWALL_EMAIL}), timeout=20)
    if not d or not isinstance(d, dict):
        return None, None
    loc = d.get("best_oa_location") or {}
    return bool(d.get("is_oa")), loc.get("url_for_pdf")


# ---------------------------------------------------------------- 合并 / 相关性 / 打标
def merge_recs(groups):
    """多源合并去重。优先保留信息更全的记录（有 doi/abstract/oa 线索者）。"""
    by_key = {}
    order = []
    for src, recs in groups:
        for r in recs or []:
            k = _norm(r.get("doi")) if r.get("doi") else _norm(r.get("title"))[:80]
            if not k:
                continue
            if k not in by_key:
                by_key[k] = dict(r, hit_from=[src]); order.append(k)
            else:
                old = by_key[k]
                old.setdefault("hit_from", []).append(src)
                # 用更完整的信息补洞
                for f in ("doi", "abstract", "oa_pdf_url", "oa_url", "venue", "cited_by",
                          "openalex_id", "pmcid", "oa_status"):
                    if not old.get(f) and r.get(f):
                        old[f] = r[f]
                old["is_oa"] = bool(old.get("is_oa") or r.get("is_oa"))
    return [by_key[k] for k in order]


def relevance_gate(rec, entities, methods, endorsed=False):
    """四档相关性门。返回 (passed, detail)，
    detail["tier"] ∈ {anchor, method-only, entity-only, drop}。

      tier=anchor       锚定实体（entities[0]）命中 **且** 至少命中 1 个方法词（含宽泛词）
                        → 正常入池，可判 exact，下载名额第一优先
      tier=method-only  锚定实体未命中但强方法词达阈 → 入池作方法学参考，
                        domain_match 封顶 adjacent，仍可占下载名额（见下）
      tier=entity-only  锚定实体命中但**零方法词** → 入池但 domain_match 封顶 adjacent，
                        排在 method-only 之后，下载名额最后才轮到它
      tier=drop         以上都不满足 → 丢弃

    强方法词阈值：普通条目需 ≥2；endorsed=True（施引反查的下游文献，已由靶心背书）
    降为 ≥1。**背书只降门槛不免检**：实测若完全豁免，「Revisiting the band gap
    problem in bulk Co3O4」(cited=16) 这类与目标体系无关的下游文献会凭施引关系被放行，
    甚至抢占 --oa-limit 下载名额。

    为何必须有锚定实体硬要求（真实 API 回归实测）：把次要实体词单独当检索词，
    会让「Structural Polymorphism of 441-Residue Tau」(PLoS Biol, cited=662)、
    「α-synuclein fibrils…polymorphism…solid-state NMR」(PNAS, cited=646)
    因「polymorph + solid-state NMR」双命中而被误判 exact，把真靶心挤出 top。
    宽泛方法词（NMR/DFT）不计分，否则「NMR Quantum Computation」会直接过门。

    为何要单拆 entity-only 档（真实 API 端到端实测）：只按「锚定实体命中」定档时，
    「Interstellar Glycine」(cited=377)、「Glycine and glycine receptor signalling in
    non-neuronal cells」(cited=100) 这类**同物质但零方法词**的泛领域文献会与 exact 同档，
    再靠高被引排到前面，把 --oa-limit 名额全部抢走，而 NMR crystallography、
    周期 DFT ¹³C shielding 精度这类真正可复用的方法学文献一篇都下不到。
    注意此档**只降优先级、不踢出池子**：「Crystal growth of α and γ glycine polymorphs」
    这类结晶学文献同样零方法词命中，但当任务问的是晶型结构而非谱学时它恰是靶心。
    """
    if not entities and not methods:
        return True, {"tier": "anchor", "anchor": "", "anchor_hit": False, "entities_core": [],
                      "entities_generic": [], "methods_strong": [], "methods_weak": [],
                      "score": 0, "note": "no-gate-terms"}
    blob = ((rec.get("title") or "") + " " + (rec.get("abstract") or "")).lower()
    anchor = entities[0] if entities else ""
    a_hit = term_hit(anchor, blob)
    core_e = [e for e in entities[1:] if term_hit(e, blob) and e.lower() not in GENERIC_MODIFIERS]
    gen_e = [e for e in entities if term_hit(e, blob) and e.lower() in GENERIC_MODIFIERS]
    strong_m = [m for m in methods if term_hit(m, blob) and m.lower() not in WEAK_METHODS]
    weak_m = [m for m in methods if term_hit(m, blob) and m.lower() in WEAK_METHODS]
    score = (4 if a_hit else 0) + 2 * len(core_e) + 1 * len(gen_e) \
        + 2 * len(strong_m) + 1 * len(weak_m)
    need = 1 if endorsed else 2
    if not methods:
        # 未给方法词时不启用 entity-only 档，否则所有记录都会被降级、下载名额全空
        tier = "anchor" if a_hit else ("method-only" if len(strong_m) >= need else "drop")
    elif a_hit and (strong_m or weak_m):
        tier = "anchor"
    elif a_hit:
        tier = "entity-only"
    elif len(strong_m) >= need:
        tier = "method-only"
    else:
        tier = "drop"
    return tier != "drop", {"tier": tier, "anchor": anchor, "anchor_hit": a_hit,
                            "entities_core": core_e, "entities_generic": gen_e,
                            "methods_strong": strong_m, "methods_weak": weak_m,
                            "score": score, "endorsed": endorsed}


def auto_domain_match(rec, entities, methods, tier="anchor"):
    """按客观规则给 domain_match 打底，并留下可审计依据。

    规则（只认词落在 title 还是 abstract，不认模型主观判断）：
      exact        **锚定实体**出现在 title，且方法词出现在 title 或 abstract
      adjacent     锚定实体只在 abstract，或只命中单侧，
                   或 tier=method-only / entity-only（两者均封顶）
      cross_domain 实体词与方法词都未命中

    两处设计取舍：
    - exact 必须要求锚定实体上 title：仅次要实体（polymorph）+ 方法命中不得算 exact，
      否则蛋白质多晶型 NMR 文献会被当成目标体系的 exact 证据。
    - 方法词匹配用**全部** methods（含 NMR/DFT 宽泛词）：语境已被锚定实体锁定，
      若在此也排除弱方法词，「Variable temperature NMR characterization of α-glycine」
      这类实验对照文献会被错降为 adjacent。

    上层可据此改严（exact→adjacent），**不得改松**。
    """
    t = (rec.get("title") or "").lower()
    a = (rec.get("abstract") or "").lower()
    anchor = entities[0] if entities else ""
    a_t = bool(anchor) and term_hit(anchor, t)
    a_a = bool(anchor) and term_hit(anchor, a)
    e_t = [e for e in entities if term_hit(e, t)]
    e_a = [e for e in entities if term_hit(e, a)]
    m_t = [m for m in methods if term_hit(m, t)]
    m_a = [m for m in methods if term_hit(m, a)]
    basis = []
    if a_t:
        basis.append("title 命中锚定实体[%s]" % anchor)
    elif a_a:
        basis.append("abstract 命中锚定实体[%s]（未上 title）" % anchor)
    if e_t:
        basis.append("title 命中实体%s" % e_t)
    if e_a:
        basis.append("abstract 命中实体%s" % e_a)
    if m_t:
        basis.append("title 命中方法%s" % m_t)
    if m_a:
        basis.append("abstract 命中方法%s" % m_a)
    if tier == "method-only":
        basis.append("锚定实体未命中→封顶 adjacent（仅方法学相关）")
        return "adjacent", "；".join(basis)
    if tier == "entity-only":
        basis.append("锚定实体命中但零方法词→封顶 adjacent（同体系、不同问题）")
        return "adjacent", "；".join(basis)
    if a_t and (m_t or m_a):
        label = "exact"
    elif (a_t or a_a) and (m_t or m_a):
        label = "adjacent"
    elif e_t or e_a or m_t or m_a:
        label = "adjacent"
    else:
        label = "cross_domain"
        basis = ["实体词与方法词均未出现在 title/abstract"]
    return label, "；".join(basis)


# ---------------------------------------------------------------- 全文获取
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
    """下载 OA PDF 并尝试抽取全文。返回 (pdf_path, fulltext_path or None)。已存在则复用。"""
    url = rec.get("oa_pdf_url")
    if not url:
        return None, None
    slug = re.sub(r"[^\w.\-]+", "_", (rec.get("doi") or rec.get("title") or "lit")[:60])
    pdf_path = os.path.join(workdir, "%s.pdf" % slug)
    if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) < 1024:
        data = get_text(url, timeout=60, binary=True)
        if not data or not isinstance(data, bytes) or not data[:5].startswith(b"%PDF"):
            return None, None  # 非 PDF（登录页/HTML），如实放弃，绝不绕墙
        with open(pdf_path, "wb") as f:
            f.write(data)
    txt_path = os.path.join(workdir, "%s_fulltext.txt" % slug)
    if os.path.exists(txt_path) and os.path.getsize(txt_path) > 0:
        return pdf_path, txt_path
    text = try_extract_pdf(pdf_path)
    if not text:
        return pdf_path, None
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    return pdf_path, txt_path


# ---------------------------------------------------------------- 主流程
def rank_key(rec):
    """下载与展示排序：相关性档位 > domain_match > 被引数。

    相关性档位排最前是实测结论：仅按被引数排会让跳领域高被引噪声
    （cited=662 的 Tau 多晶型、cited=646 的 α-synuclein）霸榜，把 cited=17 的真靶心挤到后面。

    entity-only 排在 method-only **之后**同样是实测结论：对「α/γ 甘氨酸多晶型 GIPAW
    化学位移」这类任务，「Interstellar Glycine」(cited=377)、「glycine receptor
    signalling」(cited=100) 虽命中锚定实体却零方法词，价值低于 NMR crystallography、
    周期 DFT ¹³C shielding 精度等方法学文献；若不降档，它们会靠高被引抢光 --oa-limit 名额。
    """
    rel = {"anchor": 0, "pass": 0, "method-only": 1, "entity-only": 2,
           "low-fallback": 3, "low": 4}.get(rec.get("relevance") or "anchor", 0)
    dm = {"exact": 0, "adjacent": 1, "cross_domain": 2}.get(rec.get("domain_match"), 3)
    return (rel, dm, -(rec.get("cited_by") or 0))


def main():
    global _MAILTO, UNPAYWALL_EMAIL
    ap = argparse.ArgumentParser(description="文献通道：多子查询 + 三源并行 + 相关性门 + 免费全文降级链")
    ap.add_argument("query")
    ap.add_argument("--max", type=int, default=15, help="每条子查询最多取多少条")
    ap.add_argument("--workdir", default="./online_kb")
    ap.add_argument("--fetch-oa", dest="fetch_oa", action="store_true",
                    help="对通过相关性门且有合法 OA 直链的条目下载 PDF 并尽力抽取全文")
    ap.add_argument("--oa-limit", dest="oa_limit", type=int, default=5, help="最多下载几篇 OA 全文")
    ap.add_argument("--with-arxiv", dest="with_arxiv", action="store_true",
                    help="附加 arXiv 布尔通道（abs:\"X\" AND abs:\"Y\" AND cat:…）")
    ap.add_argument("--entities", default="", help="目标实体词（逗号分隔），相关性门与 domain_match 的客观依据")
    ap.add_argument("--methods", default="", help="方法/技术词（逗号分隔）")
    ap.add_argument("--sub-queries", dest="sub_queries", default="",
                    help="显式子查询，用 | 分隔；不给则自动分解（推荐自动 + entities/methods）")
    ap.add_argument("--max-subqueries", dest="max_subqueries", type=int, default=6,
                    help="子查询条数上限（每条一个 OpenAlex 请求，控总耗时）")
    ap.add_argument("--year-from", dest="year_from", default="", help="年份下限，如 1990；经典文献常被年份门挡掉")
    ap.add_argument("--sort", default="relevance", choices=["relevance", "cited"],
                    help="OpenAlex 排序策略。默认 relevance：实测 cited 排序会把跳领域高被引"
                         "噪声（如 cited=662 的蛋白质多晶型 NMR）顶到头部，把低被引的真靶心挤出 top")
    ap.add_argument("--arxiv-cats", dest="arxiv_cats", default=DEFAULT_ARXIV_CATS, help="arXiv 类目，逗号分隔")
    ap.add_argument("--unpaywall-limit", dest="unpaywall_limit", type=int, default=20,
                    help="Unpaywall 补查预算（每条一次请求）；按相关性顺序消耗，不浪费在将被丢弃的噪声上")
    ap.add_argument("--no-unpaywall", dest="no_unpaywall", action="store_true",
                    help="关闭 Unpaywall 补查，只用 OpenAlex/EPMC 自带的 OA 线索")
    ap.add_argument("--citing-oa", dest="citing_oa", action="store_true",
                    help="对靶心(exact/adjacent)且付费墙的文献做施引反查，找开放获取下游载体")
    ap.add_argument("--citing-limit", dest="citing_limit", type=int, default=2, help="对几篇靶心做施引反查")
    ap.add_argument("--no-relevance-gate", dest="no_gate", action="store_true",
                    help="关闭相关性门（仅调试用；生产不建议）")
    ap.add_argument("--keep-irrelevant", dest="keep_irrelevant", action="store_true",
                    help="保留未过门条目并标 relevance=low（仍绝不进下载队列）")
    ap.add_argument("--no-epmc", dest="no_epmc", action="store_true", help="关闭 Europe PMC 并行源")
    ap.add_argument("--no-crossref", dest="no_crossref", action="store_true", help="关闭 Crossref 备用摘要源")
    ap.add_argument("--no-arxiv-fallback", dest="no_arxiv_fallback", action="store_true",
                    help="关闭『OpenAlex 被限流取空时自动降级到 arXiv』的定向救援")
    ap.add_argument("--top", type=int, default=12, help="stdout 打印前 N 条（勿再用 shell tail 截断）")
    ap.add_argument("--mailto", default=DEFAULT_MAILTO,
                    help="联系邮箱：OpenAlex polite pool 身份（**不提高配额**）+ Unpaywall 必需参数。"
                         "默认取环境变量 ONESCIENCE_CONTACT_EMAIL。为空时 OpenAlex 走匿名池"
                         "（实测可用），Unpaywall 自动改用中性占位（它只要求参数存在）")
    args = ap.parse_args()
    _MAILTO = args.mailto or DEFAULT_MAILTO
    # --mailto 显式传参时 Unpaywall 侧要同步跟上：help 里承诺了它是"OpenAlex 身份 + Unpaywall 必需参数"
    # 两处，若只在 import 期算一次，CLI 传邮箱就会只作用于 OpenAlex、Unpaywall 仍是占位，前后不自洽。
    UNPAYWALL_EMAIL = _MAILTO or "onescience-online-knowledge@example.org"
    os.makedirs(args.workdir, exist_ok=True)

    entities, methods = auto_split(args.query, args.entities, args.methods)
    subs = build_subqueries(args.query, entities, methods, args.sub_queries, args.max_subqueries)

    # ---- 三源并行（OpenAlex 字段级为主，EPMC 为并行主源而非死代码兜底）----
    groups, src_stat = [], {}
    for kind, q in subs:
        field = "search" if kind == "raw" else "title_and_abstract"
        recs = openalex(q, args.max, year_from=args.year_from or None, sort=args.sort, field=field)
        groups.append(("OpenAlex[%s:%s]" % (kind, q[:40]), recs))
        src_stat["OpenAlex"] = src_stat.get("OpenAlex", 0) + len(recs)
        time.sleep(0.3)   # polite：控制请求速率
    # EPMC 的检索式只由 entities/methods 决定、与子查询无关 → 只打一次，避免重复请求同一 URL
    if not args.no_epmc:
        eq = epmc_query(entities, methods, args.query)
        erecs = europepmc(eq, args.max)
        groups.append(("EuropePMC[%s]" % eq[:60], erecs))
        src_stat["EuropePMC"] = len(erecs)
    # Crossref 备用源：只打一次（与 EPMC 同为 query 级、不随子查询重复），
    # 独立限流池，专门兜住 OpenAlex/EPMC 同时无果的情形。
    if not args.no_crossref:
        crecs = crossref(args.query, args.max, year_from=args.year_from or None)
        groups.append(("Crossref[%s]" % args.query[:60], crecs))
        src_stat["Crossref"] = len(crecs)
    # arXiv 定向救援：显式 --with-arxiv（严格式），或 OpenAlex 被 IP 级限流取空(src_stat==0)
    # 时自动启用降级救援（arxiv_query rescue=True：放宽为 首实体+首方法、去 cat，实测 cat 组
    # 合取会致 arXiv 0 命中）。arXiv 走独立限流池，是 OpenAlex 死掉时的补源；但预印本缺
    # DOI/引用数，故仅作降级救援并显式标 arxiv_fallback_applied + caveat 供上层区分证据强度。
    oa_throttled = (src_stat.get("OpenAlex", 0) == 0)
    arxiv_fallback_applied = (not args.with_arxiv) and oa_throttled and (not args.no_arxiv_fallback)
    if args.with_arxiv or arxiv_fallback_applied:
        asq = arxiv_query(entities, methods, args.arxiv_cats, args.query, rescue=arxiv_fallback_applied)
        arecs = arxiv_search(asq, max(5, args.max // 3))
        groups.append(("arXiv[%s]" % (asq or "")[:60], arecs))
        src_stat["arXiv"] = len(arecs)

    online = _net_ok or any(g[1] for g in groups)
    recs = merge_recs(groups)

    # ---- 相关性门 + 客观 domain_match ----
    kept, dropped = [], []
    tier_stat = {"anchor": 0, "entity-only": 0, "method-only": 0}
    for r in recs:
        if args.no_gate:
            ok, detail = True, {"tier": "anchor", "note": "gate-disabled", "score": 0}
        else:
            ok, detail = relevance_gate(r, entities, methods)
        tier = detail.get("tier", "anchor")
        dm, basis = auto_domain_match(r, entities, methods, tier)
        r["domain_match"], r["domain_match_basis"], r["domain_match_auto"] = dm, basis, True
        r["relevance"] = tier if ok else "low"
        r["relevance_detail"] = detail
        if ok:
            tier_stat[tier] = tier_stat.get(tier, 0) + 1
        (kept if ok else dropped).append(r)
    # fail-safe：门过严导致零召回比无门更糟（会让上层误判「领域无文献」）。
    # 此时回退保留得分最高的几条，显式标 relevance=low 并给出 caveat。
    fallback = False
    if not kept and dropped:
        fallback = True
        kept = sorted(dropped, key=lambda x: -(x.get("relevance_detail", {}).get("score", 0)))[:5]
        for r in kept:
            r["relevance"] = "low-fallback"
        kept_ids = {id(r) for r in kept}
        dropped = [r for r in dropped if id(r) not in kept_ids]
        tier_stat["low-fallback"] = len(kept)
    pool = kept if not args.keep_irrelevant else (kept + dropped)

    # ---- Unpaywall 补查：给没有 PDF 直链的 DOI 找合法免费版（机构库/预印本）----
    # 放在相关性门**之后**并按 rank_key 顺序跑：预算有限的 OA 补查不该浪费在将被丢弃的
    # 噪声上，且要让最对题的条目优先获得补查机会。
    # 条件不再要求 is_oa 为假——OpenAlex 常把 green OA 只标成仓储落地页（oa_url），
    # best_oa_location.url_for_pdf 为空，此时 Unpaywall 的 oa_locations 里可能另有可下 PDF。
    upw_tried = 0
    if (args.with_arxiv or args.fetch_oa or args.citing_oa) and not args.no_unpaywall:
        for r in sorted(pool, key=rank_key):
            if not r.get("doi") or r.get("oa_pdf_url"):
                continue
            if upw_tried >= args.unpaywall_limit:
                break
            upw_tried += 1
            is_oa, pdf = unpaywall_lookup(r["doi"])
            if is_oa:
                r["is_oa"] = True
                if pdf:
                    r["oa_pdf_url"], r["oa_source"] = pdf, "unpaywall"
            time.sleep(0.2)

    # ---- 施引反查：付费墙靶心文献的免费全文替代路径 ----
    citing_found, citing_dropped = 0, 0
    if args.citing_oa:
        paywalled = [r for r in kept if r.get("domain_match") in ("exact", "adjacent")
                     and r.get("openalex_id") and not r.get("oa_pdf_url")][:args.citing_limit]
        for r in paywalled:
            c = citing_oa(r["openalex_id"], 5)
            for x in c:
                # 背书只降门槛不免检：仍要求至少命中 1 个强方法词，否则丢弃
                ok, det = relevance_gate(x, entities, methods, endorsed=True)
                if not ok:
                    citing_dropped += 1
                    continue
                citing_found += 1
                tier = det.get("tier", "method-only")
                dm, basis = auto_domain_match(x, entities, methods, tier)
                det["note"] = "endorsed-by-cited-target(%s)" % (r.get("doi") or "")[:40]
                x.update(domain_match=dm if dm != "cross_domain" else "adjacent",
                         domain_match_basis="施引自 %s；%s" % (r.get("doi") or r.get("title", "")[:40], basis),
                         domain_match_auto=True, relevance=tier, relevance_detail=det,
                         oa_source="citing")
                pool.append(x)
            time.sleep(0.3)
        pool = merge_recs([("pool", pool)])

    # ---- 排序 + 全文下载（只下过门的，按 domain_match/被引排序）----
    pool.sort(key=rank_key)
    items, oa_fetched = [], 0
    for i, r in enumerate(pool, 1):
        ev, note = "abstract-only", "无合法 OA 全文线索；**禁止**据此引用任何数值，需数值请改走数据通道或标 knowledge_gap"
        pdf_path = txt_path = None
        if r.get("oa_pdf_url") or r.get("oa_url"):
            ev, note = "abstract", "有合法 OA 免费版：%s" % (r.get("oa_pdf_url") or r.get("oa_url"))
        # 名额按 rank_key 顺序取（pool 已排序），故只需排除 fail-safe 兜底进来的
        # low/low-fallback（--keep-irrelevant 时它们在池里）。**不要**再按档名做正向白名单：
        # 实测白名单会漏掉 entity-only 档，使「Interstellar Glycine」(cited=377)、
        # 「Glycine and glycine receptor signalling」(cited=100) 这类同物质但零方法词的
        # 泛领域文献抢光名额，而 NMR crystallography、周期 DFT ¹³C shielding 精度等
        # 方法学文献一篇都下不到。
        if r.get("relevance") not in ("low", "low-fallback") and args.fetch_oa \
                and oa_fetched < args.oa_limit and r.get("oa_pdf_url"):
            pdf_path, txt_path = fetch_oa_pdf(r, args.workdir)
            if pdf_path:
                oa_fetched += 1
                # 拿到 PDF != 拿到全文。本机缺 pymupdf/pdfminer 时 txt_path 为 None，
                # 此时**绝不可**标 full-text-oa：那会把 confidence 升到 high，并把
                # oa_fulltext_count 顶成非 0，从而**吞掉**本该提示"全文通道整体失效"的
                # caveat_fulltext——与同条目 note 自述"未能抽文本"直接矛盾。实测会话 200
                # 即如此：2 条标 full-text-oa、confidence=high，而 fulltext_path 全为 null，
                # 且 caveat_fulltext 一次都没触发。
                # 退回既有 abstract 档而非新增枚举值，不动上层按 evidence_level 的既有判据。
                ev = "full-text-oa" if txt_path else "abstract"
                note = ("OA 全文已抽取：%s" % txt_path) if txt_path else \
                       ("OA PDF 已下载但本机缺 pymupdf/pdfminer，未能抽文本（%s）；"
                        "evidence_level 保持 abstract，**不得**据此引用任何数值" % pdf_path)
                # 拿到全文不等于对题。余量名额会轮到 entity-only / method-only 档，
                # 实测「Glycine and glycine receptor signalling in non-neuronal cells」
                # （神经科学综述，零方法词命中）会因高排位候选 PDF 下载失败而拿到名额；
                # 它的全文一旦进了 online_kb 又没标注，上层极可能把里面的数值归因给
                # 目标体系的谱学结果。所以全文条目必须把档位含义写进 note。
                if r.get("relevance") == "entity-only":
                    note += ("｜⚠ 本篇仅命中目标体系名、未命中任何方法词（relevance=entity-only）："
                             "属**同物质、不同问题**，不得把其数值/结论当作目标体系的谱学或计算结果")
                elif r.get("relevance") == "method-only":
                    note += ("｜⚠ 本篇未命中目标体系名（relevance=method-only）：**只作方法学参考**"
                             "（怎么做、精度多少、参照如何选），不得把其具体数值当作目标体系的数值")
        items.append({
            "key": "lit_%02d" % i,
            "channel": "literature",
            "value": dict(r, pdf_path=pdf_path, fulltext_path=txt_path),
            "provenance": ("DOI:%s" % r["doi"]) if r.get("doi") else ("title:%s" % (r.get("title") or "")[:60]),
            "source_type": "literature",
            "evidence_level": ev,
            "verified_online": online,
            "self_verified": False,
            "domain_match": r.get("domain_match"),
            "domain_match_basis": r.get("domain_match_basis"),
            "domain_match_auto": True,
            "relevance": r.get("relevance", "anchor"),
            "confidence": ("high" if ev == "full-text-oa" else "medium") if online else "low",
            "note": note if online else "OFFLINE",
        })

    dm_summary = {k: sum(1 for x in items if x["domain_match"] == k)
                  for k in ("exact", "adjacent", "cross_domain")}
    result = {
        "channel": "literature", "query": args.query,
        "sub_queries": [{"kind": k, "query": q} for k, q in subs],
        "entities": entities, "methods": methods,
        "source": "multi(OpenAlex+EuropePMC%s%s)" % (
            "+arXiv" if args.with_arxiv else ("+arXiv-fallback" if arxiv_fallback_applied else ""),
            "+Crossref" if not args.no_crossref else ""),
        "source_stats": src_stat,
        "network": "online" if online else "offline",
        "arxiv_fallback_applied": arxiv_fallback_applied,
        "openalex_throttled": oa_throttled,
        "relevance_gate": {"enabled": not args.no_gate, "threshold": GATE_THRESHOLD,
                           "anchor_entity": (entities or [""])[0],
                           "entities": entities,
                           "methods_strong": [m for m in methods if m.lower() not in WEAK_METHODS],
                           "methods_weak_excluded": [m for m in methods if m.lower() in WEAK_METHODS],
                           "tier_stats": tier_stat,
                           "passed": len(kept), "dropped": len(dropped),
                           "fallback_applied": fallback,
                           "dropped_titles": [(x.get("title") or "")[:70] for x in dropped[:10]]},
        "domain_match_summary": dm_summary,
        "paywall": {"closed_count": sum(1 for r in pool if not r.get("is_oa")),
                    "unpaywall_tried": upw_tried,
                    "unpaywall_budget": args.unpaywall_limit,
                    "unpaywall_email_source": "configured" if _MAILTO else "placeholder",
                    "openalex_identity": ("api_key" if OA_API_KEY else
                                          ("mailto" if _MAILTO else "anonymous")),
                    "citing_oa_found": citing_found, "citing_oa_dropped": citing_dropped},
        "oa_fulltext_count": sum(1 for x in items if x["evidence_level"] == "full-text-oa"),
        "found": len(items) > 0, "count": len(items), "items": items,
    }
    if items and dm_summary["exact"] == 0 and dm_summary["adjacent"] == 0:
        result["caveat"] = ("全部命中均为 cross_domain：本轮检索式未打中目标体系。"
                            "请显式传 --entities/--methods 或换 --sub-queries，勿据此判定领域无文献。")
    if fallback:
        result["caveat_gate"] = ("相关性门把全部命中挡下（已回退保留得分最高的 %d 条，标 relevance=low-fallback）。"
                                 "这通常意味着 --entities 填得太窄或目标体系名写错，而不是领域无文献；"
                                 "请校对实体词后重跑，勿直接把本结果当作知识缺口证据。" % len(kept))
    if items and result["oa_fulltext_count"] == 0:
        nxt = ("已下载但仍抽不出文本（本机缺 pymupdf/pdfminer）" if args.fetch_oa else
               "未加 --fetch-oa，本轮只拿题录/摘要；需全文请加 --fetch-oa")
        result["caveat_fulltext"] = (
            "未取到任何 OA 全文（%s）。所有 evidence_level 停在 abstract/abstract-only，"
            "**不得**作为数值来源；付费墙靶心可加 --citing-oa 走施引反查找 OA 下游载体，"
            "仍无则如实标 knowledge_gap。" % nxt)
    if arxiv_fallback_applied:
        result["caveat_arxiv"] = ("OpenAlex 疑被 IP 级限流取空，已自动降级到 arXiv 预印本源补召回。"
                                  "arXiv 条目缺 DOI/引用数、为预印本，证据强度低于同行评审正文；"
                                  "relevance 门仍按题录命中判档，但请勿把 arXiv 命中当作已验证的最终数值来源。")

    outp = os.path.join(args.workdir, "lit_result.json")
    with open(outp, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    if not online:
        print("[OFFLINE] OpenAlex/Europe PMC/arXiv 均不可达；文献通道返回空，上层如实标注离线缺口。")
    print(json.dumps({
        "source": result["source"], "network": result["network"], "count": len(items),
        "oa_fulltext": result["oa_fulltext_count"],
        "domain_match_summary": dm_summary,
        "relevance_gate": {"passed": len(kept), "dropped": len(dropped), "fallback": fallback,
                           "tiers": tier_stat, "anchor": (entities or [""])[0],
                           "strong_methods": [m for m in methods if m.lower() not in WEAK_METHODS]},
        "citing_oa_found": citing_found, "citing_oa_dropped": citing_dropped,
        "sub_queries": [q for _, q in subs],
        "top": [{"title": x["value"]["title"], "year": x["value"]["year"], "doi": x["value"]["doi"],
                 "cited_by": x["value"].get("cited_by"), "venue": x["value"].get("venue"),
                 "is_oa": x["value"].get("is_oa"), "oa_status": x["value"].get("oa_status"),
                 "src": x["value"].get("source"), "rel": x["relevance"],
                 "dm": x["domain_match"], "ev": x["evidence_level"]}
                for x in items[:args.top]],
    }, ensure_ascii=False, indent=2))
    for k in ("caveat", "caveat_gate", "caveat_fulltext"):
        if result.get(k):
            print("\n[!] %s" % result[k])
    print("\n[saved] %s" % outp)


if __name__ == "__main__":
    main()
