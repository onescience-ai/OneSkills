# Custom Skill Contribution Guide

本指南面向 `OneSkills` 用户与贡献者，说明如何在当前架构下贡献新的领域经验、资源知识或自定义 skill。

核心原则：**资源也通过 skill 接入。新增资源不要直接堆到 `skills/onescience-primitives/assets/`，而应实现或扩展对应资源类型的 `type=resource` skill，并把资源文件放在该 skill 自己的 `assets/` 目录下。**

## 一、当前架构分层

`OneSkills` 现在按四层组织新增能力：

| 层级 | 名称 | 职责 | 典型形态 |
| --- | --- | --- | --- |
| LAYER 1 | 内核层 | 意图理解、资源召回、专家召回、计划融合、执行调度、状态维护 | `onescience-orchestrator` |
| LAYER 2 | 资源层 | 通过 `type=resource` skill 召回资源摘要和详细内容 | 各类资源技能及其 `assets/` |
| LAYER 3 | 专家层 | 处理复杂规划、规则判断、fallback 设计，输出 `planner_proposal` | `type=expert` skill |
| LAYER 4 | 执行层 | 执行稳定流程，返回可验证的 `execution_result` | `type=executor` skill |

新增任务类型时，不应改大 `orchestrator` 的领域规则；应通过资源技能、专家规划 skill 或执行 skill 扩展。

## 二、先判断接入点

任何新增能力先按下面三个接入点归位：

| 接入点 | 适用对象 | 放置位置 | 输出给系统的形态 |
| --- | --- | --- | --- |
| A：资源技能化 | 可被召回、复用的模型 / 数据 / 组件 / 应用 / 工作流知识 | 对应 `type=resource` skill 的 `assets/` | `resource_retrieval_result` |
| B：执行技能化 | 有稳定入口、步骤固定、结果可验证的执行流程 | 新增或扩展 `type=executor` skill | `execution_result` |
| C：专家化 | 有复杂判断规则，需要按任务动态规划和 fallback | 新增或扩展 `type=expert` skill | `planner_proposal` |

判断规则：

- 能被调用、需要复用的“能力或知识” → 接入点 A：资源技能化。
- 有稳定 CLI / API / 作业入口，产出可验证结果 → 接入点 B：执行技能化。
- 需要根据任务特征做规划、取舍、回退 → 接入点 C：专家化。
- 仍是轻量、未验证、暂不值得独立固化的经验 → 先沉淀到对应资源 skill 的规划知识资源中。

## 三、如何新增资源

资源贡献的落点是“对应资源类型的 skill”，不是一个集中式公共 assets 目录。

### 1. 资源 skill 结构

新增资源类型时，创建或扩展一个 `type=resource` skill，例如：

```text
skills/<resource-skill-name>/
  SKILL.md
  assets/
    <domain>/
      <category>/
        <resource_name>/
          metadata.json
          spec.md
          usage.md
          workflow_planning.md
  references/
    <retrieval_rules>.md
```

说明：

- `SKILL.md` 定义资源召回范围、输入输出契约、过滤规则和内容组织方式。
- `assets/` 存放该资源 skill 私有管理的资源文件。
- `references/` 存放该资源 skill 自己的检索规则、领域路由规则或 schema 说明。
- 调用方只能通过 `resource_retrieval_request -> resource_retrieval_result` 获取资源内容，不能直接读取任何 resource skill 的 `assets/`。

不要把新增资源直接放到：

```text
skills/onescience-primitives/assets/
```

### 2. Resource skill frontmatter

```yaml
---
name: your-resource-skill
description: 说明该资源技能负责召回哪类资源、覆盖什么领域、何时使用；必须说明它返回 resource_retrieval_result，不做规划、不执行任务。
type: resource
---
```

### 3. 资源文件建议

