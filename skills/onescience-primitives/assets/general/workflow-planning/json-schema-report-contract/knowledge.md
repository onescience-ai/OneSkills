# JSON Schema 报告交付契约

## 适用范围

当需要确保自动化流水线输出的结构化报告符合预定格式、字段完整性和类型约束时，本卡提供基于 JSON Schema 的验证框架。适用于任何需要交付 JSON 格式报告的场景，包括归因分析报告、测试结果报告、数据处理报告和 API 响应验证。

## 输入

- JSON Schema 定义文件（.schema.json）
- 待验证的 JSON 报告内容
- 验证配置（严格模式/宽松模式、错误处理策略）

## 输出

- 验证结果（通过/失败）
- 错误详情（字段路径、错误类型、期望值）
- 修复建议

## 流程节点

### 1. Schema 加载与解析

加载 JSON Schema 并解析其结构：

- 声明方言：使用 `$schema` 关键字指定 JSON Schema 版本 [D1]
- 解析必填字段：提取 `required` 数组中的字段列表 [D1]
- 解析类型约束：提取 `type`、`properties`、`items` 等约束 [D1]
- 解析组合约束：处理 `allOf`、`anyOf`、`oneOf` 等组合模式 [D2]

### 2. 必填字段验证

检查报告是否包含所有必需字段：

- 顶层必填字段（如 task_id, task, summary, issues）
- 嵌套对象必填字段（如 issues[].optimization_plan）
- 条件必填字段（dependentRequired）[D1]

### 3. 类型约束验证

验证每个字段的值类型是否符合约束：

- 基础类型：null, boolean, object, array, number, string [D1]
- 数值范围：minimum, maximum, exclusiveMinimum, exclusiveMaximum [D2]
- 字符串约束：minLength, maxLength, pattern, format [D2]
- 数组约束：minItems, maxItems, uniqueItems [D2]

### 4. 语义约束验证

验证字段内容的语义正确性：

- 枚举值验证：enum 关键字限制可选值 [D2]
- 常量验证：const 关键字要求精确匹配 [D2]
- 格式验证：format 关键字验证日期、邮箱、URI 等格式 [D2]
- 依赖验证：dependencies 关键字定义字段间依赖关系 [D2]

### 5. 任务身份一致性验证

确保报告与任务身份匹配：

- task_id 与任务索引一致
- task 与任务 name 一致
- summary 为非空字符串
- issues 为数组类型

### 6. 错误聚合与报告

收集所有验证错误并生成结构化报告：

- 错误路径（JSON Pointer）
- 错误类型（required/type/pattern/...）
- 期望值与实际值
- 修复建议

## 关键参数

### 通用判据（方法层，同类体系可参考）

| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| required 数组非空 | true | [D1] | 至少定义一个必填字段 |
| type 约束明确 | true | [D1] | 每个属性应有明确类型 |
| additionalProperties | false 或 schema | [D2] | 防止未定义字段混入 |
| format 验证级别 | warn 或 error | [D2] | 根据严格程度选择 |

### 校准数值（体系专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| JSON Schema 最新版本 | 2020-12 | [D1] | 当前推荐版本 |
| OpenAPI Schema 版本 | 3.2.0 | [D4] | API 契约推荐版本 |
| 最大嵌套深度 | 建议 ≤10 层 | [D2] | 过深影响可读性 |

## 边界与分流

### Schema 定义缺失

**前提**：存在有效的 JSON Schema 定义文件。
**不成立时**：使用最小验证（仅检查 JSON 语法），或基于任务约定手动定义验证规则。

### 严格模式失败

**前提**：验证配置为严格模式（strict=true）。
**不成立时**：降级为宽松模式，仅记录警告而不中断流程。

### 格式验证不可用

**前提**：验证库支持 format 关键字。
**不成立时**：跳过格式验证，仅验证结构和类型。

### 版本不兼容

**前提**：Schema 版本与验证库版本兼容。
**不成立时**：使用 polyfill 或降级到旧版 Schema。

