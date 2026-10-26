---
name: onescience-primitives
description: OneScience 原语资源召回技能。根据自然语言需求检索相关原语资源（模型、组件、数据管线、应用、可视化规范、工作流规划、契约等）以及 Task-Centric 科研知识（Task、Method、Operation、Validation、Scenario、Workflow），通过范围判定、快速过滤和语义匹配召回，按内容需求返回相应知识；不做科研规划与代码实现。
type: resource
---

# OneScience Primitives Resource

本技能采用渐进披露：正文保留检索协议与硬约束；细则下沉 `references/`，在标注「必须先读取」的位置必须先读再做（`asset_materialization.md` 内容组织与资产物化细则、`field_value_rules.md` 字段取值与质量要求全文、`tc/card_contract.md` TC 卡契约、`domain_profile.md` 领域回退判定、`bio_profile.md` 生信召回提示）。

## Primitive Unification Scope

本技能是 OneSkills 统一原语注册表。原语（primitive）= 任何可被召回、绑定进计划、交接给 executor 或用作规划证据的可复用科研能力：模型、组件、数据管线、数据集、工具、数据库、服务、应用、可视化规范、工作流规划、输出格式、契约、执行模板；也可为第三方工具/包（以 `provider`/`provenance` 元数据记录来源，仅通过 `resource_retrieval_result` 暴露蒸馏后内容；需要转第三方技能为原语资产时用 `onescience-primitive-distiller`，本技能始终保持 retrieval-only）。

**Task-Centric Knowledge Layer**：TC 知识对象与传统资源原语**同构同址**——一律是 `assets/<domain>/<category>/<primitive>/` 下的 `metadata.json` + `knowledge.md` 文档组，**不新增 metadata 字段、不改字段名**，`catalog_search` 逻辑不变。对象类型由 `type` 区分：
- **Task**（`type: task`，category `tasks/`）：科研能力单元，含目标、输入输出契约、方法路线、操作序列、验证契约、实体槽
- **Workflow**（`type: workflow`，category `workflow/`）：以 Task 为节点的编排
- **Scenario**（`type: scenario`，category `scenario/`）：需求绑定与验收口径
- **Resource**（`type: model | tool | dataset | ...`，各资源 category）：被 Task 引用的资源，含带可运行脚本的资源卡
- **Method / Operation / Validation**：不单独建卡，作为 Task 卡 `knowledge.md` 章节 + `tags` 词表边存在

知识图的**全部连接关系编码在 `tags`**（命名空间前缀 `edge:` / `slot:` / `atom:`），字段契约见 `references/tc/card_contract.md`。TC 的 Workflow/Scenario 卡与 legacy 实例卡（`workflow-planning/`）物理隔离，不做别名归并。类别集合是开放的：`models`、`components`、`datapipes`、`datasets`、`tools`、`databases`、`services`、`application`、`visualization`、`workflow-planning`、`contracts`、`output-format`，加 TC 的 `tasks`、`workflow`、`scenario`；保留既有 legacy category 名。

你负责从 `skills/onescience-primitives/assets/` 找到最相关原语，通过范围判定、快速过滤和语义匹配召回。不生成实现方案、不改代码、不执行脚本。

## 强制协议

本技能的 `assets/` 目录**仅供本技能内部使用**。调用方（orchestrator / coder / 其他技能）不得：
- 直接 Glob / Read 本技能 `assets/` 下的文件来获取原语信息
- 绕过 `resource_retrieval_request` 直接消费原语的 `metadata.json`、`spec.md`、`usage.md` 等文件内容
- 在未收到或构造 `resource_retrieval_request` 之前阅读或引用 `assets/` 下任何文件

调用方必须通过 `resource_retrieval_request → resource_retrieval_result` 完整闭环获取资源。

**协议范围豁免**：调用方已构造合法 `resource_retrieval_request` 并按本技能召回流程执行时，可以以下操作——这属于召回逻辑的执行，不是违规直接消费：
- **优先路径 —— `catalog_search` + `catalog_resolve`**：`catalog_search`（kind=primitive, domain=..., q=...）搜索原语；`catalog_resolve`（part=body/contract/location）获取 companions 和契约。`catalog_search` 搜 OneCode 内置 catalog（含 bundled seed），不依赖本地文件系统。
- **降级路径 —— 文件系统 Glob/Read**（仅当 `catalog_search` 无结果且确认本地 `skills/onescience-primitives/assets/` 存在）：枚举候选（Glob 列目录）、快速过滤/语义匹配（Read `metadata.json`）、内容组织（Read `spec.md`/`usage.md`/`workflow_planning.md` 及白名单执行资产）、命名直查（Glob 目录名 + Read `metadata.json`）。

