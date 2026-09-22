# JSON Schema 验证与评估方法论

## 适用范围

**触发条件**：
- 需要校验 JSON 输出是否符合预定义的 Schema 契约
- 需要评估自动提取的 Schema 质量
- 需要检测数据结构随时间的演化和漂移

**适用场景**：
- API 响应格式验证
- 科研计算输出的结构化报告校验
- 数据集成中的 Schema 兼容性检测
- 数据库 Schema 提取质量评估

**不适用场景**：
- XML/HTML 等非 JSON 格式的验证
- 实时流数据的 Schema 演化（需要增量处理）
- 二进制数据格式的校验

## 输入

- 待验证的 JSON 数据实例
- 目标 JSON Schema（预定义契约）
- 可选：参考 Schema（ground truth）
- 可选：时间序列数据（用于演化检测）

## 输出

- Schema 质量评估报告（六维度得分 + SQS）
- 验证通过/失败结果
- 字段级错误详情
- 时间演化检测报告（如适用）

## 流程节点

### Step 1：数据类型准确性评估

- **操作**：比较 JSON 实例中字段的实际类型与 Schema 声明类型
- **参数**：基本类型（string/number/boolean/null/array/object）
- **工具**：JSON Schema validator、jsonschema 库
- **质量门禁**：类型一致性得分 ≥ 0.9

### Step 2：必填/可选字段检测

- **操作**：检查必填字段是否存在、可选字段出现频率
- **参数**：必填字段阈值（频率 ≥ 0.9 视为 required）
- **工具**：频率统计、关联规则挖掘
- **质量门禁**：字段存在性准确性 ≥ 0.85

### Step 3：多类型支持评估

- **操作**：检测字段是否支持多种类型（union types）
- **参数**：类型多样性惩罚系数 λ=0.5
- **工具**：类型集合比较、覆盖率计算
- **质量门禁**：类型覆盖得分 ≥ 0.8

### Step 4：集合结构一致性分析

- **操作**：评估数组字段的嵌套深度和元素类型同质性
- **参数**：同质性权重 α=0.7
- **工具**：Shannon 熵计算、嵌套深度比对
- **质量门禁**：CSC 得分 ≥ 0.75

### Step 5：实体关系恢复检测

- **操作**：识别 JSON 文档中的实体引用和包含关系
- **参数**：关系匹配规则（标准化 source-target 对）、ERR 平衡系数 β=0.7
- **工具**：图对齐、F1-score 计算、图编辑距离
- **质量门禁**：ERR 得分 ≥ 0.7

### Step 6：时间演化检测

- **操作**：检测 Schema 随时间的变化（新增/删除/类型迁移字段）
- **参数**：版本检测准确性（VDA）、变化检测率（CDR）
- **工具**：时间窗口划分、结构等价性比较
- **质量门禁**：TED 得分 ≥ 0.7

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 类型一致性阈值 | 0.9 | [1] | 基本类型必须匹配 |
| 必填字段频率阈值 | 0.9 | [1] | 频率 ≥ 0.9 视为 required |
| 类型多样性惩罚 λ | 0.5 | [1] | 惩罚过度泛化的类型联合 |
| 同质性权重 α | 0.7 | [1] | 平衡类型同质性和嵌套深度 |
| ERR 平衡系数 β | 0.7 | [1] | 平衡 F1 和图编辑距离 |
| 参考变化检测率 | 1.0 | [1] | 理想状态下的变化检测 |
| SQS 权重 | DTA:0.20, ROF:0.15, MTS:0.15, CSC:0.15, ERR:0.20, TED:0.15 | [1] | 六维度加权聚合 |

### 校准数值

以下数值来自 SVEF 框架实验，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 数据类型准确性 (DTA) | ≥ 0.95 | [1] | 基准数据集上表现 |
| 必填/可选字段 (ROF) | 0.7-0.85 | [1] | 受数据稀疏性影响 |
| 多类型支持 (MTS) | 0.8-0.9 | [1] | 取决于类型建模能力 |
| 集合结构一致性 (CSC) | 0.7-0.85 | [1] | 数组建模能力差异大 |
| 实体关系恢复 (ERR) | 0.7-0.9 | [1] | 显式关系更易恢复 |
| 时间演化检测 (TED) | 0.6-0.9 | [1] | 静态方法得分低 |

## 边界与分流

- **前提：JSON 格式正确**：若 JSON 本身格式错误（语法错误），需先修复 JSON 解析问题
- **前提：Schema 定义完整**：若 Schema 缺少某些字段定义，需先补全 Schema
- **前提：数据量足够**：若样本量过小（<10 条），统计指标可能不稳定

**分流方案**：
- JSON 格式错误 → 使用 JSON linter 修复
- Schema 不完整 → 使用 Schema 推断工具补全
- 数据量不足 → 增加样本或使用置信区间

## 质量检查

- [ ] 六维度得分是否全部计算
- [ ] SQS 加权聚合是否正确
- [ ] 字段级错误是否详细记录
- [ ] 时间演化检测是否覆盖所有时间窗口
- [ ] 验证结果是否与预期一致

## 回退策略

- 若 Schema 未定义 → 使用 Schema 推断工具自动生成
- 若数据量不足 → 使用 Bootstrap 估计置信区间
- 若时间窗口划分不合理 → 调整窗口大小或使用滑动窗口

## 资源召回建议

- 当需要校验 JSON 输出是否符合契约时召回本卡
- 配套资源：onescience-runtime（运行结果验证）、onescience-coder（代码生成）

## 证据来源

[1] Belefqih S, Barchane M, Zellou A. "Schema validation and evaluation framework for extracted schemas in JSON databases", Scientific Reports, 2026, DOI: 10.1038/s41598-026-45554-6
[2] Viotti J, Mior M. "Blaze: Compiling JSON Schema for 10x Faster Validation", Proceedings of the VLDB Endowment, 2025, DOI: 10.14778/3773749.3773764
[3] Cheong H. "Translating JSON Schema logics into OWL axioms for unified data validation on a digital manufacturing platform", Procedia Manufacturing, 2019, DOI: 10.1016/j.promfg.2018.12.030
[4] Verma U. "Improving Api Test Accuracy through Schema Validation and Real-time Json Assertions in Jenkins Pipelines", International Journal on Science and Technology, 2025, DOI: 10.71097/ijsat.v16.i3.10656
