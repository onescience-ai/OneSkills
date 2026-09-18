# 面向结构化报告的 JSON Schema 交付契约校验

## 适用范围

面向需要以 JSON 格式交付结构化报告的自动化工作流：报告生成器在输出前必须通过 JSON Schema 校验，确保必填字段存在、类型正确、任务身份与调用方一致、数组约束满足。适用于归因报告、分析报告、测试报告、审计报告等任何结构化 JSON 产物的契约校验。不适用于非 JSON 格式的报告（YAML、XML、纯文本），也不适用于运行时数据校验（如 API 请求参数校验）。

## 输入

- 待校验的 JSON 实例（报告内容，dict 或 JSON 字符串）
- JSON Schema 定义（描述报告的必填字段、类型、结构约束）
- 可选：任务身份信息（task_id、task name），用于一致性交叉校验

## 输出

- 校验结果：通过 / 失败
- 错误详情列表（每个错误含：字段路径、错误消息、期望值/类型、实际值）
- 修复建议（按错误类型生成）

## 流程节点

### 1. Schema 加载与元校验

操作：加载 JSON Schema 定义文件，先校验 Schema 本身是否合法（避免用无效 Schema 校验导致误判）。  
参数：Schema 可以是 dict 或 JSON 文件路径。  
工具：`jsonschema.validators.Draft202012Validator.check_schema(schema)` 或 `jsonschema.validate()` 内置的 Schema 自校验。  
质量门禁：Schema 必须通过 meta-schema 校验；推荐在 Schema 中声明 `$schema` 字段指定 draft 版本。  
证据来源 [D1][D3]

### 2. 必填字段校验

操作：检查 JSON 实例中所有 `required` 字段是否存在且非 null。  
参数：Schema 中 `required` 数组定义的字段名列表。  
工具：`jsonschema.validate(instance, schema)` — 缺少 required 字段时抛出 `ValidationError`。  
质量门禁：`required` 数组必须列出所有业务上不可或缺的字段；字段缺失是最常见的契约违反。  
证据来源 [D1][D3]

### 3. 类型与结构校验

操作：逐字段校验类型（string/number/boolean/array/object/null）、嵌套结构、数组元素类型、枚举值范围。  
参数：Schema 中各属性的 `type`、`properties`、`items`、`enum` 等关键字。  
工具：`jsonschema.validate()` 自动递归校验。  
质量门禁：数组字段必须同时约束 `minItems`/`maxItems`；对象字段必须约束 `additionalProperties` 防止意外字段。  
证据来源 [D1][D3]

### 4. 任务身份一致性校验

操作：比对报告中的 task_id、task name 与调用方提供的值是否一致。  
参数：报告 JSON 中的顶层 `task_id` 和 `task` 字段。  
工具：自定义校验逻辑（在 Schema 校验之后执行）。  
质量门禁：task_id 必须为字符串或整数且与任务索引匹配；task 必须为非空字符串且与任务名称一致。此项为业务语义校验，超出 JSON Schema 能力范围，需额外代码实现。  
证据来源：归因报告 task 299 的实际校验错误

### 5. 错误诊断与分类

操作：捕获 `ValidationError` 并提取结构化诊断信息。  
关键属性：

| 属性 | 含义 | 用途 |
|------|------|------|
| `message` | 人类可读错误描述 | 直接用于日志和修复建议 |
| `validator` | 失败的关键字名称（如 required、type、minItems） | 分类错误类型 |
| `path` | 实例中出错元素的路径 | 定位具体字段 |
| `schema_path` | Schema 中出错规则的路径 | 追溯 Schema 约束 |
| `instance` | 出错的实际值 | 对比期望值 |
| `context` | 子 Schema 的错误列表（anyOf/oneOf 场景） | 深层诊断 |

工具：`jsonschema.exceptions.ValidationError`。  
质量门禁：使用 `best_match()` 从多个错误中选出最相关的根因错误。  
证据来源 [D1][D2]

### 6. 错误收集与批量报告

操作：使用 `iter_errors()` 收集全部错误而非首个即停。  
参数：`v.iter_errors(instance)` 返回惰性迭代器。  
工具：`jsonschema.exceptions.ErrorTree` 可将错误组织为树状结构，便于按字段查询。  
质量门禁：批量校验时必须收集全部错误，首个错误修复后可能暴露更多问题。  
证据来源 [D1][D2]

### 7. 输出前校验拦截

