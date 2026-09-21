# OneScience Executor Dispatch Convention

## 适用范围

本卡片定义 OneScience 工作流编排中 executor 技能的正确调用方式，包括 step_handoff 格式规范、executor 输入输出契约和状态传递机制。适用于任何需要通过 orchestrator 调度 executor 执行具体步骤的科研工作流。

## 输入

- orchestrator 编排计划：包含步骤列表和依赖关系
- executor 技能列表：coder、runtime、data-standardizer 等
- step_handoff 结构：每个步骤的输入参数和前置条件

## 输出

- 每个步骤的 execution_result
- 步骤间的状态传递
- 最终任务交付物

## 流程节点

1. **步骤解析** → orchestrator 解析编排计划，识别每个步骤的 executor 类型
2. **前置条件检查** → 验证每个步骤的输入参数和依赖是否满足
3. **step_handoff 构建** → 按标准格式构建步骤交接参数
4. **executor 调用** → 调用对应技能执行步骤
5. **结果回传** → executor 返回 execution_result 给 orchestrator
6. **状态更新** → orchestrator 更新 Task State 并传递到下一步

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| step_handoff 格式 | YAML | [D1] | 标准交接结构 |
| executor 输入 | step_handoff + task_context | [D1] | 包含步骤目标和上下文 |
| executor 输出 | execution_result | [D1] | 包含状态、产物和观察 |
| 状态传递 | Task State | [D1] | orchestrator 维护的全局状态 |
| 最小 executor 调用数 | >= 步骤数 | [D2] | 每个步骤至少一次 executor 调用 |

## 边界与分流

- **executor 技能不可用**：降级为 orchestrator 直接执行，但在结果中标注降级
- **step_handoff 格式不匹配**：尝试适配或拒绝执行并报错
- **executor 执行失败**：根据重试策略决定是否重试或标记步骤失败
- **跨步骤依赖断裂**：暂停执行并报告依赖错误

## 质量检查

- 验证每个步骤有对应的 executor skill_call 记录
- 验证 step_handoff 包含所有必需字段（step_id, execution_skill, step_goal, inputs）
- 验证 execution_result 包含 status, artifacts, observation
- 验证步骤间状态传递一致性

## 回退策略

- 若 executor 调用失败，orchestrator 可直接执行简单步骤（如数据下载）
- 若所有 executor 不可用，输出降级结果并标注模拟数据
- 建议：在 agent-events.log 中记录每个步骤的 executor 调用以便追溯

## 资源召回建议

- 在 orchestrator 编排任何工作流时召回本卡
- 配套资源：onescience-coder、onescience-runtime、onescience-primitives

## 补充证据

[D1] OneScience Orchestrator SKILL.md, OneScience, skills/onescience-orchestrator/SKILL.md（accessed_at 2026-09-21）
[D2] OneScience Coder SKILL.md, OneScience, skills/onescience-coder/SKILL.md（accessed_at 2026-09-21）

## 证据来源

[1] 基于 OneScience 技能库编排规范和 orchestrator/coder SKILL.md 中的契约定义
