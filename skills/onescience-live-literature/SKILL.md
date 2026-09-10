---
name: onescience-live-literature
description: OneScience 实时文献两级检索推理技能（对齐 Biomni 的 LiteratureSearch/Fetch 工具链），领域无关的通用流程。第一级按相关性实时检索 OpenAlex 拿论文摘要、建全局编号引用池并迭代精炼检索词；第二级对选中的开放获取论文经 Europe PMC/PMC 结构化 API 取全文细节；最终输出分层深度推理答案，References 按正文出现顺序连续编号。触发：任何需要跨论文实时综合推理并带引用列表的问题（物种×性状、通路机制、基因家族、材料体系、药物靶点等）。只产出会话级证据与 harvest 种子清单，不写卡片库。
type: executor
---

# OneScience 实时文献两级检索推理

## 通用性声明（本协议领域无关）

- 本技能是**通用流程**，不是针对某一物种/某一主题的专用机制：任何需要跨论文实时综合推理的自然科学问题都走同一套六步协议。
- 协议中**没有任何领域硬编码**：检索词由 Step 1 按问题领域分解产生（物种学名、基因/酶/通路名、方法名、材料名）；全文抽取关键词由 `--keys` 参数传入。
- 换题即换参数，流程与纪律条款不变。

## 职责边界

- 本技能负责**在线会话级**文献检索与带引用的深度推理回答：摘要层检索 → 迭代精炼 → 全文层取细节 → 深度综合输出。
- 不负责：离线知识卡的撰写/晋升/导出（那是 pkp 流水线的职责）。会话结束时只通过 Step 6 的 seeds.json 交接证据。

## 协议（六步，严格按序）

### Step 1 查询分解

把用户问题拆成 2~4 组英文检索词（含同义词、物种学名、基因/酶/通路名、方法名）。每组声明 `max_papers`（默认 15）与 `year_from`（默认近 8 年）。同时从问题中提炼 3~6 个**全文抽取关键词**（英文，供 Step 4 的 `--keys` 用）。

### Step 2 第一级摘要检索（命令块 A）

把下方"命令块 A"模板原样落盘为会话临时脚本 `lit_search.py` 并执行：

```
python lit_search.py "<query>" <max_papers> <year_from> <pool_json路径>
```

- 检索走 OpenAlex works 接口，**相关性排序**（search 默认）+ `from_publication_date` 过滤；禁止改用被引排序（被引排序会漏掉当年新论文，已实测验证）。
- 输出：终端打印编号摘要行；并把条目追加进 pool_json（全局编号跨多次调用续接，形如 [1]~[n]；**按 DOI/标题去重**，重复命中跳过不占编号）。
- 条目字段：title / authors / venue / year / doi / oa_url / cited / abstract（前 400 字）。

### Step 3 迭代精炼（对齐 Biomni 的第二轮检索）

通读池内摘要，抽出实体词（基因名、酶名、菌株/物种名、通路名、方法名），组成 1~2 组**新**检索词再跑命令块 A，编号续接。至少迭代一轮；若第一轮摘要已出现明确实体名而第二轮未使用，视为协议违规。

**缺口补搜（对齐 Biomni 的权威文献覆盖）**：迭代后自查池内是否覆盖问题领域的权威一次文献——如基因组/组装级研究、起源/驯化研究、关键酶功能定性、最新调控机制、**替代路线/旁路反应/多功能酶**（检索词如 alternative route / bypass / promiscuous / multifunctional / ancestral / neofunctionalization），按领域取舍，不是全部必需。缺哪类就用「实体词 + genome / origin / characterization / regulation / alternative / evolution」等追加一轮定向检索；确认检索不到才允许放弃。

**逐实体演化追踪（每会话强制；实测教训）**：对池内出现的核心基因/酶/材料实体（最多取 5 个最关键的），各补一轮 `"<实体名>" + evolution / ancestral / origin / neofunctionalization` 定向检索——决定性证据常常藏在**单实体专项演化研究**里（辣椒 A/B 实测：pAMT 的 GABA-T→新功能化链条只有一篇 Plant J 专项研究讲透，主题级检索词捞不到它，且该文虽付费墙但摘要可拿、足以支撑 abstract 级演化结论）。核心实体一个都没做逐实体追踪 = 协议违规。

**新颖性扫描（每会话强制至少两组词面；实测教训）**：相关性排序会系统性埋没刚发表、引用少的新论文——青蒿素 A/B 实测中，决定胜负的两篇（2024 CYP71AV1 演化研究、2025 替代路线新酶 NatComm）全文通道均可达，却因新颖性盲点没进池。因此必须至少跑一轮 `year_from = 当年-1` 的命令块 A。辣椒 A/B 实测又证明**单组词面不够**：两轮扫描分别为 ① 核心实体词 + alternative/new/evolution；② 综述/盘点词面（review / QTL / mapping / genome assembly / metabolic engineering）——当年新综述常被第②组才捞到。任一组零命中时换词再跑一次才允许放弃。

