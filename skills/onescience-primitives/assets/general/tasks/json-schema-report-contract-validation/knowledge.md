# JSON Schema 报告交付契约校验

## 适用范围
适用于 CLI 工具或自动化流水线以 JSON 格式交付结构化报告时，使用 JSON Schema 对报告内容进行校验的场景。覆盖必填字段检查、字段类型校验、数组约束验证、任务身份匹配（task_id/task 名称一致性）以及输出格式合规性判定。

## 输入
- 待校验的 JSON 报告文件
- JSON Schema 定义文件（report-schema.json 或内联 schema）
- 任务元数据（task_id、task 名称）

## 输出
- 校验通过/失败判定
- 违规字段列表与错误详情
- 修复建议

## 流程节点
1. **Schema 加载** → 加载并解析 JSON Schema 定义
2. **报告解析** → 读取待校验 JSON 文件
3. **结构校验** → 验证顶层字段存在性（required 关键字）
4. **类型校验** → 验证字段类型（type 关键字）
5. **身份匹配** → 校验 task_id 和 task 字段与预期一致
6. **数组约束** → 验证数组字段的 minItems/maxItems/items 约束
7. **额外字段检测** → 识别未在 schema 中定义的额外顶层字段
8. **结果输出** → 生成结构化校验报告

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| required 关键字 | 字符串数组 | [D1] JSON Schema 规范 | 定义对象中必须存在的属性名 |
| type 关键字 | 字符串或字符串数组 | [D1] JSON Schema 规范 | 定义属性的数据类型 |
| additionalProperties | 布尔或对象 | [D1] JSON Schema 规范 | 控制是否允许未定义的额外属性 |
| minItems | 整数 | [D1] JSON Schema 规范 | 数组最小元素数 |
| maxItems | 整数 | [D1] JSON Schema 规范 | 数组最大元素数 |
| Presence Accuracy | 1/|P| * Σ 1[R_p^inf = R_p^ref] | [1] SVEF 框架 | 必填/可选字段判定准确率 |
| Data Type Accuracy | 1/|P| * Σ Type_Conformance(p) | [1] SVEF 框架 | 数据类型推断准确率 |

## 边界与分流
- 顶层缺少 required 字段 → 校验失败，报告"缺失必填字段: [字段名]"
- 存在额外顶层字段 → 警告级（非阻塞），记录多余字段名
- task_id 不匹配 → 校验失败，报告"任务身份不一致"
- task 名称不匹配 → 校验失败，报告"任务名称不一致"
- issues 字段非数组 → 校验失败，报告"issues 必须是数组类型"
- summary 为空字符串 → 校验失败，报告"summary 必须是非空字符串"
- JSON 语法错误 → 校验失败，报告"JSON 解析失败"

## 质量检查
- 校验前需验证 JSON 语法正确性
- required 字段校验必须严格匹配（不允许缺失）
- 类型校验需区分 integer/number/string/boolean/array/object/null
- 任务身份匹配需同时校验 task_id 和 task 字段
- 校验结果需包含具体违规位置和修复建议

## 回退策略
- Schema 文件不存在时，使用内置最小 required 校验
- JSON 解析失败时，检查文件编码（UTF-8）和语法
- 类型校验不确定时，报告为警告而非错误

## 资源召回建议
- 当任务涉及结构化报告生成、CLI 输出校验、自动化流水线结果验证时召回本卡
- 配套资源：cli-fault-classification-diagnostic（CLI 故障诊断）

## 补充证据（权威文档）
[D1] JSON Schema Reference - Type-specific Keywords, JSON Schema Organization, Draft 2020-12, https://json-schema.org/understanding-json-schema/reference/type（accessed_at 2026-09-22，交叉验证：与论文 [1][2] 中 type/required 语义一致）

## 证据来源
[1] Validation of Modern JSON Schema: Formalization and Complexity, Attouche et al., Proceedings of the ACM on Programming Languages, 2024, DOI: 10.1145/3632891
[2] Schema validation and evaluation framework for extracted schemas in JSON databases, Belefqih et al., Scientific Reports, 2026, DOI: 10.1038/s41598-026-45554-6
[3] Blaze: Compiling JSON Schema for 10x Faster Validation, Viotti & Mior, Proceedings of the VLDB Endowment, 2025, DOI: 10.14778/3773749.3773764
[4] Improving Api Test Accuracy through Schema Validation and Real-time Json Assertions in Jenkins Pipelines, Verma, International Journal on Science and Technology, 2025, DOI: 10.71097/ijsat.v16.i3.10656