| 文件 | 作用 | 服务对象 |
| --- | --- | --- |
| `metadata.json` | 基础识别信息，如 `name`、`type`、`domain`、`description`、`tags`、`version` | 资源召回、快速匹配 |
| `spec.md` | 规格知识，如架构、输入输出、依赖、源码锚点、实现风险 | coder / executor |
| `usage.md` | 使用知识，如启动方式、接口、资源需求、限制、常见失败 | executor |
| `workflow_planning.md` | 规划决策知识，如 when to use、procedure、constraints、fallback | expert / orchestrator |

不同资源类型可以调整字段，但 `metadata.json` 中的 `description` 必须足够支持召回。

### 4. Resource skill 输入输出契约

所有 `type=resource` skill 都必须接收统一输入：

```yaml
resource_retrieval_request:
  user_request: <用户需求描述>
  task_state_summary: <任务状态摘要，可选>
  content_request: <内容需求，可选>
  filters:
    domain: <领域过滤，可选>
    keyword: <关键词过滤，可选>
```

必须返回统一输出：

```yaml
resource_retrieval_result:
  status: success | partial | failed
  query_summary: <需求摘要>
  detected_domain: <领域>
  task_intent: <任务意图>
  matched_resources:
    - type: <具体资源类型>
      path: <资源标识或来源路径>
      name: <资源名称>
      why_matched: <匹配理由>
      limitations: <使用限制>
      content: <根据 content_request 组织的摘要、文本或结构化内容>
```

`matched_resources[].content` 是调用方唯一允许消费的资源内容载体。`path` 只用于追踪和绑定，不授权调用方直接读取底层文件。

## 四、什么时候新增非资源 skill

只有满足以下条件时，才建议新增 `type=expert` 或 `type=executor` skill：

- 现有资源 skill 或现有执行 / 专家 skill 无法承接。
- 该能力会被反复复用。
- 它有清晰输入、输出和边界。
- 它不是对 `coder/runtime/installer` 等通用执行技能的领域化复制。
- 它可以通过 `type=expert` 或 `type=executor` 明确接入 orchestrator。

不建议新增 skill 的情况：

- 只是补充一个模型、数据集、组件、应用或模板知识；这应先做成资源 skill 的资源。
- 只是把某次项目经验整理成说明；这应先沉淀为资源规划知识。
- 只是换领域名复制一份 `coder/runtime/installer`。
- 只是把 runtime 内部 `discover/preflight/execute/diagnose` 的某个阶段拆成公开 skill。
- 只是把某个智能体偏好写成通用规则。

## 五、如何新增 executor skill

适用于“流程固定且必须严格按步骤执行”的能力，例如数据集构建器、评估器、稳定 CLI 包装器、作业提交入口。

### 1. Executor frontmatter

```yaml
---
name: your-executor-skill
description: 简洁说明该执行技能处理什么任务、何时使用、输入输出边界；必须说明返回 execution_result。
type: executor
---
```

### 2. 输入契约

执行技能接收 orchestrator 的当前步骤交接，不重新规划整个用户目标：

```yaml
step_handoff:
  step_id: <步骤ID>
  execution_skill: <执行技能名称>
  step_goal: <本步骤目标>
  task_context:
    user_goal: <用户最终目标>
    constraints: <约束列表>
    relevant_artifacts: <相关产物>
  resource_bindings:
    - path: <资源路径>
      type: <资源类型>
      purpose: <用途>
  inputs: <执行所需输入>
  required_outputs: <要求输出>
  completion_criteria: <完成标准>
```

### 3. 输出契约

必须返回：

```yaml
execution_result:
  skill: <执行技能名称>
  status: success | partial | failed | blocked
  artifacts:
    <产物清单>
  observation:
    summary: <执行摘要>
    completed: <已完成内容>
    missing: <缺失项>
    risks: <风险>
    next_recommendation: <下一步建议>
```

如果执行需要模型、数据、组件或工作流知识，必须通过 `type=resource` skill 获取资源内容；不要直接读取任何 resource skill 的 `assets/`。

## 六、如何新增 expert skill

适用于“需要动态规划、资源取舍和 fallback”的能力，例如某类科研流程规划、评估方案设计、复杂数据处理路线选择。

### 1. Expert frontmatter

