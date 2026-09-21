# JSON Schema报告交付契约

## 适用范围
适用于验证JSON格式报告是否符合预定义的Schema契约，确保报告可解析且包含所有必填字段。用于诊断报告校验错误、字段缺失或类型不匹配等问题。

## 输入
- JSON报告文件（如report.json）
- JSON Schema定义文件（如report-schema.json）
- 任务身份信息（task_id、task名称）

## 输出
- 验证结果（通过/失败）
- 详细错误信息（缺失字段、类型错误、约束违反）
- 修复建议（如何调整报告以满足Schema要求）

## 流程节点
1. **Schema加载** → 解析JSON Schema定义，识别必填字段和约束
2. **报告解析** → 读取并解析JSON报告文件
3. **字段完整性检查** → 验证所有必填字段是否存在
4. **类型与格式检查** → 验证字段值是否符合Schema定义的类型和格式
5. **任务身份校验** → 验证task_id和task名称是否与任务索引一致
6. **数组约束检查** → 验证数组字段是否符合最小/最大长度约束
7. **额外字段检测** → 检查是否包含Schema未定义的额外字段

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 必填字段 | 根据Schema定义 | Schema文件 | 报告必须包含的所有字段 |
| 类型约束 | string/number/array/object等 | Schema文件 | 字段值的类型要求 |
| 数组最小长度 | 根据Schema定义 | Schema文件 | 数组字段的最小元素数 |
| 任务身份字段 | task_id, task | 任务规范 | 必须与任务索引一致 |
| 额外字段策略 | 允许/禁止 | Schema定义 | 是否允许未定义字段 |

## 边界与分流
- **字段缺失**：添加缺失字段到报告中
- **类型错误**：修正字段值类型以符合Schema定义
- **任务身份不匹配**：更新task_id和task名称以匹配任务索引
- **数组约束违反**：调整数组长度以满足最小/最大约束
- **额外字段**：移除Schema未定义的额外字段或更新Schema以包含它们

## 质量检查
- 使用标准JSON Schema验证器进行验证
- 确保所有必填字段都存在且类型正确
- 验证任务身份信息与任务索引一致
- 检查数组约束是否满足

## 回退策略
- 如果Schema文件缺失或损坏，从备份恢复或重新生成
- 如果验证器不可用，手动检查关键字段和约束
- 如果问题持续，记录详细错误信息并联系Schema维护者

## 资源召回建议
- 当遇到JSON报告校验错误时召回本卡片
- 配合具体任务领域的知识卡片使用（如MOF、CO2捕集等）

## 证据来源
[1] Schema validation and evaluation framework for extracted schemas in JSON databases, Scientific Reports, 2026, DOI: 10.1038/s41598-026-45554-6
[2] AI-assisted JSON Schema Creation and Mapping, 2025 ACM/IEEE 28th International Conference on Model Driven Engineering Languages and Systems, 2025, DOI: 10.1109/MODELS-C68889.2025.00019
[3] Streaming Validation of JSON Documents Against Schemas, Proceedings of the VLDB Endowment, 2025, DOI: 10.14778/3778092.3778109