## 质量检查

- 所有必填字段是否存在
- 字段类型是否匹配约束
- 任务身份字段是否一致
- 错误信息是否足够诊断

## 回退策略

- **Schema 加载失败**：使用 JSONLint 验证 Schema 语法，修正后重试
- **验证库不支持**：切换到其他验证库（ajv, jsonschema, fast-json-schema）
- **类型不匹配**：检查数据源是否正确序列化
- **格式验证失败**：检查输入数据的编码和格式

## 资源召回建议

当遇到以下场景时召回本卡：
- 自动化报告生成后需要格式验证
- API 响应需要符合预定义契约
- 需要确保报告字段完整性
- 需要标准化错误报告格式

配套资源：
- `cli-fault-diagnosis`：CLI 执行故障诊断

## 补充证据（开源文档）

[D1] JSON Schema: A Media Type for Describing JSON Documents, IETF / JSON Schema Organization, 2020-12, URL: https://json-schema.org/draft/2020-12/json-schema-core.html (accessed 2026-09-16, 权威规范)

[D2] JSON Schema Validation: A Vocabulary for Structural Validation of JSON, IETF / JSON Schema Organization, 2020-12, URL: https://json-schema.org/draft/2020-12/json-schema-validation.html (accessed 2026-09-16, 权威规范)

[D3] JSON Schema Reference (Understanding JSON Schema), JSON Schema Organization, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/ (accessed 2026-09-16, 官方教程)

[D4] OpenAPI Specification - Version 3.2.0, OpenAPI Initiative (Linux Foundation), 3.2.0, URL: https://swagger.io/specification/ (accessed 2026-09-16, 权威规范)

[D5] Learn JSON Schema (2020-12), JSON Schema Organization, 2020-12, URL: https://www.learnjsonschema.com/2020-12/ (accessed 2026-09-16, 官方教程)

## 证据来源

[D1] JSON Schema: A Media Type for Describing JSON Documents, IETF / JSON Schema Organization, 2020-12

[D2] JSON Schema Validation: A Vocabulary for Structural Validation of JSON, IETF / JSON Schema Organization, 2020-12

[D3] JSON Schema Reference (Understanding JSON Schema), JSON Schema Organization, 2020-12

[D4] OpenAPI Specification - Version 3.2.0, OpenAPI Initiative (Linux Foundation), 3.2.0

[D5] Learn JSON Schema (2020-12), JSON Schema Organization, 2020-12

## 批次补充（2026-09-16：JSON Schema详细规范）

### 类型验证（type关键字）

- `type` 关键字指定数据类型，可接受单个字符串或字符串数组 [D3]
- 基本类型：`array`, `boolean`, `null`, `number`, `object`, `string` [D3]
- 当 `type` 为数组时，实例数据匹配任一给定类型即有效 [D3]
- 类型映射：JSON string → Python str, JSON number → Python int/float, JSON object → Python dict, JSON array → Python list [D3]

### 对象验证（object相关关键字）

- `properties`：定义对象属性的验证模式，每个键为属性名，值为验证该属性的模式 [D3]
- `required`：指定必须存在的属性名数组，每个字符串必须唯一 [D3]
- `additionalProperties`：控制未在 `properties` 或 `patternProperties` 中列出的属性处理 [D3]
- `patternProperties`：使用正则表达式映射到模式，匹配属性名的属性值必须通过相应模式验证 [D3]
- `minProperties` / `maxProperties`：限制对象属性数量 [D3]
- `propertyNames`：验证属性名本身，无论其值如何 [D3]

### 数组验证（array相关关键字）

- `items`：定义数组元素的验证模式 [D3]
- `additionalItems`：控制未在 `items` 中定义的元素处理（仅当 `items` 为数组时）[D3]
- `minItems` / `maxItems`：限制数组长度 [D3]
- `uniqueItems`：确保数组元素唯一 [D3]

### 字符串验证（string相关关键字）

