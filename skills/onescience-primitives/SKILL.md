---
name: onescience-primitives
description: OneScience 原语资源召回技能。根据自然语言需求检索相关原语资源（模型、组件、数据管线、应用、可视化规范、工作流规划、契约等），通过范围判定、快速过滤和语义匹配召回，按内容需求返回相应知识；不做科研规划与代码实现。
type: resource
---

# OneScience Primitives Resource

你负责从 `skills/onescience-primitives/assets/` 中找到最相关的 OneScience 原语，通过范围判定、快速过滤和语义匹配进行召回。不生成实现方案、不改代码、不执行脚本。

## 强制协议

本技能的 `assets/` 目录**仅供本技能内部使用**。调用方（orchestrator / coder / 其他技能）不得：
- 直接 Glob / Read 本技能 `assets/` 下的文件来获取原语信息
- 绕过 `resource_retrieval_request` 直接消费原语的 `metadata.json`、`spec.md`、`usage.md` 等文件内容
- 在未收到或构造 `resource_retrieval_request` 之前，禁止阅读或引用 `assets/` 下的任何文件

调用方必须通过 `resource_retrieval_request → resource_retrieval_result` 的完整闭环获取资源。

当本技能被上游技能调用时，`resource_retrieval_request` 是输入控制消息，不是需要回显给用户的最终内容。本技能直接执行召回流程并返回 `resource_retrieval_result`。

## 原语资产目录

```text
assets/
  <domain>/
    <category>/
      <resource_name>/
        metadata.json            ← 基础信息（name, type, domain, description, tags, version）
        spec.md                  ← 规格知识（架构、参数、依赖）
        usage.md                 ← 使用知识（启动示例、接口、限制）
        workflow_planning.md     ← 规划决策知识（时机、流程、约束）
        scripts/                 ← 可选受控执行资产；必须由 metadata.json.execution_assets 白名单声明
```

当前 `assets/` 顶层按 domain 组织，实际目录以仓库中的现状为准；当前可见的顶层 domain 包括：

- `bio`
- `cfd`
- `climate`
- `matchem`

每个 domain 下的 category 目录可能不同，按**实际存在的目录**检索，不要求所有 domain 都具有同一套子目录。当前常见 category 包括：

- `components`
- `models`
- `datapipes`
- `application`
- `visualization`
- `workflow-planning`
- `contracts`

## 召回流程

> 本技能没有统一索引文件，原语信息以各资源目录下的 `metadata.json` 为主。因此必须先确定检索范围，再枚举该范围内的资源目录并逐个读取 `metadata.json`，不要凭目录名猜测。

0. **判定 domain scope**：先判断调用方是否通过 `filters.domain` 显式提供 domain。
   - 若 `filters.domain` 明确给出，则**直接使用调用方提供的 domain**，只检索对应的 `assets/<domain>/`，且**不要再读取** `skills/onescience-primitives/references/domain_profile.md` 做二次判断
   - 若 `filters.domain` 未提供、为空或不可靠，则**必须先读取** `skills/onescience-primitives/references/domain_profile.md`，再结合 `user_request` 与 `task_state_summary` 按其中定义的领域信号进行回退判定
   - 回退判定结果若为 `climate | cfd | matchem | bio`，则只检索对应的 `assets/<domain>/`
   - 回退判定结果若为 `unknown`，说明无法稳定路由到单一领域；此时允许检索 `assets/` 下全部 domain 目录，但输出中的 `detected_domain` 必须保持为 `unknown`
   - 当请求已路由到生信领域，且涉及生信工作流、模型/数据管线/应用选择或多候选资源取舍时，可读取`skills/onescience-primitives/references/bio_profile.md`文档作为召回提示；该文件只辅助候选排序和边界解释，不能替代 `metadata.json` 证据
