# 扩展你的科研领域经验

本指南面向想把自己的科研领域经验接入 `OneSkills` 的用户、领域专家和贡献者。

目标不是“复制一套新 skill”，而是在不破坏当前架构的前提下，把可复用的领域知识、规划经验或稳定执行流程接入现有能力体系。

## 先理解当前 OneSkills 架构

当前 `OneSkills` 以 `onescience-orchestrator` 为统一编排入口，按四层组织能力：

| 层级 | 名称 | 职责 | 典型形态 |
| --- | --- | --- | --- |
| 内核层 | orchestrator | 理解用户目标、召回资源、召回专家、融合计划、调度执行、维护 Task State | `onescience-orchestrator` |
| 资源层 | resource skills | 通过统一契约召回模型、数据、组件、应用、工作流知识 | `type=resource` skill |
| 专家层 | expert skills | 针对复杂任务做规划、取舍和 fallback，输出 `planner_proposal` | `type=expert` skill |
| 执行层 | executor skills | 落地稳定流程，返回可追踪的 `execution_result` | `type=executor` skill |

一个典型任务会按下面的方式流转：

```text
用户目标
-> onescience-orchestrator
-> 召回 type=resource 的资源摘要
-> 识别 intent_profile
-> 召回 type=expert 的专家规划
-> 融合为 global_plan
-> 调度 type=executor 执行
-> 记录 observation 并继续下一步
```

因此，扩展领域经验时不要优先修改 `onescience-orchestrator`。新增任务类型应优先通过资源 skill、专家 skill 或执行 skill 接入。

## 先判断你的经验属于哪一类

| 你的内容 | 推荐接入点 | 适合放什么 |
| --- | --- | --- |
| 模型、数据集、组件、应用、领域知识、工作流知识 | `type=resource` | 资源文件、规格说明、使用说明、规划知识 |
| 需要动态判断、方案取舍、步骤规划、失败回退 | `type=expert` | 规划规则、资源选择策略、`planner_proposal` |
| 有稳定入口、固定步骤、可验证输出 | `type=executor` | CLI/API 包装、脚本生成、运行验证、报告生成 |

如果只是某个项目的一次性经验，通常先不要新增 skill。更好的做法是把它整理成资源层的规划知识，等多次复用后再考虑 expert 或 executor 化。

## 最常见：把领域经验做成资源

大多数领域扩展都应该先进入资源层。资源可以是：

- 领域任务画像和术语说明
- 常见数据格式、变量、单位、坐标、质量要求
- 模型、组件、数据管线或应用的规格知识
- 使用示例、启动参数、依赖环境和限制
- 工作流规划知识、适用条件、失败模式和 fallback

资源应放在对应 `type=resource` skill 自己的 `assets/` 目录下，而不是绕过资源 skill 直接堆到公共目录。已有 `onescience-primitives` 负责 OneScience 原语资源召回；如果你的资源不属于它的边界，应新增或扩展对应的资源 skill。

推荐结构：

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

资源 skill 的关键约束：

- `SKILL.md` frontmatter 必须包含 `type: resource`。
- 必须接收 `resource_retrieval_request`。
- 必须返回 `resource_retrieval_result`。
- 调用方只能消费 `matched_resources[*].content`。
- `matched_resources[*].path` 只用于标识和绑定，不授权调用方直接读取资源文件。

最小输入输出契约：

```yaml
resource_retrieval_request:
  user_request: <用户需求描述>
  task_state_summary: <任务状态摘要，可选>
  content_request: <摘要 | 使用说明 | 规格说明 | 工作流规划知识 | 完整内容>
  filters:
    domain: <领域过滤，可选>
    keyword: <关键词过滤，可选>
```

```yaml
resource_retrieval_result:
  status: success | partial | failed
  detected_domain: <领域>
  task_intent: <任务意图>
  matched_resources:
    - type: <资源类型>
      path: <资源标识>
      name: <资源名称>
      why_matched: <匹配理由>
      limitations: <使用限制>
      content: <根据 content_request 返回的内容>
```

## 什么时候新增 expert skill

当你的领域经验不是“资料”，而是“判断过程”时，才考虑新增或扩展 `type=expert` skill。

适合 expert 的情况：

- 需要根据任务目标选择不同路线
- 需要在多个资源、模型或数据方案之间取舍
- 需要输出多阶段计划、依赖关系和风险说明
- 需要明确失败回退策略

不适合 expert 的情况：

- 只是补充一个模型卡、数据卡或组件说明
- 只是描述某个工具怎么用
- 只是某次项目中的人工经验
- 只是把 executor 的固定流程换个领域名复制一份

expert skill 必须只做规划，不写代码、不提交作业、不安装环境。它接收 orchestrator 的规划上下文，返回 `planner_proposal`，由 orchestrator 继续融合和调度。

frontmatter 示例：

```yaml
---
name: your-expert-skill
description: 说明该专家技能覆盖什么规划场景，何时由 orchestrator 召回，并返回 planner_proposal；不执行任务。
type: expert
---
```

## 什么时候新增 executor skill

当你的能力已经变成稳定流程，并且能产出可验证结果时，才考虑新增 `type=executor` skill。

适合 executor 的情况：

- 有固定 CLI、API、脚本入口或作业入口
- 步骤清晰，输入输出边界稳定
- 可以返回文件、报告、日志、元数据或验证结果
- 可以用 `execution_result` 描述执行状态和产物

不适合 executor 的情况：

- 还需要大量人工判断
- 只是领域知识说明
- 只是复制 `onescience-coder`、`onescience-runtime`、`onescience-installer` 的职责
- 只是 runtime 内部阶段的拆分，如单独把 `preflight` 或 `diagnose` 做成公开 skill

executor skill 接收 orchestrator 的 `step_handoff`，只完成当前步骤，不重新规划完整用户目标。

frontmatter 示例：

```yaml
---
name: your-executor-skill
description: 说明该执行技能处理什么稳定流程、输入输出边界是什么，并返回 execution_result。
type: executor
---
```

## 推荐接入路径

1. 写清楚这条领域经验解决什么问题。
2. 判断它是资源、专家规划，还是稳定执行。
3. 能资源化就先资源化，不要急着新增 executor 或 expert。
4. 如果新增资源，放到对应 `type=resource` skill 的 `assets/` 中，并补齐 `metadata.json`。
5. 如果新增 expert，确保它只返回 `planner_proposal`，不直接执行。
6. 如果新增 executor，确保它接收 `step_handoff` 并返回 `execution_result`。
7. 补充使用限制、失败条件和最小验证说明。
8. 更新相关 README 或贡献说明。

## PR 自检问题

- 是否没有把领域规则硬编码进 `onescience-orchestrator`？
- 是否先判断了 resource / expert / executor 的正确接入点？
- 新增资源是否通过 `type=resource` skill 暴露，而不是让调用方直接读 `assets/`？
- `metadata.json` 的 `description` 是否足够支持召回？
- expert 是否只规划，不执行？
- executor 是否只执行当前步骤，不重新定义用户目标？
- 是否写清楚适用范围、不适用场景和 fallback？
- 是否避免复制已有 skill 的职责？

## 进一步阅读

更完整的贡献规范、契约模板和 PR 检查项见：

- `docs/open-source/custom_skill_contribution.md`
- `skills/onescience-orchestrator/SKILL.md`
- `skills/onescience-primitives/SKILL.md`

## 一句话原则

领域知识先资源化，复杂决策再专家化，稳定流程才执行化；所有扩展都通过统一契约交给 `onescience-orchestrator` 召回、融合和调度。
