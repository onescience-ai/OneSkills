# JSON Schema 报告交付契约

## 适用范围
面向 JSON 数据结构化输出场景，提供 JSON Schema 报告交付契约规范。适用于任何需要生成符合 JSON Schema 规范的报告、确保报告可解析且与任务身份一致的自动化系统、CI/CD 流水线或数据交换场景。

## 输入
- JSON Schema 定义文件（描述报告结构）
- 待验证的 JSON 报告文档
- 任务身份信息（task_id、task name）
- 校验配置（严格模式/宽松模式）

## 输出
- 校验结果（通过/失败）
- 错误详情（缺失字段、类型不匹配、约束违反）
- 修复建议（如何使报告符合契约）
- 校验报告（结构化输出，可用于后续处理）

## 流程节点
1. Schema 加载 → 读取并解析 JSON Schema 定义
2. 报告加载 → 读取待验证的 JSON 报告文档
3. 结构校验 → 检查必填字段、数据类型、数组约束
4. 身份校验 → 验证 task_id、task name 与任务索引一致性
5. 格式校验 → 检查输出格式、字段命名规范
6. 结果生成 → 生成校验报告和修复建议

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 必填字段校验 | 严格 | [D1] | 所有标记为 "required" 的字段必须存在 |
| 类型校验 | 严格 | [D1] | 字段值必须符合 Schema 定义的类型 |
| 数组约束 | 严格 | [D1] | 数组长度、唯一性等约束必须满足 |
| 身份一致性 | 严格 | [D2] | task_id 和 task name 必须与任务索引匹配 |
| 输出格式 | JSON | [D1] | 报告必须是有效的 JSON 格式 |

### 校准数值
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| JSON 编码 | UTF-8 | [D1] | JSON 文档应使用 UTF-8 编码 |
| Schema 版本 | draft-2020-12 | [D1] | 推荐使用最新的 Schema 草案版本 |

## 边界与分流
- **Schema 加载失败**：报告 Schema 文件不存在或格式错误，无法进行校验
- **报告解析失败**：JSON 报告文档格式错误，无法解析
- **结构校验失败**：报告缺少必填字段或字段类型不匹配
- **身份校验失败**：task_id 或 task name 与任务索引不一致
- **格式校验失败**：输出格式不符合约定（如缺少 summary、issues 字段）

## 质量检查
- 验证 JSON Schema 本身是否符合 Meta-Schema 规范
- 检查报告文档是否可被标准 JSON 解析器解析
- 确认所有必填字段都存在且类型正确
- 验证 task_id 和 task name 与任务索引一致
- 检查数组字段是否满足长度和唯一性约束

## 回退策略
- Schema 加载失败时：使用默认 Schema 或报告人工干预
- 报告解析失败时：尝试修复 JSON 格式或报告解析错误
- 校验失败时：生成详细的错误报告和修复建议
- 身份不一致时：标记为待确认，等待人工核实

## 资源召回建议
- 当需要生成符合 JSON Schema 规范的报告时召回本卡片
- 当遇到 JSON 报告校验失败时参考
- 当需要设计结构化输出契约时使用
- 配套资源：CLI 非交互执行与故障分类知识（用于处理 CLI 执行异常）

## 补充证据（开源文档）
[D1] JSON Schema: A Media Type for Describing JSON Documents, Internet Engineering Task Force (IETF), draft-bhutton-json-schema-01, URL: https://json-schema.org/draft/2020-12/json-schema-core（accessed 2026-09-21，权威标准）
[D2] JSON Schema Validation: A Vocabulary for Structural Validation of JSON, Internet Engineering Task Force (IETF), draft-bhutton-json-schema-validation-01, URL: https://json-schema.org/draft/2020-12/json-schema-validation（accessed 2026-09-21，权威标准）

## 证据来源
无论文证据，仅基于权威文档。