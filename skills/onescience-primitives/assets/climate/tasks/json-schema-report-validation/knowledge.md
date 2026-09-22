# JSON Schema 报告交付契约

## 适用范围
适用于科研报告、归因分析报告、实验结果报告等结构化报告的交付校验。触发场景：报告生成后需确保字段完整、类型正确、结构合规，避免因缺失字段、类型错误或格式不匹配导致下游流程失败。

## 输入
- 报告数据（JSON格式）
- JSON Schema 定义文件（规定必填字段、数据类型、数组约束、嵌套结构）
- 任务身份信息（task_id、task名称）

## 输出
- 校验通过的JSON报告
- 校验错误详情（缺失字段、类型错误、结构不匹配）
- 校验状态码（0=成功，1=失败）

## 流程节点

1. **Schema加载** → 加载JSON Schema定义文件，解析版本（draft-04/draft-07/2020-12）
2. **必填字段校验** → 检查required数组中的字段是否全部存在
3. **任务身份校验** → 验证task_id和task字段与任务索引一致
4. **数据类型校验** → 检查每个字段的数据类型（string/number/integer/boolean/array/object）
5. **数组约束校验** → 验证数组字段的minItems/maxItems/items类型
6. **结构合规校验** → 检查嵌套对象的属性定义和additionalProperties约束
7. **输出生成** → 生成校验通过的报告或错误详情

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| required字段 | 全部存在 | [1] | 缺失required字段将导致校验失败 |
| 数据类型 | 符合type定义 | [1] | 类型不匹配（如字符串赋值给数字字段）将报错 |
| 数组约束 | 遵循minItems/maxItems | [1] | 数组长度超出范围将报错 |
| 任务身份 | task_id与索引一致 | 归因报告 | 报告中的task_id必须与任务编号匹配 |
| 任务名称 | task与任务name一致 | 归因报告 | 报告中的task字段必须与任务名称匹配 |

### 校准数值
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| JSON Schema版本 | draft-04/draft-07/2020-12 | [1] | 不同版本的关键字支持有差异 |
| 必填字段列表 | 根据具体报告Schema定义 | 归因报告 | 典型必填字段：task_id, task, summary, issues |
| issues字段类型 | 数组 | 归因报告 | issues必须是数组类型，不能为空 |
| summary字段类型 | 非空字符串 | 归因报告 | summary必须是非空字符串 |

## 边界与分流
- Schema文件不存在或无法解析 → 回退到基础字段校验（仅检查必填字段）
- Schema版本不支持某些关键字 → 跳过该关键字校验，记录警告
- 任务身份信息缺失 → 使用默认身份校验规则，记录告警
- JSON格式错误 → 直接报错，终止校验流程

## 质量检查
- 校验错误数量 = 0 时报告校验通过
- 校验错误数量 > 0 时报告校验失败，返回详细错误列表
- 校验耗时监控：单次校验应在100ms内完成（针对<1MB的报告）

## 回退策略
- Schema校验失败时，可回退到基础字段检查（仅验证必填字段存在性和类型）
- 任务身份校验失败时，可跳过身份校验，仅验证报告结构完整性

## 资源召回建议
- 何时应召回本卡片：当需要生成或校验JSON格式的科研报告时
- 配套资源：JSON Schema定义文件、报告模板、任务身份配置

## 补充证据
[D1] Adamant: a JSON schema-based metadata editor for research data management workflows, F1000Research, 2022, URL: https://doi.org/10.12688/f1000research.110875.2（交叉验证）
[D2] Schema validation and evaluation framework for extracted schemas in JSON databases, Scientific Reports, 2026, URL: https://doi.org/10.1038/s41598-026-45554-6（交叉验证）
[D3] Blaze: Compiling JSON Schema for 10x Faster Validation, Proceedings of the VLDB Endowment, 2025, URL: https://doi.org/10.14778/3773749.3773764（交叉验证）

## 证据来源
[1] Adamant: a JSON schema-based metadata editor for research data management workflows, Chaerony Siffa I, Schäfer J, Becker MM, F1000Research, 2022, DOI: 10.12688/f1000research.110875.2
[2] Schema validation and evaluation framework for extracted schemas in JSON databases, Belefqih S, Barchane M, Zellou A, Scientific Reports, 2026, DOI: 10.1038/s41598-026-45554-6
[3] Blaze: Compiling JSON Schema for 10x Faster Validation, Viotti JC, Mior MJ, Proceedings of the VLDB Endowment, 2025, DOI: 10.14778/3773749.3773764