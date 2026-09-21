---
name: onescience-knowledge-harvester
description: OneScience 知识缺口自动填补技能。当用户描述缺少某领域知识（如"缺少藏红花基因衍生推理的知识"）时，自动执行：文献检索 → 知识抽取 → 卡片生成 → 入库决策（new/modify/merge，相似知识归并同一张卡）→ 写入 onescience-primitives，使后续 OneScience 推理任务可召回这些知识卡片。论文证据为主体；附开源权威文档与用户自有数据两个低优先级补充通道。全程使用智能体原生能力（网络搜索、LLM 推理、文件操作），不依赖外部流水线或额外 API Key。触发词：缺少知识、补充知识、填补知识缺口、自动采集知识、harvest knowledge。
type: executor
---

# OneScience Knowledge Harvester

你是 OneScience 的知识缺口自动填补执行技能。你的职责是把用户描述的知识缺口转换成可被 onescience-primitives 召回的知识卡片。

**核心原则**：全程使用智能体原生能力（WebSearch、WebFetch、LLM 推理、Write），不依赖外部流水线或额外 API Key。

**证据主体**：论文证据（full-text/abstract）是卡片价值的主体；开源权威文档与用户自有数据是低优先级补充通道，只用于论文通道覆盖不到的残余缺口，且必须通过权威性与溯源门禁（见 Step 3.4–3.6）。

## 触发场景

使用本技能处理以下请求：

- "缺少藏红花基因衍生推理的知识"
- "帮我补充关于 X 的知识"
- "填补 X 领域的知识缺口"
- "自动采集 X 相关的论文知识"
- "我需要 X 方面的知识卡片"
- 任何描述知识缺口并要求自动填补的请求

不要在以下情况下自动触发：

- 用户只要求检索已有知识（那是 onescience-primitives 的职责）
- 用户只要求实时文献推理（那是 onescience-live-literature 的职责）
- 用户只要求沉淀交互经验（那是 onescience-knowledge-capture 的职责）

## 核心边界

1. 本技能是知识采集的执行层，使用智能体原生能力完成全流程。
2. 生成的卡片必须符合 onescience-primitives 的格式规范（metadata.json + knowledge.md）。
3. 卡片核心内容必须基于实际检索到的论文证据，不得编造；补充通道（开源文档/用户数据）证据必须有权威出处或用户背书，见 Step 3.4–3.6。
4. 不修改 onescience-primitives 的 SKILL.md；对已有卡片只允许按 Step 4.5/Step 5 的三态入库（new/modify/merge），且必须通过单调性校验，不得删除内容或卡片目录。
5. 生成的卡片按 Step 1 判定的 `card_type` 落盘到对应类目 `skills/onescience-primitives/assets/<domain>/<category>/<name>/`；**不得默认把所有卡都写到 `workflow-planning/`**——该类目仅承载跨领域的通用方法论卡，且被 onescience-primitives 契约禁止用于回答具体科学问题（详见 Step 1 类目选择表与「禁止事项」）。

## 执行流程

### Step 1 解析知识缺口

从用户输入中提取：

- **gap_description**：知识缺口的自然语言描述（如"藏红花基因衍生推理"）
- **domain**：领域（bio/matchem/climate/cfd/general），从描述中自动检测
- **search_queries**：2~4 组英文检索词（含同义词、物种学名、基因/酶/通路名、方法名）
- **card_identity**：卡片身份层级。内部先做一步抽象推理：这个缺口来自哪个具体场景 → 该场景属于哪一类通用问题（用一句自然语言描述，如"面向目标气体，选择或设计满足容量、选择性与再生能耗要求的捕集材料"）→ 该问题的解法能否迁移到同类其他体系。能迁移 → 卡片身份 = 通用问题类（生成通用类卡）；缺口只是单一实例事实、无可迁移方法层 → 不强行升维，卡片身份 = 实例级。**这条推理链只用于确定卡片身份，严禁以任何形式出现在卡片产物中**（见 Step 4 通用类卡撰写规范）。
- **card_type + category**（硬门禁，决定落盘类目与 metadata.type）：按缺口性质从下表选择**唯一**类型，不得默认落到 `workflow-planning`。判定证据（缺口关键词/归因报告 issues 类型/所需产物形态）必须写入 execution_result.observation.type_rationale。

