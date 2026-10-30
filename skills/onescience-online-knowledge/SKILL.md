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
2. 检索：运行 `scripts/lit_search.py "<query>"`（OpenAlex 相关性检索 + Europe PMC 兜底，离线打 `[OFFLINE]`），拿题录+摘要，按 `domain_match` 打标。**OpenAlex 响应自带合法 OA 标记（`is_oa`/`best_oa_location.pdf_url`），不再浪费免费全文线索**。
3. 加 `--with-arxiv` 附加 arXiv API 通道（cond-mat 等计算领域论文大量免费预印本），并对缺 OA 直链的 DOI 做 **Unpaywall** 补查（机构库/预印本合法 OA 版）。
4. 加 `--fetch-oa` 下载有合法 OA 直链的 PDF 并尽力抽取全文文本（本机有 pymupdf/pdfminer 时产出 `*_fulltext.txt`，`evidence_level` 升为 `full-text-oa`；缺库则只落 PDF 如实标注）。**付费墙仍然成立**：拿不到合法 OA 版的如实停在 `abstract`，绝不绕墙。
5. 需要 PMC 系全文细节时：复用 `onescience-live-literature` 的命令块 B（Europe PMC fullTextXML → NCBI BioC），**全文通道全失败的论文只引用摘要级事实并标 `abstract-only`**。
6. 每条接地数值写 `items[]`：`channel=literature`，`provenance=<DOI/编号>`，`evidence_level=full-text-oa|full-text|abstract`。

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

**A · 文献检索（含免费全文线索）**（详见 `scripts/lit_search.py`）
```bash
# 基本快查（题录+摘要+OA 标记）：
python scripts/lit_search.py "glycine 13C 15N chemical shift GIPAW reference compound" --max 20
# 加 arXiv/Unpaywall 免费全文通道，并下载抽取 OA 全文（最多 5 篇）：
python scripts/lit_search.py "glycine GIPAW NMR" --max 12 --with-arxiv --fetch-oa --oa-limit 5 --workdir ./online_kb
```

**B · 结构取数**（详见 `scripts/structure_fetch.py`）
```bash
# 只给化学式即可自动发现真编号（走 COD session 握手 + format=lst + 化学式回验）：
python scripts/structure_fetch.py --name glycine --formula C2H5NO2 --workdir ./online_kb
# 直接指定已核实编号：
python scripts/structure_fetch.py --cod-id 1556577 --formula C2H5NO2 --workdir ./online_kb
```

**C · 软件参数**（详见 `scripts/param_lookup.py`）
```bash
# 静态表基线：
python scripts/param_lookup.py --software VASP --calc NMR-GIPAW
# 推荐：加 --live 实时抓 VASP wiki 核对（失败自动退静态表）：
python scripts/param_lookup.py --software VASP --calc NMR-GIPAW --live --workdir ./online_kb
```

## 七、纪律铁律（自检清单）

1. 承重数值先在线取，取不到才用先验；先验必标 `⚠ 未经在线核实`，绝不冒充 [n] 或 COD 出处。
2. 结构坐标只来自「回验通过的 CIF」或「显式先验」两条路，杜绝无标注默写。
3. 每次下载 CIF 必做化学式回验；回验不符当错误处理，换候选，绝不将错就错。
4. 软件参数走 software-doc 出处，不强凑论文引用。
5. 缺任何一类知识都**不 blocked**——降级为带标注先验继续跑；如实标注即可。
6. 网络异常 → `[OFFLINE]` + 如实标注 + 正常退出，绝不崩溃中断上层。
7. 输出统一走 `online_knowledge.json` schema，字段齐全（source_type / evidence_level / verified_online / self_verified / provenance）。
8. 交付前逐条自检：这条真值是哪来的？在线的有没有出处？先验的有没有 `⚠` 标注且没赖给文献？
