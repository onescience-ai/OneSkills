# JSON Schema 报告交付契约方法论

## 适用范围
本卡提供结构化报告交付中JSON Schema验证、复杂度分析和性能优化的方法论，适用于科学计算、数据分析和自动化报告生成中的报告契约保障。当需要确保输出报告符合预定义格式、字段完整性和类型约束时，本方法论帮助设计、验证和优化JSON Schema。

## 输入
- JSON Schema定义（必填字段、类型约束、数组规则）
- 待验证的JSON报告数据
- 性能要求（验证延迟、吞吐量）
- 兼容性要求（JSON Schema版本、工具链）

## 输出
- 验证结果（通过/失败，包含错误详情）
- 复杂度分析报告（时间复杂度、空间复杂度）
- 性能优化建议（编译优化、缓存策略）
- 见证生成（示例数据或反例）

## 流程节点
1. **Schema解析** → 解析JSON Schema，构建内部表示。参数：Schema版本（Draft 2019-09+）。工具：Schema解析器。质量门禁：解析成功率100%，支持动态引用和注释依赖。
2. **复杂度分析** → 分析验证问题的计算复杂度。参数：Schema大小、数据大小。工具：复杂度分析器。质量门禁：复杂度分类准确率≥95%（PTIME/PSPACE）。
3. **验证执行** → 执行JSON Schema验证。参数：验证器选择（标准/编译优化）。工具：JSON Schema验证器。质量门禁：验证结果准确率100%，符合规范。
4. **性能优化** → 应用编译优化提高验证速度。参数：优化级别、缓存策略。工具：Schema编译器。质量门禁：验证速度提升≥10倍。
5. **见证生成** → 生成满足Schema的示例数据或违反Schema的反例。参数：见证类型（正面/负面）。工具：见证生成器。质量门禁：生成成功率≥90%，覆盖主要Schema特征。
6. **报告生成** → 生成结构化验证报告。参数：报告格式。工具：模板引擎。质量门禁：报告字段完整率100%。

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Schema版本支持 | Draft 2019-09+ | [论文1] | 支持动态引用和注释依赖验证 |
| 验证复杂度 | PSPACE完全 | [论文1] | 现代JSON Schema验证的最坏情况复杂度 |
| 性能优化倍数 | ≥10倍 | [论文2] | 编译优化后的验证速度提升 |
| 见证生成覆盖率 | ≥90% | [论文3] | 生成满足Schema的示例数据成功率 |
| 规范遵守度 | 100% | [论文2] | 验证器严格遵守JSON Schema规范 |

### 校准数值
以下数值来自JSON Schema研究基准，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模式集合大小 | 数千个真实模式 | [论文3] | 见证生成实验使用的模式数量 |
| 验证时间减少 | 多个数量级 | [论文2] | Blaze在某些情况下相对于次优验证器的加速 |
| 复杂度分类 | PTIME vs PSPACE | [论文1] | 经典与现代JSON Schema的复杂度差异 |
| 动态引用影响 | 指数级增长 | [论文1] | 动态引用导致Schema大小指数增长 |

## 边界与分流
- **Schema过于复杂**：简化Schema设计，分解为多个小Schema或使用引用。
- **验证性能瓶颈**：采用编译优化、缓存或异步验证，降低实时性要求。
- **见证生成失败**：降低见证完整性要求或使用随机生成加后验证。
- **版本兼容性问题**：提供Schema转换工具或降级到经典JSON Schema。
- **工具链缺失**：使用开源验证器或实现最小化验证器。

## 质量检查
- **Schema解析完整性**：所有Schema关键词解析率100%。
- **验证准确性**：已知正确/错误数据验证准确率100%。
- **性能基准**：验证延迟<100ms（中等规模数据），内存占用<50MB。
- **见证有效性**：生成的见证数据通过Schema验证率≥95%。
- **报告完整性**：验证报告包含所有错误详情和元数据。

## 回退策略
- **全自动验证失败**：提供详细错误日志，转交人工Schema设计审查。
- **性能不达标**：采用简化Schema或近似验证，接受一定误报率。
- **见证生成不可行**：提供空见证并标注，依赖人工构造示例。
- **版本不兼容**：提供Schema迁移指南或双版本支持。

## 批次补充（2026-09-21）

### type 关键字的两种形式

JSON Schema 的 `type` 关键字支持两种形式：

1. **单字符串形式**：指定单一类型
   ```json
   { "type": "number" }
   ```
   实例数据必须匹配该特定类型才有效。

2. **字符串数组形式**：指定多种允许类型
   ```json
   { "type": ["number", "string"] }
   ```
   实例数据匹配任一给定类型即有效。

证据来源 [D1]

### JSON Schema 基本类型

| JSON 类型 | Python 等价类型 | 说明 |
|-----------|-----------------|------|
| string | str | Unicode 字符串 |
| number | int/float | 无整数/浮点数区分 |
| object | dict | 键值对集合 |
| array | list | 有序值集合 |
| boolean | bool | true/false |
| null | None | 空值 |

证据来源 [D1]

### 类型特定验证关键词

| 类型 | 关键词 | 说明 |
|------|--------|------|
| array | items, additionalItems, minItems, maxItems, uniqueItems | 定义元素模式、数量约束和唯一性 |
| number | minimum, maximum, exclusiveMinimum, exclusiveMaximum, multipleOf | 定义数值范围和倍数 |
| object | required, properties, additionalProperties, patternProperties, minProperties, maxProperties | 定义必填属性、属性模式和数量 |
| string | minLength, maxLength, pattern, format | 定义长度、模式匹配和格式验证 |

证据来源 [D1]

### 内置格式验证

| 格式 | 说明 | 示例 |
|------|------|------|
| date-time | 日期时间（RFC 3339） | 2018-11-13T20:20:39+00:00 |
| time | 时间（Draft 7+） | 20:20:39+00:00 |
| date | 日期（Draft 7+） | 2018-11-13 |
| duration | 持续时间（ISO 8601） | P3D |
| email | 互联网邮箱（RFC 5321） | user@example.com |
| hostname | 互联网主机名（RFC 1123） | example.com |
| ipv4 | IPv4 地址 | 192.168.1.1 |
| ipv6 | IPv6 地址 | 2001:db8::1 |
| uri | 通用资源标识符（RFC 3986） | https://example.com |
| uuid | 通用唯一标识符（RFC 4122） | 3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a |
| json-pointer | JSON 指针（RFC 6901） | /foo/bar |
| regex | 正则表达式（ECMA 262） | ^[a-z]+$ |

证据来源 [D1]

## 资源召回建议
当遇到以下情况时召回本卡片：
- 设计科学计算报告的输出格式
- 验证数据分析结果的结构完整性
- 优化大规模数据验证的性能
- 构建自动化报告生成流水线
- 处理JSON Schema版本兼容性问题

配套资源：`general-cli-fault-classification`（用于CLI工具输出验证）、`general-data-quality-assurance`（用于数据质量保障）。

## 证据来源
[1] Validation of Modern JSON Schema: Formalization and Complexity, Lyes Attouche et al., arXiv, 2024, DOI: 10.48550/arXiv.2307.10034
[2] Blaze: Compiling JSON Schema for 10x Faster Validation, Juan Cruz Viotti et al., arXiv, 2025, DOI: 10.48550/arXiv.2503.02770
[3] Witness Generation for JSON Schema, Lyes Attouche et al., arXiv, 2022, DOI: 10.48550/arXiv.2202.12849