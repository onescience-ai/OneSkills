# JSON Schema报告交付契约验证

## 适用范围

适用于所有需要通过JSON Schema验证结构化报告交付契约的场景，包括自动化系统间数据交换、API响应验证、配置文件校验和报告生成系统。覆盖字段完整性检查、类型验证、格式合规性和嵌套结构验证。

## 输入

- JSON Schema定义文件（.json或.schema.json）
- 待验证的JSON报告数据
- 验证选项（严格模式/宽松模式）
- 自定义格式验证器（可选）

## 输出

- 验证结果（通过/失败）
- 详细错误信息（字段路径、错误类型、错误描述）
- 验证统计（通过字段数、失败字段数）
- 修复建议（可选）

## 流程节点

### 1. Schema加载与解析
- 操作：加载JSON Schema文件、解析为内部表示
- 参数：Schema文件路径、编码格式
- 工具：jsonschema库、JSON解析器
- 质量门禁：Schema语法正确、无解析错误

### 2. 数据预处理
- 操作：解析JSON报告数据、规范化格式
- 参数：JSON数据源、编码格式
- 工具：json.loads()、数据清洗函数
- 质量门禁：JSON格式有效、数据可解析

### 3. 类型验证
- 操作：验证字段数据类型是否符合Schema定义
- 参数：类型关键字（string/number/integer/boolean/array/object/null）
- 工具：type关键字验证器
- 质量门禁：所有字段类型匹配

### 4. 结构验证
- 操作：验证对象属性、数组元素、嵌套结构
- 参数：required属性、properties定义、items模式
- 工具：object/array验证器
- 质量门禁：必填字段存在、结构符合定义

### 5. 格式与约束验证
- 操作：验证字段格式（email/uri/date等）、数值范围、字符串长度
- 参数：format关键字、minimum/maximum、minLength/maxLength
- 工具：format验证器、约束检查器
- 质量门禁：格式正确、约束满足

### 6. 结果聚合与报告
- 操作：收集所有验证错误、生成结构化报告
- 参数：错误收集策略、报告格式
- 工具：错误聚合器、报告生成器
- 质量门禁：报告完整、错误信息准确

### 7. 报告身份与字段契约校验
- 操作：验证报告顶层字段与任务身份的一致性
- 参数：required 顶层字段列表（如 task_id、task、issues、summary）、字段值与任务索引的匹配
- 工具：JSON Schema required + const/enum 约束
- 质量门禁：
  - 报告包含 Schema 规定的全部必填顶层字段，无遗漏
  - 不包含 Schema 未定义的额外顶层字段（additionalProperties: false）
  - task_id 字段值与任务索引编号严格一致
  - task 字段值与任务名称严格一致
  - summary 为非空字符串
  - issues 为数组类型
  - 出现任何不一致即判定验证失败，输出具体的字段级差异

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| type关键字 | 基础类型验证 | [D1] | 验证字段是否为预期数据类型 |
| required数组 | 必填字段列表 | [D2] | 指定对象中必须存在的属性 |
| properties对象 | 属性Schema定义 | [D2] | 定义每个属性的验证规则 |
| additionalProperties | 额外属性控制 | [D2] | 是否允许未定义的属性 |
| patternProperties | 模式属性验证 | [D2] | 按正则表达式匹配属性名 |
| enum枚举 | 允许值列表 | [D1] | 限制字段只能取特定值 |
| const常量 | 固定值验证 | [D1] | 字段必须等于特定值 |
| allOf/anyOf/oneOf | 组合Schema | [D1] | 多个Schema的逻辑组合 |
| if/then/else | 条件验证 | [D1] | 基于条件的动态验证 |

### 校准数值（JSON Schema 2020-12特定）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| format:date-time | RFC 3339日期时间 | [D1] | 如"2018-11-13T20:20:39+00:00" |
| format:date | 日期格式 | [D1] | 如"2018-11-13" |
| format:time | 时间格式 | [D1] | 如"20:20:39+00:00" |
| format:email | 电子邮件格式 | [D1] | RFC 5321标准 |
| format:uri | URI格式 | [D1] | RFC 3986标准 |
| format:uuid | UUID格式 | [D1] | RFC 4122标准 |
| format:ipv4 | IPv4地址 | [D1] | 点分十进制格式 |
| format:ipv6 | IPv6地址 | [D1] | RFC 2373格式 |
| minimum/maximum | 数值范围 | [D2] | 包含边界值 |
| exclusiveMinimum/Maximum | 排他数值范围 | [D2] | 不包含边界值 |
| minLength/maxLength | 字符串长度 | [D2] | 字符数限制 |
| minItems/maxItems | 数组长度 | [D2] | 元素数量限制 |
| uniqueItems | 数组唯一性 | [D2] | 元素不能重复 |

