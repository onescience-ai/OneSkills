# JSON Schema报告交付契约

## 适用范围
面向结构化报告的自动化验证与交付场景，提供JSON Schema驱动的报告契约规范。适用于任何需要确保输出报告符合预定义Schema的科研计算任务，包括归因分析报告、数据处理结果、模型评估报告等结构化输出。

## 输入
- JSON Schema定义文件（必填）
- 待验证的JSON报告数据（必填）
- 验证选项（strict模式、错误处理策略）

## 输出
- 验证结果（通过/失败）
- 错误详情（字段路径、错误类型、错误消息）
- 修正建议（可选）

## 流程节点

### 1. Schema加载与解析
- **操作**：加载JSON Schema文件，解析为验证规则树
- **参数**：Schema文件路径、编码格式
- **工具**：jsonschema库、JSON Schema官方解析器
- **质量门禁**：Schema文件格式正确，无语法错误

### 2. 报告数据预处理
- **操作**：加载待验证的JSON报告，进行格式标准化
- **参数**：报告文件路径、编码格式
- **工具**：json.load()、编码检测
- **质量门禁**：JSON格式可解析，无语法错误

### 3. 字段级验证
- **操作**：逐字段检查必填字段、类型约束、格式约束
- **验证维度**（来自SVEF框架 [1]）：
  - **Data Type Accuracy**：字段类型与Schema定义一致
  - **Required Fields**：必填字段存在性检查
  - **Optional Fields**：可选字段存在时类型正确
  - **Multiple Type Support**：联合类型字段的类型兼容性
- **工具**：jsonschema.validate()
- **质量门禁**：所有必填字段存在，类型匹配

### 4. 结构级验证
- **操作**：检查嵌套结构、数组约束、实体关系
- **验证维度**（来自SVEF框架 [1]）：
  - **Collection Structure Consistency**：数组结构与Schema定义一致
  - **Entity Relationships Recovery**：实体关系正确性
- **工具**：jsonschema递归验证
- **质量门禁**：嵌套结构深度正确，数组元素类型一致

### 5. 语义级验证
- **操作**：检查字段间依赖关系、条件约束
- **验证维度**（来自SVEF框架 [1]）：
  - **Dependency Constraints**：字段依赖关系（if-then-else）
  - **Pattern Matching**：正则表达式约束
- **工具**：jsonschema条件验证
- **质量门禁**：依赖关系满足，模式匹配通过

### 6. 错误聚合与报告生成
- **操作**：收集所有验证错误，生成结构化错误报告
- **参数**：错误聚合策略、报告格式
- **工具**：ValidationError聚合
- **质量门禁**：错误报告完整，包含字段路径和错误详情

## 关键参数

### 通用判据（方法层，同类体系可参考）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| required字段 | 必填 | JSON Schema规范 | 字段必须存在 |
| type约束 | 类型匹配 | JSON Schema规范 | 字段类型必须匹配定义 |
| properties | 属性定义 | JSON Schema规范 | 对象属性结构 |
| items | 数组元素 | JSON Schema规范 | 数组元素类型约束 |
| anyOf/oneOf | 联合类型 | JSON Schema规范 | 字段可为多种类型之一 |
| if-then-else | 条件约束 | JSON Schema规范 | 字段依赖关系 |

### 校准数值（来自SVEF框架实验 [1]）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Presence阈值 | 0.90 | [1] | 字段出现频率≥90%视为required |
| Type Conformance | Jaccard相似度 | [1] | 观察类型与推断类型的交并比 |
| Dependency置信度 | 0.80 | [1] | 依赖关系置信度阈值 |
| Dependency提升度 | 1.20 | [1] | 依赖关系提升度阈值 |

## 边界与分流
- **关键前提1：Schema文件有效** → 不成立时：返回Schema解析错误，建议修正Schema
- **关键前提2：JSON数据可解析** → 不成立时：返回JSON解析错误，建议检查数据格式
- **关键前提3：验证库版本兼容** → 不成立时：升级验证库或降级Schema版本
- **降级策略**：严格模式失败时，尝试宽松模式验证

## 质量检查
- Schema文件符合JSON Schema规范（Draft 2019-09或更新）
- 所有必填字段存在且类型正确
- 嵌套结构深度与Schema定义一致
- 条件约束满足（if-then-else逻辑正确）

## 回退策略
- Schema验证失败时：返回详细错误报告，标注失败字段和错误类型
- JSON解析失败时：返回原始内容，标注解析异常
- 依赖验证失败时：标注冲突字段，提供修正建议

## 资源召回建议
- 何时召回本卡片：当任务需要验证JSON报告格式、确保输出符合Schema契约、进行结构化数据校验时
- 配套资源：cli-fault-classification（用于CLI执行故障处理）

## 证据来源
[1] Belefqih, S., Barchane, M., Zellou, A. (2026). Schema validation and evaluation framework for extracted schemas in JSON databases. Scientific Reports. DOI: 10.1038/s41598-026-45554-6
[2] Attouche, L., Baazizi, M.-A., Colazzo, D. (2024). Validation of Modern JSON Schema: Formalization and Complexity. Proceedings of the ACM on Programming Languages. DOI: 10.1145/3632891
[3] Siffa, I. C., Schäfer, J., Becker, M. M. (2022). Adamant: a JSON schema-based metadata editor for research data management workflows. F1000Research. DOI: 10.12688/f1000research.110875.2