- `minLength` / `maxLength`：限制字符串长度 [D3]
- `pattern`：使用正则表达式验证字符串格式 [D3]
- `format`：语义格式验证（如 `date-time`, `email`, `uri`, `uuid` 等）[D3]
- 内置格式：`date-time`, `time`, `date`, `duration`, `email`, `hostname`, `ipv4`, `ipv6`, `uri`, `uuid`, `regex` 等 [D3]

### 模式组合（boolean组合）

- `allOf`（AND）：必须通过所有子模式验证 [D3]
- `anyOf`（OR）：必须通过任一子模式验证 [D3]
- `oneOf`（XOR）：必须通过恰好一个子模式验证 [D3]
- `not`（NOT）：必须不通过给定子模式验证 [D3]
- 组合模式可用于表达复杂约束，但需注意逻辑不可能的模式 [D3]

### 数值验证（number相关关键字）

- `minimum` / `maximum`：包含边界的数值范围 [D3]
- `exclusiveMinimum` / `exclusiveMaximum`：不包含边界的数值范围 [D3]
- `multipleOf`：数值必须是给定值的倍数 [D3]

### 格式验证详细

- `format` 关键字传递语义信息，通常由其他文档描述 [D3]
- 默认情况下 `format` 仅为注解，不影响验证 [D3]
- 验证器实现可配置为将 `format` 作为断言而非注解 [D3]
- 实现可能仅支持内置格式的子集或提供部分验证 [D3]
- 自定义格式可用于交换JSON文档的双方共享信息的场景 [D3]

## 批次补充（2026-09-16：归因分析报告契约案例）

### 实际应用案例

基于归因分析任务（任务ID：396，钙钛矿封装层降解抑制机器学习筛选）的报告契约案例：

#### 报告契约定义案例
- **任务身份字段**：task_id（必须与任务索引一致）、task（必须与任务name一致）、summary（必须是非空字符串）、issues（必须是数组）
- **额外字段限制**：不允许包含未定义的顶层字段（如error, sessionID, timestamp, type）
- **验证失败案例**：实际响应包含额外字段 ['error', 'sessionID', 'timestamp', 'type']，且缺少必填字段

#### 验证流程案例
- **预检步骤**：在输出前按契约校验报告，使用report-schema.json校验最终输出
- **反例测试**：执行错配字段反例测试，确保契约一致性
- **错误报告**：校验错误必须包含字段路径和具体违规描述，不得仅返回"validation failed"

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 必填字段数量 | 4 | 任务396案例 | task_id, task, summary, issues |
| 禁止额外字段数量 | 4 | 任务396案例 | error, sessionID, timestamp, type |
| 任务身份验证点 | 2 | 任务396案例 | task_id与索引一致，task与name一致 |
| 数组类型约束 | 1 | 任务396案例 | issues必须是数组类型 |

## 批次补充（2026-09-16：任务283归因分析报告契约案例）

### 实际应用案例

基于归因分析任务（任务ID：283，气象预报驱动的小时至十日河流流量与洪峰预报）的报告契约案例：

#### 验证失败症状
- **退出码**：1（非零退出）
- **校验错误**：缺少顶层字段 ['issues', 'summary', 'task', 'task_id']
- **额外字段**：包含 ['error', 'sessionID', 'timestamp', 'type']
- **身份不一致**：task_id 与任务索引不一致、task 与任务 name 不一致

#### 故障根因分析
- CLI 进程未正常完成生命周期，导致输出结构不符合 Schema 定义
- 输出格式为错误响应而非预期的归因报告格式
- 任务身份字段缺失或不匹配，无法关联到正确的任务索引

#### 修复验证要点
- 输出前按契约校验报告，确保必填字段完整
- 使用 report-schema.json 校验最终输出并执行错配字段反例测试
- 验证 task_id 与任务索引一致、task 与任务 name 一致

## 批次补充（2026-09-17：基于论文证据的Schema执行与结构化输出稳定性）

### 论文证据补充

从最新检索的论文中抽取以下知识，丰富JSON Schema报告交付契约体系：

