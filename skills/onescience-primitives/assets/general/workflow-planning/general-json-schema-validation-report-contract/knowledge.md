# 通用JSON Schema报告契约验证

## 适用范围

面向结构化数据输出的JSON Schema契约验证，提供报告交付前的字段完整性、类型正确性和业务一致性校验。适用于自动化分析工具的输出验证、API响应合规性检查、数据管道的质量门禁等需要确保JSON输出符合预定义契约的场景。不适用于非结构化文本输出或二进制格式验证。

## 输入

- **JSON Schema定义**：描述输出结构的schema文件（JSON/YAML格式）
- **待验证数据**：实际生成的JSON输出
- **业务规则**：Schema未覆盖的额外约束（如字段间依赖、值域限制）
- **上下文信息**：任务ID、任务名称、执行环境等元数据

## 输出

- **验证结果**：通过/失败状态
- **错误列表**：每个错误包含路径、错误类型、详细消息、修复建议
- **警告列表**：非致命问题（如额外字段、可选字段缺失）
- **修复建议**：自动修复提示或人工干预指引

## 流程节点

### 1. Schema加载与解析
- **操作**：读取JSON Schema文件，解析为Python字典
- **参数**：`json.load()` 或 `yaml.safe_load()`
- **工具**：Python json/yaml模块
- **质量门禁**：验证Schema本身是否为合法JSON，检查$ref引用是否可解析

### 2. 必填字段校验
- **操作**：遍历schema中的required数组，检查每个必填字段是否存在
- **参数**：`schema.get("required", [])`
- **工具**：集合运算（required - set(data.keys())）
- **质量门禁**：缺失字段列表记录为ERROR级别

### 3. 类型约束校验
- **操作**：对每个字段按schema定义的type进行类型检查
- **参数**：type映射表（string/number/integer/boolean/array/object/null）
- **工具**：isinstance()或jsonschema内置验证
- **质量门禁**：类型不匹配记录为ERROR级别

### 4. 数组与嵌套结构校验
- **操作**：验证数组元素类型、最小/最大长度、嵌套对象结构
- **参数**：items, minItems, maxItems, additionalProperties
- **工具**：递归验证函数
- **质量门禁**：嵌套深度超过阈值时发出警告

### 5. 枚举与格式校验
- **操作**：检查字段值是否在enum定义范围内，验证format约束（如date-time, email, uri）
- **参数**：enum, format
- **工具**：正则表达式匹配或专用format检查库
- **质量门禁**：格式错误记录为WARNING级别（除非format为required）

### 6. 身份一致性校验
- **操作**：验证报告中的任务身份字段与预期一致
- **参数**：task_id, task, timestamp等元数据字段
- **工具**：字符串比较或模式匹配
- **质量门禁**：身份不匹配记录为ERROR级别，阻止报告交付

### 7. 业务规则校验
- **操作**：执行Schema未覆盖的额外约束检查
- **参数**：自定义验证函数、依赖关系规则
- **工具**：规则引擎或条件判断
- **质量门禁**：业务规则违规记录为WARNING或ERROR（取决于规则优先级）

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| required字段缺失 | ERROR | [D1] JSON Schema Core | 必填字段缺失阻止交付 |
| type类型不匹配 | ERROR | [D1] JSON Schema Validation | 类型错误为致命问题 |
| additionalProperties | WARNING | [D1] JSON Schema Core | 额外字段默认警告（除非schema禁止） |
| enum值域违规 | ERROR | [D1] JSON Schema Validation | 值不在允许范围内 |
| format格式错误 | WARNING | [D1] JSON Schema Validation | 格式问题为非致命警告 |
| $ref引用解析失败 | ERROR | [D1] JSON Schema Core | Schema自身结构错误 |
| 嵌套深度>10 | WARNING | [D2] 实践建议 | 过深嵌套可能影响可读性 |
| 字符串长度>1MB | WARNING | [D2] 实践建议 | 超长字符串可能影响性能 |

### 校准数值（实例值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 最大数组长度 | 10000 | [D2] 实践建议 | 超过此值发出性能警告 |
| 最大对象属性数 | 100 | [D2] 实践建议 | 超过此值发出可读性警告 |
| 最大嵌套深度 | 10 | [D2] 实践建议 | 超过此值发出复杂度警告 |
| 最大字符串长度 | 1MB | [D2] 实践建议 | 超过此值发出存储警告 |

