---
name: onescience-primitives
description: OneScience 原语资源召回技能。根据自然语言需求检索相关原语资源（模型、组件、数据管线、应用、可视化规范、工作流规划、契约等）以及 Task-Centric 科研知识（Task、Method、Operation、Validation、Scenario、Workflow），通过范围判定、快速过滤和语义匹配召回，按内容需求返回相应知识；不做科研规划与代码实现。
type: resource
---

# OneScience Primitives Resource

## Primitive Unification Scope

This skill is the unified OneSkills primitive registry. A primitive is any reusable scientific capability that can be recalled, bound into a plan, handed to an executor, or used as planning evidence. Primitives may be first-party OneScience resources or third-party tools, packages, databases, services, datasets, workflow patterns, output formats, validation contracts, and execution templates.

**Task-Centric Knowledge Layer**: TC 知识对象与传统资源原语**同构同址**——一律是 `assets/<domain>/<category>/<primitive>/` 下的 `metadata.json` + `knowledge.md` 文档组，**不新增 metadata 字段、不改字段名**，因此 `catalog_search` 逻辑不变。对象类型由 `type` 区分：
- **Task**（`type: task`，category `tasks/`）：科研能力单元（如 material-property-prediction），含目标、输入输出契约、方法路线、操作序列、验证契约、实体槽
- **Workflow**（`type: workflow`，category `workflow/`）：以 Task 为节点的编排（如 material-screening-workflow）
- **Scenario**（`type: scenario`，category `scenario/`）：需求绑定与验收口径（如 material-candidate-screening）
- **Resource**（`type: model | tool | dataset | ...`，各资源 category）：被 Task 引用的资源，含带可运行脚本的资源卡
- **Method / Operation / Validation**：不单独建卡，作为 Task 卡 `knowledge.md` 的章节 + `tags` 词表边存在

知识图的**全部连接关系编码在 `tags`** 里（命名空间前缀 `edge:` / `slot:` / `atom:`），字段契约见 `references/tc/card_contract.md`。

Third-party tools can be primitives. Record the source through `provider` / `provenance` metadata and expose only distilled content through `resource_retrieval_result`; do not require a permanent bridge skill unless the provider needs its own retrieval backend, credentials, lifecycle, or access policy.

Use `onescience-primitive-distiller` when a new external scientific agent skill or third-party capability needs to be converted into primitive assets. This skill remains retrieval-only: it returns existing primitive content through the resource contract and does not perform distillation, migration, file creation, or script promotion itself.

When an application or workflow primitive depends on a specific primitive such as `bio.tools.scanpy`, expose that relationship through `primitive_dependencies` in the consumer metadata and mention the `primitive_id` in the consumer spec or workflow notes.

The preferred category set is open and includes `models`, `components`, `datapipes`, `datasets`, `tools`, `databases`, `services`, `application`, `visualization`, `workflow-planning`, `contracts`, and `output-format`, plus the Task-Centric categories `tasks`, `workflow`, and `scenario`. Preserve legacy category names when they already exist. TC 的 Workflow / Scenario 卡各自独占 `workflow/` 与 `scenario/` category，与 legacy 实例卡所在的 `workflow-planning/` 物理隔离，不再做 `workflow`→`workflow-planning` 的别名归并。

你负责从 `skills/onescience-primitives/assets/` 中找到最相关的 OneScience 原语，通过范围判定、快速过滤和语义匹配进行召回。不生成实现方案、不改代码、不执行脚本。

## 强制协议

本技能的 `assets/` 目录**仅供本技能内部使用**。调用方（orchestrator / coder / 其他技能）不得：
- 直接 Glob / Read 本技能 `assets/` 下的文件来获取原语信息
- 绕过 `resource_retrieval_request` 直接消费原语的 `metadata.json`、`spec.md`、`usage.md` 等文件内容
- 在未收到或构造 `resource_retrieval_request` 之前，禁止阅读或引用 `assets/` 下的任何文件

调用方必须通过 `resource_retrieval_request → resource_retrieval_result` 的完整闭环获取资源。

**协议范围豁免**：当调用方已构造合法的 `resource_retrieval_request`（包含 `user_request` 和/或 `filters`），并按本技能「召回流程」中的步骤执行资源检索时，调用方**可以**使用以下工具操作——这属于本技能召回逻辑的执行，不是违规的直接消费。豁免范围分为两级：

**优先路径 —— `catalog_search` + `catalog_resolve`**：
- 使用 `catalog_search` 工具（kind=primitive, domain=..., q=...）搜索原语
- 使用 `catalog_resolve` 工具（part=body/contract/location）获取 companions 和契约
- `catalog_search` 搜索的是 OneCode 内置 catalog（含 bundled seed 原语），不依赖本地文件系统

**降级路径 —— 文件系统 Glob/Read**（仅当 `catalog_search` 无结果且确认 `skills/onescience-primitives/assets/` 目录在本地存在时使用）：
- 枚举候选集（步骤 2）：Glob 列出资源目录
- 快速过滤/语义匹配（步骤 3-4）：Read 各资源的 `metadata.json`
- 内容组织（步骤 7）：Read 命中资源的 `spec.md`、`usage.md`、`workflow_planning.md` 及经白名单校验的执行资产
- 命名直查（命名直查模式步骤 3-4）：Glob 搜索目录名、Read `metadata.json`

调用方仍然**不得**沿 `matched_resources[].path` 自由读取任意文件，**不得**在未构造请求的情况下随意浏览 `assets/` 目录，**不得**消费未在 `execution_assets` 白名单中声明的脚本或文件。

当本技能被上游技能调用时，`resource_retrieval_request` 是输入控制消息，不是需要回显给用户的最终内容。本技能直接执行召回流程并返回 `resource_retrieval_result`。

## 原语资产目录

```text
assets/
  <domain>/
    <category>/
      <resource_name>/
        metadata.json            ← 基础信息（name, type, domain, description, tags, version）
        knowledge.md             ← 灵活单文档形态的完整正文（与下方三文件形态二选一）
        spec.md                  ← 规格知识（架构、参数、依赖）
        usage.md                 ← 使用知识（启动示例、接口、限制）
        workflow_planning.md     ← 规划决策知识（时机、流程、约束）
        references/               ← 可按需读取的扩展知识；仅允许 metadata 声明的文件
        scripts/                 ← 可选受控执行资产；必须由 spec.md 的 # execution_assets 结构化白名单 白名单声明

    scenario/                    ← Task-Centric Scenario 层（type=scenario）：需求绑定与验收口径，由 scenario_catalogs 场景 JSON 转换而来
      <scenario_name>/
        metadata.json            ← type=scenario；edge:workflow 指向 Workflow 卡；src:scenario_id 溯源
        knowledge.md
    workflow/                    ← Task-Centric Workflow 层（type=workflow）：以 Task 为节点的编排骨架
      <workflow_name>/
        metadata.json            ← type=workflow；edge:task / edge:step 展开到各 Task；src:scenarios_count 记归并场景数
        knowledge.md
    tasks/                       ← Task-Centric Task 层（type=task，与其他 category **平级**，不嵌套 resources）
      <task_name>/
        metadata.json            ← type=task；tags 承载 edge:/slot:/atom: 全部图边
        knowledge.md             ← 任务正文（目标、实体槽、输入输出契约、方法路线、操作序列、验证契约、资源引用、Task Graph、缺口与降级）
    workflow-planning/           ← 既有实例卡（legacy，type=workflow-planning）；不再存放 TC 的 scenario/workflow 卡
    models/ tools/ datasets/ datapipes/ components/
    application/ visualization/ databases/ output-format/ contracts/
                                 ← Resource 层：既有 category，与 scenario/workflow/tasks 平级；可运行资源在卡内 script/ 或 scripts/ 下

skills/onescience-primitives/references/tc/   ← TC 辅助索引（skill 内，**不进 assets 域树**）
  card_contract.md               ← 9 字段 + tags 边契约（替代原 schemas/*.yaml）
  atoms.jsonl                    ← 原子事实（数值级召回），靠 atom:<id> tag 回链卡片
    gaps.jsonl                     ← 缺口记录（retrieval_level != full 时追加）
  knowledge_evolution_log.jsonl  ← 知识演进日志（预留双向反馈闭环）
```