1. **判定 category scope**：根据 `user_request`、`content_request`、`filters.keyword`、`task_state_summary` 判断是否明确指定资源类别。
   - 若明确指定模型、组件、数据管线、应用、可视化规范、工作流规划或契约类资源，则只检索对应 category
   - 若未明确指定，则检索当前 domain scope 下全部实际存在的 category 目录
   - **【强制】可视化信号识别**：当 `user_request` 或 `filters.keyword` 中出现以下任一信号时，必须将 `visualization` 纳入检索范畴：
     - 显式可视化词：`可视化`、`visualization`、`visualize`、`visual`、`render`、`rendering`
     - 三维结构渲染词：`3D`、`三维`、`结构展示`、`structure view`、`interactive`、`交互式`
     - 置信度着色词：`pLDDT`、`PAE`、`confidence coloring`、`B-factor`、`chain coloring`
     - 分子可视化工具名：`PyMOL`、`3Dmol`、`MolStar`、`NGL`、`cartoon`、`ribbon`、`surface`、`stick`
     - 结构文件格式（需渲染）：`.pdb`、`.cif`、`.mmcif`、`.pse`、`.pml`
     - 当上述任一信号出现时，即使主意图被判定为 model/datapipe/application，也必须将 `visualization` category 纳入检索范围，不可遗漏
2. **枚举候选集**：在已确定的 domain/category scope 内，列出所有资源目录，得到完整候选集。
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
   - `"使用说明"`：读取 `usage.md`（若存在）
   - `"规格说明"`：读取 `spec.md`（若存在）
   - `"工作流规划知识"`：读取 `workflow_planning.md`（若存在）
   - `"完整内容"`：只读取 `metadata.json`、`spec.md`、`usage.md`、`workflow_planning.md` 中实际存在的文件并组织为结构化内容；不得因为请求完整内容而自动返回任意脚本
   - 当且仅当 `include_execution_assets: true` 时，按以下子步骤物化受控执行资产：
   a. 从命中资源的 `metadata.json.execution_assets` 读取白名单数组。
   b. 遍历白名单中的每一项资产声明，以 primitive 目录（即 `assets/<domain>/<category>/<resource_name>/`）为基准拼接相对路径，得到资产的绝对磁盘路径。
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

## 输入格式

```yaml
resource_retrieval_request:
  user_request: <用户需求描述>
  task_state_summary: <当前任务状态摘要，可选>
  content_request: <内容需求，可选>
  include_execution_assets: <true | false，可选，默认 false>
  filters:
    domain: <领域过滤，可选>
    keyword: <关键词过滤，可选>
```

## 输出格式

与统一资源契约保持一致：

```yaml
resource_retrieval_result:
  status: success | partial | failed
  query_summary: <需求摘要>
  detected_domain: <climate | cfd | matchem | bio | unknown>
  task_intent: <model | component | datapipe | application | visualization | workflow | contract | mixed>
  matched_resources:
    - type: model_primitive | component_primitive | datapipe_primitive | application_primitive | visualization_primitive
      path: assets/<domain>/<category>/<primitive_name>/
      name: <原语名称>
      why_matched: <匹配理由，1句话>
      limitations: <使用限制，1-2句话>
      content: <根据 content_request 组织的内容>
```

`content` 完整格式（仅当 `content_request` 为 `"完整内容"` 时）：