**card_type 选择表（按优先级从上到下匹配，命中即停）**：

| 缺口性质 | card_type | category（落盘目录） | 命中示例 |
|---|---|---|---|
| 具体领域的**任务级** know-how：某类计算/实验/分析任务的做法、参数、验收 | `task` | `<domain>/tasks/` | "CO2 在 MOF 上的 GCMC 吸附等温线计算"、"RNA-seq 差异表达分析" |
| 具体领域的**场景级** know-how：一个完整科研场景的问题设定、判据、边界 | `scenario` | `<domain>/scenario/` | "面对含湿烟道气的 CO2 捕集材料筛选"、"MW 级电池热失控预警" |
| 具体领域的**工作流级** know-how：多个 task 的编排序列、依赖、数据流 | `workflow` | `<domain>/workflow/` | "DFT→机器学习势→MD 的跨尺度工作流" |
| 具体的**资源实体**：模型、数据集、工具、组件、数据库、服务、应用、可视化、契约、输出格式 | `model` / `dataset` / `tool` / `component` / `database` / `service` / `application` / `visualization` / `contract` / `output-format` | 对应同名目录 `<domain>/<category>/` | "MACE-MP-0 势"、"Materials Project API"、"pymatgen 结构分析工具" |
| **跨领域**的通用方法论：科研规划、通用方法族、通用建模流程、通用筛选策略 | `workflow-planning` | `<domain>/workflow-planning/` | "面向任意目标气体的捕集材料筛选方法论"、"通用 CLI 故障分类" |

**判定原则**：
- 缺口若指向**具体领域实体**（材料/物种/反应/现象/仪器），一律落到 task/scenario/workflow/resource 层；workflow-planning **只能**承载"跨领域通用方法论"，且必须能通过"把领域实体换成其他领域后卡片仍然成立"的反例测试。
- 归因报告 issues 里若已明确指向具体 step / 具体资源 / 具体任务失败，card_type 必须与该 issue 层级对齐，不得上提到 workflow-planning。
- 判定不确定时**默认落 task**（不是 workflow-planning）——task 层缺口最常见，且能被 TC 五级链正常引用。
- 一次知识补充可产多张卡，每张卡独立判 card_type；不得把整个 bundle 强行统一到同一 type。

**领域检测规则**：
- 含"基因/蛋白/生物/序列/细胞/组学/藏红花/saffron/gene/protein" → bio
- 含"材料/分子/晶体/化学/催化/电池/MXene/material/molecule" → matchem
- 含"气象/气候/天气/降水/温度/台风/预报/climate/weather" → climate
- 含"流体/流场/空气动力/涡/网格/CFD/fluid/turbulence" → cfd
- 其他 → general

**实时汇报**：`🔄 Step 1：解析知识缺口...`

### Step 2 文献检索（OpenAlex + WebSearch 混合）

**优先使用 OpenAlex API**（更精准、可控），WebSearch 作为补充。

#### 2.1 OpenAlex 检索（命令块 A）

把 `references/lit_search.py` 模板落盘为会话临时脚本并执行：

```bash
python lit_search.py "<query>" <max_papers> <year_from> pool.json
```

- 检索走 OpenAlex works 接口，**相关性排序**（search 默认）+ `from_publication_date` 过滤
- 输出：终端打印编号摘要行；并把条目追加进 pool.json（**按 DOI/标题去重**）
- 条目字段：title / authors / venue / year / doi / oa_url / cited / abstract（前 400 字）

#### 2.2 迭代精炼（对齐 Biomni 的第二轮检索）

通读池内摘要，抽出实体词（基因名、酶名、物种名、通路名、方法名），组成 1~2 组**新**检索词再跑命令块 A，编号续接。**至少迭代一轮**。

#### 2.3 新颖性扫描（每会话强制至少一轮）

相关性排序会系统性埋没刚发表、引用少的新论文。必须至少跑一轮 `year_from = 当年-1` 的检索，专门捕捉最新发现。

#### 2.4 WebSearch 补充

对 OpenAlex 未覆盖的来源（Google Scholar、bioRxiv 预印本），用 WebSearch 补充。

**实时汇报**：`🔄 Step 2：检索相关论文...（已找到 N 篇，池大小 M）`

