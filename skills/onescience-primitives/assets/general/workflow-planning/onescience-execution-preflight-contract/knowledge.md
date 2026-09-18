# OneScience 执行预检契约

## 适用范围

面向OneScience任务从规划阶段进入执行阶段的过渡环节，定义预检流程的必检项、execution-manifest.json的生成规范和验证逻辑。适用于所有OneScience任务类型（CFD、生物、气候、材料等），确保任务在正式执行前完成所有前置条件检查。不适用于任务内部步骤级预检或运行时环境检查。

## 输入

### 预检输入清单
| 输入 | 类型 | 说明 | 必填 |
|------|------|------|------|
| task_state.json | file | 任务状态文件 | 是 |
| planner_proposal.yaml | file | 规划器输出 | 是 |
| resource_bindings | dict | 资源绑定信息 | 是 |
| execution_profile | dict | 执行配置（execution_mode等） | 是 |

### 触发条件
- planner_proposal生成完成
- 所有规划步骤状态为ready或blocked（非pending）
- 用户确认（如需）

## 输出

### execution-manifest.json
```json
{
  "task_id": "<string>",
  "created_at": "<ISO timestamp>",
  "updated_at": "<ISO timestamp>",
  "status": "preflight | ready | executing | completed | failed | blocked",
  "steps": [
    {
      "step_id": "<string>",
      "name": "<string>",
      "skill": "<string>",
      "status": "pending | ready | executing | completed | failed",
      "inputs": {},
      "outputs": {},
      "dependencies": ["<step_id>", ...]
    }
  ],
  "resource_bindings": {
    "run_site": "<string>",
    "conda_env": "<string>",
    "gpu_required": <bool>,
    "slurm_config": {}
  },
  "execution_profile": {
    "mode": "local | slurm | remote",
    "timeout_seconds": <int>,
    "retry_count": <int>
  },
  "user_confirmations": [
    {
      "field": "<string>",
      "value": "<any>",
      "confirmed_at": "<ISO timestamp>",
      "confirmed_by": "<user_id>"
    }
  ]
}
```

### 预检报告
```yaml
preflight_report:
  status: pass | fail | warning
  checks:
    manifest_exists: bool
    manifest_valid: bool
    steps_complete: bool
    resources_available: bool
    user_confirmations_complete: bool
  blocking_issues: [list of issues]
  warnings: [list of warnings]
```

## 流程节点

### 节点1：必填字段完整性检查
- 操作：验证planner_proposal中所有必填字段已填充
- 参数：required_fields清单
- 工具：字段验证器
- 质量门禁：所有required字段状态非missing

### 节点2：execution-manifest.json生成
- 操作：根据planner_proposal生成manifest文件
- 参数：planner_proposal, resource_bindings
- 工具：manifest生成器
- 质量门禁：JSON格式正确，所有必填字段完整

### 节点3：用户确认收集
- 操作：对标记为需确认的字段发起用户确认
- 参数：pending_confirmations
- 工具：用户交互接口
- 质量门禁：所有必填确认项已获得用户响应

### 节点4：资源可用性验证
- 操作：检查目标运行站点、conda环境、GPU等资源
- 参数：resource_bindings
- 质量门禁：资源可用或有降级方案

### 节点5：预检报告生成
- 操作：汇总所有检查结果，生成预检报告
- 参数：all_check_results
- 工具：报告生成器
- 质量门禁：报告格式正确，所有检查项有明确结果

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| manifest_required_fields | 6 | 系统规范 | task_id, steps, status, resource_bindings, execution_profile, created_at |
| step_required_fields | 4 | 系统规范 | step_id, name, skill, status |
| confirmation_timeout | 300s | 系统规范 | 用户确认等待超时 |
| preflight_timeout | 60s | 系统规范 | 预检流程总超时 |

### 校准数值（OneScience任务）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| max_steps_per_task | 10 | 系统规范 | 单任务最大步骤数 |
| max_dependencies | 5 | 系统规范 | 单步骤最大依赖数 |
| default_timeout | 3600s | 系统规范 | 默认任务超时 |

## 边界与分流

### 前提否定即改道
| 前提条件 | 不成立时的改道方案 |
|----------|-------------------|
| planner_proposal存在 | 阻断，请求生成规划 |
| 所有必填字段已填充 | 阻断，请求用户补充 |
| 用户确认已获得 | 保存状态，等待确认 |
| 资源可用 | 尝试降级资源或阻断 |

### 异常处理
- manifest生成失败：记录错误，请求用户干预
- 验证超时：保存当前状态，标记为timeout
- 资源不可用：尝试替代资源或通知用户

## 质量检查

| 检查点 | 阈值 | 失败处理 |
|--------|------|----------|
| manifest格式正确 | 100% | 修复格式 |
| 必填字段完整 | 100% | 请求补充 |
| 步骤依赖无环 | 100% | 修复依赖图 |
| 用户确认完整 | 100% | 等待确认 |

## 回退策略

1. **manifest生成失败**：使用模板生成最小化manifest，后续步骤补充
2. **验证超时**：保存当前状态，允许用户手动触发重试
3. **资源不可用**：降级到本地执行或等待资源释放
4. **用户无响应**：使用默认配置继续（需用户显式授权）

## 资源召回建议

当任务涉及以下场景时应召回本卡片：
- OneScience任务从规划进入执行
- execution-manifest.json生成与验证
- 任务预检流程设计
- 多步骤任务的依赖管理

配套资源：
- `onescience-orchestrator-executor-handoff`：orchestrator与executor交接
- `onescience-timeout-recovery-strategy`：超时恢复策略

## 证据来源

本卡片基于OneScience系统内部流程设计，无公开论文证据。内容来源于：
- OneScience任务执行日志分析
- 预检脚本（workflow_preflight.py）行为观察
- 任务失败案例的归因分析

## 补充说明

本卡片记录的是OneScience系统内部流程规范，属于系统设计知识而非科学文献知识。当系统实现发生变化时，本卡片内容需要相应更新。
