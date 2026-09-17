# Executor 技能调用契约

## 适用范围

**触发条件**：orchestrator execution 阶段，调用 executor_step 类型的步骤时。

**适用场景**：
- 所有 executor_step 类型的步骤执行
- orchestrator 需要通过 skill 工具调用 executor 技能时
- 需要传递 step_handoff 的场景

**不适用场景**：
- 非 executor_step 类型的步骤（如 expert_step）
- 直接文件操作而非技能调用的场景

## 输入

- **step_handoff**：包含 step_id、inputs、outputs、checks 等信息的交接结构
- **executor_skill_name**：要调用的 executor 技能名称
- **task_context**：任务上下文（用户目标、约束、相关产物）

## 输出

- **execution_result**：executor 技能返回的执行结果
- **产物文件**：executor 技能生成的输出文件
- **状态更新**：task_state.json 中的步骤状态

## 流程节点

```
orchestrator 准备执行 executor_step
    ↓
构建 step_handoff 结构
    ↓
通过 skill 工具调用 executor 技能
    ↓
executor 技能接收 step_handoff
    ↓
[资源召回] 调用 type=resource 技能获取规格知识、使用知识和规划决策知识
    ↓
按分步流程执行
    ↓
返回 execution_result
    ↓
orchestrator 更新 task_state.json
```

**每步操作**：
1. orchestrator 从 Global Plan 提取 step 信息
2. 构建 step_handoff：`{step_id, execution_skill, step_goal, task_context, inputs, expected_outputs}`
3. 通过 skill 工具调用 executor 技能并传递 step_handoff
4. executor 技能接收后，先调用 type=resource 技能获取资源
5. 按 SKILL.md 定义的分步流程执行
6. 返回 execution_result（status、artifacts、observation）
7. orchestrator 更新 task_state.json 记录状态

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 传递方式 | skill 工具调用 | orchestrator 规范 | 必须通过 skill 工具 |
| 交接结构 | step_handoff | executor 技能契约 | 包含必要信息 |
| 资源召回 | type=resource 技能 | executor 技能契约 | 执行前必须调用 |
| 执行流程 | 分步流程 | executor SKILL.md | 按定义执行 |
| 返回格式 | execution_result | executor 技能契约 | 标准化返回 |

## 边界与分流

**正确调用**：通过 skill 工具调用，传递 step_handoff。

**错误调用**：仅 read SKILL.md 但不调用 skill 工具 → 违反契约。

**资源缺失**：executor 技能未调用 type=resource → 执行不完整。

**流程跳过**：executor 技能跳过分步流程 → 执行不规范。

## 质量检查

| 检查点 | 验证方式 | 失败处理 |
|--------|----------|----------|
| skill 工具调用 | 检查 agent-events.log 中的 skill 调用记录 | 重新调用 |
| step_handoff 完整性 | 检查传递的参数字段 | 补充缺失字段 |
| 资源召回记录 | 检查 executor 技能的资源调用日志 | 补充资源调用 |
| execution_result 返回 | 检查返回格式和内容 | 重新执行 |

## 回退策略

- 调用失败：重新构建 step_handoff 并重试
- 资源召回失败：记录失败原因，尝试降级执行
- 执行失败：根据 execution_result 的 status 决定重试或终止

## 资源召回建议

**何时召回本卡片**：
- orchestrator 需要调用 executor 技能执行步骤时
- 发现仅 read SKILL.md 但未调用 skill 工具时
- 需要验证 executor 技能调用是否符合契约时

**配套资源**：
- `general-pre-execution-confirmation-workflow`：预确认流程
- `general-executor-inventory-validation`：executor inventory 校验

## 证据来源

[1] OneScience Orchestrator SKILL.md 规范 - executor 技能调用机制
[2] onescience-coder SKILL.md - executor 技能执行流程
[3] 归因报告 Task 260 Issue 3 优化计划 - executor 技能调用契约知识描述

## 知识边界

- 本卡片定义调用契约的规范流程
- 不同 executor 技能可能有不同的分步流程，需按各自 SKILL.md 执行
- step_handoff 的具体字段可能因 executor 技能而异