## 边界与分流

### Schema语法错误
- 症状：Schema解析失败、JSON解析异常
- 处理：检查Schema文件格式、验证JSON语法
- 恢复：修正Schema语法后重新验证

### 数据类型不匹配
- 症状：type验证失败、类型转换错误
- 处理：检查数据源类型、验证Schema定义
- 恢复：修正数据类型或调整Schema定义

### 必填字段缺失
- 症状：required验证失败、字段不存在
- 处理：检查数据完整性、验证字段生成逻辑
- 恢复：补充缺失字段或调整required列表

### 格式验证失败
- 症状：format验证失败、格式不匹配
- 处理：检查数据格式、验证format定义
- 恢复：修正数据格式或自定义format验证器

### 嵌套结构错误
- 症状：properties验证失败、嵌套层级错误
- 处理：检查嵌套结构、验证Schema定义
- 恢复：修正嵌套结构或调整Schema定义

### 额外属性问题
- 症状：additionalProperties验证失败
- 处理：检查是否允许额外属性、验证properties定义
- 恢复：移除额外属性或设置additionalProperties为true

### 报告身份不一致
- 症状：task_id 与任务索引不匹配、task 与任务名称不一致、顶层字段缺失或多余
- 处理：逐字段对比 Schema 要求与报告实际内容，列出差异明细
- 恢复：修正报告的 task_id/task 值，或补全缺失字段、移除未定义字段后重新校验

### 报告类型约束失败
- 症状：summary 非字符串或为空、issues 非数组
- 处理：检查报告生成逻辑中的类型输出
- 恢复：确保 summary 输出为非空字符串，issues 输出为数组类型

## 质量检查

1. **Schema有效性**：确认Schema文件语法正确、符合JSON Schema规范
2. **数据可解析性**：验证JSON数据格式正确、可成功解析
3. **类型一致性**：确认所有字段类型与Schema定义匹配
4. **必填字段完整性**：验证所有required字段都存在
5. **格式合规性**：确认所有format字段符合指定格式
6. **嵌套结构正确性**：验证所有嵌套对象和数组结构正确
7. **身份一致性**：验证 task_id 与任务索引一致、task 与任务名称一致
8. **字段纯净性**：验证无 Schema 未定义的额外顶层字段（additionalProperties: false）
9. **类型严格性**：验证 summary 为非空字符串、issues 为数组

## 回退策略

1. **宽松验证**：对于非关键字段，失败时记录警告但不阻断验证
2. **自定义验证器**：对于复杂格式，提供自定义验证函数
3. **部分验证**：对于大型报告，支持字段级或章节级部分验证
4. **降级Schema**：对于旧版数据，使用兼容性更好的Schema版本
5. **人工审核**：对于验证失败的关键报告，触发人工审核流程

## 资源召回建议

当遇到以下场景时召回本卡片：
- 需要验证JSON报告是否符合预定义Schema
- 需要检查结构化输出的字段完整性
- 需要确保自动化系统间数据交换的格式一致性
- 需要诊断JSON报告验证失败的根本原因

配套资源：
- onescience-coder：生成符合Schema的报告代码
- onescience-orchestrator：协调报告生成和验证流程
- onescience-runtime：执行报告生成和验证任务

## 补充证据（开源权威文档）

[D1] JSON Schema Official Documentation, JSON Schema Organization, v2020-12, https://json-schema.org/understanding-json-schema/ (accessed_at: 2026-09-17, 单源参考)

[D2] JSON Schema - Type-specific Keywords, JSON Schema Organization, v2020-12, https://json-schema.org/understanding-json-schema/reference/type (accessed_at: 2026-09-17, 单源参考)

[D3] JSON Schema - Object Validation, JSON Schema Organization, v2020-12, https://json-schema.org/understanding-json-schema/reference/object (accessed_at: 2026-09-17, 单源参考)

## 证据来源

本文档基于以下权威来源整理：
- JSON Schema官方文档（类型验证、对象验证、格式验证）
- JSON Schema规范（2020-12版本）
- 行业最佳实践（结构化数据验证模式）