> **卡片双形态说明**：资源目录支持两种形态——(A) 传统四文件形态（`metadata.json` + `spec.md` + `usage.md` + `workflow_planning.md`）和 (B) 灵活单文档形态（`metadata.json` + `knowledge.md`）。当目录中仅有 `metadata.json` 和 `knowledge.md` 时，`knowledge.md` 即为完整正文，必须读取。

当前 `assets/` 顶层按 domain 组织，实际目录以仓库中的现状为准；当前可见的顶层 domain 包括：

- `bio`
- `cfd`
- `climate`
- `matchem`
- `general`

每个 domain 下的 category 目录可能不同，按**实际存在的目录**检索，不要求所有 domain 都具有同一套子目录。当前常见 category 包括：

- `scenario`                   ← Task-Centric Scenario 卡（type=scenario）
- `workflow`                   ← Task-Centric Workflow 卡（type=workflow）
- `tasks`                      ← Task-Centric Task 卡（bio / cfd / climate / general / matchem 五个 domain 均已建）
- `components`
- `models`
- `datapipes`
- `application`
- `visualization`
- `workflow-planning`          ← legacy 实例卡（type=workflow-planning）
- `contracts`
- `databases`
- `output-format`

## Task-Centric 知识检索路径

> **【重要】** 当调用方的请求涉及科研任务规划、科研能力查询、工作流编排时，应优先使用 Task-Centric 知识检索路径，而不是传统的资源原语检索。

### 触发条件

当 `resource_retrieval_request` 中满足以下任一条件时，进入 Task-Centric 知识检索：
- `intent` 字段为 `task`、`workflow`、`scenario` 之一
- `filters.task_id` 或 `filters.scenario_id` 已指定
- `user_request` 中包含科研目标关键词（如“筛选”“预测”“验证”“排序”“性质计算”等）
- `user_request` 中包含方法选择需求（如“用什么方法”“哪种技术路线”）
- `user_request` 中包含工作流编排需求（如“流程是什么”“步骤有哪些”）

### Task-Centric 检索步骤

0. **读契约**（首次或边约定不确定时）：Read `skills/onescience-primitives/references/tc/card_contract.md`，明确 9 字段约定与 `tags` 边命名空间（`edge:` / `slot:` / `atom:` / `runnable:` / `src:`）及解析规则。

0b. **查确定性索引（TC 检索的第一动作，不可跳过）**：Read `skills/onescience-primitives/references/tc/scenario_task_index.json`，按 `domain` + `scenario_title`（中文场景名）定位条目。条目的 `entry_points` 列出该场景**全部**入口卡（图谱 `sc-*` / 语义 / legacy `workflow-planning`），`lineages` 列出每条谱系的 workflow→tasks→resources 完整展开。命中条目时，**必须把条目列出的每一层卡片 Read 原文并全部纳入召回结果**，不得只取其中一张；`exists=false` 或 `dangling_resources` 非空的项按悬空边降级并记缺口，不得编造。仅当索引无命中（新场景、跨域、口语化描述）时才降级到下方关键词检索步骤。

1. **识别科研目标与 domain，并按 category 目录锁定 TC 层**：从 `user_request` 判断科研目标与 domain。TC 三层各自独占一个 category 目录，**先按目录锁层、再用 `metadata.json` 的 `type` 复核**（目录与 type 必须一致）：
   - **Scenario 层**（需求绑定与验收口径）→ `assets/<domain>/scenario/`，卡 `type=scenario`
   - **Workflow 层**（以 Task 为节点的编排）→ `assets/<domain>/workflow/`，卡 `type=workflow`
   - **Task 层** → `assets/<domain>/tasks/`，卡 `type=task`
   - **既有实例卡（legacy）** → `assets/<domain>/workflow-planning/`，卡 `type=workflow-planning`，不是 TC 编排层

   定位方式：Glob `assets/<domain>/scenario/*/metadata.json`、`assets/<domain>/workflow/*/metadata.json`、`assets/<domain>/tasks/*/metadata.json`。TC 层已与 legacy 的 `workflow-planning/` 物理隔离，无需再靠 Grep type 从上百张 legacy 卡里筛，误召回风险从结构上消除。

   **硬规则**：legacy 实例卡（`workflow-planning/`）仅当 TC Scenario / Workflow 无命中时才能作为补充证据返回，且必须标注 `legacy_instance: true`；**不得用 legacy 实例卡替代 TC 链的任一层**，也不得因此跳过 Scenario→Workflow→Task 的逐层展开。

   **场景溯源**：Scenario 卡通常由仓库外的 `scenario_catalogs/<域>/*.json` 场景需求书转换而来，原 `scenario_id` 记在 `src:scenario_id` tag 里（卡 `name` 用 kebab-case 英文或 `sc-*` 哈希，不等于 `scenario_id`）。请求里给的是中文场景名时，用 Grep `src:scenario_id` 定位，不要用 Grep `name`。

   **入口不是终点（硬规则）**：同一场景可能存在三类入口卡——语义 Scenario 卡、图谱 `sc-*` Scenario 卡、legacy `workflow-planning` 卡。legacy 卡已通过 `edge:scenario:<卡名>` / `edge:workflow:<卡名>` 接线，两类 Scenario 卡之间有 `edge:alias:<卡名>` 互指。无论从哪张卡进入（包括关键词 Grep 只命中一张 Task 卡或 legacy 卡的情况），都**必须**提取场景身份（顶层 `scenario_id` 字段、`src:scenario_id` tag、description 中的场景名、或 `edge:scenario:*` 边），反查定位 Scenario 卡，然后执行步骤 6 的完整展开；**命中任何单张卡即停止检索、直接进入提问或规划，属协议违规**。

2. **Task 检索（catalog 优先）**：
   - 优先 `catalog_search`（kind=primitive, domain=<domain>, q=<目标关键词>），命中 `type=task` 的卡
   - **catalog 是发布时快照**：新建的 TC 卡可能尚未进 catalog，无结果属正常，此时必须走文件系统降级路径，不得就此判定「无命中」
   - `catalog_search` 无结果时降级：Glob `assets/<domain>/tasks/*/metadata.json` → Read 各 `metadata.json`，按 `description` / `tags` 语义匹配
   - `filters.task_id` 已指定时命名直查：Glob 目录名 → Read `metadata.json`

3. **实体槽精确匹配**：从请求抽取实体（如 CO₂ / MOF / band_gap），与 Task 卡 `slot:*` tags 求交集。**无交集时不得硬套该 Task**：改道（见步骤 8）或降级并记缺口。

4. **读 Task 正文**：Read 命中 Task 的 `knowledge.md`，取方法路线、操作序列、验证契约、输入输出契约与已知缺口。（仅有 `metadata.json` + `knowledge.md` 时，`knowledge.md` 即完整正文，必读。）

