# 执行清单生成契约

## 适用范围

本卡片定义了execution-manifest.json的生成时机、内容契约和降级策略。适用于需要预检验证的工作流执行场景，特别是涉及多步骤任务编排的CFD工作流。不适用于单步执行或无预检要求的场景。

## 问题背景

execution-manifest.json是编排器输出的核心规划产物，必须在预检前生成。当manifest缺失时，预检脚本会报告失败，导致任务无法进入执行阶段。

## 生成时机

### 正常生成时机
- **Global Plan生成完成后**：编排器完成规划融合并生成Global Plan后，立即生成execution-manifest.json
- **规划阶段结束时**：无论规划成功或失败，都必须生成manifest

### 异常生成时机
- **超时降级时**：当规划融合阶段超时触发降级时，生成最小化manifest
- **规划失败时**：当规划融合阶段因其他原因失败时，生成包含错误信息的manifest

## 内容契约

### 完整manifest字段

```json
{
  "task_id": "<任务ID，必填>",
  "status": "<planning|running|completed|failed|blocked，必填>",
  "workflow": {
    "steps": [
      {
        "step_id": "<步骤ID>",
        "name": "<步骤名称>",
        "skill": "<执行技能名称>",
        "inputs": "<输入契约>",
        "outputs": "<输出契约>",
        "dependencies": ["<依赖步骤ID列表>"],
        "timeout": "<超时预算>"
      }
    ],
    "total_timeout": "<总超时预算>",
    "created_at": "<创建时间戳>"
  },
  "planner_proposals": ["<已采纳的proposal列表>"],
  "global_plan": "<Global Plan摘要>",
  "state_checkpoints": ["<状态检查点列表>"],
  "validation": {
    "preflight_required": true,
    "preflight_script": "workflow_preflight.py"
  }
}
```

### 最小化manifest字段（降级时使用）

```json
{
  "task_id": "<任务ID，必填>",
  "status": "blocked",
  "block_reason": "<阻塞原因，如timeout|planning_failed|resource_unavailable>",
  "block_stage": "<阻塞发生的阶段>",
  "partial_plan": "<已生成的规划片段（如有）>",
  "created_at": "<创建时间戳>",
  "validation": {
    "preflight_required": true,
    "preflight_script": "workflow_preflight.py"
  }
}
```

## 降级策略

### 降级触发条件
1. **规划融合超时**：规划融合阶段超时，无法生成完整Global Plan
2. **规划融合失败**：规划融合阶段因其他原因失败（如专家技能不可用）
3. **资源不足**：计算资源不足，无法完成规划

### 降级策略
1. **生成最小化manifest**：即使规划未完成，也生成包含BLOCKED状态的最小化manifest
2. **记录阻塞原因**：详细记录阻塞原因和发生阶段
3. **保存部分结果**：保存已生成的planner_proposal和Global Plan片段
4. **通过预检**：最小化manifest必须能通过预检验证（返回BLOCKED状态而非缺失错误）

### 降级产物
- **最小化manifest**：包含task_id、status=blocked、block_reason、created_at
- **阻塞报告**：详细记录阻塞原因、发生阶段和已生成的部分结果
- **恢复指引**：提供人工干预恢复的操作建议

## 预检验证要求

### 预检脚本行为
- **manifest存在性检查**：检查execution-manifest.json是否存在
- **manifest格式验证**：验证JSON格式是否正确
- **必填字段检查**：验证task_id、status等必填字段是否存在
- **状态检查**：根据status字段判断任务状态

### 预检通过条件
- **正常状态**：status为planning/running/completed时，预检通过
- **阻塞状态**：status为blocked时，预检通过（但标记为阻塞）
- **失败状态**：status为failed时，预检失败（但记录错误信息）

### 预检失败条件
- **manifest缺失**：execution-manifest.json不存在时，预检失败
- **格式错误**：JSON格式错误时，预检失败
- **必填字段缺失**：task_id或status字段缺失时，预检失败

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| manifest生成时机 | Global Plan完成后 | 工程实践 | 确保规划完成后立即生成 |
| 最小化manifest字段数 | 5 | 工程实践 | task_id, status, block_reason, created_at, validation |
| 预检脚本 | workflow_preflight.py | 系统约定 | 标准预检脚本 |
| 状态值域 | planning/running/completed/failed/blocked | 系统约定 | 任务状态枚举 |

## 边界与分流

- **无预检要求**：简单任务可跳过预检，直接生成manifest
- **manifest已存在**：当manifest已存在时，更新而非覆盖
- **预检脚本不可用**：当预检脚本不可用时，跳过预检但记录日志

## 质量检查

- **manifest完整性**：所有必填字段存在且格式正确
- **状态一致性**：manifest状态与实际任务状态一致
- **预检通过**：manifest能通过预检验证
- **降级可用**：降级策略能正常触发并生成最小化manifest

## 回退策略

- **跳过预检**：当预检脚本不可用时，跳过预检但记录警告
- **人工审核**：当manifest状态异常时，转交人工审核
- **任务重试**：当manifest生成失败时，重试生成

## 资源召回建议

- 当编排器需要生成执行清单时
- 当任务涉及预检验证时
- 当任务可能因规划失败而需要降级时
- 配套资源：预检脚本、manifest生成器、状态恢复工具

## 证据来源

本卡片基于归因报告中的工程实践经验总结，无直接论文证据。

[1] CFD_S007归因报告：execution-manifest.json生成时机与内容契约知识缺口
