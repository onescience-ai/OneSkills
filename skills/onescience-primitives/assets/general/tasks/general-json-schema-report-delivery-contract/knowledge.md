# JSON Schema 报告交付契约

## 适用范围
面向 JSON 数据结构化输出场景，提供 JSON Schema 报告交付契约规范。适用于任何需要生成符合 JSON Schema 规范的报告、确保报告可解析且与任务身份一致的自动化系统、CI/CD 流水线或数据交换场景。

## 输入
- JSON Schema 定义文件（描述报告结构）
- 待验证的 JSON 报告文档
- 任务身份信息（task_id、task name）
- 校验配置（严格模式/宽松模式）

## 输出
- 校验结果（通过/失败）
- 错误详情（缺失字段、类型不匹配、约束违反）
- 修复建议（如何使报告符合契约）
- 校验报告（结构化输出，可用于后续处理）

## 流程节点
1. Schema 加载 → 读取并解析 JSON Schema 定义
2. 报告加载 → 读取待验证的 JSON 报告文档
3. 结构校验 → 检查必填字段、数据类型、数组约束
4. 身份校验 → 验证 task_id、task name 与任务索引一致性
5. 格式校验 → 检查输出格式、字段命名规范
6. 结果生成 → 生成校验报告和修复建议

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 必填字段校验 | 严格 | [D1] | 所有标记为 "required" 的字段必须存在 |
| 类型校验 | 严格 | [D1] | 字段值必须符合 Schema 定义的类型 |
| 数组约束 | 严格 | [D1] | 数组长度、唯一性等约束必须满足 |
| 身份一致性 | 严格 | [D2] | task_id 和 task name 必须与任务索引匹配 |
| 输出格式 | JSON | [D1] | 报告必须是有效的 JSON 格式 |

### 校准数值
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| JSON 编码 | UTF-8 | [D1] | JSON 文档应使用 UTF-8 编码 |
| Schema 版本 | draft-2020-12 | [D1] | 推荐使用最新的 Schema 草案版本 |

## 边界与分流
- **Schema 加载失败**：报告 Schema 文件不存在或格式错误，无法进行校验
- **报告解析失败**：JSON 报告文档格式错误，无法解析
- **结构校验失败**：报告缺少必填字段或字段类型不匹配
- **身份校验失败**：task_id 或 task name 与任务索引不一致
- **格式校验失败**：输出格式不符合约定（如缺少 summary、issues 字段）

## 质量检查
- 验证 JSON Schema 本身是否符合 Meta-Schema 规范
- 检查报告文档是否可被标准 JSON 解析器解析
- 确认所有必填字段都存在且类型正确
- 验证 task_id 和 task name 与任务索引一致
- 检查数组字段是否满足长度和唯一性约束

## 回退策略
- Schema 加载失败时：使用默认 Schema 或报告人工干预
- 报告解析失败时：尝试修复 JSON 格式或报告解析错误
- 校验失败时：生成详细的错误报告和修复建议
- 身份不一致时：标记为待确认，等待人工核实

## 资源召回建议
- 当需要生成符合 JSON Schema 规范的报告时召回本卡片
- 当遇到 JSON 报告校验失败时参考
- 当需要设计结构化输出契约时使用
- 配套资源：CLI 非交互执行与故障分类知识（用于处理 CLI 执行异常）

## 补充证据（开源文档）
[D1] JSON Schema: A Media Type for Describing JSON Documents, Internet Engineering Task Force (IETF), draft-bhutton-json-schema-01, URL: https://json-schema.org/draft/2020-12/json-schema-core（accessed 2026-09-21，权威标准）
[D2] JSON Schema Validation: A Vocabulary for Structural Validation of JSON, Internet Engineering Task Force (IETF), draft-bhutton-json-schema-validation-01, URL: https://json-schema.org/draft/2020-12/json-schema-validation（accessed 2026-09-21，权威标准）

## 批次补充（2026-09-21）

本次补充基于SVEF框架论文，为JSON Schema报告交付契约提供更全面的验证维度：

### 1. 六维度验证框架
SVEF（Schema Validation and Evaluation Framework）提供六个互补的验证维度：
- **数据类型准确性**：验证字段类型与实际数据类型一致性
- **必填/可选字段**：验证必填字段存在性和依赖关系
- **多类型支持**：验证联合类型（union types）的表示准确性
- **集合结构一致性**：验证数组结构和嵌套深度
- **实体关系恢复**：验证实体间关系（引用、聚合）
- **时间演化检测**：验证schema随时间的变化