5. **Resource 关联（沿 tags 边）**：解析 `edge:resource:<category>/<name>` → 同 domain 的 `assets/<domain>/<category>/<name>/`，Read 其 `metadata.json`（必要时 `knowledge.md` 或四文件形态）。**解析不到目录 = 悬空边**：该资源判缺失，不得编造其能力，计入降级与缺口。

6. **Task Graph 完整展开**：解析 Scenario 的 `edge:workflow:*` → Workflow 的**全部** `edge:task:*`（不得只取一个 Task），再对每个 Task 解析其 `edge:resource:*`；并用 `edge:prev:*` / `edge:next:*` 校验顺序一致性。输出必须给出「场景 → 工作流 → 各 Task → 各资源」的**逐层卡片路径凭证**；某一 Task 的资源边悬空时，只降级该 Task，不得连带丢弃整条链。

   **检索纪律（硬规则）**：
   - ① Grep / Glob / catalog 输出中出现截断提示（`truncated`、结果数达上限等）时，**必须**缩小检索范围（按 category 目录、更精确的关键词）重查直至无截断，**禁止基于截断输出下「无命中 / 只有 N 个」的结论**。
   - ② 检索结果中出现同一场景的多张卡（语义 Scenario 卡、`sc-*` 图谱卡、legacy 卡、多张 `tk-*` / `it-*` 任务卡）是 Task Graph 存在的信号：必须把它们聚合成同一条链后按本步骤展开，**不得只挑其中一张读完就停**。
   - ③ 在向用户提问、宣布 BLOCKED、或输出任何规划之前，必须先给出本步骤要求的逐层路径凭证表（含每一层的卡片相对路径与命中方式）；凭证不完整即视为检索未完成，禁止进入下一环节。

6b. **泛化与复用判定**（上层需求是「一个场景能不能复用已有 Task」时必做）：
   - 读 Workflow 骨架卡的 `src:scenarios_count` 与 `src:scenario_family`，得到这张骨架归并了多少个场景；泛化率 = `src:scenarios_count` : 该 Workflow 的 `edge:task:*` 数量。
   - Workflow 的 `edge:step:<step_id>:<task>` 给出源场景步骤到 Task 卡的映射，用它说明「源 workflow 的第几步落在哪张卡」。
   - 判定某张 Task 是新建还是复用：Grep 该 Task 的 `name` 于 `assets/<domain>/`，看它被多少张**其他**卡引用（被 2 条以上 Workflow 或其他 Task 的 `edge:prev/next` 引用 = 已复用骨架），并把 Grep 模式与命中数作为凭证输出。
   - 请求的场景在 `src:scenario_id` 中无精确命中、但其骨架族匹配时：仍可用该 Workflow + Task 骨架，把场景差异落到 `slot:*` 取值上，并在输出里标注「骨架匹配、场景未建卡」，不计为悬空边。

7. **Atom 检索（数值级，可选）**：请求涉及具体数值或判据（如“精度多少”“形成能阈值”）时，先取 Task 卡的 `atom:<id>` tags，再 Read `skills/onescience-primitives/references/tc/atoms.jsonl` 按 `atom_id` 定位；无 tag 时按 `statement` 关键词匹配。

8. **前提核验与改道**：核对方法路线前提（势函数覆盖范围、算力与求解器可用性、阈值/权重是否可审计）。前提不满足 → 按 `edge:fallback_method:*` 改道，并在输出中写明改道原因与精度/成本影响。

9. **分层降级判定**：确定 `retrieval_level`（task_centric 路径产出）：
   - **full**：Task 卡命中 + 全部 `edge:resource:*` 解析成功 + 至少一个操作有可执行或可规划落点
   - **partial**：Task 命中，但部分资源悬空/缺失（≥1 个资源解析成功）
   - **task_only**：仅命中 Task 卡（返回目标与输入输出契约作为方法框架，显式声明缺口）
   - **none**：无 Task 命中

9b. **跨路径实质命中判定（决定 `knowledge_gap`——在线兜底触发的唯一依据，必做、不可跳过）**：`retrieval_level` 只在 task_centric 路径产生；当请求走 traditional_resource 路径、或 TC 层无卡而回退到 legacy `workflow-planning/` 平铺卡时，`retrieval_level` 不足以反映「到底查没查到领域知识」。因此**无论走哪条路径**，都必须再判定一次 `knowledge_gap`：
   - **领域实质命中（`knowledge_gap=false`，本地可答）**：命中了与 `user_request` 的目标 domain + 具体研究对象/属性/方法**直接相关**的可执行 Task 卡，或领域专属资源卡（`model / tool / dataset / datapipe / component / database / contract / scenario / workflow` 等），足以支撑对该具体科学问题的准确回答。`full` 与 `partial` 均属实质命中。
   - **没查到领域知识（`knowledge_gap=true`，触发在线兜底）**，满足任一即是：
     a. task_centric 路径 `retrieval_level ∈ {none, task_only}`；
     b. traditional_resource 路径 `matched_resources` 为空；
     c. `matched_resources` **仅**由泛化规划/流程卡构成——即全部条目都是 `workflow_planning_primitive`（或标注 `legacy_instance: true` 的通用「文献综述 / 通用分析 / 通用建模流程 / 通用四步筛选」类卡），而无任何与目标 domain 具体研究对象直接相关的领域专属资源或 Task；
     d. 命中资源的 domain 与请求目标 domain 不一致（如问 `cfd` 却只命中 `general` 域通用流程卡），且无该 domain 的实质资源。
   - **铁律**：泛化 `workflow-planning` 卡只描述「怎么做研究」的通用流程，**不构成对具体科学问题的领域知识回答**。仅命中此类卡一律等同「没查到」，必须置 `knowledge_gap=true`，不得当成「有资源可用」继续往下走。

10. **缺口记录**：`retrieval_level != full` **或** `knowledge_gap=true` 时，向 `skills/onescience-primitives/references/tc/gaps.jsonl` **追加**一行 JSON：`{ts, domain, task, retrieval_level, knowledge_gap, request_slots{}, missing_resources[], dangling_edges[], suggested_fill, domain_match_summary{exact, adjacent, cross_domain}, gate_hit, gate_layer}`。只追加、不删改历史记录。
    - `domain_match_summary`：在线兜底完成后按 step 11 的 domain_match 标签统计三档数量；未触发兜底时三档均填 0。
    - `gate_hit`：∈ {`domain_mismatch`, `bare_number_reject`, `result_identity_lock`, `validation_rollback`, `complete_downgrade`, null}。本技能只在 A 层门禁命中时填 `domain_mismatch`（cross_domain 文献被当参数来源、或兜底后 exact=0）；B/C/D 层由 orchestrator 命中后追加各自 gate_hit 行（同一 gaps.jsonl，四层共用，便于 A/B 归因统计）。
    - `gate_layer`：∈ {`A_knowledge`, `B_planning`, `C_execution`, `D_acceptance`}，与 gate_hit 配套。

