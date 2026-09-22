# JSON Schema 报告交付契约验证

## 适用范围
适用于需要确保 JSON 报告符合预定义 Schema 的场景，包括自动化报告生成、数据交换、API 响应验证等。提供 JSON Schema 校验、必填字段检查、类型约束验证和数组约束处理的通用方法，确保报告的数据完整性和格式一致性。

## 输入
- JSON Schema 定义文件（.json 或 .yaml）。
- 待验证的 JSON 报告数据。
- 校验规则（如严格模式、忽略额外字段）。

## 输出
- 校验结果：通过或失败，包含具体错误信息。
- 错误报告：列出不满足 Schema 的字段、原因和修复建议。
- 校验日志：记录校验过程、性能指标。

## 流程节点
1. **Schema 解析** → 加载并解析 JSON Schema，提取必填字段、类型约束、数组约束等规则 [1]。
2. **数据预处理** → 清洗待验证 JSON 数据，确保格式正确（如 Unicode 编码、缩进）[1]。
3. **校验执行** → 逐条应用 Schema 规则，检查字段存在性、类型匹配、数组元素约束等 [1][2]。
4. **错误收集** → 收集所有校验错误，包括缺失字段、类型错误、额外字段等 [1]。
5. **错误报告生成** → 生成结构化错误报告，包含错误位置、原因、严重级别和修复建议 [2]。
6. **校验结果输出** → 输出校验通过/失败状态，返回错误报告或成功确认。

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 必填字段 | Schema 定义 | 用户定义 | 报告必须包含的字段，如 "task_id", "summary", "issues" |
| 类型约束 | string, number, array, object 等 | JSON Schema 标准 | 字段的数据类型必须匹配 |
| 数组约束 | minItems, maxItems, uniqueItems | JSON Schema 标准 | 数组字段的长度和唯一性约束 |
| 额外字段策略 | allow/forbid | 用户定义 | 是否允许 Schema 未定义的额外字段 |
| 校验模式 | strict/lenient | 用户定义 | 严格模式下所有规则必须满足，宽松模式下允许部分违规 |

## 边界与分流
- **Schema 解析失败** → 检查 Schema 语法，输出解析错误并终止校验。
- **数据格式错误** → 尝试自动修复（如 UTF-8 编码），失败则报告格式错误。
- **校验超时** → 终止校验并报告超时，建议优化 Schema 或数据规模。
- **未知错误** → 捕获未预期异常，输出堆栈跟踪并标记校验失败。

## 质量检查
- 校验结果必须准确反映 Schema 满足情况。
- 错误报告必须包含足够的信息用于修复。
- 校验性能应满足实时性要求（如毫秒级响应）。

## 回退策略
- 当 Schema 校验失败时，回退到基础字段检查（如检查顶层字段存在性）。
- 当自动化校验不可用时，提供手动校验清单。

## 资源召回建议
- 当需要验证 JSON 报告是否符合预定义 Schema 时召回本卡片。
- 当遇到 JSON 报告字段缺失、类型错误或格式不一致时召回。
- 配套资源：具体领域的报告格式规范卡片。

## 补充证据（开源文档/用户自有，可选）
无。

## 证据来源
[1] Blaze: Compiling JSON Schema for 10x Faster Validation, Proceedings of the VLDB Endowment, 2025, DOI: 10.14778/3773749.3773764
[2] Improving Api Test Accuracy through Schema Validation and Real-time Json Assertions in Jenkins Pipelines, International Journal on Science and Technology, 2025, DOI: 10.71097/ijsat.v16.i3.10656