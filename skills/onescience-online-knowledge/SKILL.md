---
name: onescience-online-knowledge
description: OneScience 统一在线查证技能。为任务一次性补齐三类承重知识——①文献（论文题录/摘要/数值/引用）②晶体结构与物质数据（COD 等开放数据库的真实 CIF→晶格参数/空间群/分数坐标）③软件级计算参数（VASP/QE/CASTEP 的 INCAR 标签、截断能、k 点、GIPAW 设置等惯例值）。核心纪律：线上优先，线上确实取不到才允许回退到模型先验，但模型先验必须显式标注「⚠ 未经在线核实」且严禁冒充某篇文献/数据库的出处；结构数据下载后必须用化学式回验、绝不默写坐标；任何一类知识缺失都不构成 blocked 理由（不因缺知识而停摆，而是降级为「带标注的先验」继续跑）。type=executor，作为 primitives 本地召回降到 none/task_only 时的在线兜底通道，以及 orchestrator knowledge_gap=true 时的硬路由在线查证 executor。只产出会话级结构化证据对象与交接种子，不写卡片库。
type: executor
capabilities:
  owns:
    - 在线文献查证
    - 晶体结构数据查证
    - 软件计算参数查证
    - 降级先验标注
  not_owns:
    - 写卡片库
    - 代码生成
    - 训练
  inputs:
    - knowledge_query
    - domain
  outputs:
    - structured_evidence
    - seed_list
  downstream: []
  prereq:
    - 知识查证需求已明确
  intent_aspects:
    - online_verification
    - knowledge_gap_filling
  operation_types:
    - retrieve
  artifact_types:
    - knowledge
    - report
  domains:
    - general
  trigger_keywords:
    - 在线查证
    - 文献查证
    - 晶体结构
    - 计算参数
    - online knowledge
---

## 输入获取方式

本技能支持两种输入方式：

1. **上下文 handoff**（默认）：从调用方传入的 `step_handoff` 获取任务信息（待查证的知识点清单、目标域、化学式/物质名、软件栈等）。
2. **文件 handoff**（autonomous_mode）：从 `.onescience/handoff/step_{step_id}.yaml` 读取；结果写入 `step_{step_id}_result.yaml`。

启动时优先检查 `.onescience/handoff/` 是否存在交接文件；存在则文件模式，否则上下文模式。

# OneScience 统一在线查证

## 一、定位与边界

本技能把「在线找知识」拆成**三条互相独立的通道**，因为它们的信息压根不在同一种来源里，用一种检索器硬套另外两类必然失败：

| 通道 | 承重的知识 | 权威来源 | 本技能能否保证拿到 |
|---|---|---|---|
| **① 文献** | 方法学选择（泛函类别、核素、参照化合物、实验值、机理） | OpenAlex / Europe PMC / arXiv / Unpaywall | 🟡 题录+摘要稳；全文受付费墙天花板限制 |
| **② 结构/物质数据** | 晶体结构坐标、晶格参数、空间群、分子量 | COD（开放数据库，按号下 CIF）、可选 Materials Project | 🟢 按编号下载稳定；名/式→号检索需 session 握手 |
| **③ 软件参数** | ENCUT、k 网格、LCHIMAG/LEPSILON/ICHIBARE、IVDW 等 INCAR 标签 | 软件文档 + 领域惯例（**任何论文都不写这些**） | 🟢 内置带出处的参考表，稳定可得 |

**与其它技能的分工**：
- `onescience-primitives`：本地资源/知识**召回**（type=resource），命中不到领域实质知识（none/task_only）时降级到本技能。
- `onescience-live-literature`：**纯文献**的六步深度综合推理。本通道的文献深读**复用它**（命令块 A/B），本技能只做「快查数值」的轻量文献检索，不重造六步协议。
- 本技能独有价值 = 把 **② 结构数据库** 和 **③ 软件参数** 这两类「论文里根本没有、模型只能靠记忆默写」的承重知识，改成**真实在线取数 + 强制回验 + 诚实标注**。

## 二、核心纪律（最高优先，违反即协议错误）

