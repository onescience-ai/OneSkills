# JSON Schema报告交付契约

## 适用范围
本卡片定义JSON格式结构化报告的交付契约规范，适用于自动化报告生成、数据交换、API响应校验等场景。规定必填字段、类型约束、数组约束和任务身份验证，确保报告可解析且与预期格式一致。

## 输入
- 报告数据（JSON对象）
- 目标Schema定义（JSON Schema）
- 任务上下文（任务ID、任务名称）

## 输出
- 校验后的JSON报告
- 校验错误详情（如有）
- 字段缺失/多余提示

## 流程节点
1. Schema加载 → 字段定义解析 → 约束提取
2. 数据遍历 → 类型检查 → 必填验证
3. 任务身份匹配 → ID/名称一致性校验
4. 错误聚合 → 报告生成

每步含：操作、参数、工具、质量门禁

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| required_fields | 顶层必填字段列表 | 报告契约 | 如：task_id, task, summary, issues |
| type_array | issues必须是数组 | JSON Schema | 保证结构一致性 |
| type_string | task_id/task/summary必须是字符串 | JSON Schema | 类型约束 |
| id_match | task_id必须与任务索引一致 | 业务规则 | 身份验证 |
| name_match | task必须与任务name一致 | 业务规则 | 身份验证 |
| summary_nonempty | summary必须是非空字符串 | 业务规则 | 内容完整性 |

## 边界与分流
- **字段缺失**：列出缺失字段，返回校验失败
- **字段多余**：记录额外字段，不阻塞校验（警告级别）
- **类型错误**：返回类型不匹配错误
- **身份不匹配**：返回task_id/task与预期不一致的错误

## 质量检查
- 所有required_fields存在且非空
- 字段类型与Schema定义一致
- 任务身份（task_id, task）与上下文匹配
- JSON可解析，无语法错误

## 回退策略
- Schema校验失败：输出详细错误信息供人工修正
- 身份不匹配：检查任务配置或上下文传递

## 资源召回建议
当遇到以下情况时应召回本卡片：
- 报告校验失败（缺少字段、类型错误）
- 结构化输出格式不符合预期
- 任务ID/名称不匹配
- 自动化报告生成流程异常

## 补充证据（开源文档/用户自有，可选）
[D1] JSON Schema官方文档, json-schema.org（权威参考）

## 证据来源
[1] Validation of Modern JSON Schema: Formalization and Complexity, ACM POPL, 2024, DOI: 10.1145/3632891
[2] Schema validation and evaluation framework for extracted schemas in JSON databases, Scientific Reports, 2026, DOI: 10.1038/s41598-026-45554-6