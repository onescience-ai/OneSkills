# JSON Schema 报告交付契约

## 适用范围

面向结构化数据交付场景，使用 JSON Schema 定义报告或产物的契约规范。适用于需要确保交付物包含必填字段、符合类型约束、任务身份一致且可被程序解析的任务。典型触发条件包括：CLI 工具输出 JSON 报告需要校验、API 响应需要符合预定义契约、数据管道产物需要格式验证。不适用于二进制格式、流式数据或非 JSON 序列化格式。

## 输入

- JSON Schema 定义文件（.json 或内联 schema）
- 待校验的 JSON 实例文档
- 校验级别（strict/lenient）
- 自定义错误处理策略

## 输出

- 校验结果（valid/invalid）
- 错误详情列表（路径、消息、严重级别）
- 校验报告（可选）

## 流程节点

1. **Schema 加载** → 解析 JSON Schema 文档，检测元 Schema 版本
2. **实例解析** → 将待校验 JSON 文档解析为数据模型
3. **断言评估** → 对每个关键字执行约束检查（type、required、properties 等）
4. **错误收集** → 汇总所有断言失败，生成错误路径和消息
5. **输出格式化** → 按指定格式（flag/basic/detailed/verbose）输出结果
6. **契约一致性检查** → 验证任务身份字段与预期一致

每步含：操作、参数、工具、质量门禁

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| required | 字符串数组 | [D1] | 定义必填字段，缺失则校验失败 |
| type | 类型名称或数组 | [D1] | 约束实例类型：null/boolean/object/array/number/string |
| properties | 对象 | [D1] | 定义对象属性及其子 Schema |
| additionalProperties | 布尔或 Schema | [D1] | 控制是否允许额外属性 |
| items | Schema | [D1] | 约束数组元素类型 |
| prefixItems | Schema 数组 | [D1] | 按位置约束数组前 N 个元素 |

### 校准数值

以下数值来自 JSON Schema 2020-12 规范，供量级校准；其他 Schema 版本需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 元 Schema URI | https://json-schema.org/draft/2020-12/schema | [D1] | 2020-12 版本标识 |
| 媒体类型 | application/schema+json | [D1] | Schema 文档的 Content-Type |
| 布尔 Schema | true/false | [D1] | true=通过，false=失败 |
| 验证输出格式 | flag/basic/detailed/verbose | [D1] | 四种标准输出格式 |
| JSON Pointer | RFC 6901 | [D1] | 用于定位错误路径 |

## 边界与分流

- **未知关键字处理**：应视为注解（annotation），不产生断言失败
- **类型不匹配时**：大多数约束关键字对非目标类型静默通过（如 maxLength 对 number 无约束）
- **循环引用检测**：必须防止 $ref 导致的无限递归
- **多 Schema 文档**：通过 $id 和 $ref 支持跨文档引用
- **向后兼容**：新版本 Schema 应保持与旧版本的兼容性

## 质量检查

| 检查点 | 阈值 | 失败处理 |
|--------|------|----------|
| 必填字段存在性 | required 字段全部存在 | 返回缺失字段列表 |
| 类型正确性 | 实例类型匹配 type 约束 | 返回类型不匹配错误 |
| 数组长度 | 数组元素数符合 minItems/maxItems | 返回长度越界错误 |
| 任务身份一致 | task_id 字段与预期匹配 | 返回身份不匹配警告 |
| Schema 可解析 | JSON.parse 成功 | 返回解析错误详情 |

## 回退策略

- Schema 加载失败时：检查文件路径、网络连接、Schema 语法
- 校验库不可用时：使用 JSON.parse + 手动字段检查作为降级方案
- 类型冲突时：检查 Schema 定义是否过于严格，考虑使用 oneOf/anyOf
- 循环引用时：使用 $recursiveRef 替代直接 $ref

## 资源召回建议

当用户遇到以下场景时应召回本卡片：
- CLI 工具输出 JSON 报告需要格式校验
- API 响应需要符合预定义契约
- 数据管道产物需要结构验证
- 需要定义报告的必填字段和类型约束
- 需要设计可扩展的 Schema 契约

配套资源：general-cli-process-fault-diagnosis（当 CLI 执行本身需要故障诊断时）

## 补充证据（开源权威文档）

[D1] JSON Schema: A Media Type for Describing JSON Documents, IETF, draft-bhutton-json-schema-01, URL: https://json-schema.org/draft/2020-12/json-schema-core（accessed_at 2026-09-16，IETF 官方 Internet-Draft）

## 证据来源

[1] JSON Schema: A Media Type for Describing JSON Documents, Wright A., Andrews H., Hutton B., Dennis G., IETF, 2022, URL: https://json-schema.org/draft/2020-12/json-schema-core