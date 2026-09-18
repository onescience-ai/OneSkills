# JSON Schema 报告交付契约校验规范

## 适用范围
本卡面向科学计算任务的结构化报告交付场景，规范 JSON Schema 校验流程与常见错误处理。适用于归因报告、分析结果、任务执行产物等需要按约定格式交付的 JSON 文档。不适用于非结构化文本报告或二进制产物。

## 输入
- **待校验 JSON**：任务产出的结构化报告文档
- **Schema 定义**：JSON Schema 文件（draft-07 或 2020-12）
- **校验选项**：严格模式/宽松模式、错误收集策略

## 输出
- **校验结果**：通过/失败
- **错误列表**：具体违规项及位置
- **修正建议**：常见错误的修复指引

## 流程节点
1. JSON 解析 → 使用 `json.loads()` 读取报告内容
2. Schema 加载 → 解析 JSON Schema 定义文件
3. 校验执行 → 逐条检查 Schema 约束条件
4. 错误收集 → 汇总所有违规项及详细信息
5. 结果输出 → 返回结构化校验报告

每步含：操作、参数、工具、质量门禁

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| `required` 字段 | 字符串数组 | JSON Schema [D1] | 必填字段列表，缺失则校验失败 |
| `type` 约束 | 字符串/数组 | JSON Schema [D1] | 值类型必须匹配（string/number/integer/boolean/array/object/null） |
| `additionalProperties` | 布尔/对象 | JSON Schema [D1] | false 时禁止未声明的额外属性 |
| `items` 约束 | 对象/数组 | JSON Schema [D1] | 数组元素类型与结构约束 |
| `minItems`/`maxItems` | 整数 | JSON Schema [D1] | 数组长度上下限 |
| `enum` | 数组 | JSON Schema [D1] | 允许的值集合 |
| `allOf`/`anyOf`/`oneOf` | Schema 数组 | JSON Schema [D1] | 组合校验逻辑 |

### 校准数值（常见校验错误码）
以下数值来自 JSON Schema 测试套件 [D3] 和实践经验，供量级校准；其他校验器实现可能有不同的错误编码。

| 错误类型 | 典型错误码 | 来源 | 说明 |
|----------|-----------|------|------|
| 必填字段缺失 | `required` | JSON Schema [D1] | required 数组中的字段未出现 |
| 类型不匹配 | `type` | JSON Schema [D1] | 值类型与 type 约束不符 |
| 额外属性 | `additionalProperties` | JSON Schema [D1] | 出现未在 properties 中声明的字段 |
| 数组过短/过长 | `minItems`/`maxItems` | JSON Schema [D1] | 数组长度超出范围 |
| 值不在枚举中 | `enum` | JSON Schema [D1] | 值不在允许的枚举列表内 |
| 字符串过短/过长 | `minLength`/`maxLength` | JSON Schema [D1] | 字符串长度超出范围 |
| 数值超出范围 | `minimum`/`maximum` | JSON Schema [D1] | 数值超出上下限 |

## 边界与分流

| 前提条件 | 不成立时的转向方案 |
|----------|-------------------|
| JSON 语法正确 | 转向：报告 JSON 解析错误位置，提供语法修复建议 |
| Schema 文件可加载 | 转向：检查 Schema 文件路径与格式，提供 Schema 语法说明 |
| 校验器支持当前 Schema 版本 | 转向：升级校验器或降级 Schema 到兼容版本 |
| 所有必填字段存在 | 转向：逐项检查缺失字段，提供字段填写指引 |

## 质量检查

| 验证点 | 阈值 | 失败处理 |
|--------|------|----------|
| JSON 语法合法 | 无解析异常 | 报告错误位置（行号/列号） |
| 必填字段完整 | 0 个缺失 | 列出所有缺失字段名 |
| 类型约束满足 | 0 个类型错误 | 列出字段名、期望类型、实际类型 |
| 额外属性检查 | 符合 additionalProperties 设置 | 列出所有未声明属性 |
| 数组约束满足 | 长度在 minItems/maxItems 范围内 | 报告实际长度与期望范围 |

## 回退策略
- JSON 解析失败 → 修复语法错误后重新提交
- Schema 校验失败 → 根据错误列表逐项修正报告内容
- Schema 版本不兼容 → 使用兼容的 Schema 版本或升级校验器
- 校验器不可用 → 手动检查关键字段（required + type）作为降级方案

## 资源召回建议
当任务涉及以下场景时应召回本卡片：
- 生成归因报告、分析报告等结构化输出
- 校验任务执行产物的格式正确性
- 构建需要消费 JSON 报告的下游系统
- 处理 Schema 校验失败的错误诊断

配套卡片：`cfd-cli-error-handling-classification`（CLI 执行错误处理）

## 证据来源
[1] Validation of Modern JSON Schema: Formalization and Complexity, Attouche et al., ACM SIGMOD, 2024, DOI: 10.1145/3639305
[2] Reducing Ambiguity in JSON Schema Discovery, Spoth et al., ACM SIGMOD, 2021, DOI: 10.1145/3448016.3457263
[3] Definition of REST Web Services with JSON Schema, Barbaglia et al., Software: Practice and Experience, 2017, DOI: 10.1002/spe.2485

[D1] JSON Schema Official Specification, json-schema.org, Draft 2020-12
[D2] JSON Schema Validation Specification, json-schema.org, Draft 2020-12
[D3] JSON Schema Test Suite, json-schema-org (GitHub)