## 边界与分流

### 前提1：JSON Schema文件本身合法
- **不成立时转向**：先修复Schema文件（JSON语法错误、$ref循环引用等），再重新验证数据

### 前提2：Schema版本与数据格式匹配
- **不成立时转向**：检查Schema版本（Draft-04/07/2020-12），更新Schema或调整数据格式

### 前提3：业务规则可表达为Schema约束
- **不成立时转向**：将复杂业务规则拆分为Schema验证+自定义验证函数的组合

### 前提4：上下文信息完整
- **不成立时转向**：记录缺失的上下文字段，标记为"元数据不完整"警告

## 质量检查

### Schema完整性
- 验证Schema包含所有必填字段定义
- 检查$ref引用链无循环
- 验证enum值域覆盖所有合法值

### 数据一致性
- 验证所有必填字段存在且非null
- 检查类型约束满足
- 验证数组/嵌套结构符合定义

### 身份匹配
- 验证task_id与任务索引一致
- 检查task名称与任务name匹配
- 验证timestamp格式正确（ISO 8601）

### 额外字段处理
- 默认策略：额外字段发出WARNING但不阻止交付
- 严格策略：additionalProperties=false时，额外字段触发ERROR
- 选择策略：根据业务需求配置（建议：分析报告用宽松策略，API响应用严格策略）

## 回退策略

### Schema验证失败
- **必填字段缺失**：记录缺失字段列表，提供填充建议，阻止交付直到修复
- **类型错误**：记录类型不匹配详情，提供类型转换建议
- **格式错误**：记录格式问题，提供格式修正示例
- **$ref解析失败**：检查Schema文件路径和引用完整性

### 身份验证失败
- **task_id不匹配**：检查是否使用了正确的任务上下文
- **task名称不匹配**：检查任务定义文件或配置
- **timestamp无效**：使用当前时间戳替代，标记为"时间戳已修正"

### 业务规则违规
- **警告级别违规**：记录问题但允许交付，标记为"已知问题"
- **错误级别违规**：阻止交付，提供修复建议或例外申请流程

### 降级策略
- **Schema文件缺失**：使用最小化Schema（仅验证JSON语法和顶级字段存在性）
- **验证器不可用**：使用手动JSON解析进行基本检查
- **性能问题**：对大型JSON使用流式验证或分块验证

## 资源召回建议

**何时召回本卡片**：
- 需要设计CLI工具或分析工具的输出格式规范
- 需要验证JSON输出是否符合预定义契约
- 需要构建自动化数据质量检查流程
- 需要调试JSON输出格式不匹配问题

**配套资源**：
- `general-cli-fault-diagnosis-error-handling`：CLI工具执行故障诊断
- `general-data-validation-framework`：通用数据验证框架（如需更复杂的验证逻辑）
- `general-report-generation-standard`：报告生成规范（如需设计输出格式）

## 补充证据

### 开源权威文档

[D1] **JSON Schema Specification (Draft 2020-12)**, json-schema.org, 2020. URL: https://json-schema.org/draft/2020-12/json-schema-core (accessed_at: 2026-09-16, 交叉验证：JSON Schema核心规范)
- 定义了JSON Schema的语法结构、$ref引用机制、类型系统
- 规定了required、properties、items等关键字的语义

[D2] **JSON Schema Validation (Draft 2020-12)**, json-schema.org, 2020. URL: https://json-schema.org/draft/2020-12/json-schema-validation (accessed_at: 2026-09-16, 交叉验证：JSON Schema验证规则)
- 定义了type、enum、format等验证关键字
- 规定了错误报告格式和验证算法

[D3] **Python jsonschema Library Documentation**, Python Package Authority, 2024. URL: https://python-jsonschema.readthedocs.io/ (accessed_at: 2026-09-16, 单源参考：Python实现参考)
- 提供Draft4Validator、Draft7Validator、Draft202012Validator等版本支持
- 定义了validate()、iter_errors()等API接口

## 证据来源

本文档基于以下权威技术标准和官方文档：
- [D1] JSON Schema Specification (Draft 2020-12) - JSON Schema核心规范的权威定义
- [D2] JSON Schema Validation (Draft 2020-12) - JSON Schema验证规则的权威定义
- [D3] Python jsonschema Library - JSON Schema验证的Python实践参考

## 批次补充（2026-09-17：基于权威文档的Object类型验证详细规则）

### Object类型基础验证