### Step 4 第二级全文取细节（命令块 B，整篇落盘 + 分段精读）

1. 从池中挑 **4~8 篇**与推理链最相关的论文（优先 Step 3 缺口补搜找到的权威一次文献）。
2. 把命令块 B 模板落盘为 `lit_fetch.py` 并执行：
   ```
   python lit_fetch.py <outdir> --keys "<领域关键词逗号分隔>" <doi1> <doi2> ...
   ```
   内置双通道已固化（均实测）：① Europe PMC REST（DOI→pmcid/PPR→fullTextXML，覆盖 PMC OA 子集）→ ② NCBI pmcoa BioC JSON（Europe PMC 404 时兜底，实测成功）→ ③ 双通道失败 = abstract-only。出版社页面（ScienceDirect 403 / MDPI 人机验证 / bioRxiv 页面 429）实测不可用，**不要浪费时间尝试**。
3. **控制台输出只是索引**（pmcid、字符数、章节索引、关键词命中预览）。对每篇全文成功的论文，必须用读文件工具**分段读取落盘文件** `<outdir>/<doi_slug>.txt` 的完整内容提取细节：数值（浓度、滴度、同一性%、基因拷贝数、KS 峰、温度、时间、占干重比）、基因-酶-产物对应、实验条件、演化分析。**禁止只看控制台预览就写答案**——这是细节密度不足的第一根因。
4. 降级纪律：全文通道全失败的论文，禁止引用其全文细节，答案中标注 `(abstract-only)`，并在失败报告里列出尝试过的通道与状态码/错误。但 **abstract-only 论文的摘要仍是有效证据**：摘要中的实体身份、方向性结论、定性事实可以引用（证据层级标 abstract-only）——"拿不到全文"不等于"这篇论文不能用"（实测：pAMT 演化专项研究、capsinoids 低辣结论都在摘要里写得明明白白）。

### Step 5 深度综合输出（对齐 Biomni 的细节密度）

**编号规则（先重排，再输出）：**

- 综合阶段把正文**实际引用**的论文按首次出现顺序重排为**连续编号 `[1]..[k]`**（不允许跳号，如 [1][2][10] 是违规的）；行内引用与 References 全部使用新连续编号。
- 池编号只留在 pool.json 里做审计，不出现在答案中。

**深度规格（每条都是硬性要求）：**

1. 正文分 **4~6 个层级小节**组织推理，例如：基因组/物种起源层面 → 核心机制/通路 → 关键基因家族与数值 → 调控与演化 → 工程/应用 → 结论。小节切分随问题领域调整，但必须分层展开而不是平铺直叙地"简单回答"。
2. **数值配额**：全文 ≥15 个有出处 `[n]` 的具体数值；每个层级小节 ≥3 个数值（某小节确实无数值证据时，显式声明"本节为 abstract-only 证据"）。全文级论文必须引用其 Results 的具体数字（如滴度 mg/L、identity %、基因拷贝数、正选择位点、温度条件、占干重比例）。
3. 至少包含 **1 张表格**：`实体 → 功能/角色 → 关键数值 → 证据[n]`。
4. 至少包含 **1 个文字通路/机制示意**：多级箭头链，覆盖底物→酶→中间体→产物→分支的完整路径，每一步挂 `[n]`。
5. 正文体量与证据量对齐：池内有 ≥3 篇全文级论文时正文 ≥1200 字；证据确实单薄（全 abstract-only）可以短，但必须声明原因。
6. 模型自身推断必须显式标"(推断)"；摘要里没有、全文里也没有的精确数值**禁止凭记忆补写**。
7. **推理链环节审计（拦截跨事实拼接幻觉）**：每一条因果/演化断言——"A 催化 B""突变 M 驱动了功能 F 的出现""通路基因形成物理簇"等——所挂的 `[n]` 必须在**同一篇文献内直接**支持该断言。若断言是把多篇论文拼接而成（例：文1 说"GAS 是祖先通路酶"，文2 说"单个突变可改变 TPS 环化能力"，拼成"GAS 经该突变演化为 ADS"），必须标"(跨文献推断: [a]+[b]，无单篇直接证据)"。综述里的谨慎措辞（"可能""suggests"）转述时**不得升级为确定性断言**。
8. **实体身份一致性审计**：同一基因/位点/蛋白/材料名在全文只能挂**一个身份**（如 Pun3=MYB 转录因子）。池内身份证据冲突或不足时，要么定向补搜裁决，要么显式标"(文献身份冲突: [a] 称 X，[b] 称 Y)"——**无标注地双身份并列是协议违规**（辣椒 A/B 实测：Pun3 同时被写成 BCAT-KAS 簇与 CaMYB31，被裁决方点名为最大硬错误）。表格中每行实体名必须与正文同一身份。
9. **方向/极性断言接地**："更辣/低辣、更强/更弱、获得/丧失功能、上调/下调、促进/抑制"等定性方向陈述同样必须有池内出处，禁止凭记忆写极性（实测：capsinoids 被写成"更辣"，原文结论恰好相反——低辣/近乎不辣）。
10. **普遍化词反例审计**：写"主要/所有/通常/唯一/大多数"之前，先自查池内是否存在并列或反例机制——有则必须并列写出，不得无统计依据地把其中之一定为"主因"（实测：写"非辣主要由 OCR 缺失造成"，而 Pun1/pAMT/CaKR1 反例就在自己池内）。
11. 输出前深度自检：逐小节问"能否再补 2 条有数值的事实？"——能补而没补的，回到 Step 4 的 dump 文件继续读或增抓全文；确实没有的，如实保持 abstract-only 深度。同时逐条过第 7~10 条审计（环节/身份/极性/普遍化词）。

