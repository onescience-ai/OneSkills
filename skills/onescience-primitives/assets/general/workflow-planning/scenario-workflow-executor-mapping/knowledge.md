# OneScience场景工作流与执行器步骤映射规则

## 适用范围
当OneScience orchestrator需要将场景定义的工作流步骤映射为executor可执行的步骤时，使用本规则。适用于所有需要将领域工作流转换为具体执行步骤的场景。

## 输入
- 场景workflow定义：s01-s04步骤描述、输入输出契约
- executor能力视图：各executor的输入输出要求
- 任务上下文：用户目标、约束条件、相关产物

## 输出
- executor步骤列表：每个步骤对应的executor、输入输出
- 步骤映射关系：场景步骤到executor步骤的映射
- 执行清单：execution-manifest.json

## 流程节点
1. 解析场景workflow步骤 → 2. 评估executor能力 → 3. 映射步骤到executor → 4. 验证输入输出契约 → 5. 生成执行清单

每步含：操作、参数、工具、质量门禁

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 映射规则 | s01→material modeling步骤，s02→computation步骤，s03→analysis步骤，s04→recommendation步骤 | [归因报告] | 通用映射关系 |
| 契约一致性 | 场景步骤的输入输出契约必须传递到对应executor步骤 | [归因报告] | 保持契约一致 |
| 映射记录 | execution-manifest.json的step_mapping字段 | [归因报告] | 映射关系需记录 |
| 步骤对应关系 | 每个场景步骤可映射为一个或多个executor步骤 | [归因报告] | 支持多对一映射 |

## 边界与分流
- 如果场景步骤与executor能力不匹配，应调整映射或请求新executor
- 如果输入输出契约不一致，应修改映射或调整步骤
- 如果步骤映射导致功能覆盖不完整，应重新评估executor能力

## 质量检查
- 验证每个场景步骤都有对应的executor步骤
- 检查输入输出契约是否一致
- 确认映射关系已记录在execution-manifest.json中

## 回退策略
- 如果映射失败，可尝试重新拆分步骤
- 如果executor能力不足，可请求其他executor或修改任务
- 如果契约不一致，可调整输入输出格式

## 资源召回建议
- 当orchestrator需要将场景workflow映射为executor步骤时召回本卡片
- 当步骤映射导致契约不一致时召回本卡片
- 当需要验证execution-manifest.json格式时召回本卡片

## 证据来源
[归因报告] 任务369归因报告，issues[4].optimization_plan，2026