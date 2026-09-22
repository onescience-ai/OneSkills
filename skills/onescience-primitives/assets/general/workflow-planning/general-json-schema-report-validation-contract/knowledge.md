# 面向 JSON 报告交付的 Schema 验证契约

## 适用范围
本卡片为需要验证 JSON 报告结构的应用提供基于 JSON Schema 的交付契约规范。适用于任何生成 JSON 格式报告的系统，包括但不限于科研数据报告、API 响应、日志记录、配置输出等。目标是确保报告字段完整、类型正确且符合预定义结构，从而提高数据交换的可靠性和可预测性。

## 输入
- **报告内容**：待验证的 JSON 格式报告数据。
- **Schema 定义**：符合 JSON Schema 规范（如 Draft-07、Draft 2019-09、Draft 2020-12）的 Schema 文件。
- **验证上下文**（可选）：包括验证模式（严格/宽松）、错误处理策略、性能要求。

## 输出
- **验证结果**：通过/失败状态，包含详细的错误信息。
- **验证报告**（可选）：结构化的验证报告，包括错误位置、错误类型、修正建议。
- **性能指标**（可选）：验证耗时、内存使用等。

## 流程节点
1. **Schema 加载与解析**：加载 JSON Schema 文件，解析为内部表示。
   - 操作：使用 JSON Schema 验证库（如 ajv、jsonschema）解析 Schema。
   - 参数：Schema 版本、验证选项。
   - 工具：JSON Schema 验证库。
   - 质量门禁：Schema 解析成功，无语法错误。
2. **报告数据准备**：加载待验证的 JSON 报告数据。
   - 操作：解析 JSON 字符串或文件。
   - 参数：编码格式、数据来源。
   - 工具：JSON 解析库。
   - 质量门禁：JSON 解析成功，无语法错误。
3. **执行验证**：使用 Schema 验证报告数据。
   - 操作：调用验证库的验证方法。
   - 参数：验证模式（strict/loose）、错误收集策略。
   - 工具：JSON Schema 验证库。
   - 质量门禁：验证过程无异常，返回验证结果。
4. **错误处理与报告生成**：处理验证错误，生成用户友好的错误报告。
   - 操作：格式化错误信息，提供修正建议。
   - 参数：错误报告格式、详细程度。
   - 工具：自定义错误处理逻辑。
   - 质量门禁：错误报告准确、清晰、可操作。

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Schema 版本 | Draft-07, Draft 2019-09, Draft 2020-12 | [1] | 根据应用需求选择合适的 Schema 版本。 |
| 验证模式 | strict, loose | [1] | strict 模式拒绝未知字段，loose 模式忽略未知字段。 |
| 错误收集策略 | all, first | [1] | all 收集所有错误，first 遇到第一个错误即停止。 |
| 性能要求 | 根据报告大小和验证复杂度调整 | [2] | 大型报告可能需要流式验证或编译优化。 |

### 校准数值
以下数值来自特定应用系统，供量级校准；其他系统需以自身证据重新锚定。
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 典型验证耗时（小型报告 <1KB） | <10ms | [2] | 在标准硬件上使用优化验证器。 |
| 典型验证耗时（中型报告 1-100KB） | <100ms | [2] | 取决于 Schema 复杂度和验证器实现。 |
| 内存使用（中型报告） | <50MB | [2] | 取决于验证器实现和报告结构。 |

## 边界与分流
- **Schema 版本不兼容**：如果报告使用旧版 Schema，而验证器仅支持新版，则需要进行 Schema 转换或降级验证器。
- **性能瓶颈**：对于超大报告（>1MB），考虑流式验证或分块验证。
- **动态 Schema**：如果 Schema 在运行时动态生成，需要确保 Schema 本身符合元 Schema。
- **自定义验证逻辑**：如果报告需要业务逻辑验证（如字段间约束），扩展标准 Schema 验证。

## 质量检查
- **Schema 验证**：Schema 文件本身必须符合 JSON Schema 元 Schema。
- **报告验证**：报告数据必须符合 Schema 定义的所有约束。
- **错误报告准确性**：错误信息必须准确指向报告中的错误位置。
- **性能基准**：验证耗时应在可接受范围内。

## 回退策略
- **Schema 解析失败**：回退到基本 JSON 语法检查。
- **验证器不可用**：使用替代验证器或手动验证关键字段。
- **性能不足**：简化 Schema 或采用采样验证。

## 资源召回建议
- 当需要验证 JSON 报告结构时召回本卡片。
- 配套资源：JSON Schema 验证库（如 ajv、jsonschema）、JSON Schema 编辑器、在线验证工具。

## 证据来源
[1] Schema First Tool APIs for LLM Agents: A Controlled Study of Tool Misuse, Recovery, and Budgeted Performance, Akshey Sigdel, Rista Baral, arXiv.org, 2026, DOI: 10.48550/arXiv.2603.13404
[2] Blaze: Compiling JSON Schema for 10x Faster Validation, Juan Cruz Viotti, Michael J. Mior, Proceedings of the VLDB Endowment, 2025, DOI: 10.48550/arXiv.2503.02770
[3] JTutor: JSON Schema Validation Explained, Lyes Attouche, M. Baazizi, Dario Colazzo, International Workshop/Symposium on Database Programming Languages, 2025, DOI: 10.1145/3735106.3736532
[4] Validation of Modern JSON Schema: Formalization and Complexity, Lyes Attouche, M. Baazizi, Dario Colazzo, Proc. ACM Program. Lang., 2023, DOI: 10.1145/3632891