1. **线上优先，先验兜底，但不许混淆**：任一承重知识，先尝试在线通道取真值。**只有当在线通道明确返回未命中**（found=false / OFFLINE），才允许使用模型先验值；此时该条必须打 `source_type=model-prior` + `verified_online=false` + 正文标 `⚠ 未经在线核实的模型先验`。**严禁把先验值标注成文献 [n] 或数据库记录的结论**（出处造假是本协议的头号禁止项）。
2. **结构数据零默写 + 化学式回验**：任何写进 POSCAR/CIF/坐标文件的原子坐标，来源只能是：① 在线下载的 CIF（且下载后用 `_chemical_formula_sum` 与目标化学式**回验一致**才接受），或 ② 显式标注的先验兜底。下载到但**回验不符**的结构（如编号对应的是别的物质）一律丢弃、继续下一个候选，绝不将错就错。
3. **不因缺知识而 blocked**：三类知识里任何一条线上取不到，都**不停摆、不报错中断上层任务**——降级为「带标注的先验」继续，或如实声明「本条在线证据缺失」后继续其余步骤。blocked 只保留给「用户必须提供、模型无权假设」的输入（如私有结构、付费 key），不用于普通知识缺口。
4. **软件参数不套引文门**：ENCUT/k 网格/INCAR 标签这类来自软件文档与惯例，**不该被『必须带文献 [n]』的门误卡**；它们的出处写 `source_type=software-doc`（指向参考表/官方文档），不伪造论文引用。
5. **离线降级不崩溃**：所有命令块必须捕获网络异常，网络不可用时打印 `[OFFLINE]` 并如实标注，让上层继续，绝不抛栈中断。
6. **domain_match 逐条打标**（文献通道）：沿用 live-literature 口径 `exact/adjacent/cross_domain`，`cross_domain` 只能作方法学参考、不得生成本任务的具体数值。
7. **参数必须读自内容层，不许看题录就下结论**：`scripts/lit_search.py` 默认已在 stdout 的 `top[].abs` / `top[].abs_nums` 里带上前几条（域匹配 `exact` 优先）的**摘要正文与其中带单位数值**。写进方案的每个数值只能来自 ①`abs`/`abs_nums` ②已下载的全文 ③数据库记录。**只看过标题/年份/被引数就给出的数值，一律按先验处理**（按第 1 条标 `source_type=model-prior` + `⚠`）。若一次检索的 `top` 里**完全没有 `abs` 字段**（多为源被限流、或命中源本身不含摘要），必须换源/重试或如实标 `knowledge_gap`，不得退回凭标题作答。

## 三、统一输出 schema（每通道产出一个 JSON 对象，落到会话工作目录）

顶层对象 `online_knowledge.json`：

```json
{
  "task": "<原始任务/待查证问题>",
  "generated_at": "<ISO 时间>",
  "network": "online | offline",
  "items": [
    {
      "key": "<该承重知识的槽位名，如 alpha_glycine_POSCAR / NMR_functional / ENCUT>",
      "channel": "literature | structure | software-param",
      "value": "<取到的值或结构化对象（CIF 路径/晶格/空间群/分数坐标；或参数名值对）>",
      "provenance": "<出处：DOI+文献编号[n] / COD:<编号> / software-doc:<来源标识>",
      "source_type": "literature | database | software-doc | model-prior",
      "evidence_level": "full-text | abstract | db-record | curated-ref | prior",
      "verified_online": true,
      "self_verified": true,
      "domain_match": "exact | adjacent | cross_domain | null",
      "domain_match_basis": "<脚本给出的客观依据：哪个词落在 title / abstract>",
      "relevance": "anchor | method-only | entity-only | low-fallback | low",
      "confidence": "high | medium | low",
      "note": "<回验结论 / 兜底原因 / abstract-only / OFFLINE 等>"
    }
  ],
  "counts": { "verified_online": 0, "model_prior_fallback": 0, "self_verify_failed": 0 },
  "harvest_seed": { "gaps": [], "new_anchor_ids": [] }
}
```

