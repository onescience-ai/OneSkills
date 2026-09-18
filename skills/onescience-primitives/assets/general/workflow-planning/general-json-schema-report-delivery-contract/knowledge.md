# JSON Schema 报告交付契约

## 适用范围
适用于需要生成结构化报告（如 JSON 格式）的场景，确保输出符合预定义的 Schema 契约，包括必填字段、数据类型、格式约束和业务规则验证。适用于 API 响应、数据导出、系统间数据交换等。

## 输入
- JSON Schema 定义文件
- 待验证的 JSON 数据
- 验证配置（严格模式、错误处理策略）
- 上下文信息（如任务 ID、时间戳）

## 输出
- 验证结果（通过/失败）
- 错误详情（字段路径、错误类型、错误消息）
- 修正建议（可选）
- 验证报告（包含统计信息）

## 流程节点
1. **Schema 加载** → 解析 JSON Schema，构建验证器
2. **数据预处理** → 清理输入数据，处理缺失值
3. **结构验证** → 检查必填字段、数据类型、数组约束
4. **格式验证** → 验证日期格式、邮箱格式、URL 格式等
5. **业务规则验证** → 检查字段间依赖关系、范围约束
6. **任务身份验证** → 验证任务 ID、时间戳等身份字段与上下文一致性 [1]
7. **错误处理** → 收集所有错误，生成结构化错误报告
8. **验证报告** → 汇总验证结果，提供统计信息

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 必填字段检查 | 所有 required 字段必须存在 | [D1] | Schema 中定义的必填字段 |
| 类型验证 | 字段值必须符合 type 定义 | [D1] | 支持 string, number, integer, boolean, array, object, null |
| 数组约束 | minItems, maxItems, uniqueItems | [D1] | 数组长度和唯一性约束 |
| 字符串约束 | minLength, maxLength, pattern | [D1] | 字符串长度和正则匹配 |
| 任务身份验证 | task_id, timestamp 等字段与上下文一致 | [1] | 防止任务混淆和重放攻击 |

### 校准数值
以下数值来自常见实践，供量级校准；其他体系需以自身证据重新锚定。
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 最大嵌套深度 | 10 层 | [D2] | 避免递归验证过深 |
| 最大数组长度 | 1000 元素 | [D2] | 性能考虑限制 |
| 错误消息最大长度 | 256 字符 | [D2] | 便于日志记录和显示 |
| 验证超时 | 30 秒 | [D2] | 复杂 Schema 验证超时 |
| Classical JSON Schema 验证复杂度 | PTIME | [1] | 固定 Schema 时验证效率高 |
| Modern JSON Schema 验证复杂度 | PSPACE-complete | [1] | 动态引用导致复杂度显著增加 |

## 边界与分流
- **Schema 版本不兼容**：使用 Schema 版本检测，必要时进行转换
- **性能问题**：对于大型数据，采用流式验证或分块验证
- **自定义验证逻辑**：对于复杂业务规则，使用自定义验证器
- **向后兼容**：Schema 演进时确保旧数据仍能验证通过
- **复杂 Schema 验证**：Modern JSON Schema（Draft 2019-09+）的动态引用和注释依赖验证可能导致 PSPACE 复杂性 [1]
- **任务身份不匹配**：验证任务 ID、时间戳等身份字段与上下文一致性

## 质量检查
- 验证所有必填字段是否存在
- 检查数据类型是否匹配
- 验证格式约束（日期、邮箱等）
- 确保错误消息清晰可读
- 验证性能指标（验证时间、内存使用）

## 回退策略
- 若 Schema 验证失败，尝试使用宽松模式验证
- 若自定义验证器异常，回退到基础结构验证
- 若性能问题，简化验证规则或异步验证
- 若 Schema 版本不兼容，提供转换层

## 资源召回建议
当需要处理以下场景时召回本卡片：
- API 响应格式验证
- 数据导出前的格式检查
- 系统间数据交换的契约验证
- 配置文件的格式校验
- 测试数据的结构验证

## 补充证据（开源权威文档）
[D1] JSON Schema Specification, JSON Schema Organization, 版本 2020-12, URL: https://json-schema.org/specification.html（accessed_at，交叉验证）
[D2] Understanding JSON Schema, JSON Schema Organization, 版本 2020-12, URL: https://json-schema.org/understanding-json-schema/（accessed_at，交叉验证）

## 批次补充 2026-09-18（onescience-knowledge-harvester）

### 补充证据：JSON Schema 类型关键字与对象约束详解

本次补充引入 JSON Schema 官方文档中关于类型关键字和对象约束的详细规范，增强对必填字段、任务身份一致性和数组约束的校验能力。

**类型约束补充**（基于 [D3]）：

| 类型 | 关键字 | 说明 |
|------|--------|------|
| array | items, additionalItems, minItems, maxItems, uniqueItems | 定义元素 Schema、额外元素处理、长度约束、唯一性 |
| number | minimum, maximum, exclusiveMinimum, exclusiveMaximum, multipleOf | 定义数值范围和倍数约束 |
| object | required, properties, additionalProperties, patternProperties, minProperties, maxProperties, dependencies | 定义必填属性、属性 Schema、额外属性处理、模式匹配、属性数量约束 |
| string | minLength, maxLength, pattern, format | 定义字符串长度、正则匹配、语义格式 |

**对象约束补充**（基于 [D4]）：

| 关键字 | 说明 |
|--------|------|
| required | 字符串数组，声明必填字段；Draft 4 要求 ≥1 个元素，Draft 6+ 允许空数组 |
| additionalProperties | false 禁止额外字段；Schema 值限制额外字段类型；默认允许 |
| patternProperties | 正则表达式映射到 Schema，匹配属性名时验证值 |
| unevaluatedProperties | Draft 2019-09 新增，识别子 Schema 中声明的字段 |
| propertyNames | 验证属性名本身是否符合 Schema |