### 2. 量化评估指标
- **类型一致性**：使用Jaccard相似度计算类型匹配
- **存在准确率**：计算必填字段识别的准确率
- **依赖置信度**：使用关联规则（支持度、置信度、提升度）验证依赖关系
- **图编辑距离**：使用归一化图编辑距离验证关系图相似性

### 3. 实验验证方法
- 使用三个基准数据集：电商、医疗、物联网
- 比较三种schema提取方法：SBERT-RDF、Generic U-Schema、GEO-Nautilus
- 评估维度权重：DTA:0.20, ROF:0.15, MTS:0.15, CSC:0.15, ERR:0.20, TED:0.15

## 批次补充（2026-09-21 · 第二轮）

本次补充基于"单层MoS2纳米孔海水淡化设计"任务归因报告中的JSON Schema报告交付契约知识缺口，主要强化以下内容：

### 1. JSON Schema 验证复杂性
- Modern JSON Schema（Draft 2019-09+）引入了动态引用和注释依赖验证，使验证复杂性从 PTIME 增加到 PSPACE [5]
- 动态引用是导致复杂性增加的主要原因，而非注释依赖验证
- 固定实例时问题关于 Schema 大小是 PSPACE 完全的，但固定 Schema 时关于实例大小是 PTIME 的

### 2. JSON Schema 验证性能优化
- Blaze 编译器可将复杂 Schema 编译为高效表示，验证速度提升约 10 倍 [6]
- 预编译可解决 Schema 关键字间的复杂交互，减少运行时验证时间
- 部分流行验证器在某些情况下会产生错误结果，而 Blaze 严格遵守 JSON Schema 规范

### 3. LLM 结构化输出生成
- SchemaBench 包含约 40K 个不同 JSON Schema，用于评估模型生成有效 JSON 的能力 [7]
- 最新的 LLM 仍然难以生成有效的 JSON 字符串
- 使用细粒度 Schema 验证器的强化学习可增强模型对 JSON Schema 的理解

## 证据来源
[1] Schema validation and evaluation framework for extracted schemas in JSON databases, Scientific Reports, 2026, DOI: 10.1038/s41598-026-45554-6
[2] JSON Schema: A Media Type for Describing JSON Documents, Internet Engineering Task Force (IETF), draft-bhutton-json-schema-01, URL: https://json-schema.org/draft/2020-12/json-schema-core
[3] JSON Schema Validation: A Vocabulary for Structural Validation of JSON, Internet Engineering Task Force (IETF), draft-bhutton-json-schema-validation-01, URL: https://json-schema.org/draft/2020-12/json-schema-validation
[5] Validation of Modern JSON Schema: Formalization and Complexity, Lyes Attouche et al., Proc. ACM Programming Languages, 2024, DOI: 10.1145/3632891
[6] Blaze: Compiling JSON Schema for 10x Faster Validation, Juan Cruz Viotti et al., arXiv:2503.02770, 2025, DOI: 10.48550/arXiv.2503.02770
[7] Learning to Generate Structured Output with Schema Reinforcement Learning, Yaxi Lu et al., arXiv:2502.18878, 2025, DOI: 10.48550/arXiv.2502.18878

## 批次补充（2026-09-21 · 第三轮）

本次补充基于"钙钛矿氧化物与卤化物容忍因子稳定性筛选"任务归因报告中的JSON Schema报告交付契约知识缺口，主要强化以下内容：

### 1. SVEF框架六维度验证
- **数据类型准确性**：验证字段类型与实际数据类型一致性，使用Jaccard相似度计算类型匹配 [1]
- **必填/可选字段**：验证必填字段存在性和依赖关系，使用关联规则（支持度、置信度、提升度）验证依赖关系 [1]
- **多类型支持**：验证联合类型（union types）的表示准确性，通过union conformance评分衡量 [1]
- **集合结构一致性**：验证数组结构和嵌套深度，结合深度一致性和同质性指数评估 [1]
- **实体关系恢复**：验证实体间关系（引用、聚合），使用图编辑距离验证关系图相似性 [1]
- **时间演化检测**：验证schema随时间的变化，检测结构演变模式 [1]

### 2. 量化评估指标
- **类型一致性**：使用Jaccard相似度计算类型匹配，得分接近1表示推断类型与观察类型高度一致 [1]
- **存在准确率**：计算必填字段识别的准确率，通过指示函数判断推断状态与参考状态是否一致 [1]
- **依赖置信度**：使用关联规则（支持度、置信度、提升度）验证依赖关系，通常置信度阈值0.8，提升度阈值1.2 [1]
- **图编辑距离**：使用归一化图编辑距离验证关系图相似性，归一化图编辑距离=1-编辑距离/参考边数 [1]

