# JSON Schema报告交付契约验证

## 适用范围
适用于命令行工具输出结构化报告时的格式验证，确保报告内容符合预定义的JSON Schema契约。适用于自动化流水线中需要验证报告完整性、数据类型正确性和字段完整性的场景，包括数据分析报告、测试报告、审计报告等。

## 输入
- 命令行工具生成的JSON格式报告
- 预定义的JSON Schema验证规则
- 验证配置选项（严格模式、格式验证等）
- 验证结果输出格式（JSON、文本、HTML等）

## 输出
- 验证结果（通过/失败）
- 详细的错误信息和位置
- 验证报告和统计信息
- 修复建议（可选）

## 流程节点
1. **Schema加载** → 读取并解析JSON Schema文件，构建验证规则树
2. **报告解析** → 读取并解析命令行工具输出的JSON报告
3. **结构验证** → 验证JSON结构是否符合Schema定义
4. **类型检查** → 验证数据类型是否正确（字符串、数字、数组等）
5. **格式验证** → 验证数据格式（日期、邮箱、URI等）是否符合规范
6. **业务规则验证** → 验证自定义业务规则和约束条件
7. **结果生成** → 生成详细的验证报告和统计信息

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Schema版本 | 2020-12 | [D1] | 当前主流JSON Schema版本 |
| 必填字段 | required | [D2] | Schema中定义的必填字段 |
| 类型约束 | type | [D2] | 数据类型约束（string, number, array, object等） |
| 格式验证 | format | [D2] | 语义格式验证（date-time, email, uri等） |
| 枚举约束 | enum | [D2] | 允许的值枚举列表 |
| 数组约束 | items, minItems, maxItems | [D2] | 数组元素和长度约束 |
| 对象约束 | properties, additionalProperties | [D2] | 对象属性和额外属性约束 |

### 校准数值
以下数值来自JSON Schema规范，供量级校准；其他环境需以自身证据重新锚定：
- 最大嵌套深度：通常建议不超过10层，避免验证性能问题
- 字符串长度限制：根据业务需求设置minLength/maxLength
- 数值范围：根据业务需求设置minimum/maximum
- 数组长度：根据业务需求设置minItems/maxItems

## 边界与分流
- **Schema缺失**：当未提供JSON Schema时，应使用默认Schema或跳过验证
- **格式错误**：当JSON格式错误时，应报告解析错误并提供修复建议
- **Schema不兼容**：当Schema版本不兼容时，应尝试兼容性转换或报告版本冲突
- **性能问题**：当验证大型JSON文档时，应实施分块验证或异步验证
- **自定义格式**：对于非标准格式，应扩展验证器或使用自定义验证函数

## 质量检查
- 验证Schema是否符合JSON Schema规范
- 检查JSON文档是否可被正确解析
- 验证所有必填字段是否存在
- 检查数据类型是否匹配Schema定义
- 验证格式约束是否满足
- 检查业务规则约束是否满足

## 回退策略
- 当Schema验证失败时，提供详细的错误位置和修复建议
- 当Schema文件缺失时，使用基础Schema或跳过验证
- 当验证性能不足时，实施抽样验证或简化Schema
- 当遇到未知格式时，记录警告并继续验证其他字段

## 资源召回建议
- 当需要验证命令行工具输出的JSON格式报告时召回本卡片
- 当遇到报告格式不符合预期时召回本卡片
- 当需要确保自动化流水线中数据完整性时召回本卡片
- 配套资源：cli-non-interactive-execution-error-handling（用于处理CLI执行错误）

## 补充证据（开源权威文档）
[D1] JSON Schema, JSON Schema, 2020-12, URL: https://json-schema.org/（accessed_at 2026-09-17，权威官方文档）
[D2] JSON Schema reference, JSON Schema, 2020-12, URL: https://json-schema.org/understanding-json-schema/（accessed_at 2026-09-17，权威官方文档）
[D3] JSON Schema - Type-specific Keywords, JSON Schema, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/type（accessed_at 2026-09-17，权威官方文档）

## 证据来源
[无论文证据，仅使用权威文档证据]