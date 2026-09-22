# JSON Schema Report Delivery Contract

## 适用范围
适用于任何需要通过JSON格式交付结构化报告并确保其符合预定义模式的场景，包括科学计算结果、数据分析报告、系统日志等。不适用于非结构化文本或二进制数据。

## 输入
- JSON Schema定义（必填字段、数据类型、约束条件）
- 待验证的JSON报告数据
- 任务身份信息（task_id, task_name）

## 输出
- 验证结果（通过/失败，失败时提供错误详情）
- 符合Schema的标准化JSON报告
- 元数据完整性检查报告

## 流程节点
1. **Schema加载** → 读取JSON Schema定义，解析必填字段与约束。
2. **数据验证** → 将JSON报告与Schema比对，检查类型、格式、枚举值等。
3. **任务身份校验** → 确认报告中的task_id与任务索引一致，task与任务name匹配。
4. **数组约束检查** → 验证数组字段（如issues）是否为数组类型且非空（若要求）。
5. **错误处理** → 若验证失败，返回具体错误位置与原因。
6. **标准化输出** → 生成符合Schema的最终报告。

## 关键参数
### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 必填字段 | task_id, task, summary, issues | [D1] | 顶层字段必须存在 |
| 任务身份一致性 | task_id与任务索引匹配 | [2] | 防止报告错配 |
| 数组约束 | issues必须为数组 | [D1] | 即使为空也需保留数组结构 |
| 非空字符串 | summary必须是非空字符串 | [2] | 提供有效摘要 |

### 校准数值
以下数值来自JSON Schema验证框架案例，供量级校准；其他体系需以自身证据重新锚定。
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Schema版本 | Draft 2020-12 | [D1] | 支持最新特性 |
| 验证超时 | 5秒 | [2] | 避免大报告验证阻塞 |

## 边界与分流
- 若Schema缺失，使用默认宽松模式（仅检查JSON语法）。
- 若报告包含额外字段，根据策略决定：忽略（宽松）或报错（严格）。
- 若验证超时，记录警告并继续交付（降级策略）。

## 质量检查
- 验证Schema是否为有效JSON。
- 检查报告是否可解析为JSON。
- 确保所有必填字段存在且类型正确。

## 回退策略
- 若验证失败，提供修复建议（如缺失字段、类型错误）。
- 支持手动覆盖验证（紧急情况）。

## 资源召回建议
当任务涉及JSON报告生成、结构化输出或数据契约时召回本卡片。配套资源包括：CLI故障分类卡片。

## 补充证据（开源文档/用户自有，可选）
[D1] JSON Schema Official Specification, JSON Schema Organization, 2020-12, URL: https://json-schema.org/（accessed_at 2026-09-21，交叉验证）

## 证据来源
[1] PG-Schema: Schemas for Property Graphs, Renzo Angles et al., Proceedings of the ACM on Management of Data, 2023, DOI: 10.1145/3589778
[2] Schema validation and evaluation framework for extracted schemas in JSON databases, Scientific Reports, 2026, DOI: 10.1038/s41598-024-79151-2