调用方仍**不得**沿 `matched_resources[].path` 自由读取任意文件、不得在无请求时浏览 `assets/`、不得消费未在 `execution_assets` 白名单声明的脚本。当本技能被上游调用时，`resource_retrieval_request` 是输入控制消息而非最终输出；本技能直接执行召回并返回 `resource_retrieval_result`。

## 原语资产目录

```text
skills/onescience-primitives/assets/<domain>/<category>/<resource_name>/
  metadata.json     ← 基础信息（name, type, domain, description, tags, version）
  knowledge.md      ← 灵活单文档形态完整正文（与三文件形态二选一）
  spec.md           ← 规格知识（架构、参数、依赖）
  usage.md          ← 使用知识（启动示例、接口、限制）
  workflow_planning.md ← 规划决策知识（时机、流程、约束）
  references/       ← 按需读取扩展知识；仅 metadata 声明的文件
  scripts/          ← 可选受控执行资产；必须由 spec.md `# execution_assets` 白名单声明
```

TC 三层各独占 category：`scenario/`（type=scenario）、`workflow/`（type=workflow）、`tasks/`（type=task，与资源 category 平级）；legacy 实例卡在 `workflow-planning/`（type=workflow-planning）。TC 辅助索引在技能内 `references/tc/`（`card_contract.md`、`atoms.jsonl` 原子事实、`knowledge_evolution_log.jsonl`），**不进 assets 域树**。

> **知识区只读**：技能树（`skills/**`）是只读知识区，运行期一律不得写入。缺口/门禁记录 `.onescience/gaps.jsonl` 落工作区状态目录（与 `.onescience/task_state.json` 同约定，已在 `.gitignore` 内），理由见 step 10。

> **卡片双形态**：(A) 四文件形态（metadata + spec + usage + workflow_planning）；(B) 单文档形态（`metadata.json` + `knowledge.md`）。目录仅有后者时，`knowledge.md` 即完整正文，必须读取。

顶层 domain 以仓库现状为准，当前包括：`bio`、`cfd`、`climate`、`matchem`、`general`。每个 domain 下的 category 目录可能不同，按**实际存在的目录**检索；常见 category：`scenario`、`workflow`、`tasks`、`components`、`models`、`datapipes`、`application`、`visualization`、`workflow-planning`、`contracts`、`databases`、`output-format`。

## Task-Centric 知识检索路径

> **【重要】** 调用方请求涉及科研任务规划、科研能力查询、工作流编排时，应优先使用 Task-Centric 检索路径，而不是传统资源原语检索。

**触发条件**（`resource_retrieval_request` 满足任一）：`intent` 为 `task`/`workflow`/`scenario`；`filters.task_id` 或 `filters.scenario_id` 已指定；`user_request` 含科研目标关键词（"筛选""预测""验证""排序""性质计算"等）或方法选择需求（"用什么方法""哪种技术路线"）或工作流编排需求（"流程是什么""步骤有哪些"）。

### Task-Centric 检索步骤

0. **读契约**（首次或边约定不确定时）：Read `references/tc/card_contract.md`，明确 9 字段约定与 `tags` 边命名空间（`edge:` / `slot:` / `atom:` / `runnable:` / `src:`）及解析规则。

0b. **查确定性索引（TC 检索第一动作，不可跳过）**：Read `references/tc/scenario_task_index.json`，按 `domain` + `scenario_title`（中文场景名）定位条目。条目 `entry_points` 列出该场景**全部**入口卡（图谱 `sc-*` / 语义 / legacy `workflow-planning`），`lineages` 列出每条谱系 workflow→tasks→resources 完整展开。命中条目时**必须把条目列出的每一层卡片 Read 原文并全部纳入召回结果**，不得只取其一；`exists=false` 或 `dangling_resources` 非空项按悬空边降级并记缺口，不得编造。仅当索引无命中（新场景、跨域、口语化）才降级到关键词检索步骤。

1. **识别科研目标与 domain，按 category 目录锁定 TC 层**：TC 三层各独占一个 category，**先按目录锁层、再用 `metadata.json` 的 `type` 复核**（目录与 type 必须一致）：Scenario → `assets/<domain>/scenario/`；Workflow → `assets/<domain>/workflow/`；Task → `assets/<domain>/tasks/`；legacy 实例卡 → `assets/<domain>/workflow-planning/`（不是 TC 编排层）。定位用 Glob `assets/<domain>/<category>/*/metadata.json`。
   - **硬规则**：legacy 实例卡仅当 TC Scenario/Workflow 无命中时才能作补充证据返回，且必须标注 `legacy_instance: true`；不得用 legacy 卡替代 TC 链任一层，不得因此跳过 Scenario→Workflow→Task 逐层展开。
   - **场景溯源**：Scenario 卡由仓库外 `scenario_catalogs/<域>/*.json` 场景需求书转换而来，原 `scenario_id` 记在 `src:scenario_id` tag（卡 `name` 是 kebab-case 英文或 `sc-*` 哈希）。请求给中文场景名时用 Grep `src:scenario_id` 定位，不要用 Grep `name`。
   - **入口不是终点（硬规则）**：同一场景可能有三类入口卡（语义 Scenario、图谱 `sc-*`、legacy `workflow-planning`；legacy 已经 `edge:scenario:*`/`edge:workflow:*` 接线，两类 Scenario 间有 `edge:alias:*` 互指）。无论从哪张卡进入（含 Grep 只命中一张 Task 或 legacy 卡），都**必须**提取场景身份（顶层 `scenario_id`、`src:scenario_id` tag、description 场景名或 `edge:scenario:*` 边），反查定位 Scenario 卡，再执行步骤 6 完整展开；**命中任何单张卡即停止、直接进入提问或规划，属协议违规**。

2. **Task 检索（catalog 优先）**：优先 `catalog_search`（kind=primitive, domain, q=目标关键词）命中 `type=task` 卡。**catalog 是发布时快照**：新建 TC 卡可能未进 catalog，无结果属正常，必须走文件系统降级（Glob `assets/<domain>/tasks/*/metadata.json` → Read 按 `description`/`tags` 语义匹配），不得就此判「无命中」。`filters.task_id` 指定时命名直查。

3. **实体槽精确匹配**：从请求抽取实体（CO₂/MOF/band_gap 等）与 Task 卡 `slot:*` tags 求交集。**无交集时不得硬套该 Task**：改道（步骤 8）或降级并记缺口。

4. **读 Task 正文**：Read 命中 Task 的 `knowledge.md`（目标、实体槽、输入输出契约、方法路线、操作序列、验证契约、资源引用、Task Graph、缺口与降级）。

5. **Resource 关联（沿 tags 边）**：解析 `edge:resource:<category>/<name>` → 同 domain `assets/<domain>/<category>/<name>/`，Read 其 `metadata.json`（必要时正文）。**解析不到目录 = 悬空边**：该资源判缺失，不得编造其能力，计入降级与缺口。

6. **Task Graph 完整展开**：解析 Scenario 的 `edge:workflow:*` → Workflow 的**全部** `edge:task:*`（不得只取一个），再对每个 Task 解析 `edge:resource:*`；用 `edge:prev:*`/`edge:next:*` 校验顺序。输出必须给出「场景→工作流→各 Task→各资源」逐层卡片路径凭证；某 Task 资源边悬空只降级该 Task，不得连带丢弃整条链。

   **检索纪律（硬规则）**：
   - ① Grep/Glob/catalog 输出出现截断提示（`truncated`、结果达上限）时，**必须**缩小范围重查直至无截断，**禁止基于截断输出下「无命中/只有 N 个」结论**。
   - ② 同一场景出现多张卡（语义 Scenario、`sc-*`、legacy、多张 `tk-*`/`it-*`）是 Task Graph 存在信号：必须聚合为同一条链后全部展开，**不得只挑一张读完就停**。
   - ③ 在向用户提问、宣布 BLOCKED 或输出任何规划之前，必须先给出逐层路径凭证表（每层卡片相对路径 + 命中方式）；凭证不完整 = 检索未完成，禁止进入下一环节。

6b. **泛化与复用判定**（上层问「一个场景能不能复用已有 Task」时必做）：读 Workflow 骨架卡 `src:scenarios_count` 与 `src:scenario_family`（泛化率 = scenarios_count : edge:task 数量）；用 `edge:step:<step_id>:<task>` 说明源场景步骤到 Task 卡映射；判定新建/复用：Grep 该 Task `name` 于 `assets/<domain>/`，被 2 条以上 Workflow 或其他 Task 的 `edge:prev/next` 引用 = 已复用骨架，输出 Grep 模式与命中数作凭证；场景在 `src:scenario_id` 无精确命中但骨架族匹配时：仍可用该骨架，把场景差异落到 `slot:*` 取值，标注「骨架匹配、场景未建卡」，不计悬空边。

7. **Atom 检索（数值级，可选）**：请求涉及具体数值或判据时，取 Task 卡 `atom:<id>` tags 后 Read `references/tc/atoms.jsonl` 按 `atom_id` 定位；无 tag 时按 `statement` 关键词匹配。

8. **前提核验与改道**：核对方法路线前提（势函数覆盖、算力与求解器可用性、阈值/权重可审计性）。前提不满足 → 按 `edge:fallback_method:*` 改道，写明改道原因与精度/成本影响。

9. **分层降级判定**：`retrieval_level`（task_centric 路径产出）：
   - **full**：Task 命中 + 全部 `edge:resource:*` 解析成功 + 至少一个操作有可执行或可规划落点
   - **partial**：Task 命中，但部分资源悬空/缺失（≥1 个解析成功）
   - **task_only**：仅命中 Task 卡（返回目标与契约作方法框架，显式声明缺口）
   - **none**：无 Task 命中

9b. **跨路径实质命中判定（决定 `knowledge_gap`——在线兜底触发的唯一依据，必做、不可跳过）**：`retrieval_level` 只在 task_centric 路径产生；走 traditional_resource 路径、或 TC 无卡回退 legacy 平铺卡时，也必须再判定一次 `knowledge_gap`：
   - **领域实质命中（`knowledge_gap=false`，本地可答）**：命中与 `user_request` 目标 domain + 具体研究对象/属性/方法**直接相关**的可执行 Task 卡或领域专属资源卡（model/tool/dataset/datapipe/component/database/contract/scenario/workflow 等），足以支撑对该具体科学问题的准确回答。`full` 与 `partial` 均属实质命中。
   - **没查到领域知识（`knowledge_gap=true`，触发在线兜底）**，任一即是：a. TC 路径 `retrieval_level ∈ {none, task_only}`；b. traditional 路径 `matched_resources` 为空；c. 命中**仅**由泛化规划/流程卡构成（全部是 `workflow_planning_primitive` 或 `legacy_instance: true` 的通用「文献综述/通用分析/通用建模流程/通用四步筛选」类卡），无任何领域专属资源或 Task；d. 命中资源 domain 与请求 domain 不一致且无该 domain 实质资源。
   - **铁律**：泛化 `workflow-planning` 卡只描述「怎么做研究」的通用流程，**不构成对具体科学问题的领域知识回答**。仅命中此类卡一律 `knowledge_gap=true`，不得当成「有资源可用」继续往下走。

10. **缺口记录**：`retrieval_level != full` **或** `knowledge_gap=true` 时，向工作区状态目录 `.onescience/gaps.jsonl`（相对当前工作区根，**不是** `skills/` 内任何路径）**追加**一行 JSON：`{ts, domain, task, retrieval_level, knowledge_gap, request_slots{}, missing_resources[], dangling_edges[], suggested_fill, domain_match_summary{exact, adjacent, cross_domain}, gate_hit, gate_layer}`。只追加、不删改历史。
    - **禁止写进技能树内路径**（`skills/**` 只读；运行期写入会污染知识库、破坏「同一知识库多次运行结果可比」）。`.onescience/` 不存在时先创建（不得为写入修改技能树内任何文件）。
    - `domain_match_summary`：兜底完成后按 step 11 标签统计三档数量；未触发时三档填 0。
    - `gate_hit` ∈ {`domain_mismatch`, `bare_number_reject`, `result_identity_lock`, `validation_rollback`, `complete_downgrade`, null}：本技能只在 A 层命中时填 `domain_mismatch`（cross_domain 文献被当参数来源、或兜底后 exact=0）；B/C/D 层由 orchestrator 各自追加（同一 gaps.jsonl 四层共用，便于 A/B 归因）。`gate_layer` ∈ {`A_knowledge`, `B_planning`, `C_execution`, `D_acceptance`}。

11. **在线兜底检索（`knowledge_gap=true` 时强制触发——涵盖 none / task_only / 空召回 / 仅命中泛化卡 / domain 不符五种情形）**：本地资产无法产出准确完整回答 → **调用 `onescience-live-literature` 技能联网兜底**：把上层需求转成该技能 Step 1 查询分解，走两级在线检索（OpenAlex 摘要层迭代精炼 + Europe PMC/PMC 全文层取细节），产出带连续编号引用 `[n]` 的分层综合答案。硬约束：
    ① 答案顶部显式标注「⚠ 本地知识缺口（knowledge_gap=true, retrieval_level=<值>），以下为在线文献兜底结果」；
    ② 全程遵守 live-literature 纪律铁律（只引池内论文、数值/极性有出处、abstract-only 降权标注、失败通道显式报告）；
    ③ 在 step 10 缺口行 `suggested_fill` 末尾追加「已触发在线兜底」；
    ④ 兜底答案是**补充而非替代**——仍有本地 Task/资源命中时须一并列出本地凭证；
    ⑤ **严禁编造**：不得用泛化剧本假装完成、不得返回「模拟检索结果/模拟数据/默认参数/历史案例」充数；联网通道不可用（离线）时**不得报错、不得中断整个任务**：如实标注「本地知识缺口 + 当前离线，在线兜底不可用」，把缺口作为已知限制交回上层继续任务其余部分（离线不构成 blocked）；
    ⑥ **单一集中通道 + 证据并回召回结果**：本 step 是在线兜底**唯一集中执行点**；产出的带编号引用与接地事实必须以 `online_evidence` 字段**并入本技能召回结果**（见输出格式），作为上层消费文献证据的唯一来源；orchestrator 见 `online_evidence` 非空**不得重复触发**（防限流/防双跑）；
    ⑦ **召回阶段证据边界（严禁自造）**：召回结果不得填入任何未经「用户提供/本地卡/在线引文[n]」支持的参数、阈值、数据集或研究对象；无法支持者只能标 `proposed_candidate(待确认)` 或留空；
    ⑧ **domain_match 标签与跨域降级（A 层门禁）**：`online_evidence.citations[]` 每条必须带 `domain_match ∈ {exact, adjacent, cross_domain}`——`exact`=研究对象与本任务目标域及具体对象直接一致；`adjacent`=同域不同子场景；`cross_domain`=不同应用领域。**cross_domain 只能作方法学参考，不得作本次参数/阈值/几何/工况来源**；违反则该参数降级 `proposed_candidate(待确认)` 并追加 gaps.jsonl `gate_hit=domain_mismatch, gate_layer=A_knowledge`。兜底后池内 `exact`=0：必须触发第二轮场景锚词精炼检索（锚词=目标域+具体研究对象）；仍为 0 则在 `online_evidence` 顶部标注「在线兜底形式成功、实质未命中目标域（exact=0）」，相关科学结论保持 BLOCKED/诚实 PARTIAL，不得用 adjacent/cross_domain 硬凑。`knowledge_gap=false` 不触发兜底，仅在缺口处按 step 10 记录。

12. **可执行落点识别**：Task 的 `edge:operation:*` 在某资源卡有对应实现且该卡带 `runnable:script` tag 时，该操作**本机可执行**：输出脚本相对路径与可直接运行命令；否则标「无可执行落点，仅规划」。

13. **组织输出**：按下方输出格式返回。

### Task 检索与传统资源检索的桥接

- Task 卡 `edge:resource:<category>/<name>` 指向的就是传统原语目录，解析成功后按传统路径 Read 其 `metadata.json` + 正文。
- **悬空边**视为资源缺失：不得编造资源能力，计入 `partial` 降级并写 `gaps.jsonl`。
- **反向边**：资源卡可用 `edge:task:<name>` 声明被哪些 Task 引用，便于从资源侧回查。
- TC 卡与传统资源卡**共用同一检索基础设施**（catalog_search 优先 + 文件系统降级），无需第二套索引。

---

## 召回流程

> **【检索路径优先级】** 原语可能存于两处：1) **数据库/Blob Store**（`catalog_search` + `catalog_resolve`，OneCode 内置 catalog）——默认路径，优先级最高；2) **本地文件系统**（Glob + Read `skills/onescience-primitives/assets/`）——降级路径，仅当路径 1 无结果且确认本地 assets 目录存在时使用。
> **强制规则**：召回**必须先尝试路径 1**，不得跳过；回退路径 2 后，命名直查与常规管道（步骤 0-9）的文件系统操作规则仍适用。

> 本技能无统一索引文件，原语信息以各资源目录 `metadata.json` 为主。必须先确定检索范围，再枚举资源目录逐个读 `metadata.json`，不要凭目录名猜测。
>
> **【路径规范】** `assets/` 绝对路径为 `skills/onescience-primitives/assets/`；三层嵌套 `<domain>/<category>/<primitive_name>/`。凡出现 `assets/<domain>/...` 均指代相对仓库根的 `skills/onescience-primitives/assets/<domain>/...`。Glob 必须用 `**` 递归模式（如 `assets/bio/**/metadata.json`），不得单层 `*` 漏目录；Read 必须拼接完整前缀 `skills/onescience-primitives/`。
>
> **【命名直查优先】** 执行常规管道（步骤 0-6）前先检查是否满足命名直查条件。

### 命名直查模式

调用方明确知道目标原语名称时，跳过召回管道直接定位返回。**触发条件**（同时满足）：a. `filters.keyword` 含可识别的原语目录名（如 `complex_structure_visualization`、`alphafold3`）；b. `filters.domain` 已明确指定。

**执行步骤**：
1. 从 `filters.keyword` 提取名称候选（规范化：下划线连接、去空格标点，与目录名比对）
2. **优先 `catalog_search`**（kind=primitive, domain, q=名称）；若命中，`catalog_resolve` 取 body/contract，跳步骤 6
3. **回退文件系统**：`catalog_search` 未命中且本地 assets 存在时，Glob `skills/onescience-primitives/assets/<domain>/**/<name>/metadata.json`（必须 `**` 递归）
4. 唯一匹配直接读 `metadata.json`；多匹配（跨 category）读全部取语义最接近
5. 未找到则回退常规管道（步骤 0-6）
6. 命中后直接跳步骤 7（组织内容），**跳过步骤 0-6 枚举、过滤、语义匹配和截断**
7. `why_matched` 标注 `named_lookup`

**约束**：命名直查是精确匹配辅助，不是语义搜索替代；keyword 含多个名称时分别执行；仍遵守内容组织规则（步骤 7-9）含白名单校验；不绕过强制协议（仍需经 `resource_retrieval_request` 发起）。

### 常规召回管道

仅在命名直查未命中时执行。

0. **优先 `catalog_search`**（kind=primitive，传 domain/keyword）；非空则 `catalog_resolve(part=body)` 取内容，跳过文件系统枚举。无结果时继续以下流程。
   **判定 domain scope**：`filters.domain` 明确 → 直接用该 domain，**不再读** `references/domain_profile.md`；未提供/为空/不可靠 → **必须先读** `domain_profile.md` 按领域信号回退判定；判定为 `climate|cfd|matchem|bio|general` 时只检索对应目录；`unknown` 时允许搜全部 domain 目录且输出 `detected_domain: unknown`。请求已路由生信且涉及生信工作流/模型/管线/应用选择时，可读 `references/bio_profile.md` 作候选排序提示（只辅助排序与边界解释，不能替代 `metadata.json` 证据）。
1. **判定 category scope**：请求明确指定模型/组件/管线/应用/可视化/工作流规划/输出格式/契约/数据库等类别时只检索对应 category；未指定则搜当前 domain scope 下全部实际 category。
   **【强制】可视化信号识别**：`user_request` 或 `filters.keyword` 出现任一信号时必须将 `visualization` 纳入检索范畴——显式可视化词（可视化/visualization/visualize/render）、三维渲染词（3D/三维/结构展示/interactive/交互式）、置信度着色词（pLDDT/PAE/confidence coloring/B-factor/chain coloring）、分子可视化工具（PyMOL/3Dmol/MolStar/NGL/cartoon/ribbon/surface/stick）、结构文件格式（.pdb/.cif/.mmcif/.pse/.pml）；即使主意图被判为 model/datapipe/application 也不可遗漏。
2. **枚举候选集**：在已定 domain/category 内 Glob `skills/onescience-primitives/assets/<domain>/**/metadata.json`（`**` 递归）得完整候选集。从每个匹配路径提取 domain/category/primitive_name 三层；路径拼接保留完整三层结构，不得省略中间 category 层。
3. **快速过滤**：仅当 `filters.keyword` 提供关键词时执行；结合目录名与 `metadata.json` 的 `name`/`domain`/`description`/`tags` 排除明显不相关资源。
4. **语义匹配**：遍历候选 `metadata.json`，对比 `user_request` 与 `description` 语义相关性。
5. **上下文增强**：结合 `task_state_summary` 筛选排序，但不能用上下文替代资源本身证据。
6. **按匹配度排序并截断**：返回最相关 **5-8 个**；无强相关则返回空列表，不要凑数。
   **【强制】多类别覆盖保障**：当检索范围为全部 category 且候选含多类实际资源时：先按匹配度得全序列；取前 5；若某实际存在的 category 全部资源未进前 5 且该 category 存在匹配度 ≥ 最高分 60% 的资源，则从该 category 追加 1 个最高分资源（可超出 5-8）；追加后总数不超 10，超出按匹配度去尾；追加项 `why_matched` 备注 `category_coverage`。目的：多类别隐含需求（如"分析蛋白质结构预测结果并可视化"）时 visualization 资源不被 model/component 挤掉。
7. **逐个组织内容**：按 `content_request` 读取并填充各命中资源 `content`。**`content_request` 非摘要、或请求含 `include_execution_assets: true` 时，必须先读取 `references/asset_materialization.md`**（含各内容类型读取规则、execution_assets 白名单校验与 64 KiB 物化流程、content 完整 YAML 格式、执行/知识资产强制规则）。摘要模式：只读 `metadata.json` 生成简短摘要。
8. **【强制】检索依赖组件**：命中资源为模型（`models` category）且需规格/使用知识时：读模型 `spec.md` 的 `# key_dependencies` → 提取依赖组件 → 在同 domain `components` 下检索各依赖组件目录 → 读其 `spec.md`/`usage.md`（若存在）→ 将信息作为 `dependent_components` 字段附加到模型资源输出。依赖组件在 `components` 不存在时在 `limitations` 说明缺失项。**此步不可跳过**：即使 `content_request` 为 `"摘要"`，也必须检索依赖组件并至少返回基本信息（name、description）。
9. **填充输出字段**：按「字段取值规则」推导 `detected_domain`、`task_intent`、各资源 `type`，并按「质量要求」生成 `why_matched`、摘要 `content`、`limitations`。**填充前必须先读取 `references/field_value_rules.md`**（domain/category scope 判定细则、枚举映射表、质量要求全文）。
   **【强制·跨路径兜底闸门，不可跳过】**本 traditional_resource 路径填充输出后**同样必须**执行上文 TC 检索步骤的 step 9b（跨路径实质命中判定）、step 10（缺口记录）、step 11（在线兜底）——不因走常规管道而豁免（否则 off-shape 场景会因回退本路径命中泛化卡而绕过兜底）：
   - 按 9b 计算 `knowledge_gap`：`matched_resources` 为空、或**仅**命中泛化 `workflow_planning_primitive`（legacy「文献综述/通用分析/通用建模流程/通用四步筛选」类卡）而无领域专属资源、或命中 domain 与请求不符 → 一律 `knowledge_gap=true`，`retrieval_level` 折算 `none`。
   - `knowledge_gap=true` 时按 step 10 追加 gaps.jsonl、按 step 11 强制调用 `onescience-live-literature` 联网兜底，`online_fallback` 置 `live_literature`；**严禁**把泛化卡当领域知识回答返回，更严禁编造模拟结果充数。
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

