# OneScience 超时处理与恢复策略

## 适用范围

面向OneScience任务执行过程中的超时检测与恢复机制，定义超时阈值设置、自动恢复策略（任务拆分、重试、降级）和用户通知机制。适用于所有OneScience任务类型，特别是长时间运行的计算密集型任务（如大规模CFD模拟、模型训练等）。不适用于步骤级超时（由执行技能内部处理）或用户主动取消。

## 输入

### 超时配置
| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| task_timeout | int | 任务总超时（秒） | 3600 |
| step_timeout | int | 单步骤超时（秒） | 1800 |
| heartbeat_interval | int | 心跳间隔（秒） | 60 |
| max_retry_count | int | 最大重试次数 | 3 |
| recovery_enabled | bool | 是否启用自动恢复 | true |

### 触发条件
- 任务执行时间超过task_timeout
- 单步骤执行时间超过step_timeout
- 心跳丢失超过3个间隔
- 执行智能体报告超时

## 输出

### 超时检测报告
```yaml
timeout_report:
  task_id: <string>
  timeout_type: task | step | heartbeat
  elapsed_time: <int>
  timeout_threshold: <int>
  last_heartbeat: <ISO timestamp>
  current_step: <string>
  progress: <float>
```

### 恢复决策
```yaml
recovery_decision:
  action: retry | split | degrade | notify_user | abort
  reason: <string>
  parameters:
    retry_count: <int>
    split_strategy: <string>
    degrade_target: <string>
  state_snapshot:
    saved_at: <ISO timestamp>
    snapshot_path: <string>
```

### 恢复执行结果
```yaml
recovery_result:
  status: success | partial | failed
  action_taken: <string>
  outputs_recovered: <any>
  remaining_work: [list]
  next_steps: [list]
```

## 流程节点

### 节点1：超时检测
- 操作：监控任务执行时间，检测超时条件
- 参数：task_timeout, step_timeout, heartbeat_interval
- 工具：超时监控器
- 质量门禁：超时检测准确，误报率<5%

### 节点2：状态快照保存
- 操作：超时触发时立即保存当前任务状态
- 参数：current_task_state, current_step_outputs
- 工具：状态快照器
- 质量门禁：快照完整，可恢复

### 节点3：恢复策略选择
- 操作：根据超时类型和任务状态选择恢复策略
- 策略选择矩阵：
  | 超时类型 | 任务进度 | 推荐策略 |
  |----------|----------|----------|
  | step_timeout | <30% | 重试 |
  | step_timeout | 30-70% | 拆分步骤 |
  | step_timeout | >70% | 降级或通知用户 |
  | task_timeout | <50% | 拆分任务 |
  | task_timeout | >50% | 通知用户 |
  | heartbeat | any | 重试或通知用户 |
- 质量门禁：策略选择合理

### 节点4：恢复执行
- 操作：执行选定的恢复策略
- 参数：recovery_decision, state_snapshot
- 工具：恢复执行器
- 质量门禁：恢复过程有日志记录

### 节点5：用户通知
- 操作：向用户发送超时通知和恢复状态
- 参数：timeout_report, recovery_decision, recovery_result
- 工具：通知发送器
- 质量门禁：通知包含足够信息供用户决策

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| min_task_timeout | 300s | 系统规范 | 最小任务超时（防止误触发） |
| max_task_timeout | 86400s | 系统规范 | 最大任务超时（24小时） |
| heartbeat_loss_threshold | 3 | 系统规范 | 心跳丢失触发阈值 |
| state_snapshot_interval | 300s | 系统规范 | 状态快照保存间隔 |
| recovery_attempt_interval | 60s | 系统规范 | 恢复尝试间隔 |

### 校准数值（OneScience任务）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| cfd_simulation_timeout | 7200s | 经验值 | CFD模拟任务超时 |
| model_training_timeout | 14400s | 经验值 | 模型训练任务超时 |
| data_standardization_timeout | 1800s | 经验值 | 数据标准化任务超时 |
| max_retry_for_compute | 2 | 经验值 | 计算任务最大重试次数 |

## 边界与分流

### 前提否定即改道
| 前提条件 | 不成立时的改道方案 |
|----------|-------------------|
| 超时检测可用 | 使用固定超时+用户手动检查 |
| 状态快照可保存 | 记录最后已知状态，标记为uncertain |
| 恢复策略可执行 | 直接通知用户，等待人工干预 |
| 用户可通知 | 记录日志，等待用户主动检查 |

### 异常处理
- 快照保存失败：记录错误，继续执行恢复（可能丢失部分状态）
- 恢复执行失败：通知用户，提供手动恢复指引
- 用户无响应：保存状态，标记为pending_user_action

## 质量检查

| 检查点 | 阈值 | 失败处理 |
|--------|------|----------|
| 超时检测准确 | 95% | 调整检测参数 |
| 状态快照完整 | 100% | 重试快照保存 |
| 恢复策略有效 | 80% | 切换备选策略 |
| 用户通知送达 | 100% | 尝试替代通知渠道 |

## 回退策略

1. **自动恢复失败**：通知用户，提供手动恢复入口
2. **状态快照损坏**：使用最近的完好快照，标记可能的数据丢失
3. **恢复策略不适用**：降级为最保守策略（重试）
4. **用户长时间无响应**：定期发送提醒，最终标记为abandoned

## 资源召回建议

当任务涉及以下场景时应召回本卡片：
- 长时间运行的OneScience任务
- 任务超时后的状态保存与恢复
- 多步骤任务的断点续传
- 任务失败后的自动恢复

配套资源：
- `onescience-execution-preflight-contract`：预检契约
- `onescience-orchestrator-executor-handoff`：技能交接协议

## 证据来源

本卡片基于OneScience系统内部流程设计，无公开论文证据。内容来源于：
- blocked-run.log中任务超时记录分析
- 任务失败案例的归因分析
- 系统异常恢复机制设计

## 补充说明

本卡片记录的是OneScience系统内部流程规范，属于系统设计知识而非科学文献知识。当系统实现发生变化时，本卡片内容需要相应更新。
