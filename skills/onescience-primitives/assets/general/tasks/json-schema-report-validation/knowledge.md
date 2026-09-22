# JSON Schema 报告交付契约验证

## 适用范围
适用于任何需要确保 JSON 数据符合预定义结构的场景，包括科研数据管理、API 测试、数据集成、配置验证和报告生成。涵盖 JSON Schema 设计、验证执行、错误诊断和合规性检查。

## 输入
- JSON Schema 定义文件
- 待验证的 JSON 文档
- 验证配置（严格模式、忽略额外属性等）

## 输出
- 验证结果（通过/失败）
- 错误详情（路径、消息、严重级别）
- 合规性报告

## 流程节点
1. **Schema 加载与解析**：加载 JSON Schema 并解析为内部表示。
2. **文档加载与预处理**：加载待验证的 JSON 文档，进行必要的预处理。
3. **验证执行**：根据 Schema 规则验证文档结构、类型、约束。
4. **错误收集与分类**：收集所有验证错误，按严重级别分类。
5. **报告生成**：生成结构化验证报告，包含错误详情和建议。

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Schema 版本 | Draft 2020-12 | 标准 | 最新 JSON Schema 标准 |
| 验证模式 | strict/lax | 用户定义 | 严格模式禁止额外属性 |
| 错误限制 | 可配置 | 用户定义 | 最大报告错误数 |
| 性能优化 | 编译 Schema | 可选 | 提高重复验证性能 |

## 边界与分流
- **Schema 无效**：Schema 本身不符合 JSON Schema 规范 → 终止并报告 Schema 错误。
- **文档格式错误**：JSON 语法错误 → 报告解析错误。
- **验证超时**：大型文档验证超时 → 分块验证或增加超时时间。
- **循环引用**：Schema 中存在循环引用 → 检测并报告。

## 质量检查
- 验证结果准确，无漏报/误报。
- 错误消息清晰，包含具体路径和建议。
- 性能可接受（大型文档验证时间）。
- 支持主流 JSON Schema 版本。

## 回退策略
- Schema 降级：使用兼容的旧版本 Schema。
- 部分验证：只验证关键字段。
- 异步验证：对大型文档采用流式验证。

## 资源召回建议
当用户遇到以下情况时召回本卡片：
- 需要设计 JSON Schema 数据契约
- 需要验证 JSON 文档是否符合 Schema
- 需要诊断 JSON 验证错误
- 需要确保 API 报告符合预定义格式

## 补充证据（开源文档/用户自有，可选）
[D1] Validation of Modern JSON Schema: Formalization and Complexity, ACM on Programming Languages, 2024, DOI: 10.1145/3632891（论文证据，提供 JSON Schema 验证复杂性分析）
[D2] Blaze: Compiling JSON Schema for 10x Faster Validation, Proceedings of the VLDB Endowment, 2025, DOI: 10.14778/3773749.3773764（论文证据，提供高性能验证方法）
[D3] Schema validation and evaluation framework for extracted schemas in JSON databases, Scientific Reports, 2026, DOI: 10.1038/s41598-026-45554-6（论文证据，提供 Schema 评估框架）

## 证据来源
[1] Validation of Modern JSON Schema: Formalization and Complexity, Attouche et al., ACM on Programming Languages, 2024, DOI: 10.1145/3632891
[2] Blaze: Compiling JSON Schema for 10x Faster Validation, Viotti & Mior, Proceedings of the VLDB Endowment, 2025, DOI: 10.14778/3773749.3773764
[3] Schema validation and evaluation framework for extracted schemas in JSON databases, Belefqih et al., Scientific Reports, 2026, DOI: 10.1038/s41598-026-45554-6