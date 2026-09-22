# JSON Schema 报告交付契约方法论

## 适用范围
本卡片服务于基于 JSON Schema 定义报告交付契约的场景，确保自动化生成的报告（如科研计算结果、数据分析报告、任务执行报告）符合预定义的结构、类型和必填字段要求。适用于任何需要结构化输出并保证数据完整性的领域。

## 输入
- JSON Schema 定义文件（描述报告结构、字段类型、必填字段、约束条件）
- 待校验的 JSON 报告数据
- 任务上下文（任务 ID、任务名称、执行环境）

## 输出
- 校验结果（通过/失败）
- 错误详情（不满足的约束、缺失的字段、类型错误）
- 校验后的报告数据（可能包含默认值填充或格式修正）

## 流程节点
1. **Schema 加载** → 加载并解析 JSON Schema 定义文件。
2. **报告数据准备** → 准备待校验的 JSON 报告数据。
3. **Schema 校验** → 使用 JSON Schema 校验器验证报告数据。
4. **错误处理** → 解析校验错误，生成人类可读的错误消息。
5. **修复与填充** → 根据 Schema 定义填充可选字段的默认值，修正格式问题。
6. **交付确认** → 确认报告符合契约，准备交付。

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 必填字段 | 如 "task_id", "task", "issues", "summary" | JSON Schema 定义 | 报告必须包含这些字段 |
| 字段类型 | 如 string, array, object | JSON Schema 定义 | 字段必须符合指定类型 |
| 数组约束 | 如 minItems, maxItems, uniqueItems | JSON Schema 定义 | 数组字段的长度和唯一性约束 |
| 字符串模式 | 如 pattern, minLength, maxLength | JSON Schema 定义 | 字符串字段的格式约束 |
| 任务身份一致性 | task_id 与任务索引匹配 | 业务规则 | 报告中的任务身份必须与上下文一致 |

## 边界与分流
- **Schema 版本不兼容**：不同版本的 JSON Schema 可能有不同语法，需指定版本。
- **校验器实现差异**：不同校验器可能有细微行为差异，需选择权威校验器。
- **性能考虑**：对于大型报告，校验可能耗时，需考虑异步校验或分块校验。
- **错误恢复**：当校验失败时，是终止流程还是尝试修复，需根据业务规则决定。

## 质量检查
- 验证 JSON Schema 本身是否符合 JSON Schema 规范。
- 检查报告数据是否通过所有必填字段校验。
- 确保错误消息包含具体的字段路径和违反的约束。
- 验证校验后的报告数据仍然保持语义正确性。

## 回退策略
- 当 JSON Schema 校验器不可用时，使用基本字段存在性检查作为降级方案。
- 当 Schema 定义过于复杂时，可拆分为多个子 Schema 分别校验。
- 当校验失败且无法自动修复时，生成详细的错误报告并终止交付。

## 资源召回建议
- 当任务需要生成结构化报告时，召回本卡片。
- 配套资源：JSON Schema 定义文件、校验器工具、报告模板。
- 相关卡片：任务执行工作流卡片、数据输出格式卡片。

## 补充证据（开源文档/用户自有，可选）
[D1] JSON Schema 官方文档，JSON Schema 标准组织，2023年发布（交叉验证）
[D2] ajv 校验器文档，MIT 许可，2024年发布（单源参考）

## 证据来源
[1] Schema validation and evaluation framework for extracted schemas in JSON databases, Saad Belefqih et al., Scientific Reports, 2026, DOI: 10.1038/s41598-026-45554-6
[2] Improving Api Test Accuracy through Schema Validation and Real-time Json Assertions in Jenkins Pipelines, Udayan Verma, International Journal on Science and Technology, 2025, DOI: 10.71097/ijsat.v16.i3.10656
[3] Blaze: Compiling JSON Schema for 10x Faster Validation, Juan Cruz Viotti et al., Proceedings of the VLDB Endowment, 2025, DOI: 10.14778/3773749.3773764
[4] Validation of Modern JSON Schema: Formalization and Complexity, Lyes Attouche et al., Proceedings of the ACM on Programming Languages, 2024, DOI: 10.1145/3632891