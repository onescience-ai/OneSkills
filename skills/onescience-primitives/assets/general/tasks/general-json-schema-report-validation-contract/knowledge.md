# JSON Schema 报告交付契约校验

## 适用范围

**触发条件**：
- 需要确保结构化报告（JSON 格式）符合预定义的 Schema 契约
- 需要在报告输出前校验必填字段、数据类型和格式合规性
- 需要在自动化流水线中集成 Schema 校验步骤

**适用场景**：
- 科研任务的归因报告、执行结果报告的格式校验
- API 响应的结构化验证（RESTful API、GraphQL）
- 元数据质量保证（研究数据管理、数据集描述）
- CI/CD 流水线中的数据格式回归检测

**不适用场景**：
- 非 JSON 格式的报告（XML、YAML、CSV）
- 需要语义级校验的场景（如业务逻辑校验）
- 需要实时流式校验的场景（大数据流）

## 输入

- **report_json**：待校验的 JSON 报告内容（字符串或字典对象）
- **schema_json**：JSON Schema 定义（字符串或字典对象）
- **校验选项**：是否启用严格模式、是否返回完整错误信息

## 输出

- **valid**：校验是否通过（布尔值）
- **errors**：校验错误列表（每项含 path、message、params）
- **warnings**：警告信息列表（可选字段缺失但非必需时）

## 流程节点

### Step 1：Schema 加载与编译
- **操作**：解析 JSON Schema 字符串为对象，编译为验证器
- **参数**：schema_version="2020-12", strict_mode=true
- **工具**：Ajv（JavaScript）、jsonschema（Python）、jsonschema-rs（Rust）
- **质量门禁**：Schema 本身符合 JSON Schema 规范（meta-schema 校验）

### Step 2：报告预处理
- **操作**：确保报告为有效 JSON，处理编码问题
- **参数**：encoding='utf-8', ensure_ascii=false
- **工具**：json.loads(), json.dumps()
- **质量门禁**：报告可被解析为字典对象

### Step 3：Schema 校验
- **操作**：使用编译后的验证器校验报告
- **参数**：all_errors=true, remove_additional=false
- **工具**：Ajv.validate(), jsonschema.validate()
- **质量门禁**：返回 valid 标志和 errors 列表

### Step 4：错误信息解析
- **操作**：将校验错误转换为可读格式，定位到具体字段路径
- **参数**：error_format="detailed"
- **工具**：Ajv.errorsText(), 自定义错误格式化
- **质量门禁**：每个错误包含 path 和 message

### Step 5：校验结果输出
- **操作**：返回结构化的校验结果
- **参数**：include_warnings=true
- **工具**：自定义结果对象
- **质量门禁**：结果对象包含 valid、errors、warnings 字段

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Schema 版本 | Draft 2020-12 或 Draft 2019-09 | [D1] | 最新稳定版本，支持动态引用和注解依赖校验 |
| 必填字段校验 | required 关键字 | [1][D1] | 字段缺失时返回 "required" 错误 |
| 类型校验 | type 关键字 | [1][D1] | 类型不匹配时返回 "type" 错误 |
| 数组约束 | minItems/maxItems/items | [1][D1] | 数组长度和元素类型约束 |
| 字符串格式 | format 关键字 | [1][D1] | 预定义格式（date-time, email, uri 等） |
| 嵌套对象校验 | properties/additionalProperties | [1][D1] | 对象属性的递归校验 |
| 严格模式 | strictMode=true | [D2] | 禁止未声明的额外属性 |
| 错误聚合 | allErrors=true | [D2] | 返回所有错误而非首个错误 |

### 校准数值（通用示例，非特定体系）

> 以下为 JSON Schema 校验的通用配置值，供其他体系参考；具体 Schema 定义需根据实际报告结构调整。

| 配置项 | 推荐值 | 说明 |
|--------|--------|------|
| Schema draft | 2020-12 | 支持最新的 keywords 和校验特性 |
| 校验库选择 | Ajv (JS) / jsonschema (Python) | 主流实现，社区活跃 |
| 错误输出格式 | detailed | 包含 path、message、params |
| 额外属性处理 | additionalProperties: false | 严格模式下禁止未声明字段 |
| 空值处理 | allowEmptyValues: true | 视业务需求决定 |

## 边界与分流

- **Schema 本身不合法**：先校验 Schema 是否符合 meta-schema，修正后再校验报告
- **报告非 JSON 格式**：捕获 JSON 解析异常，返回 "invalid_json" 错误
- **Schema 版本不兼容**：检测 Schema 的 $schema 字段，降级到兼容模式或报错
- **循环引用**：检测 Schema 中的 $ref 循环，抛出明确错误
- **性能问题**：对于大型报告（>10MB），使用流式校验或分块校验

## 质量检查

| 检查点 | 阈值 | 失败处理 |
|--------|------|----------|
| Schema 合法性 | 通过 meta-schema 校验 | 修正 Schema 后重试 |
| 报告可解析 | json.loads() 成功 | 返回 "parse_error" |
| 必填字段完整 | required 字段全部存在 | 返回缺失字段列表 |
| 类型匹配 | 所有字段类型正确 | 返回类型错误详情 |
| 数组约束满足 | minItems ≤ length ≤ maxItems | 返回数组长度错误 |
| 格式合规 | format 关键字校验通过 | 返回格式错误详情 |

## 回退策略

- **Schema 校验库不可用时**：使用手动字段检查（仅检查必填字段存在性）
- **严格模式失败时**：降级到宽松模式（允许额外属性）
- **校验库版本不兼容时**：使用旧版 API 或手动实现基础校验
- **大型 Schema 加载缓慢时**：使用 Schema 缓存或预编译

## 资源召回建议

- 当任务涉及结构化报告输出时召回本卡片
- 配套资源：general-cli-noninteractive-execution-fault-classification（确保 CLI 输出可被校验）
- 与 onescience-primitives 的 metadata.json 校验逻辑配合使用

## 补充证据

[D1] "JSON Schema Official Specification", json-schema.org, Draft 2020-12, URL: https://json-schema.org/draft/2020-12/json-schema-core（accessed 2026-09-21，官方规范文档，权威来源）

[D2] "Ajv: Another JSON Schema Validator Documentation", Evgeny Poberezkin, v8.x, URL: https://ajv.js.org/（accessed 2026-09-21，主流验证库官方文档，权威来源）

## 证据来源

[1] L. Attouche, M.-A. Baazizi, D. Colazzo et al., "Validation of Modern JSON Schema: Formalization and Complexity", Proceedings of the ACM on Programming Languages, 2024, DOI: 10.1145/3632891

[2] S. Belefqih, M. Barchane, A. Zellou et al., "Schema validation and evaluation framework for extracted schemas in JSON databases", Scientific Reports, 2026, DOI: 10.1038/s41598-026-45554-6

[3] U. Verma, "Improving Api Test Accuracy through Schema Validation and Real-time Json Assertions in Jenkins Pipelines", International Journal on Science and Technology, 2025, DOI: 10.71097/ijsat.v16.i3.10656

[4] I. C. Siffa, J. Schäfer, M. M. Becker, "Adamant: a JSON schema-based metadata editor for research data management workflows", F1000Research, 2022, DOI: 10.12688/f1000research.110875.2
