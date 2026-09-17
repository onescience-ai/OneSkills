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
