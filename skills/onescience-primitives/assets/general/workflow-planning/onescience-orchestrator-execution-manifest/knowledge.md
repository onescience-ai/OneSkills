# OneScience Orchestrator执行清单生成规则

## 适用范围

**触发条件**：
- OneScience orchestrator完成全局计划融合后，进入执行阶段前
- 需要生成execution-manifest.json作为preflight检查的必要文件
- 需要确保工作流从planning阶段正确切换到execution阶段

**适用场景**：
- OneScience任务编排与执行
- 工作流状态管理与验证
- 多步骤任务的结构化清单生成

**不适用场景**：
- 非OneScience框架的工作流编排
- 简单单步骤任务无需复杂清单
- 已有execution-manifest.json的任务

## 输入

- planner_proposal.json：规划器提案
- global_plan.json：全局计划
- task_state.json：任务状态
- resource_bindings：资源绑定信息

## 输出

- .onescience/execution-manifest.json：执行清单文件
- 清单包含task_id、步骤列表、依赖关系、资源绑定、验收标准
- 清单通过JSON格式校验

## 流程节点

### Step 1：全局计划融合完成
- **操作**：确认planner_proposal.json和global_plan.json已生成且有效
- **参数**：文件路径、JSON格式、必填字段完整性
- **工具**：JSON解析器
- **质量门禁**：两个文件均存在且可解析

### Step 2：清单内容生成
- **操作**：基于全局计划生成execution-manifest.json内容
- **参数**：task_id、步骤数组、依赖关系图、资源绑定、验收标准
- **工具**：模板填充或程序化生成
- **质量门禁**：清单包含所有必填字段，格式符合schema

### Step 3：清单校验
- **操作**：验证execution-manifest.json格式和内容
- **参数**：JSON schema、必填字段、数据类型
- **工具**：JSON schema验证器
- **质量门禁**：通过schema验证，无缺失字段

### Step 4：状态更新
- **操作**：更新task_state.json，设置status为ready_to_execute
- **参数**：状态标记、时间戳、清单路径
- **工具**：JSON更新器
- **质量门禁**：状态正确更新，清单路径可访问

### Step 5：Preflight检查
- **操作**：执行preflight检查，确认清单存在
- **参数**：清单文件路径、检查脚本
- **工具**：preflight检查脚本
- **质量门禁**：preflight通过，无错误

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 生成时机 | 全局计划融合后、执行前 | [归因报告] | 避免preflight失败 |
| 必填字段 | task_id, steps, dependencies, resource_bindings, expected_artifacts, checks | [场景标准] | 清单完整性 |
| JSON格式 | 合法JSON，UTF-8编码 | [领域知识] | 可解析性 |
| 校验方式 | JSON schema验证 | [领域知识] | 格式正确性 |
| 状态标记 | ready_to_execute | [场景标准] | 执行阶段标识 |

### 校准数值（以下数值来自OneScience框架，供量级校准；其他体系需以自身证据重新锚定）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 清单文件路径 | .onescience/execution-manifest.json | [归因报告] | 标准路径 |
| 最大步骤数 | 无限制，但建议≤20 | [领域知识] | 可读性考虑 |
| 依赖关系深度 | 建议≤5层 | [领域知识] | 避免循环依赖 |
| 校验超时 | 10秒 | [领域知识] | 性能考虑 |

## 边界与分流

- **清单生成失败**：检查planner_proposal和global_plan是否完整，修复后重新生成
- **校验失败**：根据错误信息修复清单内容，重新校验
- **preflight失败**：检查清单文件是否存在于正确路径，检查文件权限
- **状态更新失败**：检查task_state.json是否可写，修复权限问题
- **依赖循环**：重新设计工作流步骤，避免循环依赖

## 质量检查

- 清单文件存在且可读
- JSON格式合法，可被标准解析器解析
- 包含所有必填字段
- 字段类型符合预期
- 无循环依赖
- 步骤顺序合理

## 回退策略

- 清单生成失败：手动创建清单模板，填充关键信息
- 校验持续失败：跳过校验，直接进入执行（不推荐）
- preflight失败：记录错误，尝试修复后重试
- 无法修复：标记任务为BLOCKED，输出部分结果

## 资源召回建议

- 当OneScience orchestrator需要生成执行清单时召回本卡片
- 配套资源：onescience-orchestrator（主控技能）、onescience-runtime（执行技能）
- 若涉及preflight检查，可关联 onescience-runtime 的 preflight 阶段

## 补充证据（权威文档）

无公开论文证据，基于OneScience框架内部规范和归因报告分析。

## 证据来源

[1] 归因报告 CFD_S100：execution-manifest.json缺失导致preflight失败分析
[2] OneScience Orchestrator SKILL.md：工作流编排规范
[3] OneScience Runtime SKILL.md：preflight检查流程