11. **在线兜底检索（`knowledge_gap=true` 时强制触发——即 step 9b 判定「本地没查到领域实质知识」，涵盖 none / task_only / 空召回 / 仅命中泛化 workflow-planning 卡 / domain 不符 五种情形）**：本地资产已无法产出准确完整的回答 → **调用 `onescience-live-literature` 技能联网兜底**：把上层需求转成该技能 Step 1 的查询分解，走两级在线检索（OpenAlex 摘要层迭代精炼 + Europe PMC/PMC 全文层取细节），产出带连续编号引用 `[n]` 的分层综合答案作为兜底。兜底硬约束：① 答案顶部显式标注「⚠ 本地知识缺口（knowledge_gap=true, retrieval_level=<none|task_only|empty|generic_only>），以下为在线文献兜底结果」；② 全程遵守 live-literature 的纪律铁律（只引池内论文、数值/极性有出处、abstract-only 降权标注、失败通道显式报告）；③ 在 step 10 已写入的 gaps.jsonl 缺口行 `suggested_fill` 末尾追加「已触发在线兜底」；④ 兜底答案是**补充而非替代**——若仍有任意本地 Task/资源命中，须一并列出本地凭证；⑤ **严禁编造**：`knowledge_gap=true` 时不得用泛化 workflow-planning 剧本假装完成、不得返回「模拟检索结果 / 模拟数据 / 默认参数 / 历史案例」充数；联网通道不可用（离线）时**不得报错、不得中断整个任务**：如实标注「本地知识缺口 + 当前离线，在线兜底不可用」，把该缺口作为已知限制交回上层，由上层继续执行任务其余部分（离线不构成 blocked，更不是编造模拟数据的理由）。⑥ **单一集中通道 + 证据并回召回结果**：本 step 11 是在线兜底的**唯一集中执行点**；兜底产出的带编号引用与接地事实必须以 `online_evidence` 字段**并入本技能召回结果**（见输出格式），作为上层规划/执行消费文献证据的唯一来源；orchestrator 见到 `online_evidence` 非空时**不得重复触发**检索（单次集中通道，防限流/防双跑）。⑦ **召回阶段证据边界（严禁自造）**：召回结果中不得填入任何未经「用户提供 / 本地卡 / 在线引文[n]」支持的参数、阈值、数据集或研究对象；无法支持的项只能标 `proposed_candidate(待确认)` 或留空，绝不伪造。⑧ **domain_match 标签与跨域降级（A 层门禁，修 ws07 文献场景错配）**：兜底产出的 `online_evidence.citations[]` 每条必须带 `domain_match ∈ {exact, adjacent, cross_domain}` 标签——`exact`=文献研究对象与本任务目标域及具体研究对象直接一致（如本任务问数据中心浸没液冷，文献即研究 immersion cooling of data center/server rack）；`adjacent`=同目标域但不同冷却方式/子场景（如 data center 但 air-cooled、liquid-cooled battery 但非机柜级）；`cross_domain`=不同应用领域（如电池热管理、PCM 储能、铸造、氢能）。**cross_domain 文献只能作为方法学参考**（验证思路、网格无关性方法、湍流模型候选），不得作为本次参数/阈值/几何/工况来源；违反时该参数降级为 `proposed_candidate(待确认)` 并向 gaps.jsonl 追加 `gate_hit=domain_mismatch, gate_layer=A_knowledge`。兜底完成后若池内 `exact` 数为 0：必须要求 live-literature 触发第二轮场景锚词精炼检索（锚词=目标域+具体研究对象，如「immersion cooling」+「data center」）；仍为 0 则在 `online_evidence` 顶部如实标注「在线兜底形式成功、实质未命中目标域（exact=0）」，相关科学结论保持 BLOCKED/诚实 PARTIAL，不得用 adjacent/cross_domain 文献硬凑本次参数。`knowledge_gap=false`（full / partial / 命中领域专属资源）**不触发**兜底，仍走本地链，仅在缺口处按 step 10 记录。

12. **可执行落点识别**：若 Task 的 `edge:operation:*` 在某资源卡上有对应实现，且该卡带 `runnable:script` tag，则该操作**本机可执行**：输出中给出脚本相对路径与可直接运行的命令；否则标注「无可执行落点，仅规划」。

13. **组织输出**：按下方输出格式返回。

### Task 检索与传统资源检索的桥接

- Task 卡的 `edge:resource:<category>/<name>` 指向的就是传统原语目录（如 `edge:resource:models/mace` → `assets/matchem/models/mace/`），解析成功后按传统路径 Read 其 `metadata.json` + `knowledge.md`（或 `spec.md` / `usage.md` / `workflow_planning.md`）。
- **悬空边**（无对应目录）视为资源缺失：不得编造资源能力，计入 `partial` 降级并写 `gaps.jsonl`。
- **反向边**：资源卡可用 `edge:task:<name>` 声明被哪些 Task 引用（如 `prediction-metric-calculator` → `prediction-accuracy-evaluation`），便于从资源侧回查任务。
- Task / Workflow / Scenario 卡与传统资源卡**共用同一套检索基础设施**（catalog_search 优先 + 文件系统降级），无需第二套索引文件。

---

## 召回流程

> **【检索路径优先级】**：OneScience 原语资产可能存储在两处：
> 1. **数据库/Blob Store**（通过 `catalog_search` + `catalog_resolve` 访问）：bundled seed 或已同步至 OneCode 内置 catalog 的原语。这是**默认检索路径**，优先级最高。
> 2. **本地文件系统**（通过 Glob + Read 访问 `skills/onescience-primitives/assets/`）：通过 oneskills 安装器解压到磁盘的原语。这是**降级检索路径**，仅在路径 1 无结果且确认本地 assets 目录存在时使用。
>
> **强制规则**：
> - 执行召回时，**必须先尝试路径 1**（`catalog_search`），不得跳过。
> - 仅当 `catalog_search` 返回空结果，**且**确认 `skills/onescience-primitives/assets/` 目录在本地存在时，才回退到路径 2（文件系统 Glob/Read）。
> - 回退到路径 2 后，命名直查和常规召回管道的文件系统操作规则（步骤 0-9）仍然适用。

> 本技能没有统一索引文件，原语信息以各资源目录下的 `metadata.json` 为主。因此必须先确定检索范围，再枚举该范围内的资源目录并逐个读取 `metadata.json`，不要凭目录名猜测。
>
> **【路径规范】**：本技能所有 `assets/` 目录的绝对路径为 `skills/onescience-primitives/assets/`。资源目录采用**三层嵌套结构**：`<domain>/<category>/<primitive_name>/`（如 `bio/visualization/complex_structure_visualization/`）。在以下步骤中，凡出现 `assets/<domain>/` 或 `assets/<domain>/<category>/` 等路径，均指代相对于仓库根目录的 `skills/onescience-primitives/assets/<domain>/...`。使用 Glob 搜索候选资源时必须使用 `**` 递归模式（如 `assets/bio/**/metadata.json`），不得使用单层 `*` 导致遗漏嵌套子目录。使用 Read 工具访问资产文件时，必须拼接完整路径前缀 `skills/onescience-primitives/`，不得使用不包含此前缀的相对路径。
>
> **【命名直查优先】**：在执行常规召回管道（步骤 0-6）之前，必须先检查是否满足命名直查条件。

### 命名直查模式

当调用方明确知道目标原语名称时，跳过召回管道，直接定位并返回该原语。

**触发条件**（同时满足以下两项时进入命名直查）：
a. `filters.keyword` 中包含一个可识别的原语名称（如 `complex_structure_visualization`、`alphafold3`、`openfold_data_pipeline` 等——即 `assets/<domain>/<category>/` 下的某个目录名）
b. `filters.domain` 已明确指定（如 `bio`、`cfd`、`climate`、`matchem`）

