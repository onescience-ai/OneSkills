# 生物信息学 JSON Schema 报告交付契约

## 适用范围
适用于生物信息学分析任务的结构化报告生成与验证，确保报告符合预定义的 JSON Schema 契约，包含必填字段、任务身份验证、数组约束和输出格式规范。不适用于非结构化文本报告或二进制输出格式。

## 输入
- 分析结果数据（JSON 格式）
- 任务元数据（任务 ID、名称、执行时间、输入参数）
- 评估指标（准确率、召回率、F1 值等）
- 验证数据（独立测试集结果、交叉验证结果）

## 输出
- 结构化报告（JSON 格式）
- 验证结果（通过/失败及详细错误信息）
- 元数据（生成时间、Schema 版本、验证器版本）

## 流程节点

### 1. Schema 定义
- 定义报告的 JSON Schema 结构
- 指定必填字段（如 task_id、task_name、status、results）
- 定义数组约束（如 results 数组的最小/最大长度）
- **质量门禁**：Schema 必须通过 JSON Schema 验证器自身验证

### 2. 报告生成
- 按 Schema 结构填充报告内容
- 验证字段类型（字符串、数字、布尔、数组、对象）
- 处理嵌套结构（如 results[].metrics[].value）
- **质量门禁**：报告必须通过 JSON Schema 验证

### 3. 任务身份验证
- 验证 task_id 与当前任务一致
- 验证 task_name 与任务描述匹配
- 验证 execution_time 在合理范围内
- **质量门禁**：身份验证失败时拒绝报告

### 4. 数组约束验证
- 验证数组长度在指定范围内
- 验证数组元素类型一致
- 验证数组元素顺序（如需）
- **质量门禁**：数组约束违规时记录警告

### 5. 输出格式验证
- 验证 JSON 语法正确性
- 验证字段名符合命名约定
- 验证数值精度（如浮点数位数）
- **质量门禁**：格式验证失败时拒绝报告

### 6. 报告交付
- 写入报告文件（如 report.json）
- 生成验证日志
- 更新任务状态（如 COMPLETED、FAILED）
- **质量门禁**：交付成功后记录审计信息

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Schema 版本 | Draft 2020-12 | [论文2] | 支持最新特性 |
| 必填字段 | task_id, task_name, status, results | [论文1] | 基础元数据 |
| 数组最小长度 | 0 | [论文1] | 允许空结果 |
| 数组最大长度 | 1000 | [论文1] | 防止内存溢出 |
| JSON 缩进 | 2 空格 | [论文3] | 可读性优先 |

### 校准数值
以下数值来自 Adamant 和 FAIR 数据站，供量级校准；其他体系需以自身证据重新锚定：
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 验证超时 | 30s | [论文3] | 大型报告可能需要更长时间 |
| 最大嵌套深度 | 10 层 | [论文1] | 防止递归过深 |
| 字符串最大长度 | 10000 字符 | [论文3] | 防止内存溢出 |
| 数值精度 | 6 位小数 | [论文4] | 浮点数标准化 |

## 边界与分流
- **Schema 缺失**：使用默认 Schema 或拒绝报告
- **必填字段缺失**：拒绝报告并记录缺失字段
- **类型不匹配**：尝试类型转换，失败则拒绝报告
- **数组约束违规**：记录警告但不拒绝（除非严重违规）
- **JSON 语法错误**：拒绝报告并记录语法错误位置

## 质量检查
- Schema 验证：使用 JSON Schema 验证器（如 jsonschema）
- 任务身份：验证 task_id 和 task_name 一致性
- 数组约束：验证长度和元素类型
- 输出格式：验证 JSON 语法和字段命名
- 审计日志：记录所有验证操作和结果

## 回退策略
- Schema 验证失败：使用更宽松的 Schema 或人工审核
- 必填字段缺失：从上下文推断或询问用户
- 类型不匹配：使用默认值或拒绝报告
- JSON 语法错误：修复语法错误后重新生成

## 资源召回建议
- 当任务需要生成结构化报告时召回本卡
- 当需要验证报告符合预定义契约时召回本卡
- 当需要确保报告的可追溯性和可复现性时召回本卡
- 配套资源：bio-cli-pipeline-non-interactive-execution-failure-classification（CLI 执行知识）

## 证据来源
[1] Schema validation and evaluation framework for extracted schemas in JSON databases, Belefqih et al., Scientific Reports, 2026, DOI: 10.1038/s41598-026-45554-6
[2] Validation of Modern JSON Schema: Formalization and Complexity, Proceedings of the ACM on Programming Languages, 2024, DOI: 10.1145/3649506
[3] Adamant: a JSON schema-based metadata editor for research data management workflows, F1000Research, 2022, DOI: 10.12688/f1000research.125545.2
[4] FAIR data station for lightweight metadata management and validation of omics studies, GigaScience, 2022, DOI: 10.1093/gigascience/giad015