### Step 3 知识抽取（全文抓取 + LLM 推理）

#### 3.1 全文抓取（命令块 B）

从池中挑 **4~8 篇**与推理链最相关的论文，把 `references/lit_fetch.py` 模板落盘为会话临时脚本并执行：

```bash
python lit_fetch.py <outdir> --keys "<领域关键词逗号分隔>" <doi1> <doi2> ...
```

内置双通道（均实测）：
- Europe PMC REST（DOI→pmcid→fullTextXML）
- NCBI pmcoa BioC JSON（Europe PMC 404 时兜底）
- 双通道失败 = abstract-only

**控制台输出只是索引**。对每篇全文成功的论文，必须用 Read 工具**分段读取落盘文件** `<outdir>/<doi_slug>.txt` 的完整内容提取细节。

#### 3.2 LLM 知识抽取

从论文中抽取：
- 核心方法/技术
- 关键参数/数值（浓度、滴度、同一性%、基因拷贝数、温度等）
- 输入/输出契约
- 流程步骤
- 边界条件/限制
- 质量检查点

#### 3.3 推理链环节审计（拦截跨事实拼接幻觉）

每一条因果/演化断言——"A 催化 B""突变 M 驱动了功能 F"——所挂的证据必须在**同一篇文献内直接**支持该断言。若断言是把多篇论文拼接而成，必须标"(跨文献推断: [a]+[b]，无单篇直接证据)"。

**抽取原则**：
- 只抽取论文中明确陈述的事实，不得编造
- 数值必须来自论文原文，不得凭记忆补写
- 每条知识必须绑定到具体证据

#### 3.4 补充通道 A：开源权威文档（低优先级）

**触发条件**：论文主路（2.1–3.3）完成后仍存在残余缺口（关键参数/流程节点无论文证据），或用户显式要求参考开源文档；论文通道已覆盖时不启动，避免稀释主路。

**权威白名单（仅允许采集）**：
- 官方项目文档（官网 / docs 子域 / 官方手册 PDF）
- 标准组织文档（ISO、ASTM、GB、IEEE、IUPAC 等）
- 政府与公共机构库（NCBI、NOAA、NASA、CDC、EMEA 等）
- 大学官方讲义 / 实验手册
- 官方 GitHub 组织的 README / releases / docs

**权威黑名单（禁止采集）**：个人博客、内容农场与转载站、无日期页面、厂商营销页、AI 生成内容站、真实性不明的论坛帖子。

**交叉验证**：关键事实（数值、阈值、命令、参数）须 ≥2 个独立权威来源一致陈述，或与池内论文证据互证不冲突；单源事实只能以"参考级"写入并标注来源。

**溯源**：每条记录 url、publisher、版本号或发布日期、accessed_at，写入 metadata.evidence_docs；无版本信息的文档视为低置信。

#### 3.5 补充通道 B：用户自有数据（低优先级，仅被动）

- 只消费用户在会话中显式附带或指定路径的数据；禁止主动爬取用户目录。
- 入库前做脱敏扫描（对齐 onescience-knowledge-capture 的校验规则：API key、Bearer token、密码、私钥、云凭证、JWT）；命中即剔除该部分并汇报。
- 溯源：记录 provider、provided_at、文件路径或描述，写入 metadata.evidence_user。
- 该通道事实在正文一律标注"(用户自有, 未经公开源验证)"；若与论文/权威文档证据互证不冲突，可标注"(用户自有, 经[n]佐证)"。

#### 3.6 证据价值分级与冲突裁决（全局约束）

价值排序：论文 full-text > 论文 abstract > 权威文档(交叉验证) > 权威文档(单源参考) > 用户自有(经佐证) > 用户自有(未验证)。

- 卡片核心骨架（流程节点、关键参数表主体）必须基于论文证据；补充通道事实只能进入"补充证据"章节或在关键参数表追加行并标注来源层级。
- 补充通道事实与论文证据冲突时：论文优先，冲突写入 metadata.conflicts 待人工裁决，禁止覆盖。
- 补充通道检索失败或零命中：汇报原因后跳过，不阻塞主流程。

**实时汇报**：`🔄 Step 3：从 N 篇论文中抽取知识...（全文级 X 篇，摘要级 Y 篇；补充通道：文档 D 条/用户 U 条）`