**命名直查执行步骤**：
1. 从 `filters.keyword` 中提取原语名称候选（将关键词按下划线连接、去空格、去标点等规范化处理后，与目录名比对）
2. **优先使用 `catalog_search`**：调用 `catalog_search` 工具（kind=primitive, domain=<filters.domain>, q=<从 keyword 提取的名称>）。若命中，直接使用 `catalog_resolve` 获取 body/contract，并跳转到步骤 6。
3. **回退到文件系统**：若 `catalog_search` 未命中且确认 `skills/onescience-primitives/assets/` 目录存在，则在 `skills/onescience-primitives/assets/<filters.domain>/` 下递归搜索匹配的目录名（使用 Glob 搜索 `skills/onescience-primitives/assets/<domain>/**/<name>/metadata.json`，其中 `<domain>` 替换为实际 domain 值如 `bio`，`<name>` 替换为从 keyword 提取的目录名）。必须使用 `**` 递归匹配，不得使用单层 `*`。
4. 若找到唯一匹配，直接读取该目录的 `metadata.json`；若找到多个匹配（跨 category），读取所有匹配并取 domain 和 keyword 语义最接近的一个
5. 若未找到匹配，回退到常规召回管道（步骤 0-6）
6. 命中后，直接跳转到步骤 7（组织内容），**跳过步骤 0-6 的枚举、过滤、语义匹配和截断**
7. 命名直查命中的资源在 `why_matched` 中标注 `named_lookup`，说明是通过名称直查而非语义匹配

**重要约束**：
- 命名直查是精确匹配辅助机制，不是语义搜索的替代品
- 若 keyword 同时包含多个候选名称，对每个名称分别执行直查
- 命名直查仍然遵守内容组织规则（步骤 7-9），包括执行资产白名单校验
- 命名直查不绕过强制协议：调用方仍需通过 `resource_retrieval_request` 发起，不得直接读取 assets

---

### 常规召回管道

以下步骤仅在命名直查未命中时执行。

0. **优先使用 `catalog_search`**：首先调用 `catalog_search` 工具（kind=primitive），传入 domain、keyword 等过滤条件。若返回非空结果，直接对结果项使用 `catalog_resolve(part=body)` 获取完整内容，跳过后续文件系统枚举步骤。仅当 `catalog_search` 无结果时，继续执行以下文件系统流程。

   **判定 domain scope**：先判断调用方是否通过 `filters.domain` 显式提供 domain。
   - 若 `filters.domain` 明确给出，则**直接使用调用方提供的 domain**，只检索对应的 `skills/onescience-primitives/assets/<domain>/`，且**不要再读取** `skills/onescience-primitives/references/domain_profile.md` 做二次判断
   - 若 `filters.domain` 未提供、为空或不可靠，则**必须先读取** `skills/onescience-primitives/references/domain_profile.md`，再结合 `user_request` 与 `task_state_summary` 按其中定义的领域信号进行回退判定
   - 回退判定结果若为 `climate | cfd | matchem | bio | general`，则只检索对应的 `skills/onescience-primitives/assets/<domain>/`
   - 回退判定结果若为 `unknown`，说明无法稳定路由到单一领域；此时允许检索 `skills/onescience-primitives/assets/` 下全部 domain 目录，但输出中的 `detected_domain` 必须保持为 `unknown`
   - 当请求已路由到生信领域，且涉及生信工作流、模型/数据管线/应用选择或多候选资源取舍时，可读取`skills/onescience-primitives/references/bio_profile.md`文档作为召回提示；该文件只辅助候选排序和边界解释，不能替代 `metadata.json` 证据
1. **判定 category scope**：根据 `user_request`、`content_request`、`filters.keyword`、`task_state_summary` 判断是否明确指定资源类别。
   - 若明确指定模型、组件、数据管线、应用、可视化规范、工作流规划、输出格式、契约或数据库/服务类资源，则只检索对应 category
   - 若未明确指定，则检索当前 domain scope 下全部实际存在的 category 目录
   - **【强制】可视化信号识别**：当 `user_request` 或 `filters.keyword` 中出现以下任一信号时，必须将 `visualization` 纳入检索范畴：
     - 显式可视化词：`可视化`、`visualization`、`visualize`、`visual`、`render`、`rendering`
     - 三维结构渲染词：`3D`、`三维`、`结构展示`、`structure view`、`interactive`、`交互式`
     - 置信度着色词：`pLDDT`、`PAE`、`confidence coloring`、`B-factor`、`chain coloring`
     - 分子可视化工具名：`PyMOL`、`3Dmol`、`MolStar`、`NGL`、`cartoon`、`ribbon`、`surface`、`stick`
     - 结构文件格式（需渲染）：`.pdb`、`.cif`、`.mmcif`、`.pse`、`.pml`
     - 当上述任一信号出现时，即使主意图被判定为 model/datapipe/application，也必须将 `visualization` category 纳入检索范围，不可遗漏
2. **枚举候选集**：在已确定的 domain/category scope 内，使用 Glob 递归搜索 `skills/onescience-primitives/assets/<domain>/**/metadata.json`（必须使用 `**` 递归匹配，不得使用单层 `*`），得到完整候选集。从每个匹配路径中提取三层信息：domain（`assets/` 后第一段）、category（domain 后第一段）、primitive_name（category 后第一段）。示例：路径 `assets/bio/visualization/complex_structure_visualization/metadata.json` → domain=`bio`, category=`visualization`, primitive_name=`complex_structure_visualization`。后续所有路径拼接必须保留完整的 `<domain>/<category>/<primitive_name>/` 三层结构，不得省略中间 category 层。
3. **快速过滤**：仅当 `filters.keyword` 提供了关键词时执行；结合目录名、`metadata.json` 的 `name`、`domain`、`description` 与 `tags` 排除明显不相关的资源。未提供关键词时跳过本步。
4. **语义匹配**：遍历剩余每个候选资源的 `metadata.json`，对比 `user_request` 与 `description` 字段的语义相关性。
5. **上下文增强**：结合 `task_state_summary` 进一步筛选和排序，但不能用上下文替代资源本身的证据。
6. **按匹配度排序并截断**：按语义相关性排序，返回最相关的 **5-8 个**资源；没有强相关资源时返回空列表，不要凑数。
   - **【强制】多类别覆盖保障**：当检索范围为全部 category（即未限定单一 category），且候选集中存在多个 category 的实际资源时，截断必须满足以下覆盖规则：
     a. 先按语义匹配度排序得到全序列表。
     b. 从高到低选取前 5 个资源（保障核心语义匹配质量）。
     c. 检查这 5 个资源是否覆盖了候选集中所有实际存在资源的 category。若某个 category 中的全部资源均未进入前 5，且该 category 中存在至少一个资源的语义匹配度不低于最高分的 60%，则从该 category 中取匹配度最高的 1 个资源追加到结果中（即使超出 5-8 范围也不得丢弃）。
     d. 追加后结果总数不超过 10 个；若超过 10 个，按语义匹配度去掉末尾超出部分。
     e. 追加的资源在 `why_matched` 中备注 `category_coverage` 标签，说明其被保留是因为类别覆盖而非纯语义排序。
   - **说明**：此规则确保当查询信号隐含多类别需求（如"分析蛋白质结构预测结果并可视化"），`visualization` 类资源不会因 model/component 类资源在纯语义排序中得分略高而被截断丢弃。
