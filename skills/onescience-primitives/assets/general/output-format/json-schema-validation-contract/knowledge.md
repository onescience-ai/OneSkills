# JSON Schema 验证与报告交付契约

## 适用范围

本卡片适用于需要生成、验证或消费符合 JSON Schema 规范的结构化报告的场景。包括但不限于：CLI 工具输出验证、API 响应格式校验、元数据质量检查、数据集成前的 Schema 合规性测试。不适用于非 JSON 格式的报告（如 XML、CSV）或不涉及 Schema 验证的简单 JSON 序列化。

## 输入

- JSON Schema 定义文件（支持 Draft 4/7/2019-09/2020-12 版本）
- 待验证的 JSON 文档或报告
- 可选：参考 Schema（用于对比验证）

## 输出

- 验证结果（通过/失败）
- 错误详情（字段路径、错误类型、错误消息）
- 质量评分（可选，基于六维验证框架）

## 流程节点

### 1. Schema 加载与解析
- 操作：读取并解析 JSON Schema 文件
- 工具：jsonschema 库、Ajv（JavaScript）
- 质量门禁：Schema 文件可被正确解析，无语法错误

### 2. 数据类型准确性验证
- 操作：检查每个属性的数据类型是否与 Schema 声明一致
- 公式：Type Conformance(p) = |PT_obs ∩ PT_inf| / |PT_obs ∪ PT_inf| [1]
- 质量门禁：DTA（Data Type Accuracy）得分 ≥ 0.9

### 3. 必填/可选字段验证
- 操作：检查 required 字段是否都存在，optional 字段是否按条件出现
- 公式：Presence Accuracy = (1/|P|) × Σ 1[R_inf = R_ref] [1]
- 质量门禁：Presence Accuracy ≥ 0.95

### 4. 多类型支持验证
- 检查：union 类型是否正确覆盖所有观察到的类型变体
- 公式：MTS(p) = |T_obs ∩ T_inf| / |T_obs| - λ × max(0, |T_inf| - |T_obs|) / |T_obs| [1]
- 质量门禁：MTS 得分 ≥ 0.85

### 5. 集合结构一致性验证
- 检查：数组的嵌套深度和元素类型同质性
- 公式：CSC = (1/|A|) × Σ (α × Homogeneity(a) + (1-α) × DepthConformance(a)) [1]
- 质量门禁：CSC 得分 ≥ 0.8

### 6. 实体关系恢复验证
- 检查：推断 Schema 是否正确捕获实体间的关系
- 公式：ERR = β × F1 + (1-β) × GED_norm [1]
- 质量门禁：ERR 得分 ≥ 0.75

### 7. 时序演化检测（可选）
- 检查：Schema 是否能检测数据结构的时间演化
- 适用场景：数据结构随时间变化的场景

### 8. 综合评分
- 公式：SQS = Σ w_i × S_i，Σ w_i = 1 [1]
- 权重可根据应用场景调整

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| DTA 阈值 | 0.9 | [1] | 数据类型准确性最低要求 |
| Presence Accuracy 阈值 | 0.95 | [1] | 必填字段验证最低要求 |
| MTS 阈值 | 0.85 | [1] | 多类型支持最低要求 |
| CSC 阈值 | 0.8 | [1] | 集合结构一致性最低要求 |
| ERR 阈值 | 0.75 | [1] | 实体关系恢复最低要求 |
| 依赖置信度阈值 | 0.8 | [1] | 字段依赖关系的最低置信度 |
| 依赖提升度阈值 | 1.2 | [1] | 字段依赖关系的最低提升度 |

## 边界与分流

- **Schema 版本不兼容**：优先使用与 Schema 声明版本匹配的验证器；若无法匹配，使用最保守的验证策略
- **部分验证失败**：区分关键错误（required 字段缺失）和警告（类型不精确），关键错误必须修复
- **性能瓶颈**：对于大型 JSON 文档，考虑流式验证或分块验证

## 质量检查

- 验证器本身需通过 JSON Schema Test Suite 测试
- 自定义关键字验证需有单元测试覆盖
- 验证结果需包含足够的错误上下文（字段路径、实际值、期望值）

## 回退策略

- 若 Schema 验证库不可用，可使用 JSON Schema 的 `$ref` 和 `allOf` 进行手动验证
- 若验证失败，输出详细的错误日志以便调试

## 资源召回建议

- 当任务涉及 CLI 输出校验时，同时召回 `cli-noninteractive-execution` 卡片
- 当任务涉及 API 响应验证时，考虑召回 API 设计相关的知识卡片
- 当任务涉及科研数据管理时，考虑召回 FAIR 原则相关的知识卡片

## 证据来源

[1] Belefqih S, Barchane M, Zellou A. Schema validation and evaluation framework for extracted schemas in JSON databases. Scientific Reports, 2026. DOI: 10.1038/s41598-026-45554-6

[2] Siffa IC, Schäfer J, Becker MM. Adamant: a JSON schema-based metadata editor for research data management workflows. F1000Research, 2022. DOI: 10.12688/f1000research.110875.2