### Step 4 卡片生成

将抽取的知识组织成知识卡片：

**证据编号**：论文 `[1]..[n]`、开源文档 `[D1]..`、用户自有 `[U1]..`，三套编号独立不混排。

**卡片目录结构**（`<category>` 由 Step 1 判定的 card_type 决定，见选择表）：
```
skills/onescience-primitives/assets/<domain>/<category>/<card-name>/
  metadata.json
  knowledge.md
```

**metadata.json 格式**（固定 9 字段 + harvested 标记；`type` 必须等于 Step 1 判定的 card_type，`<category>` 必须与 type 对齐）：
```json
{
  "name": "<card-name>",
  "type": "<task|scenario|workflow|model|dataset|tool|component|database|service|application|visualization|contract|output-format|workflow-planning>",
  "domain": "<bio|matchem|climate|cfd|general>",
  "version": "1.0.0",
  "visibility": "public",
  "created_at": "<ISO日期>",
  "updated_at": "<ISO日期>",
  "description": "<信息密集的描述；通用类卡以需求级开头（面向目标X，做Y、满足Z），实例词只出现在校准数值/证据体系从句>",
  "tags": ["<tag1>", "<tag2>", ...],
  "aliases": ["<实例别名，纯字符串数组，仅用于召回（可选）>"],
  "harvested": true,
  "harvest_source": "onescience-knowledge-harvester",
  "harvest_query": "<原始知识缺口描述>",
  "evidence_papers": [
    {"title": "<论文标题>", "doi": "<DOI>", "year": <年份>}
  ],
  "evidence_docs": [
    {"title": "<文档标题>", "url": "<URL>", "publisher": "<发布机构>", "version": "<版本或发布日期>", "accessed_at": "<ISO日期>"}
  ],
  "evidence_user": [
    {"provider": "user", "provided_at": "<ISO日期>", "location": "<路径或描述>"}
  ],
  "merged_batches": ["<批次标识，每次 modify/merge 追加一条>"],
  "conflicts": ["<补充证据与论文证据的待裁决冲突描述>"]
}
```

aliases 与后四个字段均为可选：aliases 是实例别名数组（如具体分子式、材料牌号、体系俗称），只用于提高实例词查询的召回率，不参与身份面表达；evidence_docs/evidence_user/merged_batches/conflicts 在存在补充通道证据或发生 modify/merge 时才写入。细则见 `references/card_format.md`。

**knowledge.md 格式**（灵活单文档，推荐章节）：
```markdown
# <卡片标题>

## 适用范围
<触发条件、适用场景、不适用场景>

## 输入
<输入数据格式、来源、预处理要求>

## 输出
<输出产物、格式、验证标准>

## 流程节点
<步骤1> → <步骤2> → ...
每步含：操作、参数、工具、质量门禁

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| ... | ... | [论文N] | ... |

## 边界与分流
<异常处理、降级策略、分支条件>

## 质量检查
<验证点、阈值、失败处理>

## 回退策略
<失败时的替代方案>

## 资源召回建议
<何时应召回本卡片、配套资源>

## 补充证据（开源文档/用户自有，可选）
[D1] <文档标题>, <发布机构>, <版本/日期>, URL: <url>（accessed_at，交叉验证/单源参考）
[U1] <用户自有数据描述>, <provided_at>（用户自有, 未经公开源验证）

## 证据来源
[1] <论文标题>, <作者>, <期刊>, <年份>, DOI: <DOI>
[2] ...
```

**通用类卡撰写规范（硬门禁）**——card_identity 为通用问题类的卡片必须全部满足：

1. **自然散文身份**："适用范围"节以自然散文开场，陈述本卡服务的问题类（面向什么对象、做什么事、满足什么要求），读者一眼能看出卡为哪类任务服务；不得以具体实例场景开场。
2. **脚手架词零出现**：全文（含 metadata 的 description/harvest_query）严禁出现："具体场景""上层需求""本卡解决""槽位""槽位迁移""迁移矩阵""复用协议""抽象层级""升维"。生成期的抽象推理链不得在产物中留下任何痕迹。
3. **具体体系只出现在四个自然位置**：a) 流程节点中的例句（"以 X 体系为例，……"）；b) 校准数值表的引语；c) 术语/同义词表的举例引语；d) metadata 的 aliases/tags（仅供召回，读者不可见）。
4. **通用论断主句通用**：前提与判据句的主句必须是问题类级的通用陈述，证据用引用编号挂靠句尾；严禁把具体实例塞进前提清单的括号里当例证。
5. **参数分表**："关键参数"节分两张表——通用判据（方法层，同类体系可参考，逐条带证据编号）与校准数值（体系专属值，引语写明"以下数值来自 X 体系，供量级校准；其他体系需以自身证据重新锚定"）。
6. **前提否定即改道**："边界与分流"节须写明每条关键前提不成立时转向哪类方案族（改道目标属领域知识，不得编造具体参数）。