7. **逐个组织内容**：对每个命中的资源，按 `content_request` 分别读取并填充该资源的 `content` 字段：
   - 留空或 `"摘要"`：优先只读取 `metadata.json`，生成简短摘要，`description` 字段的关键信息不进行过度压缩
   - `"使用说明"`：读取 `usage.md`（若存在）；若不存在且存在 `knowledge.md`，则读取 `knowledge.md`
   - `"规格说明"`：读取 `spec.md`（若存在）；若不存在且存在 `knowledge.md`，则读取 `knowledge.md`
   - `"工作流规划知识"`：读取 `workflow_planning.md`（若存在）；若不存在且存在 `knowledge.md`，则读取 `knowledge.md`
   - `"完整知识正文"`：读取 `knowledge.md`（若存在）；这是灵活单文档形态卡片的完整正文
   - `"参考资料"` / `"扩展知识"`：只读取 `metadata.json` 中 `knowledge_assets` 声明的 `references/` 文件，并按主题组织返回
   - `"完整内容"`：读取 `metadata.json`、`spec.md`、`usage.md`、`workflow_planning.md` 及 `knowledge.md`（若存在）和 `knowledge_assets` 索引；不得因为请求完整内容而自动返回全部参考文件或任意脚本。当目录中仅有 `metadata.json` + `knowledge.md` 时，`knowledge.md` 即完整正文，必须读取
   - `"完整参考资料"`：在路径、大小和 SHA-256 校验通过后，读取 `knowledge_assets` 声明的参考文件；大文件按物化规则处理
   - 当且仅当 `include_execution_assets: true` 时，按以下子步骤物化受控执行资产：
   a. 读取命中资源的 spec.md，定位唯一的一级标题
   # execution_assets。

   读取该标题后紧邻的第一个 yaml 代码块，并从根字段
   execution_assets 获取白名单数组。

   不得从其他章节、自然语言、表格或 scripts/ 目录推测资产。
   若章节不存在、代码块不存在、YAML 无法解析、根字段缺失或
   出现重复 # execution_assets 标题，则视为白名单不可用。
   b. 遍历白名单中的每一项资产声明，以 primitive 目录（即 `skills/onescience-primitives/assets/<domain>/<category>/<resource_name>/`）为基准拼接相对路径，得到资产的绝对磁盘路径。
   c. 对每个资产执行：
      ① 检查文件是否存在。不存在时，该资产的 `status` 标记为 `unavailable`，`reason` 填 `file_not_found`，跳过后续校验。
      ② 读取文件原始内容，计算 SHA-256 并与白名单中的 `sha256` 比对。不匹配时，`status` 标记为 `failed`，`reason` 填 `sha256_mismatch`（记录期望值与实际值），不返回该资产的内容，不挂载到结果。
      ③ 校验通过后：
         - 若文件内容 ≤ 64 KiB，直接将原文填充到该资产的 `content` 字段，`status` 标记为 `available`。
         - 若文件内容 > 64 KiB，将资产物化到当前工作区的 `.onescience_assets/<primitive_name>/<version>/` 目录（保留原始文件名），`status` 标记为 `materialized`，`materialized_path` 填写物化后的绝对路径，`content_size_bytes` 填写文件字节数。`content` 字段留空。
   d. 遍历完成后，汇总所有资产的状态摘要：统计 `available`、`materialized`、`unavailable`、`failed` 四类计数。
   e. 即使部分资产不可用或校验失败，也必须返回可用/已物化部分，并在结果中附完整的逐资产状态列表。不得因单个资产失败而丢弃全部可用资产。
   f. 全部白名单资产均不可用时，该资源的 `execution_assets` 仍返回，但每一项 `status` 均为 `unavailable` 或 `failed`，并在 `limitations` 中明确说明原因。
8. **【强制】检索依赖组件**：当命中的资源为模型类型（`models` category 下的资源）且需要获取规格知识和使用知识时，**必须**执行以下步骤：
   - 读取该模型的 `spec.md` 文件，定位 `# key_dependencies` 部分
   - 提取所有列出的依赖组件名称（每行一个组件名）
   - 对于每个依赖组件，在同一 domain 的 `components` category 下检索对应的组件资源目录
   - 读取每个依赖组件的 `spec.md`（若存在）和 `usage.md`（若存在）
   - 将检索到的依赖组件信息作为 `dependent_components` 字段附加到该模型资源的输出中
   - 若某个依赖组件在 `components` 中不存在，在 `limitations` 中说明缺失的组件
   - **此步骤不可跳过**：即使 `content_request` 为 `"摘要"`，也必须检索依赖组件并至少返回其基本信息（name、description）
9. **填充输出字段**：按下方「字段取值规则」推导 `detected_domain`、`task_intent`、每个资源的 `type`，并按「质量要求」生成 `why_matched`、摘要形式的 `content`、`limitations`。
   - **【强制·跨路径兜底闸门，不可跳过】** 填充输出后，本 traditional_resource 路径**同样必须**执行上文「Task-Centric 检索步骤」中的 step 9b（跨路径实质命中判定）、step 10（缺口记录）、step 11（在线兜底检索）——这三步**不因走常规召回管道而豁免**（否则 off-shape 场景如 CFD 会因回退到本路径命中泛化卡而绕过兜底）。具体地：
     - 按 step 9b 计算 `knowledge_gap`：若 `matched_resources` 为空、或**仅**命中泛化 `workflow_planning_primitive`（如「文献综述 / 通用分析 / 通用建模流程 / 通用四步筛选」类 legacy 卡）而无任何与目标 domain 具体研究对象直接相关的领域专属资源、或命中 domain 与请求 domain 不符，一律置 `knowledge_gap=true`，`retrieval_level` 折算为 `none`。
     - `knowledge_gap=true` 时按 step 10 追加 gaps.jsonl，并按 step 11 强制调用 `onescience-live-literature` 联网兜底，`online_fallback` 置 `live_literature`；**严禁**把泛化 workflow-planning 卡当作领域知识回答返回，更严禁编造「模拟检索结果 / 模拟数据 / 默认参数 / 历史案例」充数。
     - `knowledge_gap=false`（命中领域专属资源）时 `online_fallback` 置 `not_triggered`，正常返回。

## 输入格式

```yaml
resource_retrieval_request:
  user_request: <用户需求描述>
  task_state_summary: <当前任务状态摘要，可选>
  content_request: <内容需求，可选>
  include_execution_assets: <true | false，可选，默认 false>
  intent: <resource | task | workflow | scenario，可选，默认 resource>
  filters:
    domain: <领域过滤，可选>
    keyword: <关键词过滤，可选>
    task_id: <Task ID 过滤，可选，用于 Task-Centric 检索>
    scenario_id: <Scenario ID 过滤，可选，用于 Task-Centric 检索>
    method_id: <Method ID 过滤，可选，用于 Task-Centric 检索>
```

> **intent 字段说明**：
> - `resource`（默认）：走传统原语资源检索路径
> - `task`：走 Task-Centric 知识检索路径，返回 Task 定义及其关联的 Method/Resource/Operation/Validation
> - `workflow`：走 Task-Centric 知识检索路径，返回 Workflow 的 Task Graph 及各 Task 定义
> - `scenario`：走 Task-Centric 知识检索路径，返回 Scenario 及关联的 Workflow 和 Task

## 输出格式

与统一资源契约保持一致：