**[1] Schema Enforcement and Structured-Output Stability in Locally Deployed LLMs for Clinical Admission-Note Editing (PMID: 42512666)**

| 概念 | 描述 | 来源 | 说明 |
|------|------|------|------|
| 模式执行 | 强制LLM输出符合预定义Schema的结构化数据 | [1] | 所有模型在模式执行下产生70/70首次通过有效的输出 |
| 结构化输出稳定性 | 评估LLM输出的JSON/schema有效性、运行间稳定性 | [1] | 自动化代理指标评估JSON/schema有效性、运行间稳定性、指令遵循、冗长度 |
| 代理指标 | 使用代理指标评估输出质量 | [1] | 评估JSON/schema有效性、运行间稳定性、指令遵循、冗长度、数字令牌保留、不确定性标记变化 |
| 模型特定行为 | 不同模型在文档行为上存在差异 | [1] | 包括冗长度和数字令牌保留的差异 |

### 补充边界与分流

- **Schema执行验证**：当使用LLM生成结构化输出时，应实施Schema执行，确保输出符合预定义Schema[1]
- **运行间稳定性评估**：评估LLM输出的运行间稳定性，使用代理指标评估JSON/schema有效性、运行间稳定性、指令遵循等[1]
- **模型特定行为处理**：注意不同模型在文档行为上的差异，包括冗长度和数字令牌保留的差异[1]
- **代理指标使用**：使用代理指标评估输出质量，包括JSON/schema有效性、运行间稳定性、指令遵循、冗长度、数字令牌保留、不确定性标记变化[1]

### 补充质量检查

- 验证Schema执行是否强制LLM输出符合预定义Schema
- 检查结构化输出的运行间稳定性，使用代理指标评估JSON/schema有效性
- 确保不同模型在文档行为上的差异得到适当处理
- 验证代理指标是否包括JSON/schema有效性、运行间稳定性、指令遵循、冗长度、数字令牌保留、不确定性标记变化

### 补充回退策略

- **Schema执行失败**：当Schema执行失败时，应检查Schema定义是否正确，或使用更简单的Schema
- **运行间稳定性差**：当运行间稳定性差时，应调整模型参数或使用更稳定的模型
- **模型特定行为问题**：当模型特定行为导致问题时，应针对特定模型进行调整或使用替代模型
- **代理指标不可用**：当代理指标不可用时，应使用手动验证方法评估输出质量

## 批次补充（2026-09-17：任务81归因分析报告契约案例）

### 实际应用案例

基于归因分析任务（任务ID：81，细胞类型特异调控DNA条件生成）的报告契约案例：

#### 验证失败症状
- **退出码**：1（非零退出）
- **校验错误**：缺少顶层字段 ['issues', 'summary', 'task', 'task_id']
- **额外字段**：包含 ['error', 'sessionID', 'timestamp', 'type']
- **身份不一致**：task_id 与任务索引不一致、task 与任务 name 不一致
- **字段约束违反**：summary 必须是非空字符串；issues 必须是数组

#### 故障根因分析
- 归因分析智能体退出码为1，未正常完成生命周期
- 报告校验错误表明输出结构不符合预定Schema定义
- 缺少核心必填字段导致无法关联到正确的任务身份
- 包含额外字段说明输出格式为错误响应而非预期的归因报告格式

#### 修复验证要点
- 输出前按契约校验报告，确保必填字段（task_id, task, summary, issues）完整
- 使用 report-schema.json 校验最终输出并执行错配字段反例测试
- 验证 task_id 与任务索引一致、task 与任务 name 一致
- 确保 summary 为非空字符串、issues 为数组类型
- 移除未定义的额外字段（error, sessionID, timestamp, type）

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 必填字段数量 | 4 | 任务81案例 | task_id, task, summary, issues |
| 禁止额外字段数量 | 4 | 任务81案例 | error, sessionID, timestamp, type |
| 任务身份验证点 | 2 | 任务81案例 | task_id与索引一致，task与name一致 |
| 字段类型约束 | 2 | 任务81案例 | summary为非空字符串，issues为数组 |

