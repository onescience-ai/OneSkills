# JSON Schema 报告交付契约

## 适用范围
面向JSON格式的结构化报告输出场景，定义报告交付契约的Schema规范，确保输出可解析、可校验、与任务身份一致。适用于自动化系统、API响应、日志记录、数据交换等需要结构化输出的场景，覆盖必填字段定义、类型约束、数组格式、嵌套对象结构及验证标准。

## 输入
- 任务标识信息（task_id、task_name）
- 报告内容数据
- 输出格式要求（JSON Schema版本）
- 验证规则配置（可选）

## 输出
- 符合Schema规范的JSON报告
- 验证结果（通过/失败）
- 验证错误详情（若失败）

## 流程节点
1. Schema定义 → 2. 数据填充 → 3. 格式验证 → 4. 内容校验 → 5. 输出生成 → 6. 交付确认

### 步骤详解

**步骤1：Schema定义**
- 操作：定义JSON Schema，包括必填字段、字段类型、约束条件
- 参数：Schema版本、字段规范
- 工具：JSON Schema定义器
- 质量门禁：Schema符合JSON Schema规范，包含所有必要字段

**步骤2：数据填充**
- 操作：将任务数据映射到Schema字段，处理默认值和可选字段
- 参数：任务数据、Schema映射规则
- 工具：数据映射器
- 质量门禁：所有必填字段有值，数据类型匹配

**步骤3：格式验证**
- 操作：验证JSON格式正确性，检查语法错误
- 参数：JSON字符串、Schema定义
- 工具：JSON解析器、Schema验证器
- 质量门禁：JSON可解析，无语法错误

**步骤4：内容校验**
- 操作：根据Schema校验字段值、约束条件、业务规则
- 参数：JSON数据、Schema规则、业务规则
- 工具：Schema验证器、业务规则引擎
- 质量门禁：所有校验规则通过

**步骤5：输出生成**
- 操作：格式化JSON输出，设置编码和缩进
- 参数：验证后的JSON数据、输出配置
- 工具：JSON序列化器
- 质量门禁：输出格式规范，编码正确

**步骤6：交付确认**
- 操作：确认输出可被下游系统解析，记录交付状态
- 参数：输出文件/流、交付目标
- 工具：交付验证器
- 质量门禁：交付成功，下游系统确认接收

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 必填字段检查 | 100%覆盖 | [1] | 所有Schema定义的required字段必须存在 |
| 类型约束 | 严格匹配 | [1] | 字段值必须符合Schema定义的type |
| 数组格式 | 至少1项 | [1] | 数组类型字段不能为空（若Schema要求） |
| 嵌套对象 | 完整结构 | [1] | 嵌套对象必须包含其Schema定义的所有必填字段 |
| 字符串长度 | 符合min/max | [1] | 字符串字段必须满足长度约束 |
| 数值范围 | 符合minimum/maximum | [1] | 数值字段必须在定义范围内 |

### 校准数值
以下数值来自特定报告交付场景，供量级校准；其他场景需以自身证据重新锚定：
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Schema版本 | Draft 2020-12 | [1] | 使用最新稳定版本 |
| 最大嵌套深度 | 5层 | [2] | 防止过深嵌套影响性能 |
| 最大数组长度 | 1000项 | [2] | 防止过大数组影响解析性能 |
| 字符串最大长度 | 10000字符 | [2] | 防止过长字符串影响存储 |

## 边界与分流
- **前提1：Schema定义有效** → 若Schema无效，转向Schema修复流程
- **前提2：输入数据可序列化** → 若数据包含不可序列化类型，转向数据转换流程
- **前提3：验证器可用** → 若验证器不可用，转向降级验证（仅格式检查）
- **前提4：下游系统兼容** → 若下游系统不兼容当前Schema版本，转向版本转换流程

## 质量检查
- 验证点1：JSON格式正确，可被标准解析器解析
- 验证点2：所有必填字段存在且类型正确
- 验证点3：业务规则校验通过
- 验证点4：输出编码正确，无乱码
- 失败处理：若检查失败，记录详细错误信息，触发修复流程

## 回退策略
- 降级验证：若Schema验证器不可用，仅执行格式检查
- 手动修复：若自动修复失败，触发人工干预
- 版本回退：若新版本Schema不兼容，回退到旧版本验证
- 部分交付：若部分字段验证失败，交付已验证部分并标注未验证字段

## 资源召回建议
- 何时应召回本卡片：当需要设计或验证JSON格式的结构化报告输出时
- 配套资源：
  - general-cli-fault-classification-troubleshooting：用于CLI输出结果的结构化验证
  - 具体领域报告模板卡片：提供特定领域的报告格式规范

## 证据来源
[1] Validation of Modern JSON Schema: Formalization and Complexity, Attouche et al., Proceedings of the ACM on Programming Languages, 2024, DOI: 10.1145/3632891
[2] Think Inside the JSON: Reinforcement Strategy for Strict LLM Schema Adherence, Agarwal et al., arXiv, 2025, DOI: 10.48550/arXiv.2502.14905
[3] PARSE: LLM Driven Schema Optimization for Reliable Entity Extraction, Shrimal et al., EMNLP Industry, 2025, DOI: 10.18653/v1/2025.emnlp-industry.184
[4] Blaze: Compiling JSON Schema for 10x Faster Validation, Viotti & Mior, Proceedings of the VLDB Endowment, 2025, DOI: 10.14778/3773749.3773764