**卡片命名规则**：
- 使用 kebab-case，长度不超过 80 字符
- 名称与卡片身份层级一致：
  - **通用类卡**：`<domain>-<问题类>-<方案/交付物>`（如 `matchem-gas-capture-material-design-validation`），**不得含实例分子/材料/模型专名**（如 co2、saffron、mxene）
  - **实例级卡**：`<domain>-<topic>-<method>`（如 `bio-saffron-gene-derivative-reasoning`），可含实体名
- **零信息目录名一律禁止**（不限领域、不限卡片类型）：哈希 id（`it-01684b6f`、`tk-bio-9a8b7c6d`）、裸占位词（`card`、`task`）、场景编号骨架（`cfd-s001-workflow`）、中文/空格名均不合格；拿不出语义名就回到卡片内容重取名，**不得用 id 或哈希后缀防撞名**（细则与反例表见 `./references/card_format.md`“禁止清单”）
- 定名前自检：`python validate_knowledge.py --names-only --quiet` 必须 `RESULT: PASS`

**实时汇报**：`🔄 Step 4：生成知识卡片...`

### Step 4.5 入库决策（new / modify / merge）

写入前必须先与已有卡片比对，决定入库方式，避免相似知识产生重复卡：

1. **枚举**：Glob `skills/onescience-primitives/assets/<domain>/**/metadata.json`，只把 `type == <本次 card_type>` 的卡作为 modify/merge 候选（跨类型不得互相吞并：task 卡不 merge 进 workflow-planning，反之亦然；resource 类卡按同名 category 过滤）；候选超过 20 张时先按"与候选卡 tags 交集 ≥2 或 description 命中缺口实体词"初筛，再逐张 Read 候选卡 metadata（description/tags）。
2. **判定**（对最佳候选卡依次回答三问）：
   - a. 同身份层级且同对象：两卡同为通用类卡且属同一问题类（同需求、同方法族），或同为实例级卡且同目标实体（同物种/材料/体系/研究对象）？一为类级、一为实例级 → 视为不同对象（类卡给方法论、实例卡给事实，职责不同不得互相吞并）。
   - b. 同任务目标（同 workflow 目的）？
   - c. 内容重合：候选卡关键章节/参数与本次抽取重合过半，或 tags Jaccard ≥ 0.5？
   - a∧b∧c → **modify**：原位升级该卡——用新证据更新参数/步骤，被替换的旧值保留为"历史值"注记，version 升 minor。
   - a∧b∧¬c → **merge**：相似知识归并同一张卡——把本次新知识以"批次补充"节追加到该卡 knowledge.md 末尾，metadata 做并集（tags 取并、evidence 追加、merged_batches 加一条），不新建目录。
   - a∧¬b，或跨身份层级（一类级一实例级）→ **new**，且在两张卡的"资源召回建议"中互相引用（类卡指向实例专卡作为证据锚点，实例卡指向类卡作为方法论框架）。
   - 全否或判定不确定 → **new**（默认，与旧版行为一致）。
3. **边界**：两张已存在旧卡之间的合并不在本技能执行范围，只在 observation.next_recommendation 中输出归并建议。
4. 决策与理由写入 execution_result.artifacts.ingest_decision。

**实时汇报**：`🔄 Step 4.5：入库决策...（action=new|modify|merge，target=<卡名或无>）`

### Step 5 写入文件系统

按 Step 4.5 的决策执行：

**new**：
1. 创建目录：`skills/onescience-primitives/assets/<domain>/<category>/<card-name>/`（`<category>` 由 Step 1 card_type 决定，不得硬编码 workflow-planning）
2. 写入 `metadata.json` 与 `knowledge.md`
3. 验证文件存在且格式正确，且 `metadata.type` 与目录 `<category>` 一致