操作：在报告写入文件或返回给调用方之前，执行完整 Schema 校验；校验失败则阻止输出并返回诊断。  
参数：校验函数、Schema、待输出实例。  
工具：上述流程组合。  
质量门禁：校验失败时必须返回足够详细的诊断信息（字段路径 + 错误消息 + 期望值），不可仅返回"校验失败"。

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Schema 声明 | 必须包含 `$schema` | [D1][D3] | 指定 draft 版本，避免默认版本不一致 |
| required 字段 | 按业务需求定义 | [D3] | 列出所有不可或缺的顶层和嵌套字段 |
| type 约束 | 每个属性必须声明 type | [D3] | 防止类型混淆（如 string 传入 number） |
| additionalProperties | 推荐显式设置 | [D3] | 防止意外字段静默通过校验 |
| 错误收集 | iter_errors() 全量收集 | [D2] | 不可仅用 validate() 首错即停 |

### 校准数值

以下数值来自 jsonschema 4.26.0 实践，供量级校准；其他版本需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认 draft | Draft 2020-12 | [D1] | 未声明 $schema 时的默认版本 |
| format 校验 | 默认不启用 | [D1] | 需显式传入 FormatChecker 才启用 |
| best_match() | 启发式算法 | [D2] | 返回值可能随版本更新变化 |

## 边界与分流

- **Schema 本身不合法**：`check_schema()` 抛出 `SchemaError`。改道：先修复 Schema 定义，再执行实例校验。
- **JSON 解析失败**：输入不是合法 JSON。改道：捕获 `json.JSONDecodeError`，在 Schema 校验前增加 JSON 解析步骤。
- **跨 draft 版本兼容**：不同 draft 版本的关键字支持不同（如 Draft 4 不支持 `if/then/else`）。改道：在 Schema 中显式声明 `$schema`，并使用对应版本的 Validator 类。
- **任务身份字段超出 Schema 能力**：task_id 与外部索引的比对是业务逻辑，非 Schema 校验范畴。改道：Schema 校验通过后，额外执行业务语义校验。
- **性能敏感场景**：Schema 校验有开销。改道：对批量报告使用 `Draft202012Validator` 直接实例化（跳过 `validate()` 的 Schema 自校验），前提是已确认 Schema 合法。

## 质量检查

- [ ] Schema 包含 `$schema` 声明
- [ ] 所有必填字段在 `required` 中列出
- [ ] 每个属性有 `type` 约束
- [ ] 校验捕获全部错误（使用 `iter_errors()`）
- [ ] 错误诊断包含字段路径和期望/实际值
- [ ] 任务身份一致性在 Schema 校验后额外检查
- [ ] 校验失败阻止报告输出

## 回退策略

- jsonschema 库不可用时：回退到手动字段检查（逐字段 if/else），功能受限但可工作
- Schema 过于复杂导致校验慢时：回退到关键字段子集校验（仅 required + type）
- 需要校验 JSON 字符串而非 dict 时：先 `json.loads()` 解析再校验

## 资源召回建议

当任务涉及以下场景时应召回本卡片：
- 自动化工作流需要对 JSON 输出执行结构化校验
- 报告生成器需要在输出前验证契约合规性
- 需要诊断 JSON 报告中哪些字段不符合预期格式
- 任务身份一致性检查（task_id / task name 比对）
- 批量报告的批量校验与错误汇总

配套卡片：`general-cli-noninteractive-fault-classification`（当报告由 CLI 工具生成时，配合进程退出码诊断）

## 补充证据（开源权威文档）

[D1] jsonschema — Schema Validation, jsonschema community / Julian Berman, jsonschema 4.26.0 documentation, URL: https://python-jsonschema.readthedocs.io/en/stable/validate/（accessed 2026-09-17，Python JSON Schema 实现官方文档）

[D2] jsonschema — Handling Validation Errors, jsonschema community / Julian Berman, jsonschema 4.26.0 documentation, URL: https://python-jsonschema.readthedocs.io/en/stable/errors/（accessed 2026-09-17，错误处理官方文档）

[D3] JSON Schema reference — Understanding JSON Schema, JSON Schema Org, 2020-12 draft, URL: https://json-schema.org/understanding-json-schema/（accessed 2026-09-17，JSON Schema 规范官方参考）

## 证据来源

[1] jsonschema 4.26.0 文档 — Schema Validation, Julian Berman, 2026, URL: https://python-jsonschema.readthedocs.io/en/stable/validate/
[2] jsonschema 4.26.0 文档 — Handling Validation Errors, Julian Berman, 2026, URL: https://python-jsonschema.readthedocs.io/en/stable/errors/
[3] JSON Schema 2020-12 规范参考, JSON Schema Org, 2026, URL: https://json-schema.org/understanding-json-schema/
