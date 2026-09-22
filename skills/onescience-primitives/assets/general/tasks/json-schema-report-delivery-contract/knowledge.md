# JSON Schema报告交付契约

## 适用范围
适用于所有需要输出结构化报告（如归因报告、分析报告、测试报告）的系统。本卡片提供JSON Schema交付契约的定义、校验与错误处理方法，确保报告输出可解析、一致且符合预期格式。

## 输入
- 报告内容（JSON格式）
- 预期Schema定义（JSON Schema）
- 校验规则（必填字段、数据类型、格式约束）

## 输出
- 校验通过的报告（符合Schema）
- 校验错误信息（包含字段路径、错误类型、错误描述）
- 校验结果（通过/失败）

## 流程节点
1. **Schema定义** → 定义报告的JSON Schema，包括必填字段、数据类型、格式约束、嵌套结构等。[D1]
2. **Schema校验** → 使用JSON Schema校验库（如jsonschema、ajv）对报告进行校验。[D1]
3. **错误处理** → 捕获校验错误，生成结构化的错误信息，包含字段路径、错误类型、错误描述。[D1]
4. **错误报告** → 将错误信息输出到标准错误流或日志，便于调试。[D1]
5. **重试与恢复** → 根据错误类型决定是否重试或降级处理。[D1]

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 必填字段 | 由Schema定义 | [D1] | 报告必须包含的字段 |
| 数据类型 | string, number, integer, boolean, array, object, null | [D1] | 字段的数据类型约束 |
| 格式约束 | date-time, email, uri, ipv4, ipv6等 | [D1] | 字段的格式约束 |
| 嵌套结构 | 通过$ref引用其他Schema | [D1] | 支持复杂嵌套结构 |
| 错误输出格式 | 结构化JSON | [D1] | 包含field, message, schemaPath等 |

## 边界与分流
- **Schema不存在**：当Schema文件缺失或无法解析时，跳过校验并记录警告。[D1]
- **Schema版本不兼容**：当Schema版本与校验库不兼容时，降级到基础校验或跳过校验。[D1]
- **性能限制**：当报告体积过大时，采用流式校验或分块校验。[D1]
- **自定义校验器**：对于复杂业务逻辑，扩展JSON Schema校验器或使用自定义验证函数。[D1]

## 质量检查
- 验证所有必填字段都存在
- 验证字段数据类型正确
- 验证格式约束（如日期格式、邮箱格式）
- 验证嵌套结构符合Schema定义
- 验证错误信息包含足够的诊断信息

## 回退策略
- 如果Schema校验失败，尝试使用默认值填充缺失字段
- 如果Schema版本不兼容，使用最宽松的校验模式
- 记录详细的校验日志以便事后分析

## 资源召回建议
- 当需要定义报告输出格式时召回本卡片
- 当需要校验报告输出是否符合预期时召回本卡片
- 当需要诊断报告格式错误时召回本卡片

## 补充证据（开源文档）
[D1] JSON Schema Specification, JSON Schema Organization, Draft 2020-12, URL: https://json-schema.org/specification.html（accessed_at 2026-09-21，权威官方文档）
[D2] Validation of Modern JSON Schema: Formalization and Complexity, ACM, 2024, DOI: 10.1145/3632891（accessed_at 2026-09-21，学术论文；原记 10.1145/3649506 为 DOI 错配，经 Crossref 核验修正）

## 批次补充（batch-214）

### 新增论文证据

[3] Attouche L, Baazizi M-A, Colazzo D, et al. "Validation of Modern JSON Schema: Formalization and Complexity", Proceedings of the ACM on Programming Languages, 2024, DOI: 10.1145/3632891 (cited=17, JSON Schema 验证的形式化与复杂度分析，揭示动态引用和注解依赖验证等新特性的评估模型变化)

[4] Siffa I C, Schäfer J, Becker M M. "Adamant: a JSON schema-based metadata editor for research data management workflows", F1000Research, 2022, DOI: 10.12688/f1000research.110875.2 (cited=15, 全文, JSON Schema 在科研数据管理中的应用，展示 Schema 到 Web 表单的自动渲染和 Ajv 库的校验实践)

### 补充知识要点

- JSON Schema Draft 2019-09+ 引入 dynamicRef 和 annotation-dependent validation，改变评估模型 [3]
- Ajv 库（v8.8.2）可用于前端 JSON 表单数据校验，识别数据与 Schema 间的差异 [4]
- JSON Schema 可自动渲染为 Web 表单，支持用户友好界面的元数据收集 [4]

## 证据来源
[1] Schema validation and evaluation framework for extracted schemas in JSON databases, Scientific Reports, 2026, DOI: 10.1038/s41598-026-45554-6（摘要级证据；原记 10.1038/s41598-026-00000-0 为占位 DOI，经 Crossref 核验修正）
[2] Improving Api Test Accuracy through Schema Validation and Real-time Json Assertions, International Journal on Science and Technology, 2025（摘要级证据）
[3] Validation of Modern JSON Schema: Formalization and Complexity, Proceedings of the ACM on Programming Languages, 2024, DOI: 10.1145/3632891（摘要级证据）
[4] Blaze: Compiling JSON Schema for 10x Faster Validation, Juan Cruz Viotti et al., Proceedings of the VLDB Endowment, 2025, DOI: 10.14778/3773749.3773764
[5] Adamant: a JSON schema-based metadata editor for research data management workflows, F1000Research, 2022, DOI: 10.12688/f1000research.110875.2