# JSON Schema 报告交付契约

## 适用范围
适用于任何需要通过 JSON 格式交付结构化报告的场景，包括 API 响应、配置文件、数据导出、自动化报告等。目标是使用 JSON Schema 定义报告契约，验证必填字段、任务身份、数组约束及输出格式，确保报告符合预定规范。不适用于非 JSON 格式或动态 schema 场景。

## 输入
- 报告 JSON 数据
- JSON Schema 定义文件（包含必填字段、类型约束、数组规则等）
- 验证上下文（如任务 ID、任务名称、时间戳等）

## 输出
- 验证结果（通过/失败）
- 错误详情（缺失字段、类型错误、数组约束违反等）
- 修复建议

## 流程节点
1. 加载 JSON Schema → 2. 解析报告 JSON → 3. 执行验证 → 4. 分析错误 → 5. 输出结果

每步含：
- 操作：使用 JSON Schema 验证器（如 ajv、jsonschema）进行校验
- 参数：schema 版本（如 draft-07）、错误报告格式
- 工具：JSON Schema 验证库、命令行工具（如 jsonschema-cli）
- 质量门禁：验证必须覆盖所有必填字段；错误报告必须包含具体位置和原因

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 必填字段 | `required` 关键字定义的字段 | [D1] | 缺失任一必填字段即验证失败 |
| 任务身份 | `task_id` 和 `task` 字段 | [D2] | 报告必须包含任务标识，且与上下文一致 |
| 数组约束 | `type: "array"` 及 `items` 定义 | [D1] | 数组字段必须符合 items 中定义的 schema |
| 输出格式 | `properties` 和 `additionalProperties` | [D1] | 字段类型、格式必须符合 schema 定义 |
| 字符串格式 | `format` 关键字 | [D1] | 支持 date-time、email、uri 等预定义格式 |

## 边界与分流
- JSON Schema 草案版本不匹配时，需明确指定验证器支持的版本（如 draft-07、2020-12）。
- `additionalProperties` 默认为 `true`，若需禁止额外字段，需显式设置为 `false`。
- 嵌套对象或数组的验证需递归应用 schema。
- 当验证器不支持特定 `format` 时，该格式仅作为注解，不影响验证结果。

## 质量检查
- 验证点：所有必填字段存在且类型正确；数组长度符合 `minItems`/`maxItems`；字符串格式符合 `format` 约束。
- 阈值：验证通过率应达到 100%（即所有报告均通过 schema 校验）。
- 失败处理：验证失败时，提供具体的错误位置和修复建议；记录失败案例用于 schema 优化。

## 回退策略
- 当 JSON Schema 验证器不可用时，可使用简单的类型检查和字段存在性检查作为临时方案。
- 若 schema 定义不完整，建议补充 `description` 和 `examples` 以提高可维护性。

## 资源召回建议
- 当遇到报告格式不一致、API 响应校验失败、配置文件解析错误时召回本卡片。
- 配套资源：`general-json-parsing-error-handling`、`general-api-contract-design`。

## 补充证据（开源文档/用户自有，可选）
[D1] JSON Schema reference, JSON Schema, Understanding JSON Schema, URL: https://json-schema.org/understanding-json-schema/reference/（accessed_at 2026-09-17，交叉验证）
[D2] Type-specific Keywords, JSON Schema, Understanding JSON Schema, URL: https://json-schema.org/understanding-json-schema/reference/type（accessed_at 2026-09-17，交叉验证）

## 证据来源
[1] JSON Schema reference, JSON Schema, Understanding JSON Schema, URL: https://json-schema.org/understanding-json-schema/reference/
[2] Type-specific Keywords, JSON Schema, Understanding JSON Schema, URL: https://json-schema.org/understanding-json-schema/reference/type