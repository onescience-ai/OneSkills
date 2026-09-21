# JSON Schema报告交付契约

## 适用范围
适用于自动化系统间结构化报告的定义、生成与验证。覆盖必填字段声明、类型约束、嵌套结构规范、任务身份匹配及输出格式校验等核心环节，确保报告可被下游消费方正确解析。

## 输入
- JSON Schema定义文件（.schema.json）
- 待验证的报告JSON数据
- 任务上下文（task_id、task_name等身份信息）

## 输出
- 验证结果（valid/invalid）
- 错误详情（字段路径、违规类型、预期值）
- 修正建议

## 流程节点

### 1. Schema加载与解析
- **操作**：读取JSON Schema文件，构建验证器实例
- **参数**：Schema路径、格式版本（Draft-07/2020-12）
- **工具**：jsonschema库（Python）、ajv（JavaScript）
- **质量门禁**：Schema本身必须是合法JSON，通过meta-schema校验

### 2. 必填字段检查
- **操作**：遍历required数组，验证每个字段存在性
- **参数**：required字段列表、嵌套路径
- **工具**：Validator.validate()
- **质量门禁**：所有required字段必须存在且非null

### 3. 类型约束验证
- **操作**：根据type字段验证值类型
- **参数**：type声明（string/number/integer/boolean/array/object/null）
- **工具**：type-aware validator
- **质量门禁**：类型不匹配时返回精确错误位置

### 4. 嵌套结构递归验证
- **操作**：对object/array类型递归应用子Schema
- **参数**：properties/items定义、additionalProperties约束
- **工具**：递归validator
- **质量门禁**：嵌套深度不超过预设限制（防栈溢出）

### 5. 任务身份匹配校验
- **操作**：验证报告中的task_id/task与任务索引一致
- **参数**：任务身份字段、匹配规则（精确/模糊）
- **工具**：自定义校验函数
- **质量门禁**：task_id必须为字符串，task必须非空

### 6. 自定义约束应用
- **操作**：执行pattern/enum/minimum/maximum等约束
- **参数**：正则表达式、枚举值列表、数值范围
- **工具**：组合validator
- **质量门禁**：约束冲突检测（如minimum > maximum）

## 关键参数

### 通用判据（方法层）
| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| required字段 | 必须声明 | [D1] | 每个报告必须定义核心身份字段 |
| type声明 | 显式声明 | [D1] | 避免隐式类型推断导致歧义 |
| additionalProperties | false | [D1] | 防止未知字段污染 |
| 嵌套深度限制 | ≤10层 | [D2] | 防止恶意/错误嵌套导致栈溢出 |
| Type Conformance | 0-1分 | [1] | 类型一致性：推断类型与观测类型的重叠度 |
| Presence Accuracy | 0-1分 | [1] | 字段存在准确性：必填/可选字段判定正确率 |
| Union Conformance | 0-1分 | [1] | 联合类型一致性：多类型支持的覆盖率 |
| Depth Conformance | 0-1分 | [1] | 深度一致性：嵌套结构的层级匹配度 |
| Homogeneity | 0-1分 | [1] | 同质性：数组元素类型的一致性程度 |

### SVEF验证框架维度（新增）
| 维度 | 指标 | 计算方式 | 来源 | 说明 |
|------|------|----------|------|------|
| Data Type Accuracy (DTA) | Type Conformance均值 | 各属性类型一致性算术平均 | [1] | 评估基本类型推断准确性 |
| Required/Optional Fields | Presence Accuracy + 依赖规则 | 必填字段正确率 + 关联规则挖掘 | [1] | 评估字段存在性和依赖关系 |
| Multiple Type Support (MTS) | Union Conformance | 多类型字段的类型覆盖率 | [1] | 评估异构类型支持能力 |
| Collection Structure Consistency (CSC) | Depth + Homogeneity | 深度一致性与同质性加权组合 | [1] | 评估数组结构完整性 |
| Entity Relationships Recovery (ERR) | F1 + GED_norm | 边级别精确率/召回率与图编辑距离 | [1] | 评估实体关系恢复能力 |
| Temporal Evolution Detection | 版本差异检测 | 时间戳版本的结构演化识别 | [1] | 评估Schema演化追踪能力 |

### 标准报告字段模板
| 字段名 | 类型 | required | 说明 |
|--------|------|----------|------|
| task_id | string | true | 任务唯一标识符 |
| task | string | true | 任务名称/描述 |
| summary | string | true | 执行摘要（非空） |
| issues | array | true | 问题列表（数组类型） |
| timestamp | string | false | ISO 8601时间戳 |
| version | string | false | 报告版本号 |

### 常见违规模式与修复
| 违规类型 | 错误示例 | 修复方法 |
|----------|----------|----------|
| 缺少required字段 | 缺少issues字段 | 添加issues: [] |
| 类型不匹配 | summary: null | 改为summary: "描述" |
| 数组约束违反 | issues: "string" | 改为issues: [] |
| 任务身份不一致 | task_id与索引不匹配 | 校正task_id值 |

## 边界与分流

### Schema版本分流
- Draft-07：使用旧版validator，不支持if/then/else
- 2020-12：使用新版validator，支持动态引用
- 混合版本：统一升级到最新稳定版

### 验证失败分流
- 结构性错误（缺字段）：阻断执行，要求修复
- 格式性错误（类型不匹配）：警告但允许执行
- 语义性错误（值域越界）：根据业务规则决定

### 性能边界分流
- 小报告(<1KB)：实时同步验证
- 大报告(>1MB)：异步批量验证
- 流式报告：增量验证，边生成边校验

## 质量检查
- Schema本身通过meta-schema校验
- 所有required字段存在且类型正确
- 嵌套结构符合depth限制
- 任务身份字段匹配任务索引

## 回退策略
- Schema缺失：使用默认最小Schema（仅校验task_id+issues）
- 验证器不可用：降级到正则表达式模式匹配
- 性能瓶颈：采样验证（10%样本）+ 异步全量验证

## 资源召回建议
- 当需要定义结构化报告格式时召回本卡
- 配合`general-cli-execution-fault-diagnosis`验证CLI输出
- 适用于API响应校验、日志格式验证、数据管道Schema

## 补充证据（权威文档）
[D1] JSON Schema Official Specification, JSON Schema Organization, Draft 2020-12, https://json-schema.org/draft/2020-12/json-schema-core (accessed_at: 2026-09-21, 交叉验证)
[D2] Understanding JSON Schema, json-schema.org, 2024, https://json-schema.org/understanding-json-schema/ (accessed_at: 2026-09-21, 交叉验证)

## 证据来源
[1] Schema validation and evaluation framework for extracted schemas in JSON databases, Scientific Reports, 2026, DOI: 10.1038/s41598-026-45554-6（新增）
[2] JSON Schema Official Specification, JSON Schema Organization, Draft 2020-12（交叉验证）
[3] Understanding JSON Schema, json-schema.org, 2024（交叉验证）