**modify / merge**：
1. 写前 Read 旧 `knowledge.md` 与旧 `metadata.json` 全文；新内容 = 旧内容全量保留 + 增量更新（modify）或末尾追加补充节（merge）。
2. 写回后必须通过**单调性校验**（任一不通过 → 放弃本次 modify/merge，回退为 new，并在汇报中说明原因）：
   - 旧 knowledge.md 的 `## ` 标题集合 ⊆ 新标题集合；
   - 新 knowledge.md 字符数 ≥ 旧字符数；
   - 旧 tags ⊆ 新 tags；旧 evidence_papers 条目逐条保留（只增不删）；
   - 旧数值事实全部保留在新正文中，或转为"历史值"注记，禁止静默删除。
3. metadata 更新：updated_at、version 升 minor、merged_batches 追加、evidence 字段取并集；description 只允许扩写、必须保留原有全部实体词。
4. 禁止删除任何卡片目录或文件。

**实时汇报**：`🔄 Step 5：写入卡片到 onescience-primitives...（action=<new|modify|merge>）`

### Step 6 验证召回

确认生成的卡片可被 onescience-primitives 召回：

1. 用 Glob 搜索 `skills/onescience-primitives/assets/<domain>/**/metadata.json`
2. 确认新卡片在搜索结果中
3. 用 Read 读取 metadata.json，确认 description 和 tags 与知识缺口相关
4. 模拟检索：用 gap_description 作为查询，确认卡片会被语义匹配命中
5. modify/merge 时：用旧卡的原召回词（原 description 首句、原 tags）复查仍能命中该卡，确认旧知识未被挤没
6. 通用类卡：另构造 **≥2 条"同需求换体系"变体查询**（把缺口中的实例实体替换为同类别的其他实体，如 CO2→SO2），模拟检索确认本卡仍能命中；若因 description/tags 被实例词饱和导致变体查询不命中，判定不合格，回 Step 4 重写身份面（而不是往 description 里加更多实例词）

**实时汇报**：`🔄 Step 6：验证卡片可召回性...（原始查询 + N 条变体查询）`

## 输入契约

标准输入是 orchestrator 传入的 `step_handoff`：

```yaml
step_handoff:
  step_id: <步骤ID>
  execution_skill: onescience-knowledge-harvester
  step_goal: <填补指定知识缺口并生成可召回卡片>
  task_context:
    user_goal: <用户最终目标>
    constraints: <约束列表>
    relevant_artifacts: <相关产物路径或摘要>
  inputs:
    knowledge_gap:
      description: <知识缺口描述，必填>
      domain: <bio | matchem | climate | cfd | general，可选>
      max_cards: <最大生成卡片数，默认 3>
      max_papers: <最大检索论文数，默认 10>
    expected_outputs:
      required_files: [metadata.json, knowledge.md]
      cards_required: <true | false>
  resource_bindings: <可选>
  required_outputs: <要求输出>
  completion_criteria: <完成标准>
```

## 输出契约

必须返回：

```yaml
execution_result:
  skill: onescience-knowledge-harvester
  status: success | partial | failed
  artifacts:
    cards_generated:
      total: <生成卡片总数>
      paths:
        - <卡片目录路径列表>
    cards_updated:
      total: <modify/merge 的卡片数>
      actions:
        - {path: <卡片路径>, action: modify | merge}
    ingest_decision:
      action: new | modify | merge
      target: <目标卡名或无>
      reason: <三问判定理由>
    supplementary_evidence:
      docs: <开源文档证据条数>
      user: <用户自有证据条数>
    papers_used:
      total: <使用论文总数>
      references:
        - <论文引用列表>
  observation:
    summary: <采集结果摘要>
    gaps_filled: <已填补的缺口描述>
    quality_notes: <质量说明>
    next_recommendation: <后续建议>
```

没有成功生成任何卡片时，不得返回 `success`。

## 验证要求

完成前必须执行：