基于 JSON Schema Object Reference [D4] 补充以下对象验证规则：

| 关键字 | 功能 | 来源 | 说明 |
|--------|------|------|------|
| type: "object" | 验证值为对象（Python dict） | [D4] | JSON对象键必须为字符串 |
| properties | 定义对象属性及其Schema | [D4] | 每个键对应一个属性Schema |
| required | 必填属性数组 | [D4] | 数组中的属性必须存在 |
| additionalProperties | 额外属性控制 | [D4] | false=禁止额外属性；Schema=验证额外属性 |
| patternProperties | 按正则匹配的属性Schema | [D4] | 属性名匹配正则时应用对应Schema |
| unevaluatedProperties | 未评估属性控制 | [D4] | 可识别子Schema中声明的属性 |
| minProperties/maxProperties | 属性数量约束 | [D4] | 非负整数，限制对象属性数量 |
| propertyNames | 属性名验证 | [D4] | 验证属性名是否符合Schema |

### additionalProperties 详细机制

| 配置 | 行为 | 来源 | 说明 |
|------|------|------|------|
| additionalProperties: false | 禁止任何未在properties/patternProperties中声明的属性 | [D4] | 严格模式 |
| additionalProperties: {type: "string"} | 额外属性的值必须为字符串 | [D4] | 宽松模式，但限制额外属性类型 |
| 默认值（不设置） | 允许任意额外属性 | [D4] | 最宽松模式 |

### required 与 properties 交互

| 场景 | 结果 | 来源 | 说明 |
|------|------|------|------|
| 属性在required中但不在properties中 | ERROR | [D4] | 必填但未定义Schema |
| 属性在properties中但不在required中 | 有效 | [D4] | 可选属性 |
| 属性值为null | 不等同于属性不存在 | [D4] | null是有效值，需单独定义type |

### patternProperties 正则匹配

| 正则示例 | 匹配属性 | 来源 | 说明 |
|----------|----------|------|------|
| "^S_" | 所有以S_开头的属性 | [D4] | 需用^和$锚定避免误匹配 |
| "^I_" | 所有以I_开头的属性 | [D4] | 例如I_0, I_42 |
| "p" | 所有包含p的属性 | [D4] | 会匹配apple等，通常不推荐 |

### unevaluatedProperties vs additionalProperties

| 特性 | additionalProperties | unevaluatedProperties | 来源 |
|------|---------------------|----------------------|------|
| 识别子Schema声明的属性 | 不识别 | 识别 | [D4] |
| 与allOf组合使用 | 可能导致意外失败 | 正常工作 | [D4] |
| 条件属性声明 | 不支持 | 支持（配合if/then） | [D4] |
| 推荐使用场景 | 简单单层Schema | 复杂组合Schema | [D4] |

### propertyNames 验证

| 配置 | 行为 | 来源 | 说明 |
|------|------|------|------|
| propertyNames: {pattern: "^[A-Za-z_][A-Za-z0-9_]*$"} | 属性名必须为有效标识符 | [D4] | 确保可作为编程语言属性名 |
| propertyNames: {maxLength: 50} | 属性名长度限制 | [D4] | 防止过长属性名 |

### 实际应用示例

```json
{
  "type": "object",
  "properties": {
    "task_id": {"type": "string"},
    "task": {"type": "string"},
    "issues": {"type": "array"},
    "summary": {"type": "string"}
  },
  "required": ["task_id", "task", "issues", "summary"],
  "additionalProperties": false
}
```
[D4] 此Schema定义了归因报告的基本结构，additionalProperties:false确保不接受额外字段。

### 常见错误与修复

| 错误 | 原因 | 修复方案 | 来源 |
|------|------|----------|------|
| Missing property | required中的属性不存在 | 添加缺失属性 | [D4] |
| Additional property | additionalProperties:false时有额外属性 | 删除额外属性或设置为true | [D4] |
| Invalid type | 属性值类型不匹配 | 检查properties中的type定义 | [D4] |
| Invalid pattern | 属性名不符合正则 | 调整属性名或正则表达式 | [D4] |

[D4] JSON Schema Object Reference, json-schema.org, Draft 2020-12. URL: https://json-schema.org/understanding-json-schema/reference/object (accessed_at: 2026-09-17, 交叉验证：JSON Schema官方文档)

## 批次补充（2026-09-17：基于Understanding JSON Schema的类型验证详细规则）