```yaml
---
name: your-expert-skill
description: 简洁说明该专家技能覆盖的规划场景、何时使用、输出什么 planner_proposal；必须说明不执行任务。
type: expert
---
```

### 2. 输入契约

专家技能接收 orchestrator 分配的规划方面：

```json
{
  "task_state": {},
  "intent_profile": {},
  "assigned_aspect": {
    "aspect_id": "string",
    "goal": "string",
    "evidence": []
  },
  "available_resource_summaries": [],
  "available_execution_skills": [],
  "latest_observation": {}
}
```

### 3. 输出契约

通用 expert skill 应返回当前架构的标准 `planner_proposal`：

```json
{
  "planner_id": "your-expert-skill",
  "covered_aspect": "string",
  "confidence": "high|medium|low",
  "plan_fragment": [
    {
      "stage_id": "string",
      "goal": "string",
      "depends_on": [],
      "execution_skill": "string|null",
      "required_resources": [
        {
          "resource_type": "summary|knowledge|implementation_asset|contract|runtime|evaluation",
          "query": "string",
          "required": true
        }
      ],
      "expected_artifacts": [],
      "completion_criteria": [],
      "fallback": "string"
    }
  ],
  "resource_preferences": [],
  "risks": [],
  "conflicts": [],
  "blocked_reason": null
}
```

特定专家 skill 可以在不破坏上述字段的前提下增加 `planner_payload` 等扩展字段。专家 skill 只做规划，不直接写代码、不提交作业、不安装环境，也不要绕过 orchestrator 调度执行技能。

## 七、从经验到技能的演进路径

建议按下面路径沉淀能力：

1. 隐式经验：临时 prompt、人工操作、一次性脚本。
2. 资源化沉淀：写入对应 `type=resource` skill 的 `assets/`。
3. 反复验证：在真实任务中被多次召回，收集 observation 和失败条件。
4. 技能化固化：流程稳定、边界清楚、产出可验证后，再判断固化为 `type=executor` 或 `type=expert`。
5. 内核无感扩展：注册后由 orchestrator 召回或调度，不修改主控逻辑。

落地判据：

- 只是可复用知识、资源卡片、模型卡、数据卡、组件契约 → `type=resource`。
- 步骤稳定、依赖强、必须严格按顺序执行 → `type=executor`。
- 需要根据任务特征做规划、资源取舍和 fallback → `type=expert`。

## 八、推荐提交流程

1. 写清楚新增能力解决什么问题。
2. 按接入点 A/B/C 判断应该做成 resource、executor 还是 expert。
3. 优先做最小改动：能做资源 skill 就不新增执行 / 专家 skill。
4. 按契约补齐必要文件：
   - resource：`SKILL.md`、`assets/` 下的资源文件、必要的检索规则
   - executor：`SKILL.md`、必要的 `references/`、`scripts/` 或 `assets/`
   - expert：`SKILL.md`、必要的规划协议或参考文档
5. 检查与现有 skill 的职责边界是否重叠。
6. 补充可验证示例、失败条件或使用限制。
7. 提交 PR，并在说明中写明接入点、skill 类型和验证方式。

## 九、PR 自查清单

- 是否没有修改 `onescience-orchestrator` 的领域硬编码规则？
- 新增资源是否放在对应 `type=resource` skill 的 `assets/` 下，而不是直接放入 `skills/onescience-primitives/assets/`？
- resource skill 是否接收 `resource_retrieval_request` 并返回 `resource_retrieval_result`？
- resource skill 是否明确禁止调用方直读自己的 `assets/`？
- 如果新增资源，`metadata.json` 的 `description` 是否足够支持召回？
- 如果新增 executor，是否接收 `step_handoff` 并返回标准 `execution_result`？
- 如果新增 expert，是否接收 planner 输入并返回标准 `planner_proposal`？
- 是否写清楚不适用场景、约束和 fallback？

## 十、一句话原则

资源通过 `type=resource` skill 接入，执行通过 `type=executor` skill 落地，复杂决策通过 `type=expert` skill 规划；三者都遵守统一契约，由 orchestrator 统一召回、融合和调度。
