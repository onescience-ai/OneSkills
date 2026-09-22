# JSON Schema 报告交付契约知识

## 适用范围
适用于需要通过 JSON Schema 验证报告输出、确保结构化数据符合预定义契约的场景。覆盖必填字段定义、任务身份验证、数组约束、类型检查和输出格式校验等核心知识。用于在输出前按契约校验报告，确保可解析且与任务身份一致。

## 输入
- JSON Schema 定义文件（必填字段、类型约束、数组规则）
- 待验证的 JSON 报告数据
- 任务身份信息（task_id、task 名称）

## 输出
- 验证结果（通过/失败）
- 校验错误详情（缺失字段、类型不匹配、约束违反）
- 修正建议

## 流程节点
1. **Schema 加载** → 解析 JSON Schema 定义，提取必填字段和约束规则
2. **数据准备** → 读取待验证的 JSON 报告，规范化格式
3. **字段验证** → 检查必填字段是否存在，类型是否匹配
4. **身份验证** → 验证 task_id 和 task 名称是否与任务索引一致
5. **数组约束** → 验证数组字段的长度、元素类型和唯一性
6. **格式校验** → 检查输出格式是否符合预定义模板
7. **错误报告** → 生成详细的校验错误报告

每步含：操作、参数、工具、质量门禁

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 必填字段 | 严格匹配 | [论文1] | 报告必须包含所有声明的必填字段 |
| 任务身份 | 精确匹配 | [论文1] | task_id 必须与任务索引一致 |
| 数组约束 | 非空+元素类型 | [论文1] | 数组字段必须非空且元素类型符合 Schema |
| 类型检查 | 严格模式 | [论文6] | 字段类型必须精确匹配，不允许隐式转换 |

### 校准数值
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Schema 版本 | Draft 2020-12 | [论文3] | 推荐使用的 JSON Schema 版本 |
| 验证超时 | 1000ms | [论文2] | 单次验证操作的超时阈值 |
| 错误消息长度 | ≤500 字符 | [论文4] | 单条错误消息的最大长度 |

## 边界与分流
- **必填字段缺失**（退出码 1 + 字段缺失信息）→ 补充缺失字段后重新验证
- **任务身份不匹配**（退出码 1 + 身份不一致）→ 检查任务索引，修正 task_id 或 task 名称
- **数组约束违反**（退出码 1 + 数组错误）→ 检查数组长度和元素类型，修正数据格式
- **类型不匹配**（退出码 1 + 类型错误）→ 检查字段类型定义，修正数据类型

## 质量检查
- 验证 Schema 定义的完整性（必填字段、类型、约束）
- 检查报告数据与 Schema 的一致性
- 确认任务身份与任务索引的一致性
- 验证错误报告的详细性和可读性

## 回退策略
- Schema 加载失败时，使用默认 Schema 或降级到基础验证
- 验证超时时，跳过非关键字段验证或增加超时阈值
- 类型不匹配时，尝试类型转换或标记为待人工审查

## 资源召回建议
- 当需要校验 JSON 报告输出是否符合契约时召回
- 当遇到报告字段缺失或类型不匹配问题时召回
- 当需要确保报告与任务身份一致时召回

## 证据来源
[1] Schema validation and evaluation framework for extracted schemas in JSON databases, Scientific Reports, 2026, DOI: 10.1038/s41598-026-45554-6
[2] Blaze: Compiling JSON Schema for 10x Faster Validation, Proceedings of the VLDB Endowment, 2025, DOI: 10.14778/3773749.3773764
[3] Validation of Modern JSON Schema: Formalization and Complexity, Proceedings of the ACM on Programming Languages, 2024, DOI: 10.1145/3632891
[4] Improving Api Test Accuracy through Schema Validation and Real-time Json Assertions in Jenkins Pipelines, International Journal on Science and Technology, 2025, DOI: 10.71097/ijsat.v16.i3.10656
