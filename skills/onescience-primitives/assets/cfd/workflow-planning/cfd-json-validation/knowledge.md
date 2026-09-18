# JSON输出格式化与校验

## 适用范围

面向科学报告和配置文件的JSON输出格式化与校验，提供字符串转义规则、Schema校验最佳实践、自动校验机制。适用于归因报告、任务配置、元数据文件等JSON产物的生成和验证。

## 输入

- 原始数据结构（Python dict/list、嵌套对象）
- 特殊字符：双引号、反斜杠、换行符、Unicode字符
- Schema定义（可选）

## 输出

- 格式化JSON文件（符合RFC 8259）
- 校验结果（通过/失败 + 错误详情）
- 修复建议（针对格式错误）

## 流程节点

1. **数据序列化** → 使用json.dumps()生成JSON字符串
2. **转义处理** → 自动转义特殊字符
3. **格式化输出** → 设置indent、ensure_ascii等参数
4. **Schema校验** → 使用ajv/jsonschema验证结构
5. **自动修复** → 检测常见错误并提示修复

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 缩进空格数 | 2或4 | [1] | 保持一致性，推荐2空格 |
| ensure_ascii | false | [1] | 允许非ASCII字符直接输出 |
| 字符串转义 | 自动 | [1] | json.dumps自动处理 |
| 校验时机 | 输出前 | [2] | 防止错误JSON传播 |

### 校准数值（特殊字符转义规则）

| 字符 | 转义序列 | 说明 | 来源 |
|------|----------|------|------|
| 双引号 `"` | `\"` | 字符串边界 | [1] |
| 反斜杠 `\` | `\\` | 转义字符本身 | [1] |
| 换行 `\n` | `\n` | 行分隔符 | [1] |
| 回车 `\r` | `\r` | 行首返回 | [1] |
| 制表符 `\t` | `\t` | 缩进 | [1] |
| Unicode | `\uXXXX` | 非ASCII字符 | [1] |

## 边界与分流

- **简单数据**：直接json.dumps()，无需额外处理
- **嵌套对象**：递归序列化，注意循环引用检测
- **大文件**：使用流式写入，避免内存溢出
- **Schema定义**：校验失败时提供详细错误位置和修复建议

## 质量检查

- JSON解析测试：json.loads()验证可解析性
- Schema校验：使用jsonschema.validate()检查结构
- 字符编码检查：确认UTF-8编码正确
- 文件完整性：检查文件大小、行数、结束符

## 回退策略

- 格式错误：自动检测并提示修复位置
- Schema校验失败：提供修复建议
- 大文件处理失败：分块处理或流式写入

## 资源召回建议

- 生成JSON格式的报告或配置文件时召回本卡片
- 配套资源：cfd-workflow-fault-recovery（容错机制）

## 证据来源

[1] RFC 8259 - The JavaScript Object Notation (JSON) Data Interchange Format, IETF, 2017, URL: https://www.rfc-editor.org/rfc/rfc8259
[2] JSON Schema Validation, JSON Schema, 2020-12, URL: https://json-schema.org/draft/2020-12/json-schema-validation

## 补充证据（开源文档）

[D1] RFC 8259 - The JavaScript Object Notation (JSON) Data Interchange Format, IETF, 2017, URL: https://www.rfc-editor.org/rfc/rfc8259（accessed_at，标准文档）
[D2] JSON Schema Validation, JSON Schema, 2020-12, URL: https://json-schema.org/draft/2020-12/json-schema-validation（accessed_at，标准文档）
