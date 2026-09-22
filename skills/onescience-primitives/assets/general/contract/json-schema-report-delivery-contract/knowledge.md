# JSON Schema 报告交付契约

## 适用范围
适用于任何需要交付JSON格式报告的自动化任务，确保报告结构可被下游系统解析、验证并正确关联到任务身份。常见于数据管道输出、API响应、分析结果交付等场景。

## 输入
- 任务身份标识（task_id, task_name）
- 报告数据内容（结构化JSON对象）
- 可选：JSON Schema定义文件（用于验证）

## 输出
- 符合预定义Schema的JSON报告文件
- 验证通过/失败状态
- 可选的错误详情（校验失败时）

## 流程节点
1. **定义Schema** → 根据任务需求设计JSON Schema，包含必填字段、数据类型、数组约束等
2. **生成报告** → 将任务结果填充到预定义结构中
3. **Schema验证** → 使用验证库（如ajv、jsonschema）校验报告是否符合Schema
4. **任务身份绑定** → 确保报告中的task_id与任务索引一致，task与任务name一致
5. **交付与存储** → 将验证通过的报告写入指定路径或通过API返回

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| required_fields | ["task_id", "task", "summary", "issues"] | [1] | 报告必须包含这些顶层字段 |
| field_types | object, string, array | [1] | 各字段的数据类型约束 |
| task_identity_match | task_id == 任务索引 | [1] | 身份一致性校验 |
| array_constraints | issues必须为数组 | [1] | 数组字段不能为空或非数组类型 |
| validation_library | ajv, jsonschema, pydantic | [2] | 常用验证工具 |
| schema_draft | draft-07, 2019-09, 2020-12 | [3] | JSON Schema版本选择 |

## 边界与分流
- **Schema缺失**：若未提供Schema，则跳过验证步骤，但任务身份绑定仍需执行
- **验证失败**：报告被拒绝，返回错误详情，触发重新生成或修正流程
- **身份不匹配**：task_id或task与任务索引/名称不一致时，报告视为无效
- **空字段**：summary必须是非空字符串，issues必须是数组，否则校验失败

## 质量检查
- 验证报告可被标准JSON解析器解析
- 检查所有必填字段存在且类型正确
- 确认任务身份字段与任务索引匹配
- 执行数组约束检查（issues为数组类型）
- 可选：使用JSON Schema校验工具进行完整验证

## 回退策略
- 若Schema验证失败，记录错误详情并返回，不交付无效报告
- 若任务身份不匹配，拒绝报告并提示核对任务信息
- 若JSON解析失败，返回格式错误信息

## 资源召回建议
当任务需要交付结构化JSON报告时召回本卡片，适用于数据管道、分析任务、API输出等需要标准化交付契约的场景。

## 证据来源
[1] Schema validation and evaluation framework for extracted schemas in JSON databases, Belefqih et al., Scientific Reports, 2026, DOI: 10.1038/s41598-026-45554-6
[2] Improving Api Test Accuracy through Schema Validation and Real-time Json Assertions in Jenkins Pipelines, Verma, International Journal on Science and Technology, 2025, DOI: 10.71097/ijsat.v16.i3.10656
[3] Validation of Modern JSON Schema: Formalization and Complexity, Attouche et al., Proceedings of the ACM on Programming Languages, 2024, DOI: 10.1145/3632891
[4] Blaze: Compiling JSON Schema for 10x Faster Validation, Viotti & Mior, Proceedings of the VLDB Endowment, 2025, DOI: 10.14778/3773749.3773764