## 批次补充（2026-09-17：任务291归因分析报告契约案例）

### 实际应用案例

基于归因分析任务（任务ID：291，渤黄海海浪智能订正模型）的报告契约案例：

#### 验证失败症状
- **退出码**：1（非零退出）
- **校验错误**：缺少顶层字段 ['issues', 'summary', 'task', 'task_id']
- **额外字段**：包含 ['error', 'sessionID', 'timestamp', 'type']
- **身份不一致**：task_id 与任务索引不一致、task 与任务 name 不一致
- **字段约束违反**：summary 必须是非空字符串；issues 必须是数组

#### 故障根因分析
- 归因分析智能体退出码为1，未正常完成生命周期
- 报告校验错误表明输出结构不符合预定Schema定义
- 缺少核心必填字段导致无法关联到正确的任务身份
- 包含额外字段说明输出格式为错误响应而非预期的归因报告格式

#### 修复验证要点
- 输出前按契约校验报告，确保必填字段（task_id, task, summary, issues）完整
- 使用 report-schema.json 校验最终输出并执行错配字段反例测试
- 验证 task_id 与任务索引一致、task 与任务 name 一致
- 确保 summary 为非空字符串、issues 为数组类型
- 移除未定义的额外字段（error, sessionID, timestamp, type）

#### 与前次失败案例的对比
- Task 29、Task 49、Task 81同样出现退出码1和结构化输出契约失败
- Task 291的特征与Task 81相似：缺少必需字段、包含额外字段、任务身份不一致
- 共同根因：CLI执行成功但输出格式不符合Schema校验要求

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 必填字段数量 | 4 | 任务291案例 | task_id, task, summary, issues |
| 禁止额外字段数量 | 4 | 任务291案例 | error, sessionID, timestamp, type |
| 任务身份验证点 | 2 | 任务291案例 | task_id与索引一致，task与name一致 |
| 字段类型约束 | 2 | 任务291案例 | summary为非空字符串，issues为数组 |

## 批次补充（2026-09-17：任务292归因分析报告契约案例）

### 实际应用案例

基于归因分析任务（任务ID：292，渤黄海海浪智能预报模型）的报告契约案例：

#### 验证失败症状
- **退出码**：1（非零退出）
- **校验错误**：缺少顶层字段 ['issues', 'summary', 'task', 'task_id']
- **额外字段**：包含 ['error', 'sessionID', 'timestamp', 'type']
- **身份不一致**：task_id 与任务索引不一致、task 与任务 name 不一致
- **字段约束违反**：summary 必须是非空字符串；issues 必须是数组

#### 故障根因分析
- 归因分析智能体退出码为1，未正常完成生命周期
- 报告校验错误表明输出结构不符合预定Schema定义
- 缺少核心必填字段导致无法关联到正确的任务身份
- 包含额外字段说明输出格式为错误响应而非预期的归因报告格式

#### 修复验证要点
- 输出前按契约校验报告，确保必填字段（task_id, task, summary, issues）完整
- 使用 report-schema.json 校验最终输出并执行错配字段反例测试
- 验证 task_id 与任务索引一致、task 与任务 name 一致
- 确保 summary 为非空字符串、issues 为数组类型
- 移除未定义的额外字段（error, sessionID, timestamp, type）

#### 与前次失败案例的对比
- Task 29、Task 49、Task 81、Task 291同样出现退出码1和结构化输出契约失败
- Task 292的特征与Task 291相似：缺少必需字段、包含额外字段、任务身份不一致
- 共同根因：CLI执行成功但输出格式不符合Schema校验要求

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 必填字段数量 | 4 | 任务292案例 | task_id, task, summary, issues |
| 禁止额外字段数量 | 4 | 任务292案例 | error, sessionID, timestamp, type |
| 任务身份验证点 | 2 | 任务292案例 | task_id与索引一致，task与name一致 |
| 字段类型约束 | 2 | 任务292案例 | summary为非空字符串，issues为数组 |