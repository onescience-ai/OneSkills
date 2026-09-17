# JSON Schema报告交付契约

## 适用范围
面向结构化数据交换场景，提供JSON Schema定义、验证、错误处理与报告交付契约的通用方法框架。确保数据格式一致性、字段完整性与类型正确性，适用于API契约、配置文件、报告生成、数据验证等场景。不适用于二进制数据格式或非JSON数据交换。

## 输入
- JSON Schema定义文件（.json）
- 待验证的JSON数据
- 验证选项配置（可选）
- 自定义格式验证器（可选）

## 输出
- 验证结果（通过/失败）
- 错误详情列表
- 错误位置信息（行号、列号）
- 格式化错误报告

## 流程节点

### 1. Schema加载与解析
- **操作**：解析JSON Schema文件，验证Schema本身的有效性
- **参数**：schema_file_path
- **工具**：jsonschema (Python), ajv (Node.js)
- **质量门禁**：Schema必须符合JSON Schema规范

### 2. 数据准备
- **操作**：准备待验证的报告数据，确保格式正确
- **参数**：data_file_path
- **工具**：json (Python), JSON.parse (JavaScript)
- **质量门禁**：数据必须是有效的JSON

### 3. 字段校验
- **操作**：检查必填字段是否存在，字段类型是否正确
- **参数**：required_fields, field_types
- **质量门禁**：所有required字段必须存在

### 4. 任务身份验证
- **操作**：验证task_id和task字段与任务索引一致
- **参数**：task_id, task_name
- **质量门禁**：任务身份必须匹配

### 5. 数组约束检查
- **操作**：验证数组字段的长度、元素类型和约束
- **参数**：array_field, minItems, maxItems
- **质量门禁**：数组长度必须在指定范围内

### 6. 格式校验
- **操作**：检查日期格式、字符串格式、数值范围等
- **参数**：format_keywords
- **质量门禁**：格式验证必须通过（如启用）

### 7. 错误处理
- **操作**：收集所有校验错误，提供详细错误报告
- **参数**：validation_errors
- **质量门禁**：错误报告必须包含完整的位置信息

### 8. 结果输出
- **操作**：生成校验报告，包含通过/失败状态和错误详情
- **参数**：validation_result
- **质量门禁**：报告格式必须符合预定义Schema

## 关键参数

### 通用判据（方法层）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| type | string/number/boolean/array/object/null | [D1] | 基本数据类型定义 |
| required | 字段名数组 | [D1] | 必填字段列表 |
| properties | 字段定义对象 | [D1] | 字段类型和约束定义 |
| format | date-time/email/uri等 | [D1] | 语义格式验证 |
| minItems/maxItems | 整数 | [D1] | 数组最小和最大长度限制 |
| additionalProperties | boolean/object | [D1] | 是否允许额外字段 |
| enum | 值数组 | [D1] | 枚举值约束 |
| pattern | 正则表达式 | [D1] | 字符串模式匹配 |

### 校准数值（示例参考）
以下数值来自 JSON Schema 规范和行业实践，供量级校准；其他场景需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| JSON Schema版本 | 2020-12 | [D1] | 当前稳定版本 |
| 常用格式 | date-time, email, uri, uuid | [D1] | 内置格式类型 |
| 最大嵌套深度 | 10层 | [D1] | 避免过深嵌套导致性能问题 |
| 字符串最大长度 | 10000字符 | [D1] | 防止过长字符串导致内存问题 |

## 边界与分流

### Schema解析失败时的分流
- **前提**：Schema本身格式错误
- **分流**：抛出解析异常，提供Schema修复建议

### 数据格式错误时的分流
- **前提**：JSON数据无法解析
- **分流**：抛出JSONDecodeError，提供数据修复建议

### 验证失败时的分流
- **前提**：数据不符合Schema约束
- **分流**：返回错误详情列表，提供修复建议

### 未知格式时的分流
- **前提**：遇到未定义的format
- **分流**：验证器应忽略该格式（注解模式）

### 严格模式时的分流
- **前提**：strict=true时遇到控制字符
- **分流**：导致验证失败，提供清理建议

