# JSON Schema报告交付契约

## 适用范围
适用于归因报告、分析报告等结构化JSON产物的校验与交付。定义必填字段、类型约束、数组约束及任务身份一致性要求，确保报告产物可解析且符合契约规范。

## 输入
- JSON Schema定义文件（定义报告结构）
- 待校验的JSON报告实例

## 输出
- 校验结果：通过/失败
- 失败详情：不匹配的字段、缺失字段、类型错误

## 流程节点

1. **加载Schema** → 读取JSON Schema定义
2. **解析实例** → 将JSON报告解析为内存对象
3. **类型校验** → 检查每个字段的数据类型是否匹配schema定义
4. **必填字段校验** → 检查required字段是否全部存在
5. **数组约束校验** → 检查items类型、minItems、maxItems等
6. **输出格式校验** → 检查顶层结构是否符合契约

## 关键参数

### 类型约束（type keyword）
| 类型 | JSON值 | 说明 |
|------|--------|------|
| null | null | 空值 |
| boolean | true/false | 布尔值 |
| object | { } | 对象 |
| array | [ ] | 数组 |
| number | 数值 | 整数或浮点数 |
| string | "..." | 字符串 |

### 必填字段（required keyword）
- required字段必须在对象中存在
- 缺失required字段将导致校验失败

### 数组约束（items keyword）
- items定义数组元素的类型约束
- minItems/maxItems约束数组长度

## 任务身份一致性要求

### 顶层字段约束
报告JSON必须包含以下顶层字段：
- **task_id**: 任务编号（字符串或数字，需与任务索引匹配）
- **task**: 任务名称（字符串，需与任务定义匹配）
- **summary**: 摘要（非空字符串）
- **issues**: 问题列表（数组）

### 不允许的额外字段
- 不应包含error、sessionID、timestamp、type等非契约字段
- 如需扩展字段，应在schema中预先定义

## 边界与分流
- 校验失败时：返回详细错误信息，定位到具体字段
- schema缺失时：无法执行校验，需先定义schema
- 字段类型不匹配时：明确报告期望类型与实际类型

## 质量检查
- 使用标准JSON Schema验证器（如jsonschema库）
- 校验task_id与任务索引一致性
- 校验summary为非空字符串
- 校验issues为数组类型
- 执行错配字段反例测试（如用error替代task_id）

## 回退策略
- 若schema校验库不可用，可手动检查关键字段
- 考虑使用JSONLint等工具进行基础格式校验

## 资源召回建议
- 当需要验证归因报告、分析报告等结构化产物时召回本卡片
- 配套卡片：CLI非交互执行与故障分类（用于生成报告的CLI工具）

## 补充证据（开源权威文档）
[D1] JSON Schema: A Media Type for Describing JSON Documents, IETF/json-schema-org, draft-bhutton-json-schema-01 (2022), https://json-schema.org/draft/2020-12/json-schema-core (accessed 2026-09-21)