**硬约束**：`source_type=model-prior` 的条目，`verified_online` 必须为 `false`、`provenance` 必须写成 `model-prior(no online hit: <原因>)`、**且 `evidence_level` 只能是 `prior`**，永远不得携带 DOI/COD 号。`channel=structure` 的条目 `verified_online=true` 的前提是 `self_verified=true`（化学式回验通过）。

## 四、通道执行流程

### 通道① 文献（快查数值 + 免费全文 + 深度综合复用）
1. 从任务里抽出「需要文献接地的方法学/数值问题」列表。
2. **先把问题拆成检索要素再跑脚本**：`--entities` 填目标体系名（如 `glycine,polymorph`），`--methods` 填方法与实验手段（如 `GIPAW,chemical shift,solid-state NMR`）。脚本据此自动分解出多条 ≤4 词子查询并行打 OpenAlex，并与 Europe PMC / arXiv **并行**检索后合并去重（EPMC 不再是「OpenAlex 返空才兜底」的死代码）。
   > **不要把整句任务描述当一条查询串塞进去**：OpenAlex 的 `search=<长串>` 是全字段逐词 AND，实测 14 词长串只返回 count=2 且头部全不对题；拆成子查询走 `filter=title_and_abstract.search:` 后同一语料 count=370、头部即靶心。
3. 脚本内置**四档相关性门**（核心实体词/强方法词加权计分，宽泛词如 NMR/DFT 不计分）与**客观 `domain_match`**（只看词落在 title 还是 abstract，附 `domain_match_basis`）。未过门（`relevance=low`）的条目**不进下载队列**——这修掉了旧版「只要 is_oa 就下载」使量子计算综述、缪子探测器论文占满 `online_kb` 与 `--oa-limit` 名额的问题。四档含义（写在每条的 `relevance` 字段）：
   | `relevance` | 判据 | 对下游的意义 |
   | --- | --- | --- |
   | `anchor` | 锚定实体（`--entities` 第一个词）命中 **且** ≥1 个方法词命中 | 直接对题，可判 `exact`，下载名额第一优先 |
   | `method-only` | 锚定实体未命中，但 ≥2 个强方法词命中 | 方法学参考（怎么做/精度多少），`domain_match` 封顶 `adjacent` |
   | `entity-only` | 锚定实体命中但**零方法词** | 同物质、不同问题（如问谱学时命中的「Interstellar Glycine」），封顶 `adjacent`，排在 `method-only` 之后 |
   | `low` / `low-fallback` | 以上都不满足 | 丢弃；仅当门把全部命中挡下时 fail-safe 回退保留最高分 5 条，**绝不可当证据用** |
   > `entity-only` 只降优先级、**不踢出池子**：当任务问的是晶型结构而非谱学时，「Crystal growth of α and γ glycine polymorphs」这类零方法词命中的结晶学文献恰恰是靶心。判档只看词面命中，**上层不要自行改判**。