### 任务身份不匹配时的分流
- **前提**：task_id或task字段与任务索引不一致
- **分流**：提供身份验证错误，建议检查任务配置

### 数组约束违反时的分流
- **前提**：数组长度超出minItems/maxItems范围
- **分流**：提供数组约束错误，建议调整数组内容

## 质量检查
| 检查点 | 验证方式 | 失败处理 |
|--------|----------|----------|
| Schema有效性 | 验证Schema符合JSON Schema规范 | 抛出Schema解析异常 |
| 必填字段 | 检查所有required字段是否存在 | 返回字段缺失错误 |
| 字段类型 | 验证字段类型是否匹配 | 返回类型错误 |
| 格式验证 | 检查格式验证是否通过 | 返回格式错误 |
| 错误报告 | 确保错误报告包含完整的位置信息 | 提供通用错误消息 |

## 回退策略
1. **Schema验证器不可用**：使用基本类型检查
2. **格式验证失败**：降级为仅类型验证
3. **错误详情不足**：提供通用错误消息
4. **验证库异常**：使用内置JSON解析验证

## 资源召回建议
- **何时召回本卡片**：
  - 需要定义数据交换格式契约时
  - 需要验证JSON数据符合Schema时
  - 需要生成结构化错误报告时
  - 需要设计API响应格式时
- **配套资源**：
  - general-cli-non-interactive-execution-fault-classification：验证CLI输出
  - 领域特定的数据格式卡片：如气象/生信等领域的专用格式

## 批次补充 2026-09-17（onescience-knowledge-harvester）

### 约束税测量 [1]

硬Schema解码将有效性从61.5%提升到100%，但答案准确率从19.7%下降到11.0%：
- 有效性-准确率权衡：严格约束提高格式正确性但降低内容准确性
- "约束税"定义：为满足Schema约束而损失的准确性
- 关键发现：小语言模型在严格约束下性能下降更明显

### 结构化提取基准 [2]

35个PDF文档，12,867个字段的基准测试：
- 前沿模型在369字段Schema上实现0%有效输出
- 复杂Schema导致模型输出质量急剧下降
- 关键发现：Schema复杂度与模型性能呈负相关

### 语法约束解码优化 [3]

解析器栈分类实现700倍加速：
- 复杂语法：700倍加速
- JSON Schema：30倍加速
- 关键发现：语法约束解码可通过优化实现高效执行

### 数据契约自动生成 [4]

LLM框架自动生成JSON Schema和Avro契约：
- 工作负载减少70%以上
- 自动生成契约提高数据工程质量
- 关键发现：LLM可有效辅助数据契约设计

## 补充证据
[D1] Understanding JSON Schema, JSON Schema Organization, 2020-12, URL: https://json-schema.org/understanding-json-schema/（accessed_at 2026-09-16，权威官方文档）
[D2] Python json Module Documentation, Python Software Foundation, 3.14.7, URL: https://docs.python.org/3/library/json.html（accessed_at 2026-09-16，权威官方文档）
[D3] JSON Schema reference, JSON Schema, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/（accessed_at 2026-09-16，权威官方文档）

## 证据来源
[1] Ray, "The Constraint Tax: Measuring Validity-Correctness Tradeoffs in Structured Outputs for Small Language Models", arXiv cs.LG, 2026, DOI: 10.48550/arXiv.2605.26128
[2] Ferguson et al., "ExtractBench: A Benchmark and Evaluation Methodology for Complex Structured Extraction", arXiv cs.LG, 2026, DOI: 10.48550/arXiv.2602.12247
[3] Li et al., "Efficient Grammar-Constrained Decoding via Parser Stack Classification", ISSTA 2026, DOI: 10.48550/arXiv.2608.03065
[4] Bhoite, "AI-Driven Generation of Data Contracts in Modern Data Engineering", arXiv cs.DB, 2025, DOI: 10.48550/arXiv.2507.21056
[5] Understanding JSON Schema, JSON Schema Organization, 2020-12
[6] Python json Module Documentation, Python Software Foundation, 2026
[7] JSON Schema reference, JSON Schema, 2020-12