### 3. 实验验证方法
- **基准数据集**：使用三个基准数据集：电商、医疗、物联网 [1]
- **基线方法**：比较三种schema提取方法：SBERT-RDF、Generic U-Schema、GEO-Nautilus [1]
- **评估维度权重**：DTA:0.20, ROF:0.15, MTS:0.15, CSC:0.15, ERR:0.20, TED:0.15 [1]
- **全局质量评分**：通过加权组合计算Schema Quality Score (SQS)，权重可根据评估重点调整 [1]

### 4. 评估框架定位
- **系统化评估**：SVEF提供系统化、基于度量的模型，用于评估推断schema的质量 [1]
- **方法比较**：支持在共同基础上比较现有和未来的推理方法，促进更透明的分析 [1]
- **trade-off理解**：帮助深入理解schema属性之间的权衡 [1]
- **标准化评估**：为schema提取研究提供更稳健的经验基础 [1]

## 批次补充（2026-09-21 · 第四轮）

本次补充基于气象预报驱动河流流量与洪峰预报任务归因报告，主要强化JSON Schema官方文档的权威证据：

### 1. 对象类型验证 [D3]
- `type: "object"` 验证数据为JSON对象类型
- 对象键必须为字符串，值可以是任意JSON类型
- 空对象 `{}` 默认是有效的

### 2. 属性定义与验证 [D3]
- `properties` 定义每个属性的验证模式
- 不匹配 `properties` 中任何名称的属性默认被忽略
- 可通过 `additionalProperties: false` 禁止额外属性
- `patternProperties` 使用正则表达式匹配属性名

### 3. 必填属性验证 [D3]
- `required` 关键字接受字符串数组，每个字符串必须唯一
- 缺少必填属性的JSON文档无效
- 属性值为 `null` 不等同于属性不存在
- Draft 4 要求 `required` 至少包含一个字符串

### 4. 属性数量约束 [D3]
- `minProperties` 和 `maxProperties` 限制属性数量
- 值必须为非负整数

## 补充证据

[D1] Schema validation and evaluation framework for extracted schemas in JSON databases, Scientific Reports, 2026, DOI: 10.1038/s41598-026-45554-6

[D2] JSON Schema: A Media Type for Describing JSON Documents, Internet Engineering Task Force (IETF), draft-bhutton-json-schema-01, URL: https://json-schema.org/draft/2020-12/json-schema-core

[D3] Understanding JSON Schema - Object, JSON Schema, 2026, URL: https://json-schema.org/understanding-json-schema/reference/object（accessed 2026-09-21，权威官方文档，交叉验证：定义了对象类型验证和必填属性规范）

[D5] Validation of Modern JSON Schema: Formalization and Complexity, Lyes Attouche et al., Proc. ACM Programming Languages, 2024, DOI: 10.1145/3632891

[D6] Blaze: Compiling JSON Schema for 10x Faster Validation, Juan Cruz Viotti et al., arXiv:2503.02770, 2025, DOI: 10.48550/arXiv.2503.02770

[D7] Learning to Generate Structured Output with Schema Reinforcement Learning, Yaxi Lu et al., arXiv:2502.18878, 2025, DOI: 10.48550/arXiv.2502.18878

## 批次补充（2026-09-21 · 第五轮）

本次补充基于草地地上生物量遥感估计与气候响应诊断任务归因报告，主要强化 API 测试中的 JSON Schema 验证实践：

### 1. API 测试中的 Schema 验证集成
- JSON Schema 验证可集成到 Jenkins 流水线中作为自动化测试步骤 [8]
- 实时 JSON 断言可与 Schema 验证结合，提供更全面的 API 测试覆盖
- 结构回归检测是确保 API 兼容性的关键环节

### 2. 大规模微服务环境下的挑战
- 传统功能测试在大规模微服务生态系统中可能不够有效 [8]
- 结构回归可能导致灾难性的集成错误
- 自动化 Schema 验证可显著减少人工验证成本

### 3. 与报告交付契约的关联
- API 测试中的 Schema 验证原则可应用于报告交付契约验证
- 实时断言方法可用于报告字段的动态校验
- 流水线集成思路可扩展到报告生成流程的质量门禁

## 证据来源

[8] Improving Api Test Accuracy through Schema Validation and Real-time Json Assertions in Jenkins Pipelines, Udayan Verma, International Journal on Science and Technology, 2025, DOI: 10.71097/ijsat.v16.i3.10656