**References 格式：**

- 文末 `References` = 正文实际引用的论文（连续编号），每条含：编号、标题、venue、year、作者前 3 位 et al、doi、证据层级（**full-text** / abstract-only）。所有字段必须取自 pool.json 对应条目；缺失字段写 `(池内无)`，**禁止 doi:10.xxxx 之类占位符**。
- 两轮检索后池仍为空 → 声明证据不足，拒出引用列表，只给模型先验回答并显著标注。

### Step 6 harvest 交接（把会话证据沉淀进离线库存）

把 References 子集写入 `<工作区>/data/scenarios/live_<topic_slug>.seeds.json`：

```json
{"topic": "...", "captured_at": "ISO日期", "seeds": [{"title": "...", "doi": "...", "oa_url": "..."}]}
```

供 pkp 流水线的种子论文通道（scenario related_papers）离线全文蒸馏成卡。答案末尾声明"已登记 N 篇种子论文"。**本技能不直接写任何卡片库。**

## 命令块 A 模板（lit_search.py）

```python
import json, re, sys
from urllib.parse import quote
from urllib.request import urlopen, Request

q, n, year, out = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
url = ("https://api.openalex.org/works?search=" + quote(q)
       + f"&per-page={n}"
       + f"&filter=is_paratext:false,type:article,from_publication_date:{year}-01-01"
       + "&select=id,title,doi,publication_date,open_access,primary_location,"
         "authorships,cited_by_count,abstract_inverted_index")
req = Request(url, headers={"User-Agent": "OneSkills-live-lit/0.1 (mailto:onetools@example.com)"})
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
```

## 命令块 B 模板（lit_fetch.py v2，全文层；双通道实测：Europe PMC OA 子集 + NCBI BioC 兜底）

```python
import json, os, re, sys, urllib.parse, urllib.request
from xml.etree import ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows GBK 控制台防崩
UA = {"User-Agent": "OneSkills-live-lit/0.2"}

def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")

def norm_id(raw):
    # 防双重前缀坑：接受 "123"/"PMC123"/"PPR123"，统一规范化（旧版 PMCPMC123 导致全线 404）
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
```

## 纪律铁律

1. 只允许引用池内论文；**禁止编造文献**（标题/作者/年份任一字段不得凭记忆补写）。答案中的 `[n]` 是 Step 5 重排后的连续编号，不得跳号。References 字段全部取自 pool.json 对应条目，缺失字段写 `(池内无)`，**禁止 doi:10.xxxx 之类占位符**。
2. 数值与实体对应关系必须来自 full-text 或 abstract 原文；因果/演化断言必须有单篇文献**直接**支持，跨论文拼接必须标"(跨文献推断)"，综述谨慎措辞不得升级为断言；方向/极性类定性结论（更辣/低辣、获得/丧失、上调/下调）同样必须有池内出处；否则标"(推断)"，禁止凭记忆补写摘要里没有的精确数值或极性结论。
3. 同一实体名全文只能挂一个身份，冲突必须显式报告；"主要/所有/通常"类普遍化断言必须先过池内反例审计。
4. 全文层只走结构化 API（Europe PMC fullTextXML → NCBI BioC）；出版社页面实测被反爬，不要尝试；非 OA 一律 abstract-only 降权标注，但其摘要仍可作证据使用。
5. 检索与 fetch 失败要显式报告失败原因（状态码/异常），不得静默跳过。
6. 全文抓取成功的论文，必须用读文件工具实际分段读取其 dump 文件后再写答案；只看控制台预览写作视为协议违规。
7. 深度规格不达标（数值配额、表格、通路示意、体量任一缺失）视为协议违规，输出前必须自检补齐。
8. 不修改工作区外的任何库文件；harvest 只写 seeds.json。
