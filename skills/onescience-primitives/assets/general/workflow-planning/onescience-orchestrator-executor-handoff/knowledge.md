# OneScience Orchestrator-Executor 技能交接协议

## 适用范围

面向OneScience orchestrator（编排器）与executor（执行器）技能之间的任务交接流程，定义step_handoff的标准格式、执行技能的选择逻辑和任务状态传递机制。适用于所有需要从规划阶段切换到执行阶段的OneScience任务。不适用于单技能内部的子任务调度或运行时环境管理。

## 输入

### 交接触发条件
| 条件 | 说明 | 必须满足 |
|------|------|----------|
| Global Plan生成完成 | 所有规划步骤已确定 | 是 |
| execution-manifest.json存在 | 预检通过 | 是 |
| 资源绑定完成 | run_site/conda_env已确定 | 是 |
| 用户确认（如需） | 关键参数已确认 | 视情况 |

### 交接输入数据
```yaml
step_handoff:
  step_id: <string>
  execution_skill: <skill_name>
  step_goal: <string>
  task_context:
    user_goal: <string>
    constraints: [list]
    relevant_artifacts: [list]
  inputs:
    <step-specific inputs>
  resource_bindings:
    run_site: <string>
    conda_env: <string>
    gpu_required: <bool>
  required_outputs:
    <expected output spec>
  completion_criteria:
    <success criteria>
```

## 输出

### 交接确认
```yaml
handoff_confirmation:
  status: accepted | rejected | deferred
  executor_response:
    skill: <skill_name>
    step_id: <string>
    readiness: ready | needs_input | blocked
    estimated_duration: <int>
    blocking_issues: [list]
```

### 执行状态更新
```yaml
execution_update:
  step_id: <string>
  status: executing | completed | failed
  progress: <float>
  outputs: <any>
  errors: [list]
```

## 流程节点

### 节点1：交接准备检查
- 操作：验证所有交接前置条件
- 参数：handoff_prerequisites
- 工具：前置条件检查器
- 质量门禁：所有必填条件满足

### 节点2：step_handoff构建
- 操作：根据planner_proposal构建标准交接包
- 参数：planner_proposal_step, resource_bindings
- 工具：handoff构建器
- 质量门禁：handoff格式符合规范

### 节点3：执行技能选择
- 操作：根据step_goal和skill能力边界选择执行技能
- 参数：step_goal, available_skills
- 技能选择矩阵：
  | 任务类型 | 推荐技能 |
  |----------|----------|
  | 数据标准化 | onescience-data-standardizer |
  | 代码生成 | onescience-coder |
  | 模型训练 | onescience-trainer |
  | 模型推理 | onescience-infer |
  | 环境安装 | onescience-installer |
  | 运行执行 | onescience-runtime |
- 质量门禁：选择的技能能力覆盖step_goal

### 节点4：交接执行
- 调用选定的executor技能，传递step_handoff
- 参数：step_handoff
- 工具：skill调用器
- 质量门禁：技能成功接收handoff

### 节点5：状态同步
- 操作：更新task_state.json中的步骤状态
- 参数：execution_update
- 工具：状态更新器
- 质量门禁：状态变更记录完整

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| handoff_required_fields | 6 | 系统规范 | step_id, execution_skill, step_goal, task_context, inputs, resource_bindings |
| skill_selection_timeout | 30s | 系统规范 | 技能选择决策超时 |
| handoff_retry_count | 3 | 系统规范 | 交接失败重试次数 |
| state_sync_delay | 5s | 系统规范 | 状态同步最大延迟 |

### 技能能力边界矩阵
| 技能 | 输入要求 | 输出产物 | 适用场景 |
|------|----------|----------|----------|
| onescience-coder | coder_task_description.md | 代码文件 | 代码生成任务 |
| onescience-trainer | training_spec | checkpoint | 模型训练任务 |
| onescience-infer | inference_spec | predictions | 模型推理任务 |
| onescience-data-standardizer | raw_data_path | standardized_data | 数据标准化任务 |
| onescience-runtime | execution_manifest | execution_log | 运行执行任务 |

## 边界与分流

### 前提否定即改道
| 前提条件 | 不成立时的改道方案 |
|----------|-------------------|
| Global Plan完成 | 阻断，返回规划阶段 |
| execution-manifest.json存在 | 阻断，触发预检流程 |
| 资源绑定完成 | 阻断，请求资源绑定 |
| executor技能可用 | 尝试替代技能或阻断 |

### 异常处理
- 交接失败：重试最多3次，仍失败则保存状态并通知用户
- 技能拒绝：记录拒绝原因，尝试替代技能
- 状态不一致：强制同步状态，记录冲突

## 质量检查

| 检查点 | 阈值 | 失败处理 |
|--------|------|----------|
| handoff格式正确 | 100% | 修复格式 |
| 技能选择正确 | 100% | 重新选择 |
| 状态同步成功 | 100% | 重试同步 |
| 交接确认收到 | 100% | 重试交接 |

## 回退策略

1. **交接失败**：保存当前状态，允许用户手动触发重试
2. **技能不可用**：尝试替代技能或降级处理
3. **状态不一致**：强制同步并记录冲突日志
4. **用户无响应**：使用默认配置继续（需显式授权）

## 资源召回建议

当任务涉及以下场景时应召回本卡片：
- OneScience任务从规划切换到执行
- 多技能任务的调度与协调
- step_handoff格式设计
- 执行技能选择逻辑

配套资源：
- `onescience-execution-preflight-contract`：预检契约
- `onescience-timeout-recovery-strategy`：超时恢复策略

## 证据来源

本卡片基于OneScience系统内部流程设计，无公开论文证据。内容来源于：
- OneScience orchestrator技能实现分析
- agent-events.log中技能调用记录
- 任务失败案例的归因分析

## 补充说明

本卡片记录的是OneScience系统内部流程规范，属于系统设计知识而非科学文献知识。当系统实现发生变化时，本卡片内容需要相应更新。