```yaml
resource_retrieval_result:
  status: success | partial | failed
  query_summary: <需求摘要>
  detected_domain: <climate | cfd | matchem | bio | general | unknown>
  task_intent: <model | component | datapipe | application | tool | database | output-format | visualization | workflow | contract | mixed | task | scenario>
  retrieval_path: <traditional_resource | task_centric>   # 标识使用了哪条检索路径
  retrieval_level: <full | partial | task_only | none>     # 分层降级级别（task_centric 路径产出；traditional_resource 路径按 step 9b 折算：领域专属资源命中=partial/full，空或仅泛化卡=none）
  knowledge_gap: <true | false>                            # step 9b 跨路径实质命中判定，在线兜底触发的唯一依据；true=本地没查到领域实质知识（含 none/task_only/空召回/仅命中泛化 workflow-planning 卡/domain 不符）
  online_fallback: <not_triggered | live_literature>        # knowledge_gap=true 时置 live_literature，否则 not_triggered
  online_fallback_status: <online | offline | not_applicable>  # 兜底通道实际状态；offline=联网失败/限流已优雅降级（不报错不停摆）
  online_evidence:                                            # 在线兜底真实检索到的文献证据（单一集中通道产出；orchestrator 见非空不得重复检索）
    citations: [ "[n] 标题 | venue | year | doi | domain_match=<exact|adjacent|cross_domain> | evidence_level=<full-text|abstract-only>" ]  # 仅池内真实论文，连续编号；domain_match 必填（A 层门禁）
    grounded_facts: [ "事实陈述（标注 [n] 出处 + 该文献 domain_match）" ]   # 可供规划/执行直接 grounding 参数与结论的文献接地事实；cross_domain 文献的事实只能作方法学参考，不得作本次参数来源
    domain_match_summary: { exact: <int>, adjacent: <int>, cross_domain: <int> }  # 三档计数；exact=0 时必须已触发第二轮场景锚词精炼检索，仍为 0 则顶部标注「实质未命中目标域」
    # 为空（offline 或未触发）时上层必须进入证据边界模式：不得自造参数/数据/阈值充当本次结果
  matched_resources:
    - type: model_primitive | component_primitive | datapipe_primitive | application_primitive | tool_primitive | database_primitive | output_format_primitive | visualization_primitive | workflow_planning_primitive | contract_primitive | task_primitive | method_primitive | operation_primitive | validation_primitive | scenario_primitive | workflow_task_graph_primitive | atom_primitive
      path: assets/<domain>/<category>/<primitive_name>/   # TC 卡与传统资源卡共用同一三层路径
      name: <原语名称>
      why_matched: <匹配理由，1句话>
      limitations: <使用限制，1-2句话>
      content: <根据 content_request 组织的内容>
  gap_record:                                              # 仅 retrieval_level != full 时存在，与 gaps.jsonl 追加行同构
    gap_id: <string>
    missing_layer: <task | resource | operation | validation | atom | executable>
    dangling_edges: [<tags 中解析失败的 edge:* 值>]
    suggested_harvest: <string>
```

> **Task-Centric 检索结果说明**：
> 当 `retrieval_path` 为 `task_centric` 时，`matched_resources` 中的条目可能包含：
> - `task_primitive`：Task 卡，content 包含 `knowledge.md` 正文（目标、实体槽、输入输出契约、方法路线、操作序列、验证契约）与沿 `edge:*` 展开的资源信息；若操作有可执行落点，附带脚本相对路径与可运行命令
> - `scenario_primitive` / `workflow_task_graph_primitive`：Scenario 需求绑定与 Workflow 的 Task Graph（阶段链 + 各阶段门槛）
> - `tool_primitive` / `model_primitive` 等：沿 `edge:resource:*` 解析到的传统资源卡（含带 `runnable:script` 的可执行资源）
> - `atom_primitive`：原子事实，content 包含 statement、value、unit、evidence（来自 `references/tc/atoms.jsonl`）
>
> Method / Operation / Validation **不单独成条**，而是作为 `task_primitive` content 内的章节与 `edge:method:*` / `edge:operation:*` / `edge:validation:*` 词表边返回。
>
> **retrieval_level 说明**：
> - `full`：Task 卡命中 + 全部 `edge:resource:*` 解析成功 + 至少一个操作有可执行或可规划落点
> - `partial`：Task 命中，但部分资源边悬空/缺失（≥1 个资源解析成功）
> - `task_only`：仅命中 Task 卡，返回目标与输入输出契约作为方法框架并声明缺口
> - `none`：无 Task 命中
>
> **knowledge_gap 说明（跨两条检索路径，在线兜底触发的唯一依据，见 step 9b）**：
> - `false`：命中领域专属 Task 或资源（full / partial / traditional_resource 路径命中领域专属资源），本地足以作答。
> - `true`：本地没查到领域实质知识——`retrieval_level ∈ {none, task_only}`、或 `matched_resources` 为空、或仅命中泛化 `workflow-planning` 流程卡（如「文献综述工作流」）而无领域专属资源、或命中 domain 与请求 domain 不符。**泛化流程卡只讲「怎么做研究」，不等于对具体科学问题的领域回答，仅命中它一律 `knowledge_gap=true`。**
> - **在线兜底**：`knowledge_gap=true` 时按检索协议 step 11 强制触发 `onescience-live-literature` 联网兜底，产出带连续编号引用的分层综合答案并显式标注「本地知识缺口」；`knowledge_gap=false`（full / partial / 领域专属资源命中）不触发兜底。

`content` 完整格式（仅当 `content_request` 为 `"完整内容"` 时）：

```yaml
content:
  metadata: <metadata.json 内容>
  spec: <spec.md 内容>
  usage: <usage.md 内容>
  workflow_planning: <workflow_planning.md 内容>
  knowledge_assets:
    - path: <metadata.json 的 knowledge_assets 白名单中的相对路径>
      title: <参考资料标题>
      purpose: <该资料解决的问题>
      source: <来源文件或上游文档>
      sha256: <白名单声明的校验值>
      status: <available | materialized | unavailable | failed>
      content: <仅 status=available 且文件较小时填充原文>
      materialized_path: <仅 status=materialized 时填充物化后的绝对路径>
      content_size_bytes: <文件字节数>
  execution_assets:
    - path: < spec.md 的 `# execution_assets` 结构化白名单中声明的相对路径 >
      kind: <python_cli | template | javascript_runtime | license | other>
      media_type: <MIME type>
      sha256: <白名单声明的校验值>
      status: <available | materialized | unavailable | failed>
      reason: <unavailable/failed 时的原因，如 file_not_found | sha256_mismatch>
      content: <仅 status=available 且 ≤ 64 KiB 时填充原文>
      materialized_path: <仅 status=materialized 时填充物化后的绝对路径>
      content_size_bytes: <status=materialized 时填充文件字节数>
  execution_assets_summary:
    total: <白名单资产总数>
    available: <计数>
    materialized: <计数>
    unavailable: <计数>
    failed: <计数>
```

执行资产强制规则：

- 只有请求显式包含 `include_execution_assets: true` 时才能返回。
- 只允许 `spec.md 的 # execution_assets 结构化白名单` 中逐项声明的相对路径；拒绝未声明文件、绝对路径、`..` 和路径穿越。
- 规范化后的路径必须仍位于当前 primitive 目录内。
- 返回前校验 SHA-256；不匹配时不返回该资产内容，逐资产标记 `status: failed` 及 `reason: sha256_mismatch`（记录期望值与实际值），但不应影响其他已通过校验的资产。
- 调用方只能消费 `content.execution_assets`，不得沿 `matched_resources[].path` 直接读取文件。
- 大文件处理：≤ 64 KiB 的文本文件直接内联到 `content` 字段；> 64 KiB 的文件（如 3Dmol.js ~150KB、HTML 模板 ~200KB）物化到工作区 `.onescience_assets/<primitive_name>/<version>/` 目录，`status` 设为 `materialized`，通过 `materialized_path` 传递绝对路径。
- 状态汇总：必须同时返回 `execution_assets_summary`，便于调用方在不解析全部资产明细的前提下快速判断整体可用性。
- 部分失败不阻塞全部：只要至少有一个核心资产（如 `render_complex_structure.py`）`available` 或 `materialized`，结果 `status` 可为 `partial` 而非 `failed`，让调用方自行降级决策。

知识资产强制规则：