4. 加 `--with-arxiv`：arXiv 走 `abs:"X" AND abs:"Y" AND (cat:… OR cat:…)` 布尔检索（**绝不用 `all:<裸串>`**，实测裸串返回大量跳领域噪声）。缺 PDF 直链的 DOI 会走 **Unpaywall** 补查（机构库/预印本合法 OA 版）：补查在相关性门**之后**按相关性顺序消耗预算（`--unpaywall-limit`，默认 20，`--no-unpaywall` 可关），不浪费在将被丢弃的噪声上；用量与预算写在输出的 `paywall.unpaywall_tried` / `unpaywall_budget`。Unpaywall 必须带 email 参数（实测空值 422），未设 `ONESCIENCE_CONTACT_EMAIL` 时脚本自动用中性占位，输出以 `paywall.unpaywall_email_source=placeholder` 标明**用的是占位而非你的邮箱**（不影响能否查到）。green OA 常只给到仓储落地页而无 PDF，此时 Unpaywall 也可能查不到直链——**这是付费墙成立，不是脚本故障**。
5. 加 `--fetch-oa`：**只对通过相关性门的条目**下载 PDF 并抽全文（**只有真抽出文本**才升 `full-text-oa`；PDF 下载成功但本机缺 pymupdf/pdfminer 时停在 `abstract` 并在 `note` 里说明，`oa_fulltext_count` 随之为 0 并触发 `caveat_fulltext`——抽不出文本就当没拿到全文，绝不高标）。名额严格按 `relevance` 档位 > `domain_match` > 被引数排序消耗，`low`/`low-fallback` 永不下载。**不要按被引数判断谁更该下载**：实测 `entity-only` 档的「Interstellar Glycine」(cited=377)、「glycine receptor signalling」(cited=100) 会靠高被引抢光全部名额，而 cited=1~12 的 NMR crystallography、周期 DFT ¹³C shielding 精度等方法学文献一篇都下不到。
6. 靶心文献被付费墙挡住时加 `--citing-oa`：走 OpenAlex 施引反查（`filter=cites:W…,is_oa:true`）找**开放获取的下游文献**承载同一数值。实测两篇 closed 靶心分别给出 8 / 17 篇 OA 施引文献（含 ¹³C shielding tensors、NMR crystallography 专题）。**付费墙仍然成立：拿不到合法 OA 版的如实停在 `abstract`，绝不绕墙。**
7. 需要 PMC 系全文细节时：复用 `onescience-live-literature` 的命令块 B（Europe PMC fullTextXML → NCBI BioC）。`evidence_level=abstract-only` 的条目**禁止**作为数值来源。
8. 每条接地数值写 `items[]`：`channel=literature`，`provenance=<DOI/编号>`，`evidence_level=full-text-oa|full-text|abstract`，`domain_match` 沿用脚本判定值并原样带上 `domain_match_basis`。
9. **数值型知识（如具体 ppm）不要指望文献通道兜底**：全文拿不到就如实标 `knowledge_gap`、改走通道②/③ 的数据源，或标带 `⚠` 的先验值，**绝不无出处默写**。
10. **读完内容层再落参数（必经）**：stdout 的 `top[]` 默认附 `abs`（摘要正文，条数由 `--abstract-top` 控制，默认 5，且只从确实带摘要的条目里选；`--abstract-chars` 默认 600 字符）与 `abs_nums`（摘要中带单位的数值，如 `873K`/`513MPa`/`3.5meV`）。**每个写进交付的数值必须能指到 `abs`/`abs_nums`、全文或数据库记录三者之一**；只有题录时不许据此推参数。带出的摘要仍是 `evidence_level=abstract`：可作方法学与量级依据，不等于全文精度，需要更细的数值仍要 `--fetch-oa`。要回到旧的精简输出用 `--abstract-top 0`。

### 通道② 结构 / 物质数据（本技能新增核心能力）
运行 `scripts/structure_fetch.py`（详见第六节命令块）。内部逻辑：
1. **在线发现为默认主路**：给定化学式即走 COD 的正确检索姿势（GET `result.php?formula=<Hill 式带空格 URL 编码>` 建立 `CODSESSION` → `result.php?format=lst&CODSESSION=...` 拿纯编号列表），得到**候选编号列表**。裸 `chemical_name=`/猜编号会被 COD 忽略或返回错条目，必须走这条路。
2. **锚点表仅作兜底**：在线发现为空（多为端点不可达/离线）时才查 `assets/cod_anchors.json`（已核实物质→编号缓存），且同样要过回验——锚点是加速缓存，不是数据源头。
3. **按号下载 CIF**：`https://www.crystallography.net/cod/<id>.cif`（此路已实测稳定 200）。
4. **化学式回验（不可跳过）**：解析下载 CIF 的 `_chemical_formula_sum`，与目标化学式做**元素计数归一化比对**；不一致 → 判为「编号错配」，丢弃、试下一个候选；连续不匹配则进第 6 步先验兜底。
5. **成功产出**：回验通过 → 抽取晶格参数、空间群、分数坐标，写 `items[]`：`channel=structure`、`source_type=database`、`provenance=COD:<id>`、`evidence_level=db-record`、`verified_online=true`、`self_verified=true`，并把 CIF 落地到工作目录供下游生成 POSCAR。
6. **全候选失败**：写 `items[]`：`source_type=model-prior`、`verified_online=false`、`note="COD 检索/回验未命中"`，坐标可给先验值但必须带 `⚠ 未经在线核实`，并记进 `harvest_seed.gaps` 供后续补锚点。