> `intent`：`resource`（默认）走传统原语路径；`task` 返回 Task 定义及关联 Method/Resource/Operation/Validation；`workflow` 返回 Workflow 的 Task Graph 及各 Task；`scenario` 返回 Scenario 及关联 Workflow 和 Task。

## 输出格式

与统一资源契约一致（`content` 完整格式与资产规则见 `references/asset_materialization.md`）：

```yaml
resource_retrieval_result:
  status: success | partial | failed
  query_summary: <需求摘要>
  detected_domain: <climate | cfd | matchem | bio | general | unknown>
  task_intent: <model | component | datapipe | application | tool | database | output-format | visualization | workflow | contract | mixed | task | scenario>
  retrieval_path: <traditional_resource | task_centric>
  retrieval_level: <full | partial | task_only | none>     # TC 路径产出；traditional 路径按 step 9b 折算
  knowledge_gap: <true | false>                            # step 9b 跨路径实质命中判定，在线兜底触发的唯一依据
  online_fallback: <not_triggered | live_literature>       # gap=true 时置 live_literature
  online_fallback_status: <online | offline | not_applicable>  # offline=联网失败/限流已优雅降级（不报错不停摆）
  online_evidence:                                         # 兜底真实检索到的文献证据（单一集中通道产出；orchestrator 见非空不得重复检索）
    citations: [ "[n] 标题 | venue | year | doi | domain_match=<exact|adjacent|cross_domain> | evidence_level=<full-text|abstract-only>" ]
    grounded_facts: [ "事实陈述（标注 [n] 出处 + domain_match）" ]   # cross_domain 文献只作方法学参考，不得作本次参数来源
    domain_match_summary: { exact: <int>, adjacent: <int>, cross_domain: <int> }  # exact=0 时必须已触发第二轮锚词检索
    # 为空（offline 或未触发）时上层必须进入证据边界模式：不得自造参数/数据/阈值充当本次结果
  matched_resources:
    - type: model_primitive | component_primitive | datapipe_primitive | application_primitive | tool_primitive | database_primitive | output_format_primitive | visualization_primitive | workflow_planning_primitive | contract_primitive | task_primitive | method_primitive | operation_primitive | validation_primitive | scenario_primitive | workflow_task_graph_primitive | atom_primitive
      path: assets/<domain>/<category>/<primitive_name>/
      name: <原语名称>
      why_matched: <匹配理由，1句话>
      limitations: <使用限制，1-2句话>
      content: <根据 content_request 组织的内容>
  gap_record:                                              # 仅 retrieval_level != full 时存在，与 gaps.jsonl 追加行同构
    gap_id: <string>
    missing_layer: <task | resource | operation | validation | atom | executable>
    dangling_edges: [<解析失败的 edge:* 值>]
    suggested_harvest: <string>
```