- `references/` 只承载可阅读的领域知识、API 参考、方法说明、示例和来源材料，不承载默认可执行代码。
- 每个参考文件必须在 `metadata.json` 的 `knowledge_assets` 白名单中声明 `path`、`title`、`purpose`、`source`、`sha256` 和 `media_type`。
- 只允许相对于当前 primitive 目录的路径；拒绝绝对路径、`..`、未声明文件和路径穿越。
- 默认摘要和完整内容只返回参考资料索引；只有 `content_request` 明确请求 `参考资料` 或 `完整参考资料` 时才读取其正文。
- 参考资料返回前校验 SHA-256；失败时标记 `status: failed`，不得静默使用未校验内容。
- 参考资料与执行资产分开统计、分开授权；读取参考资料不会授予执行权限。

## 字段取值规则

输出中的枚举字段不能凭空填写，按以下规则从数据推导：

- **`domain scope` 判定**：先判断请求是否路由到单个 domain。
  - `filters.domain` 明确时优先使用，且一旦使用就不要再读取 `domain_profile.md` 进行二次判定
  - `filters.domain` 缺失时，必须读取 `skills/onescience-primitives/references/domain_profile.md`，按其中标准化规则将请求映射到 `bio | cfd | climate | matchem | general | unknown`
  - 目录路由值按当前 assets 顶层目录解释，如 `bio | cfd | climate | matchem | general`
  - 若回退判定为 `unknown`，则不路由到单个目录，而是检索全部 domain 目录并保持 `detected_domain: unknown`
- **`category scope` 判定**：按自然语言语义映射到 category 目录。
  - 模型 / `model` → `models`
  - 组件 / `module` / `block` / `encoder` / `decoder` → `components`
  - 数据管线 / `datapipe` / `dataset` / `loader` / `preprocessing` → `datapipes`
  - 应用 / `app` / `toolkit` / `template` → `application`
  - 输出格式 / `docx` / `pdf` / `pptx` / `markdown` / `mermaid` / `report` / `slide` → `output-format`
  - 可视化 / `visualization` / `visualize` / `visual` / `render` / `rendering` / `3D` / `三维` / `结构展示` / `interactive` / `交互式` / `pLDDT` / `PAE` / `PyMOL` / `3Dmol` / `cartoon` / `ribbon` / `surface` / `stick` / `.pdb` / `.cif` / `.mmcif` → `visualization`
  - 工作流规划 / `planning` / `route` / `decision` → `workflow-planning`
  - 若请求未明确 category，则检索当前 domain scope 下全部实际存在的 category 目录
  - 当 `filters.keyword` 中包含明确的可视化信号但 `user_request` 未直接体现时，仍须将 `visualization` category 纳入检索范围
- **`detected_domain`**：按标准化 domain 枚举输出 `climate | cfd | matchem | bio | general | unknown`。
  - 若 `filters.domain` 已明确提供，则优先使用该值作为检索路由依据；输出时仍需与命中资源的 `metadata.json.domain` 保持一致性
  - 若 `filters.domain` 缺失，则以 `domain_profile.md` 回退判定结果作为领域判断基线
  - 若命中结果跨多个不兼容 domain、或回退判定本身为 `unknown`、或资源证据不足以支撑单一领域，则填 `unknown`
- **`matched_resources[].type`**：优先由资源所在 category 与 `metadata.json.type` 共同推导。
  - `models` 下的 `model` → `model_primitive`
  - `components` 下的 `component` 或普通 `module` → `component_primitive`
  - `datapipes` 下的 `datapipe` → `datapipe_primitive`
  - `application` 下的 `application` → `application_primitive`
  - `output-format` 下的 `output-format` → `output_format_primitive`
  - `visualization` 下的 `visualization` → `visualization_primitive`
  - `tools` 下的 `tool` → `tool_primitive`
  - `databases` 下的 `database` → `database_primitive`
  - `workflow-planning` 下的 `workflow-planning` → `workflow_planning_primitive`（legacy 实例卡）
  - `scenario` 下的 `scenario` → `scenario_primitive`
  - `workflow` 下的 `workflow` → `workflow_task_graph_primitive`
  - `contracts` 下的 `contract` → `contract_primitive`
  - 若 `metadata.json.type` 与目录语义冲突，优先采用更能反映资源用途的目录语义，并在 `limitations` 中说明
- **`task_intent`**：根据 `user_request` 的主要意图判断。
  - 需要完整模型能力时填 `model`
  - 需要组件、模块、算子或内部结构时填 `component`
  - 需要数据准备、数据处理、数据接口时填 `datapipe`
  - 需要模板、脚本集合、分析工具或交付应用时填 `application`
  - 需要文档、幻灯片或报告交付格式时填 `output-format`
  - 需要结构、数据或模型结果的视觉呈现规范时填 `visualization`
  - 需要契约、接口约束或对接规则时填 `contract`
  - 需要数据库、公共 API 或知识库检索约定时填 `database`
  - 需要工作流规划、路由、决策知识时填 `workflow`
  - 多种意图并存且无法归一时填 `mixed`

## 质量要求

- **命名直查优先**：收到请求后，首先检查 `filters.keyword` 是否包含可识别的原语目录名。若满足命名直查条件（domain 已指定 + keyword 含目录名），必须优先执行命名直查，不得跳过直查直接进入常规召回管道。
- 命名直查命中后，直接跳转到内容组织步骤，不受语义排序和截断限制。
- 命名直查未命中时，回退到常规召回管道。

- 先判定 domain scope，再判定 category scope；不要跳过范围判定直接做全局模糊搜索。
- 调用方给出 `filters.domain` 时，必须直接使用该值路由，且不得再读取 `domain_profile.md` 做二次领域判断。
- 调用方未给出 `filters.domain` 时，必须先读取 `skills/onescience-primitives/references/domain_profile.md` 做回退判定。
- 回退判定为 `climate`、`cfd`、`matchem`、`bio` 或 `general` 时，只能搜索对应 domain 目录。
- 回退判定为 `unknown` 时，才允许搜索全部 domain 目录。
- 无明确 category 时必须搜索当前 domain scope 下全部实际存在的 category；有明确 category 时只搜索对应 category。
- 当检索范围为全部 category 且用户请求中隐含多类型需求时，必须执行多类别覆盖保障规则，确保 `visualization`、`workflow-planning` 等非主力 category 中的高匹配资源不会被 model/component 类资源完全挤占截断位置。
- 当 `filters.keyword` 包含可视化信号词但 `user_request` 语义较弱时，仍必须匹配 `visualization` category 并至少检查该 category 下是否存在匹配资源。
- 通过语义匹配 `metadata.json` 的 `description` 字段召回，不依赖额外索引文件。
- `why_matched` 说明 query 与 description 的对应关系（1句话）。
- 摘要模式下的 `content` 从 `description` 字段提取核心能力一段话。
- `limitations` 优先从 `spec.md` 或 `workflow_planning.md` 的约束部分提炼；若相关文件缺失，可根据 `metadata.json` 已知边界简要说明。
- 某些资源可能缺少 `usage.md`、`spec.md` 或 `workflow_planning.md`；若请求内容部分存在、部分缺失，可返回 `status: partial`，并在 `limitations` 中说明缺失项。
- 没有匹配资源时返回空 `matched_resources: []`，不编造资源。
- **禁止泛化卡冒充领域命中**：仅命中通用 `workflow-planning` 流程卡（文献综述 / 通用分析 / 通用筛选等）时，必须置 `knowledge_gap=true` 并按 step 11 触发在线兜底，不得把泛化流程卡当作领域知识回答返回、更不得据此编造「模拟检索结果 / 模拟数据 / 默认参数」充数。本地无领域知识时的唯一合法出路是联网兜底或如实报告缺口（`knowledge_gap=true` + `online_fallback` 交回上层）。
