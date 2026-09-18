# OneScience 任务执行清单契约

## 适用范围
适用于所有 OneScience 工作流任务，确保任务可追溯性、预检通过和归因分析。

## 执行清单文件
### 文件名
`execution-manifest.json`

### 生成时机
**必须在任务启动时创建**，具体时机：
1. 任务规划阶段完成后
2. 第一个步骤执行前
3. 任务状态标记为 `running` 之前
4. **必须在写入 global_plan.json 的同一事务中同步生成**，不得先写 global_plan.json 再延迟生成 execution-manifest.json

> **CFD_S046 失败模式**：orchestrator 仅写入 global_plan.json 和 task_state.json，未同步生成 execution-manifest.json，导致 workflow_preflight.py 检测到文件缺失后返回退出码 1，任务被标记为 BLOCKED，s01-s05 全部步骤无法调度。根因是 orchestrator 未按 SKILL.md 要求在融合 Global Plan 后同步生成 execution-manifest.json。

### 文件位置
```
<task_artifact_dir>/.onescience/execution-manifest.json
```
其中 `<task_artifact_dir>` 是任务产物根目录。

## 内容契约
### 必填字段
```json
{
  "task_id": "string",
  "task_name": "string",
  "status": "string",
  "started_at": "ISO8601",
  "scenario_id": "string",
  "domain": "string",
  "steps": []
}
```

### 字段规范
| 字段 | 类型 | 描述 | 必填 | 示例 |
|------|------|------|------|------|
| task_id | string | 任务唯一标识 | 是 | "bio-007" |
| task_name | string | 任务名称 | 是 | "单纯形流匹配的调控DNA序列设计" |
| status | string | 任务状态 | 是 | "running", "blocked", "completed", "failed" |
| started_at | string | 任务开始时间（ISO8601） | 是 | "2026-09-15T08:30:00.000000+00:00" |
| scenario_id | string | 场景标识 | 是 | "B70" |
| domain | string | 领域 | 是 | "bio", "cfd", "climate", "matchem", "general" |
| steps | array | 步骤列表 | 是 | [] |
| updated_at | string | 最后更新时间 | 否 | "2026-09-15T08:35:00.000000+00:00" |
| error | object | 错误信息（仅失败时） | 否 | {"message": "...", "code": "..."} |

### 步骤数组格式
```json
{
  "steps": [
    {
      "step_id": "s01",
      "step_name": "基因组输入与坐标规范化",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "artifacts": [],
      "executor_skill": "onescience-data-standardizer",
      "depends_on": []
    }
  ],
  "dependency_graph": {
    "s01": [],
    "s02": ["s01"],
    "s03": ["s02"]
  }
}
```

### 必须包含的信息（从 global_plan.steps 映射）
| 字段 | 说明 | 来源 |
|------|------|------|
| steps 数组 | 每个步骤的 ID、名称、初始状态、绑定的 executor_skill | global_plan.steps |
| dependency graph | 步骤间依赖关系 | global_plan 步骤依赖 |
| executor_skill 绑定 | 每个步骤对应的 executor 技能名 | executor_inventory 校验结果 |
| expected_artifacts | 每个步骤的预期产物列表 | 步骤输出契约 |

## 预检要求
### 预检脚本
`workflow_preflight.py`

### 预检检查项
1. **execution-manifest.json 存在性检查**
   - 文件必须存在
   - 文件必须是有效JSON
   - 必须包含必填字段

2. **任务状态一致性检查**
   - manifest 中的状态与 task_state.json 一致
   - 步骤状态与实际执行情况匹配

3. **产物目录结构检查**
   - 必要目录存在
   - 文件权限正确

### 预检失败处理
- 退出码：1
- 错误信息：`execution-manifest.json is missing`
- 任务状态标记为 `blocked`

## 流程节点
1. **任务初始化** → 2. **创建清单文件** → 3. **执行预检** → 4. **开始任务执行** → 5. **更新清单状态** → 6. **任务完成**

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 文件格式 | JSON | [规范] | 标准JSON格式 |
| 时间格式 | ISO8601 | [规范] | 国际标准时间格式 |
| 状态枚举 | pending/running/completed/failed/blocked | [规范] | 任务状态机 |
| 步骤ID格式 | s01, s02, ... | [规范] | 两位数步骤编号 |

## 边界与分流
### 异常处理
- 文件创建失败：记录错误并终止任务
- JSON解析失败：标记任务为 `blocked`
- 状态不一致：自动修复或提示用户

### 降级策略
- 无清单文件时：生成最小化清单并继续
- 清单损坏时：从task_state.json重建

## 质量检查
1. JSON格式有效性
2. 必填字段完整性
3. 时间戳格式正确性
4. 状态枚举值有效性
5. 步骤ID唯一性

## 回退策略
1. 清单文件缺失时：创建默认清单
2. 清单损坏时：备份并重建
3. 预检失败时：修复后重新预检

## 资源召回建议
- 需要任务状态管理时：召回 `general-task-state` 类资源
- 需要预检脚本时：召回 `general-workflow-preflight` 类资源
- 需要归因分析时：召回 `general-attribution-analysis` 类资源

## 闭环更新协议

### 更新时机
orchestrator 必须在每个 executor_step 完成后立即更新 execution-manifest.json，确保清单状态与实际执行同步。

### 更新触发点
1. **step_result 返回后**：当 executor 技能返回执行结果时
2. **observation 阶段**：在 orchestrator 的 observation 阶段，处理 step_result 后立即调用 manifest_append 工具
3. **状态变更时**：当步骤状态从 running 变为 completed/failed 时

### 更新操作
- **追加条目**：调用 `manifest_append` 工具写入该步完成记录
- **字段更新**：更新对应步骤的 status、completed_at、artifacts、exit_code、timestamp
- **任务状态同步**：更新 manifest 中的 overall status 和 updated_at

### 字段要求
每个步骤更新必须包含：
```json
{
  "step_id": "s01",
  "status": "completed",
  "completed_at": "ISO8601",
  "artifacts": ["file1.csv", "model.pt"],
  "exit_code": 0,
  "timestamp": "ISO8601",
  "execution_duration": 120.5
}
```

### 验证方式
- 重新执行任务后检查 execution-manifest.json 存在且每个 step 条目与 task_state.completed_steps 一一对应
- 验证 manifest 中的步骤状态与实际执行日志一致

## 证据来源
[1] OneScience Workflow Execution Standard v2.1, 内部文档, 2026
[2] workflow_preflight.py 实现代码, 项目仓库
[U1] 归因报告 CFD_S092 任务分析，用户自有数据，2026-09-17（用户自有, 未经公开源验证）