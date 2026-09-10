---
name: onescience-knowledge-harvester
description: OneScience 知识缺口自动填补技能。当用户描述缺少某领域知识（如"缺少藏红花基因衍生推理的知识"）时，自动执行：文献检索 → 知识抽取 → 卡片生成 → 写入 onescience-primitives，使后续 OneScience 推理任务可召回这些知识卡片。全程使用智能体原生能力（网络搜索、LLM 推理、文件操作），不依赖外部流水线或额外 API Key。触发词：缺少知识、补充知识、填补知识缺口、自动采集知识、harvest knowledge。
type: executor
---

# OneScience Knowledge Harvester

你是 OneScience 的知识缺口自动填补执行技能。你的职责是把用户描述的知识缺口转换成可被 onescience-primitives 召回的知识卡片。

**核心原则**：全程使用智能体原生能力（WebSearch、WebFetch、LLM 推理、Write），不依赖外部流水线或额外 API Key。

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
3. 卡片内容必须基于实际检索到的论文证据，不得编造。
4. 不修改 onescience-primitives 的 SKILL.md 或已有卡片。
5. 生成的卡片写入 `skills/onescience-primitives/assets/<domain>/workflow-planning/<name>/`。

## 执行流程

### Step 1 解析知识缺口

从用户输入中提取：

- **gap_description**：知识缺口的自然语言描述（如"藏红花基因衍生推理"）
- **domain**：领域（bio/matchem/climate/cfd/general），从描述中自动检测
- **search_queries**：2~4 组英文检索词（含同义词、物种学名、基因/酶/通路名、方法名）

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

**实时汇报**：`🔄 Step 3：从 N 篇论文中抽取知识...（全文级 X 篇，摘要级 Y 篇）`

### Step 4 卡片生成

将抽取的知识组织成知识卡片：

**卡片目录结构**：
```
skills/onescience-primitives/assets/<domain>/workflow-planning/<card-name>/
  metadata.json
  knowledge.md
```

**metadata.json 格式**（固定 9 字段 + harvested 标记）：
```json
{
  "name": "<card-name>",
  "type": "workflow-planning",
  "domain": "<bio|matchem|climate|cfd|general>",
  "version": "1.0.0",
  "visibility": "public",
  "created_at": "<ISO日期>",
  "updated_at": "<ISO日期>",
  "description": "<信息密集的描述，含核心能力、适用场景、关键参数>",
  "tags": ["<tag1>", "<tag2>", ...],
  "harvested": true,
  "harvest_source": "onescience-knowledge-harvester",
  "harvest_query": "<原始知识缺口描述>",
  "evidence_papers": [
    {"title": "<论文标题>", "doi": "<DOI>", "year": <年份>}
  ]
}
```

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

## 证据来源
[1] <论文标题>, <作者>, <期刊>, <年份>, DOI: <DOI>
[2] ...
```

**卡片命名规则**：
- 使用 kebab-case
- 格式：`<domain>-<topic>-<method>`（如 `bio-saffron-gene-derivative-reasoning`）
- 长度不超过 80 字符

**实时汇报**：`🔄 Step 4：生成知识卡片...`

### Step 5 写入文件系统

使用 Write 工具将卡片写入 onescience-primitives：

1. 创建目录：`skills/onescience-primitives/assets/<domain>/workflow-planning/<card-name>/`
2. 写入 `metadata.json`
3. 写入 `knowledge.md`
4. 验证文件存在且格式正确

**实时汇报**：`🔄 Step 5：写入卡片到 onescience-primitives...`

### Step 6 验证召回

确认生成的卡片可被 onescience-primitives 召回：

1. 用 Glob 搜索 `skills/onescience-primitives/assets/<domain>/**/metadata.json`
2. 确认新卡片在搜索结果中
3. 用 Read 读取 metadata.json，确认 description 和 tags 与知识缺口相关
4. 模拟检索：用 gap_description 作为查询，确认卡片会被语义匹配命中

**实时汇报**：`🔄 Step 6：验证卡片可召回性...`

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

## 禁止事项

- 不得编造论文或知识内容；每条事实必须绑定到检索到的论文证据。
- 不得凭记忆补写论文中没有的精确数值。
- 不得修改 onescience-primitives 的 SKILL.md 或已有卡片。
- 不得生成空卡片或只有 metadata.json 没有 knowledge.md 的卡片。
- 不得因为检索结果少就降低卡片质量标准；证据不足时如实标注"证据有限"。

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
| `./references/card_format.md` | 卡片格式详细规范：metadata.json 字段、knowledge.md 章节、命名规则、质量门禁 |
| `./references/lit_search.py` | OpenAlex 检索脚本模板（命令块 A） |
| `./references/lit_fetch.py` | 全文抓取脚本模板（命令块 B，Europe PMC + NCBI BioC 双通道） |
| `skills/onescience-primitives/SKILL.md` | 原语召回技能：卡片如何被发现和使用 |
| `skills/onescience-live-literature/SKILL.md` | 实时文献检索：检索策略和命令块原始模板 |