### 通道③ 软件参数（内置参考表 + 在线 wiki 核对）
运行 `scripts/param_lookup.py --software <SW> --calc <类型> --live`（读 `assets/` 参数表 + 实时核对）。
1. 按软件栈（VASP/QE/CASTEP）+ 计算类型（opt/NMR-GIPAW/elastic…）从 `assets/param_reference.json` 取**推荐参数与出处**。
2. **推荐加 `--live`**：逐标签实时抓 VASP 官方 wiki 页面并摘录定义段，命中项升为 `verified_online=true`、出处写 `software-doc:vasp-wiki:<TAG>` 并附 `wiki_url`；抓不到自动退回静态表并如实标注，不阻断。
3. 写 `items[]`：`channel=software-param`、`source_type=software-doc`、`provenance=software-doc:<标识>`、`evidence_level=curated-ref`，**不写 DOI**。

## 五、与 orchestrator / primitives 的衔接

- primitives 本地召回到 `none/task_only` → orchestrator 步骤判定 `knowledge_gap=true` → **硬路由本技能**补在线证据。
- 本技能回传 `online_knowledge.json`，其中：
  - `verified_online=true` 的条目 → 下游可直接作为承重参数，引用其 `provenance`。
  - `source_type=model-prior` 的条目 → 下游可继续用（不停摆），但在方案/报告里**必须原样保留 `⚠ 未经在线核实` 标注**，不得升格为「来自文献/数据库」。
- 本技能**不做**：不写卡片库、不提交作业、不执行计算——只交付「带出处的证据对象 + 先验兜底」。

## 六、命令块

> 均为纯标准库（urllib），网络不可用时捕获异常打 `[OFFLINE]` 后正常退出。脚本随技能置于 `scripts/`，参数表置于 `assets/`。
>
> **必须 `python3`**：脚本依赖 `http.client` 等 Python 3 标准库；HPC 站点的 `python` 常指向 Python 2，
> 首调即崩在 `ImportError: No module named http.client`（实测两个会话各白烧一次调用才换 `python3`）。
>
> **OpenAlex 配额与 429 的真实成因**：现为 credits 制——list 检索每次 10 credits，免费档 100,000 credits/天
> 且 ≤100 req/s，超出即 `HTTP 429`。**`mailto` 只决定进 polite pool（响应更稳定）、不提高配额**；额度杠杆是
> 免费 API key（官方：日额度 ×10）。无 key 时额度按**出口 IP** 归属，集群共享 NAT 出口下会同 IP 互相耗尽——
> 实测同一台机器相隔 3 小时从 0 次 429 变成连续 429，**与检索式与相关性门都无关**。邮箱与 key 只从环境变量读，
> 不硬编也不走命令行（命令行会进 `ps` 与 shell 历史）：`ONESCIENCE_CONTACT_EMAIL`、`OPENALEX_API_KEY`（额度 ×10）。
> 不设邮箱时的实测行为：OpenAlex **不带 mailto 走匿名池、照常出数**（本机实测 `count=16`）；Unpaywall
> 自动改用中性占位邮箱继续工作（实测 `email=""` 会被 422 拒、占位值 200），**两条通道都不因缺配置而失效**。
> 连续 429 时应如实记 `knowledge_gap` 并改走数据/参数通道，不要反复重跑同一检索式。

