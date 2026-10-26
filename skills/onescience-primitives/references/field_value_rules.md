# 字段取值规则与质量要求全文（从 SKILL.md 剥离）

> **在「填充输出字段」（召回流程步骤 9）之前必须先读取本文**。原会话日志证明这两节长期位于 SKILL.md 尾部被输出截断丢弃，剥离到本文后按需读取反而真正可见。

## 字段取值规则

输出中的枚举字段不能凭空填写，按以下规则从数据推导：

- **`domain scope` 判定**：先判断请求是否路由到单个 domain。
  - `filters.domain` 明确时优先使用，且一旦使用就不要再读取 `domain_profile.md` 进行二次判断
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
