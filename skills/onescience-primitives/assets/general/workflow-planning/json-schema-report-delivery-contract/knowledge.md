# JSON Schema 报告交付契约

## 适用范围

本卡片服务于JSON格式报告的结构化验证与契约合规检查任务。适用于数据交换、API响应、配置文件、科学报告、归因分析输出等需要确保JSON数据符合预定Schema的场景。帮助开发者和数据工程师定义、验证和维护JSON数据的结构契约，确保数据交付的完整性和一致性。

## 输入

- JSON Schema定义文件（.json）
- 待验证的JSON数据
- 验证配置（strict模式、错误处理策略）
- 验证上下文（字段描述、业务规则）

## 输出

- 验证结果（通过/失败）
- 错误详情（缺失字段、类型不匹配、格式错误）
- 校验报告（符合Schema的字段列表、不符合项）
- 修复建议（如何调整数据以符合Schema）

## 流程节点

1. **Schema加载与解析** → 读取JSON Schema文件，构建验证规则树
2. **数据加载与预处理** → 读取JSON数据，处理编码和格式问题
3. **类型验证** → 检查字段类型是否符合Schema定义
4. **结构验证** → 检查必需字段、属性约束、数组长度
5. **格式验证** → 检查字符串格式（日期、邮箱、URI等）
6. **组合验证** → 使用allOf/anyOf/oneOf/not进行复杂约束验证
7. **条件验证** → 使用if/then/else进行条件字段验证
8. **结果生成与报告** → 生成详细的验证报告和修复建议

每步含：操作、参数、工具、质量门禁

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| type | string/number/boolean/null/object/array | [D2] | 字段基础类型定义 |
| required | ["field1", "field2"] | [D5] | 必需字段列表 |
| properties | { "field": schema } | [D5] | 对象属性定义 |
| items | schema | [D4] | 数组元素Schema |
| enum | [value1, value2] | [D7] | 枚举值约束 |
| const | value | [D8] | 固定值约束 |
| pattern | "regex" | [D6] | 字符串正则约束 |
| minimum/maximum | number | [D6] | 数值范围约束 |
| minLength/maxLength | number | [D6] | 字符串长度约束 |
| minItems/maxItems | number | [D4] | 数组长度约束 |
| additionalProperties | false/schema | [D5] | 额外属性控制 |
| allOf/anyOf/oneOf/not | [schema...] | [D7] | 组合约束 |
| if/then/else | schema | [D8] | 条件约束 |

### 校准数值

以下数值来自JSON Schema官方文档，供量级校准；其他Schema变体需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认行为 | 允许额外属性 | [D5] | 未设置additionalProperties时的默认行为 |
| 默认行为 | 属性可选 | [D5] | 未设置required时的默认行为 |
| 正则语法 | ECMA 262子集 | [D9] | JSON Schema支持的正则表达式语法 |
| 格式验证 | 可选启用 | [D3] | format关键字默认为注解，可配置为断言 |
| 嵌套限制 | 无硬性限制 | [D7] | 递归Schema可能导致性能问题 |

## 边界与分流

- **Schema版本不兼容**：不同JSON Schema版本（Draft 4/6/7/2019-09/2020-12）关键字可能不同，需确认版本
- **性能问题**：复杂组合Schema（allOf/anyOf/oneOf）可能显著增加验证时间
- **格式验证失败**：format关键字默认为注解，需显式启用格式断言
- **循环引用**：$ref和$recursiveRef可能导致无限递归，需设置深度限制
- **未知关键字**：Schema中包含未知关键字时，验证器通常忽略但不报错
- **空Schema**：{}匹配任何数据，可能掩盖验证缺失

## 质量检查

- 验证Schema本身是否为有效JSON
- 检查required字段是否在properties中定义
- 验证enum值是否唯一
- 检查minimum/maximum逻辑一致性
- 验证正则表达式语法正确性
- 检查嵌套Schema深度是否合理
- 验证$ref引用路径是否有效

## 回退策略

- Schema验证失败时，提供详细的错误位置和修复建议
- 格式验证不通过时，提供格式转换工具或正则修正建议
- 组合验证复杂时，拆分为多个简单Schema逐步验证
- 循环引用时，使用$recursiveRef或重构Schema结构
- 性能不足时，优化Schema结构或使用增量验证

## 资源召回建议

- 当需要定义JSON数据结构契约时召回本卡片
- 当需要验证JSON数据是否符合Schema时召回本卡片
- 当需要诊断JSON验证失败原因时召回本卡片
- 配套资源：JSON Schema官方文档、JSON验证器库（ajv、jsonschema等）

## 补充证据（开源文档）

[D1] JSON Schema reference, JSON Schema, 2020-12, URL: https://json-schema.org/understanding-json-schema/（accessed_at 2026-09-17，交叉验证）
[D2] JSON Schema - Type-specific Keywords, JSON Schema, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/type（accessed_at 2026-09-17，交叉验证）
[D3] JSON Schema - Schema annotations and comments, JSON Schema, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/metadata（accessed_at 2026-09-17，交叉验证）
[D4] JSON Schema - array, JSON Schema, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/array（accessed_at 2026-09-17，交叉验证）
[D5] JSON Schema - object, JSON Schema, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/object（accessed_at 2026-09-17，交叉验证）
[D6] JSON Schema - string, JSON Schema, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/string（accessed_at 2026-09-17，交叉验证）
[D7] JSON Schema - Boolean JSON Schema combination, JSON Schema, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/combining（accessed_at 2026-09-17，交叉验证）
[D8] JSON Schema - Conditional schema validation, JSON Schema, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/conditionals（accessed_at 2026-09-17，交叉验证）
[D9] JSON Schema - Regular Expressions, JSON Schema, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/regular_expressions（accessed_at 2026-09-17，交叉验证）

## 证据来源

[1] JSON Schema官方参考文档
[2] JSON Schema类型关键字文档
[3] JSON Schema注解与评论文档
[4] JSON Schema数组验证文档
[5] JSON Schema对象验证文档
[6] JSON Schema字符串验证文档
[7] JSON Schema组合验证文档
[8] JSON Schema条件验证文档
[9] JSON Schema正则表达式文档