**A · 文献检索（多子查询 + 三源并行 + 相关性门 + 免费全文降级链）**（详见 `scripts/lit_search.py`）
```bash
# 基本快查（自动分解子查询 + OpenAlex/EuropePMC 并行 + 相关性门）：
python3 scripts/lit_search.py "glycine 13C 15N chemical shift GIPAW" \
    --entities "glycine,polymorph" --methods "GIPAW,chemical shift,solid-state NMR" --max 12 --top 12

# 全量推荐：arXiv 布尔 + Unpaywall + OA 全文下载 + 付费墙靶心的施引反查 + 年份下限：
python3 scripts/lit_search.py "glycine polymorph alpha gamma 13C 15N solid-state NMR chemical shift GIPAW DFT" \
    --entities "glycine,polymorph" \
    --methods "GIPAW,chemical shift,magnetic shielding,solid-state NMR,DFT" \
    --with-arxiv --fetch-oa --oa-limit 5 --citing-oa --year-from 1990 \
    --max 10 --top 14 --workdir ./online_kb

# 检索式自己控（| 分隔多条，每条 ≤4 词）：
python3 scripts/lit_search.py "glycine GIPAW" --sub-queries "glycine GIPAW|glycine NMR chemical shift|polymorph magnetic shielding"
```
> 输出条数用 `--top N` 控制，**不要用 shell `head`/`tail` 再截**（截断会使上层看不到 `domain_match_summary`/`caveat` 而误判）。完整结果始终落在 `<workdir>/lit_result.json`。脚本输出的 `domain_match_summary` 可直接抄进 `gaps.jsonl`，无需自行点数。

**B · 结构取数**（详见 `scripts/structure_fetch.py`）
```bash
# 只给化学式即可自动发现真编号（走 COD session 握手 + format=lst + 化学式回验）：
python3 scripts/structure_fetch.py --name glycine --formula C2H5NO2 --workdir ./online_kb
# 直接指定已核实编号：
python3 scripts/structure_fetch.py --cod-id 1556577 --formula C2H5NO2 --workdir ./online_kb
```

**C · 软件参数**（详见 `scripts/param_lookup.py`）
```bash
# 静态表基线：
python3 scripts/param_lookup.py --software VASP --calc NMR-GIPAW
# 推荐：加 --live 实时抓 VASP wiki 核对（失败自动退静态表）：
python3 scripts/param_lookup.py --software VASP --calc NMR-GIPAW --live --workdir ./online_kb
```

**D · 引用溯源自检（终稿交付前必跑，把铁律 1 变成可机判断言）**（详见 `scripts/check_provenance.py`）
```bash
# 把终稿里的 DOI / COD 号 / arXiv / PDB / UniProt 标识符与本轮工具产出做集合差：
python3 scripts/check_provenance.py --answer ./answer.md --workdir ./online_kb
# 退出码：0=全部可溯源或已如实标注先验；2=存在 violation（无工具回执且未标先验）——必须修正
# 可选：--strict（已标先验也计违规）/ --evidence <工具输出转储> / --allow-selfauthored（慎用的自写文件纳入）
```

## 七、纪律铁律（自检清单）

1. 承重数值先在线取，取不到才用先验；先验必标 `⚠ 未经在线核实`，绝不冒充 [n] 或 COD 出处。
2. 结构坐标只来自「回验通过的 CIF」或「显式先验」两条路，杜绝无标注默写。
3. 每次下载 CIF 必做化学式回验；回验不符当错误处理，换候选，绝不将错就错。
4. 软件参数走 software-doc 出处，不强凑论文引用。
5. 缺任何一类知识都**不 blocked**——降级为带标注先验继续跑；如实标注即可。
6. 网络异常 → `[OFFLINE]` + 如实标注 + 正常退出，绝不崩溃中断上层。
7. 输出统一走 `online_knowledge.json` schema，字段齐全（source_type / evidence_level / verified_online / self_verified / provenance）。
8. `domain_match` 以脚本给出的客观判定为准（看 `domain_match_basis`）：上层**只能改严（exact→adjacent）不得改松**；`gaps.jsonl` 的 `domain_match_summary` 直接抄脚本输出的同名字段，不得自行点数。
9. `evidence_level=abstract-only` 的文献**禁止承载任何数值**；缺数值就如实标 `knowledge_gap` 或走带 `⚠` 的先验值，绝不无出处默写。
10. 交付前逐条自检：这条真值是哪来的？在线的有没有出处？先验的有没有 `⚠` 标注且没赖给文献？
11. **可机判版铁律 1**：终稿交付前必跑 `scripts/check_provenance.py`——每个具体标识符要么逐字见于本轮工具证据（`lit_result.json`/`structure_result.json`/`param_result.json`/回验 CIF），要么**同一行**标为模型先验；退出码 2 未修而交付即协议错误。自己写的 `online_knowledge.json` 不构成出处（循环论证）。