### 基础类型验证

基于 Understanding JSON Schema [D5] 补充以下类型验证规则：

| 类型 | JSON值 | Python等价类型 | 验证规则 | 来源 |
|------|--------|----------------|----------|------|
| string | "hello" | str | 验证值为字符串 | [D5] |
| number | 42, 3.14 | int/float | 验证值为数字（整数或浮点数） | [D5] |
| integer | 42 | int | 验证值为整数 | [D5] |
| boolean | true/false | bool | 验证值为布尔值 | [D5] |
| array | [1, 2, 3] | list | 验证值为数组 | [D5] |
| object | {"key": "value"} | dict | 验证值为对象 | [D5] |
| null | null | None | 验证值为空 | [D5] |

### 数组验证规则

| 关键字 | 功能 | 示例 | 来源 |
|--------|------|------|------|
| items | 定义数组元素的Schema | {"items": {"type": "string"}} | [D5] |
| minItems | 数组最小长度 | {"minItems": 1} | [D5] |
| maxItems | 数组最大长度 | {"maxItems": 10} | [D5] |
| uniqueItems | 数组元素唯一性 | {"uniqueItems": true} | [D5] |
| contains | 数组必须包含至少一个匹配元素 | {"contains": {"type": "number"}} | [D5] |

### 数值验证规则

| 关键字 | 功能 | 示例 | 来源 |
|--------|------|------|------|
| minimum | 最小值（包含） | {"minimum": 0} | [D5] |
| maximum | 最大值（包含） | {"maximum": 100} | [D5] |
| exclusiveMinimum | 最小值（不包含） | {"exclusiveMinimum": 0} | [D5] |
| exclusiveMaximum | 最大值（不包含） | {"exclusiveMaximum": 100} | [D5] |
| multipleOf | 倍数约束 | {"multipleOf": 5} | [D5] |

### 字符串验证规则

| 关键字 | 功能 | 示例 | 来源 |
|--------|------|------|------|
| minLength | 最小长度 | {"minLength": 1} | [D5] |
| maxLength | 最大长度 | {"maxLength": 255} | [D5] |
| pattern | 正则表达式匹配 | {"pattern": "^[a-zA-Z0-9]+$"} | [D5] |
| format | 格式验证 | {"format": "email"} | [D5] |

### 格式验证详细规则

基于 Understanding JSON Schema [D5] 补充以下格式验证规则：

| 格式 | 验证内容 | 示例值 | 来源 |
|------|----------|--------|------|
| date-time | ISO 8601日期时间 | "2026-09-17T16:50:00Z" | [D5] |
| date | ISO 8601日期 | "2026-09-17" | [D5] |
| time | ISO 8601时间 | "16:50:00Z" | [D5] |
| email | 电子邮件地址 | "user@example.com" | [D5] |
| hostname | 互联网主机名 | "example.com" | [D5] |
| ipv4 | IPv4地址 | "192.168.1.1" | [D5] |
| ipv6 | IPv6地址 | "2001:0db8:85a3:0000:0000:8a2e:0370:7334" | [D5] |
| uri | 统一资源标识符 | "https://example.com" | [D5] |
| uuid | 通用唯一标识符 | "3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a" | [D5] |

### 类型验证错误处理

| 错误类型 | 错误消息示例 | 修复建议 | 来源 |
|----------|--------------|----------|------|
| type-mismatch | "Expected string, got number" | 检查字段值类型 | [D5] |
| format-violation | "Invalid email format" | 修正字段格式 | [D5] |
| range-violation | "Value below minimum" | 调整数值范围 | [D5] |
| length-violation | "String too short" | 调整字符串长度 | [D5] |
| pattern-violation | "String does not match pattern" | 修正字符串内容 | [D5] |

### 类型验证最佳实践

| 实践 | 描述 | 来源 |
|------|------|------|
| 使用最具体的类型 | 优先使用integer而非number（当值为整数时） | [D5] |
| 组合类型验证 | 使用"anyOf"/"oneOf"验证多种可能类型 | [D5] |
| 条件类型验证 | 使用"if/then/else"根据条件选择类型验证 | [D5] |
| 默认值设置 | 使用"default"为可选字段提供默认值 | [D5] |

[D5] Understanding JSON Schema, JSON Schema, 2026. URL: https://json-schema.org/understanding-json-schema/ (accessed_at: 2026-09-17, 交叉验证：JSON Schema官方文档)