**格式验证补充**（基于 [D3]）：

| 格式 | 说明 |
|------|------|
| date-time | RFC 3339 日期时间，如 2018-11-13T20:20:39+00:00 |
| date | RFC 3339 日期，如 2018-11-13 |
| time | RFC 3339 时间，如 20:20:39+00:00 |
| email | RFC 5321 邮箱地址 |
| uri | RFC 3986 URI |
| uuid | RFC 4122 UUID |
| ipv4/ipv6 | IP 地址格式 |
| regex | ECMA 262 正则表达式 |

**组合 Schema 注意事项**：
- additionalProperties 只识别同级 subschema 中声明的字段
- 使用 allOf 扩展 Schema 时，需在扩展层重新声明 additionalProperties
- unevaluatedProperties 可解决跨 subschema 识别问题

### 补充证据：JSON Schema 验证复杂性与性能优化

本次补充引入 JSON Schema 验证的理论复杂性分析和性能优化方法，增强对验证过程的理解和优化能力。

**验证复杂性分析**（基于 [1]）：

| Schema 版本 | 验证复杂度 | 关键特性 | 说明 |
|-------------|------------|----------|------|
| Classical JSON Schema (≤ Draft-07) | PTIME | 静态引用、注释独立 | 验证效率高，适合实时场景 |
| Modern JSON Schema (≥ Draft 2019-09) | PSPACE-complete | 动态引用、注释依赖验证 | 复杂度显著增加，需谨慎设计 |

**性能优化方法**（基于 [2]）：

| 方法 | 说明 | 性能提升 |
|------|------|----------|
| Schema 编译 | 将复杂 Schema 编译为高效表示 | 平均 10x 加速 |
| 预构建验证器 | 在构建时解析 Schema，运行时直接使用 | 减少运行时开销 |
| 严格规范遵守 | 确保验证结果符合 JSON Schema 规范 | 避免错误验证结果 |

**见证生成算法**（基于 [3]）：

| 问题 | 说明 | 解决方法 |
|------|------|----------|
| Schema 可满足性 | 判断 Schema 是否有有效实例 | 交替树自动机可达性 |
| Schema 包含性 | 判断一个 Schema 是否包含另一个 | 见证生成算法 |
| Schema 等价性 | 判断两个 Schema 是否等价 | 互相包含性检查 |

**否定闭包问题**（基于 [4]）：

| 问题 | 说明 | 影响 |
|------|------|------|
| 否定运算符不封闭 | JSON Schema 缺少否定对偶运算符 | 部分否定表达式无法直接表示 |
| 代数重构 | 定义 JSON Schema 的代数重构形式 | 支持见证生成和 Schema 分析 |

## 批次补充 2026-09-18（任务 254 归因报告）

### 归因分析 JSON Schema 校验失败案例（任务 254）

以下案例来自任务 254 的归因报告，展示了 JSON Schema 报告交付契约校验失败的典型模式：

| 校验失败类型 | 症状 | 根本原因 | 处理建议 |
|-------------|------|----------|----------|
| 必填字段缺失 | 缺少顶层字段 issues/summary/task/task_id | 输出结构未遵循 Schema 定义 | 在输出前验证必填字段完整性 |
| 额外字段包含 | 包含额外字段 error/sessionID/timestamp/type | 输出结构包含未定义字段 | 使用 additionalProperties: false 约束 |
| 任务身份不匹配 | task_id 与任务索引不一致、task 与任务 name 不一致 | 身份信息传递错误 | 确保任务身份在整个流程中一致 |
| 类型约束违反 | summary 必须是非空字符串、issues 必须是数组 | 字段类型不符合 Schema 定义 | 验证字段类型和格式约束 |

**关键观察**：
- 必填字段缺失和额外字段包含是最常见的 Schema 校验失败模式
- 任务身份不匹配（task_id 与任务索引不一致）会导致下游系统无法正确关联任务
- 类型约束违反（如 issues 必须是数组）会导致数据解析失败
- 即使退出码为 0，Schema 校验失败也会导致报告无法被下游系统接受

**补充证据**：
[U1] 任务 254 归因报告，任务：复杂地形风电场轮毂高度短期风速预报，故障：报告校验错误（缺少顶层字段 issues/summary/task/task_id、包含额外字段 error/sessionID/timestamp/type、task_id 与任务索引不一致、task 与任务 name 不一致、summary 必须是非空字符串、issues 必须是数组），2026-09-18（用户自有，经归因报告佐证）

## 证据来源
[1] Lyes Attouche, Mohamed-Amine Baazizi, Dario Colazzo, Giorgio Ghelli, Carlo Sartiani, Stefanie Scherzinger, "Validation of Modern JSON Schema: Formalization and Complexity", arXiv:2307.10034, 2023
[2] Juan Cruz Viotti, Michael J. Mior, "Blaze: Compiling JSON Schema for 10x Faster Validation", arXiv:2503.02770, 2025
[3] Lyes Attouche, Mohamed-Amine Baazizi, Dario Colazzo, Giorgio Ghelli, Carlo Sartiani, Stefanie Scherzinger, "Witness Generation for JSON Schema", arXiv:2202.12849, 2022
[4] Mohamed-Amine Baazizi, Dario Colazzo, Giorgio Ghelli, Carlo Sartiani, Stefanie Scherzinger, "Negation-Closure for JSON Schema", arXiv:2202.13434, 2022
[D1] JSON Schema Specification, JSON Schema Organization, 版本 2020-12
[D2] Understanding JSON Schema, JSON Schema Organization, 版本 2020-12