# JSON Schema报告交付契约方法论

## 适用范围
适用于所有需要生成结构化JSON报告的应用场景，包括数据处理结果、分析报告、系统状态报告、审计报告等。提供JSON Schema验证、报告结构设计、字段约束定义和输出格式标准化。

## 输入
- 报告数据源（数据库、API、文件等）
- JSON Schema定义文件
- 报告模板和格式要求
- 验证规则和约束条件

## 输出
- 符合JSON Schema的结构化报告
- 验证结果（通过/失败）
- 错误详情（如验证失败）
- 报告元数据（生成时间、版本、来源等）

## 流程节点
1. **Schema定义** → 设计JSON Schema，定义必填字段、类型约束、数组结构
2. **数据收集** → 从数据源收集报告所需数据
3. **数据转换** → 将原始数据转换为JSON格式
4. **Schema验证** → 使用JSON Schema验证报告结构
5. **错误处理** → 处理验证失败，生成错误详情
6. **报告生成** → 生成最终JSON报告
7. **元数据添加** → 添加报告元数据（版本、时间戳等）
8. **输出交付** → 将报告写入文件或通过API返回

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Schema版本 | Draft 2020-12 | [JSON Schema官方] | 使用最新的JSON Schema版本 |
| 验证严格度 | strict | [通用实践] | 严格验证所有约束条件 |
| 错误报告详细度 | detailed | [通用实践] | 提供详细的错误位置和描述 |
| 字符编码 | UTF-8 | [通用实践] | 统一使用UTF-8编码 |

### 报告结构规范
| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| task_id | string | 是 | 唯一标识 | 任务唯一标识符 |
| task | string | 是 | 非空 | 任务名称或描述 |
| summary | string | 是 | 非空 | 执行结果摘要 |
| issues | array | 是 | 至少0条 | 问题列表 |
| issues[].failed_check | string | 是 | 非空 | 失败的检查项 |
| issues[].location | string | 是 | 非空 | 问题发生位置 |
| issues[].error_detail | string | 是 | 非空 | 错误详细信息 |
| issues[].capability_attributions | array | 是 | 至少1条 | 能力归因列表 |
| issues[].responsibility_attribution | string | 是 | 非空 | 责任归因 |
| issues[].optimization_plan | array | 是 | 至少1条 | 优化计划列表 |
| timestamp | string | 是 | ISO 8601 | 报告生成时间 |
| version | string | 是 | 语义化版本 | 报告版本号 |

### 验证维度
| 维度 | 描述 | 验证方法 |
|------|------|----------|
| 类型准确性 | 字段类型是否正确 | Schema类型验证 |
| 必填字段 | 必填字段是否存在 | required数组验证 |
| 数组约束 | 数组元素是否符合约束 | items和minItems验证 |
| 字符串约束 | 字符串长度、格式是否符合 | minLength、maxLength、pattern验证 |
| 数值约束 | 数值范围是否符合 | minimum、maximum验证 |
| 对象约束 | 对象属性是否符合 | properties和additionalProperties验证 |

## 边界与分流
- **Schema验证失败**：返回详细错误信息，不生成报告
- **数据源不可用**：返回数据源错误，不执行后续流程
- **字段缺失**：根据策略选择使用默认值或拒绝生成报告
- **类型不匹配**：尝试类型转换或拒绝生成报告
- **数组约束违反**：截断数组或拒绝生成报告

## 质量检查
- 所有报告必须通过JSON Schema验证
- 报告必须包含完整的元数据
- 字段命名必须符合约定（snake_case或camelCase）
- 字符串字段必须处理特殊字符和编码
- 数组字段必须验证元素类型和数量
- 必填字段必须存在且非空

## 回退策略
1. **Schema验证失败回退**：使用宽松Schema或跳过验证
2. **数据源不可用回退**：使用缓存数据或默认值
3. **字段缺失回退**：使用默认值或空值
4. **类型不匹配回退**：尝试类型转换或使用字符串表示
5. **数组约束违反回退**：截断数组或使用空数组

## 资源召回建议
当需要执行以下任务时召回本卡片：
- 生成结构化JSON报告
- 验证JSON数据格式
- 设计数据契约和API接口
- 实现数据质量检查
- 构建自动化报告系统

## 补充证据
[1] Schema validation and evaluation framework for extracted schemas in JSON databases, Scientific Reports, 2026, DOI: 10.1038/s41598-026-45554-6（提供JSON Schema验证框架的详细方法论）

## 证据来源
[1] Schema validation and evaluation framework for extracted schemas in JSON databases, Scientific Reports, 2026, DOI: 10.1038/s41598-026-45554-6
[2] 基于JSON Schema官方规范和最佳实践