```yaml
content:
  metadata: <metadata.json 内容>
  spec: <spec.md 内容>
  usage: <usage.md 内容>
  workflow_planning: <workflow_planning.md 内容>
  execution_assets:
    - path: <metadata.json.execution_assets 中声明的相对路径>
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
- 只允许 `metadata.json.execution_assets` 中逐项声明的相对路径；拒绝未声明文件、绝对路径、`..` 和路径穿越。
- 规范化后的路径必须仍位于当前 primitive 目录内。
- 返回前校验 SHA-256；不匹配时不返回该资产内容，逐资产标记 `status: failed` 及 `reason: sha256_mismatch`（记录期望值与实际值），但不应影响其他已通过校验的资产。
- 调用方只能消费 `content.execution_assets`，不得沿 `matched_resources[].path` 直接读取文件。
- 大文件处理：≤ 64 KiB 的文本文件直接内联到 `content` 字段；> 64 KiB 的文件（如 3Dmol.js ~150KB、HTML 模板 ~200KB）物化到工作区 `.onescience_assets/<primitive_name>/<version>/` 目录，`status` 设为 `materialized`，通过 `materialized_path` 传递绝对路径。
- 状态汇总：必须同时返回 `execution_assets_summary`，便于调用方在不解析全部资产明细的前提下快速判断整体可用性。
- 部分失败不阻塞全部：只要至少有一个核心资产（如 `render_complex_structure.py`）`available` 或 `materialized`，结果 `status` 可为 `partial` 而非 `failed`，让调用方自行降级决策。

## 字段取值规则

输出中的枚举字段不能凭空填写，按以下规则从数据推导：

- **`domain scope` 判定**：先判断请求是否路由到单个 domain。
  - `filters.domain` 明确时优先使用，且一旦使用就不要再读取 `domain_profile.md` 进行二次判定
  - `filters.domain` 缺失时，必须读取 `skills/onescience-primitives/references/domain_profile.md`，按其中标准化规则将请求映射到 `bio | cfd | climate | matchem | unknown`
  - 目录路由值按当前 assets 顶层目录解释，如 `bio | cfd | climate | matchem`
  - 若回退判定为 `unknown`，则不路由到单个目录，而是检索全部 domain 目录并保持 `detected_domain: unknown`
- **`category scope` 判定**：按自然语言语义映射到 category 目录。
  - 模型 / `model` → `models`
  - 组件 / `module` / `block` / `encoder` / `decoder` → `components`
  - 数据管线 / `datapipe` / `dataset` / `loader` / `preprocessing` → `datapipes`
  - 应用 / `app` / `toolkit` / `template` → `application`
  - 可视化 / `visualization` / `visualize` / `visual` / `render` / `rendering` / `3D` / `三维` / `结构展示` / `interactive` / `交互式` / `pLDDT` / `PAE` / `PyMOL` / `3Dmol` / `cartoon` / `ribbon` / `surface` / `stick` / `.pdb` / `.cif` / `.mmcif` → `visualization`
  - 工作流规划 / `planning` / `route` / `decision` → `workflow-planning`
  - 若请求未明确 category，则检索当前 domain scope 下全部实际存在的 category 目录
  - 当 `filters.keyword` 中包含明确的可视化信号但 `user_request` 未直接体现时，仍须将 `visualization` category 纳入检索范围
- **`detected_domain`**：按标准化 domain 枚举输出 `climate | cfd | matchem | bio | unknown`。
  - 若 `filters.domain` 已明确提供，则优先使用该值作为检索路由依据；输出时仍需与命中资源的 `metadata.json.domain` 保持一致性
  - 若 `filters.domain` 缺失，则以 `domain_profile.md` 回退判定结果作为领域判断基线
  - 若命中结果跨多个不兼容 domain、或回退判定本身为 `unknown`、或资源证据不足以支撑单一领域，则填 `unknown`
- **`matched_resources[].type`**：优先由资源所在 category 与 `metadata.json.type` 共同推导。
  - `models` 下的 `model` → `model_primitive`
  - `components` 下的 `component` 或普通 `module` → `component_primitive`
  - `datapipes` 下的 `datapipe` → `datapipe_primitive`
  - `application` 下的 `application` → `application_primitive`
  - `visualization` 下的 `visualization` → `visualization_primitive`
  - 若 `metadata.json.type` 与目录语义冲突，优先采用更能反映资源用途的目录语义，并在 `limitations` 中说明
- **`task_intent`**：根据 `user_request` 的主要意图判断。
  - 需要完整模型能力时填 `model`
  - 需要组件、模块、算子或内部结构时填 `component`
  - 需要数据准备、数据处理、数据接口时填 `datapipe`
  - 需要模板、脚本集合、分析工具或交付应用时填 `application`
  - 需要结构、数据或模型结果的视觉呈现规范时填 `visualization`
  - 需要契约、接口约束或对接规则时填 `contract`
  - 需要工作流规划、路由、决策知识时填 `workflow`
  - 多种意图并存且无法归一时填 `mixed`

## 质量要求

- 先判定 domain scope，再判定 category scope；不要跳过范围判定直接做全局模糊搜索。
- 调用方给出 `filters.domain` 时，必须直接使用该值路由，且不得再读取 `domain_profile.md` 做二次领域判断。
- 调用方未给出 `filters.domain` 时，必须先读取 `skills/onescience-primitives/references/domain_profile.md` 做回退判定。
- 回退判定为 `climate`、`cfd`、`matchem` 或 `bio` 时，只能搜索对应 domain 目录。
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