**TC 检索结果说明**（`retrieval_path=task_centric` 时）：条目可能含 `task_primitive`（content 为 `knowledge.md` 正文 + 沿 `edge:*` 展开资源；有可执行落点时附脚本路径与命令）、`scenario_primitive`/`workflow_task_graph_primitive`（Task Graph 与阶段门槛）、传统资源卡（沿 `edge:resource:*` 解析）、`atom_primitive`（statement/value/unit/evidence）。Method/Operation/Validation **不单独成条**，作为 task_primitive content 章节与词表边返回。

**knowledge_gap 说明**：`false`=命中领域专属 Task/资源，本地足以作答；`true`=本地没查到领域实质知识（none/task_only/空召回/仅泛化卡/domain 不符）——**泛化流程卡只讲「怎么做研究」，不等于领域回答，仅命中它一律 true**。true 时按 step 11 强制触发联网兜底并显式标注「本地知识缺口」；false 不触发。

## 按需读取

- 组织非摘要内容或处理 `include_execution_assets` 前：`references/asset_materialization.md`。
- 填充输出字段（常规管道步骤 9）前：`references/field_value_rules.md`。
- TC 卡 9 字段与 tags 边契约：`references/tc/card_contract.md`；原子事实：`references/tc/atoms.jsonl`；场景确定性索引：`references/tc/scenario_task_index.json`。
- domain 回退判定：`references/domain_profile.md`；生信召回提示：`references/bio_profile.md`。