1. 生成的卡片目录含 `metadata.json` 和 `knowledge.md`。
2. `metadata.json` 可被标准 JSON 解析，含 `harvested: true` 标记。
3. `knowledge.md` 非空，含推荐章节中的至少 5 个。
4. 用 Glob 确认卡片在 `skills/onescience-primitives/assets/<domain>/` 下可被发现。
5. 卡片内容基于实际检索到的论文证据，每条关键事实有证据来源标注。
6. modify/merge 操作通过 Step 5 单调性校验（标题子集、字符数单调、tags/evidence 只增不删）。
7. 补充通道事实均有溯源（evidence_docs/evidence_user）与正文来源层级标注；未脱敏的用户数据不得出现在任何产物中。
8. 补充证据与论文证据的冲突已写入 metadata.conflicts，未被静默覆盖。
9. 通用类卡：用 Grep 对 knowledge.md 与 metadata.json 自查脚手架禁词（Step 4 规范第 2 条词表）零命中；description 以需求级通用主语开头；通用判据与校准数值分表。

## 禁止事项

- 不得编造论文或知识内容；每条事实必须绑定到检索到的证据（论文/权威文档/用户自有，对应编号）。
- 不得凭记忆补写论文中没有的精确数值。
- 不得修改 onescience-primitives 的 SKILL.md；对已有卡片只允许按 Step 4.5/Step 5 做 modify/merge。
- 不得删除任何卡片目录或文件；不得静默删除旧卡内容、tags、evidence 条目。
- 不得生成空卡片或只有 metadata.json 没有 knowledge.md 的卡片。
- 不得因为检索结果少就降低卡片质量标准；证据不足时如实标注"证据有限"。
- 不得让补充通道证据占据卡片核心骨架（流程节点、关键参数表主体）；论文通道已覆盖同一知识时不得启动文档通道。
- 不得采集权威黑名单来源；不得把未脱敏的用户数据写入卡片。
- 不得把生成期抽象推理链（"具体场景→上层需求→具体方案"）及其元术语写入卡片正文或 metadata。
- 不得让通用类卡的 name/description 被实例分子/材料专名饱和；实例召回词只进 tags/aliases。
- **不得把具体领域缺口（task/scenario/workflow/resource 层）默认落到 `workflow-planning/`**——该类目按 onescience-primitives SKILL.md L198/L206/L542 契约禁止用于回答具体科学问题，误落会导致卡片在召回阶段被 step 9b 判为 `knowledge_gap=true` 直接触发在线兜底，等于本次采集产出对具体问题零贡献。判定不确定时默认落 `task`。
- 不得让 metadata.type 与落盘 category 不一致（如 type=task 却写到 workflow-planning/ 目录）；Step 5 写入前必须自查一致。

## 回归保护条款

- 论文主路协议（Step 2 检索三轮+新颖性扫描、Step 3 全文双通道与分段精读、推理链审计）不被本版本任何条款修改、跳过或替代。
- 入库决策不确定时默认 new：判定异常时本技能的入库行为退化为旧版（纯新增），保证已有召回不受影响。
- 补充通道检索失败或零命中只汇报跳过，不阻塞主流程，不占用论文通道的检索配额。
- 任何 modify/merge 必须通过单调性校验否则回退 new：已有有价值知识不会被本版本逻辑挤没或覆盖。

## 与 onescience-live-literature 的区别

| 维度 | onescience-live-literature | onescience-knowledge-harvester |
|------|---------------------------|-------------------------------|
| 目的 | 实时推理回答 | 生成持久化知识卡片 |
| 输出 | 会话级答案 + seeds.json | metadata.json + knowledge.md |
| 持久性 | 会话结束即消失 | 写入 primitives，可被后续召回 |
| 触发 | 需要跨论文推理的问题 | 描述知识缺口并要求填补 |

## 参考文件

| 文件 | 用途 |
|------|------|
| `./references/card_format.md` | 卡片格式详细规范：metadata.json 字段（含补充证据/merge 扩展字段）、knowledge.md 章节、命名规则、质量门禁 |
| `./references/lit_search.py` | OpenAlex 检索脚本模板（命令块 A） |
| `./references/lit_fetch.py` | 全文抓取脚本模板（命令块 B，Europe PMC + NCBI BioC 双通道） |
| `skills/onescience-primitives/SKILL.md` | 原语召回技能：卡片如何被发现和使用 |
| `skills/onescience-live-literature/SKILL.md` | 实时文献检索：检索策略和命令块原始模板 |
