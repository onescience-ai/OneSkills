# JSON Schema 结构化输出契约验证

## 适用范围

**触发条件**：
- 需要定义外部工具或流程的输出格式规范，并在运行时验证输出是否符合契约
- 遇到输出缺失字段、类型不匹配、数组格式错误等问题，需要系统化的校验方法

**适用场景**：
- CLI 工具生成结构化报告（JSON）后的格式校验
- API 响应格式的质量保证与自动化测试
- 科学计算流水线中中间产物和最终报告的契约验证
- 多系统间数据交换的格式一致性保障

**不适用场景**：
- 非 JSON 格式的输出验证
- 纯文本日志或流式数据的校验

## 输入

| 输入项 | 格式 | 说明 |
|--------|------|------|
| 待验证 JSON | 对象 | 需要校验的 JSON 数据 |
| JSON Schema | 对象 | 定义契约的 schema 文档 |
| 校验选项 | 对象 | 可选，如 additionalProperties、format 校验开关 |

## 输出

| 输出项 | 格式 | 说明 |
|--------|------|------|
| 校验结果 | 布尔值 | 通过/不通过 |
| 错误列表 | 数组 | 不符合契约的字段及原因 |
| 修复建议 | 数组 | 针对每个错误的修复方案 |

## 流程节点

### Step 1：Schema 定义与契约设计
- **操作**：定义 JSON Schema，声明必填字段、类型约束、数组约束
- **参数**：type, required, properties, items, additionalProperties
- **工具**：JSON Schema 规范文档、在线编辑器
- **质量门禁**：Schema 可被标准解析器解析，必填字段完整

### Step 2：类型验证
- **操作**：检查每个字段的数据类型是否符合 schema 定义
- **参数**：type 关键字（string/number/integer/boolean/array/object/null）
- **工具**：JSON Schema 校验器
- **质量门禁**：所有字段类型匹配，无类型混淆

### Step 3：必填字段与结构验证
- **操作**：验证 required 数组中的字段是否存在
- **参数**：required, properties, minProperties
- **工具**：JSON Schema 校验器
- **质量门禁**：必填字段全部存在，无额外未声明字段（若 additionalProperties=false）

### Step 4：数组约束验证
- **操作**：验证数组字段的元素类型、长度、唯一性
- **参数**：items, minItems, maxItems, uniqueItems
- **工具**：JSON Schema 校验器
- **质量门禁**：数组元素类型一致，长度在范围内

### Step 5：错误分类与修复建议生成
- **操作**：将校验错误分类为缺失字段、类型错误、约束违反等类别
- **参数**：错误路径、错误类型、期望值
- **工具**：错误处理逻辑
- **质量门禁**：每个错误有明确的修复路径

## 关键参数

### 通用判据（方法层）

| 参数 | 判据 | 来源 | 说明 |
|------|------|------|------|
| type | 数据类型匹配 | [D1][D2] | 基础类型校验（string/number/boolean/array/object/null） |
| required | 必填字段存在 | [D1] | 声明的字段必须在 JSON 中出现 |
| properties | 属性定义 | [D1] | 每个属性的 schema 约束 |
| additionalProperties | 额外属性控制 | [D1] | false 时禁止未声明属性 |
| items | 数组元素类型 | [D2] | 数组中每个元素的 schema |
| minItems / maxItems | 数组长度约束 | [D2] | 数组元素数量范围 |
| uniqueItems | 数组唯一性 | [D2] | true 时元素不可重复 |
| format | 语义格式校验 | [D2] | date-time/email/uri 等预定义格式 |
| enum | 枚举值约束 | [D1] | 字段值必须在枚举列表中 |

### 校准数值（实例参考）

以下数值来自 JSON Schema 规范示例，供量级校准；具体项目的 schema 需以自身需求重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 基础类型 | string, number, integer, boolean, array, object, null | [D2] | JSON Schema 定义的 7 种基础类型 |
| format 预定义 | date-time, time, date, duration, email, hostname, ipv4, ipv6, uri, uuid, regex | [D2] | 常用语义格式 |

## 边界与分流

| 前提 | 不成立时的处理 |
|------|----------------|
| Schema 本身语法正确 | 先修复 schema 定义错误（使用 schema 校验器自检） |
| 待验证数据为合法 JSON | 先修复 JSON 解析错误（检查编码、语法） |
| 校验器支持所需 draft 版本 | 降级到兼容的 draft 版本或更换校验器 |
| format 校验器可用 | 仅做注解级别校验，不阻断流程 |

## 质量检查

| 检查点 | 阈值 | 失败处理 |
|--------|------|----------|
| Schema 可解析 | 解析器无报错 | 修复 schema 语法 |
| 必填字段完整 | required 数组字段全部存在 | 补充缺失字段或调整 schema |
| 类型匹配 | 每个字段 type 一致 | 转换数据类型或修改 schema |
| 数组约束 | 长度/唯一性符合 | 截断/去重或调整约束 |
| 无额外字段 | additionalProperties 约束通过 | 删除多余字段或开放声明 |

## 回退策略

1. **Schema 不兼容回退**：使用 JSON Schema draft-07 兼容模式，降低校验严格度
2. **format 不支持回退**：跳过 format 校验（仅做注解），改用正则手动校验
3. **部分校验回退**：仅校验核心必填字段，跳过可选字段的约束
4. **宽松模式回退**：设置 additionalProperties=true，容忍额外字段

## 资源召回建议

当用户遇到以下问题时应召回本卡片：
- CLI 工具输出的 JSON 缺少必填字段
- 需要定义报告交付的格式契约
- JSON Schema 校验失败，需要分类错误并生成修复建议
- 多系统间 JSON 数据交换格式不一致

配套资源：`general-cli-noninteractive-execution-fault-classification`（CLI 故障诊断）

## 补充证据（开源权威文档）

[D1] "JSON Schema - Understanding JSON Schema", JSON Schema Organization, 2020-12, URL: https://json-schema.org/understanding-json-schema/（accessed 2026-09-16，权威来源：JSON Schema 官方文档）
[D2] "JSON Schema - Type-specific Keywords", JSON Schema Organization, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/type（accessed 2026-09-16，权威来源：JSON Schema 官方文档）

## 证据来源

[D1] JSON Schema - Understanding JSON Schema, JSON Schema Organization, https://json-schema.org/understanding-json-schema/
[D2] JSON Schema - Type-specific Keywords, JSON Schema Organization, https://json-schema.org/understanding-json-schema/reference/type
