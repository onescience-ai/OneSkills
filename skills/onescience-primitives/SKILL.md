---
name: onescience-primitives
description: OneScience 原语资源召回技能。根据自然语言需求检索相关原语资源（模型、组件、数据管线、应用、工作流规划、契约等），通过范围判定、快速过滤和语义匹配召回，按内容需求返回相应知识；不做科研规划与代码实现。
type: resource
---

# OneScience Primitives Resource

你负责从 `skills/onescience-primitives/assets/` 中找到最相关的 OneScience 原语，通过范围判定、快速过滤和语义匹配进行召回。不生成实现方案、不改代码、不执行脚本。

## 强制协议

本技能的 `assets/` 目录**仅供本技能内部使用**。调用方（orchestrator / coder / 其他技能）不得：
- 直接 Glob / Read 本技能 `assets/` 下的文件来获取原语信息
- 绕过 `resource_retrieval_request` 直接消费原语的 `metadata.json`、`spec.md`、`usage.md` 等文件内容
- 在未输出 `resource_retrieval_request` 之前，阅读或引用 `assets/` 下的任何文件

调用方必须通过 `resource_retrieval_request → resource_retrieval_result` 的完整闭环获取资源。

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
- `workflow-planning`
- `contracts`

## 召回流程

> 本技能没有统一索引文件，原语信息以各资源目录下的 `metadata.json` 为主。因此必须先确定检索范围，再枚举该范围内的资源目录并逐个读取 `metadata.json`，不要凭目录名猜测。

0. **判定 domain scope**：先判断调用方是否通过 `filters.domain` 显式提供 domain。
   - 若 `filters.domain` 明确给出，则**直接使用调用方提供的 domain**，只检索对应的 `assets/<domain>/`，且**不要再读取** `skills/onescience-primitives/references/domain_profile.md` 做二次判断
   - 若 `filters.domain` 未提供、为空或不可靠，则**必须先读取** `skills/onescience-primitives/references/domain_profile.md`，再结合 `user_request` 与 `task_state_summary` 按其中定义的领域信号进行回退判定
   - 回退判定结果若为 `climate | cfd | matchem | bio`，则只检索对应的 `assets/<domain>/`
   - 回退判定结果若为 `unknown`，说明无法稳定路由到单一领域；此时允许检索 `assets/` 下全部 domain 目录，但输出中的 `detected_domain` 必须保持为 `unknown`
1. **判定 category scope**：根据 `user_request`、`content_request`、`task_state_summary` 判断是否明确指定资源类别。
   - 若明确指定模型、组件、数据管线、应用、工作流规划或契约类资源，则只检索对应 category
   - 若未明确指定，则检索当前 domain scope 下全部实际存在的 category 目录
2. **枚举候选集**：在已确定的 domain/category scope 内，列出所有资源目录，得到完整候选集。
3. **快速过滤**：仅当 `filters.keyword` 提供了关键词时执行；结合目录名、`metadata.json` 的 `name`、`domain`、`description` 与 `tags` 排除明显不相关的资源。未提供关键词时跳过本步。
4. **语义匹配**：遍历剩余每个候选资源的 `metadata.json`，对比 `user_request` 与 `description` 字段的语义相关性。
5. **上下文增强**：结合 `task_state_summary` 进一步筛选和排序，但不能用上下文替代资源本身的证据。
6. **按匹配度排序并截断**：按语义相关性排序，返回最相关的 **3-5 个**资源；没有强相关资源时返回空列表，不要凑数。
7. **逐个组织内容**：对每个命中的资源，按 `content_request` 分别读取并填充该资源的 `content` 字段：
   - 留空或 `"摘要"`：优先只读取 `metadata.json`，生成简短摘要，`description` 字段的关键信息不进行过度压缩
   - `"使用说明"`：读取 `usage.md`（若存在）
   - `"规格说明"`：读取 `spec.md`（若存在）
   - `"工作流规划知识"`：读取 `workflow_planning.md`（若存在）
   - `"完整内容"`：读取该资源目录下实际存在的相关文件并组织为结构化内容（见下方 `content` 完整格式）
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
  task_intent: <model | component | datapipe | application | workflow >
  matched_resources:
    - type: model_primitive | component_primitive | datapipe_primitive | application_primitive
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
```

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
  - 工作流规划 / `planning` / `route` / `decision` → `workflow-planning`
  - 若请求未明确 category，则检索当前 domain scope 下全部实际存在的 category 目录
- **`detected_domain`**：按标准化领域枚举输出 `climate | cfd | matchem | bio | unknown`。
  - 若 `filters.domain` 已明确提供，则优先使用该值作为检索路由依据；输出时仍需与命中资源的 `metadata.json.domain` 保持一致性
  - 若 `filters.domain` 缺失，则以 `domain_profile.md` 回退判定结果作为领域判断基线
  - 若命中结果跨多个不兼容 domain、或回退判定本身为 `unknown`、或资源证据不足以支撑单一领域，则填 `unknown`
- **`matched_resources[].type`**：优先由资源所在 category 与 `metadata.json.type` 共同推导。
  - `models` 下的 `model` → `model_primitive`
  - `components` 下的 `component` 或普通 `module` → `component_primitive`
  - `datapipes` 下的 `datapipe` → `datapipe_primitive`
  - `application` 下的 `application` → `application_primitive`
  - 若 `metadata.json.type` 与目录语义冲突，优先采用更能反映资源用途的目录语义，并在 `limitations` 中说明
- **`task_intent`**：根据 `user_request` 的主要意图判断。
  - 需要完整模型能力时填 `model`
  - 需要组件、模块、算子或内部结构时填 `component`
  - 需要数据准备、数据处理、数据接口时填 `datapipe`
  - 需要模板、脚本集合、分析工具或交付应用时填 `application`
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
- 通过语义匹配 `metadata.json` 的 `description` 字段召回，不依赖额外索引文件。
- `why_matched` 说明 query 与 description 的对应关系（1句话）。
- 摘要模式下的 `content` 从 `description` 字段提取核心能力一段话。
- `limitations` 优先从 `spec.md` 或 `workflow_planning.md` 的约束部分提炼；若相关文件缺失，可根据 `metadata.json` 已知边界简要说明。
- 某些资源可能缺少 `usage.md`、`spec.md` 或 `workflow_planning.md`；若请求内容部分存在、部分缺失，可返回 `status: partial`，并在 `limitations` 中说明缺失项。
- 没有匹配资源时返回空 `matched_resources: []`，不编造资源。
