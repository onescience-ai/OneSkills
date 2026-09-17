# JSON Schema 报告交付契约

## 适用范围

**触发条件**：
- 程序输出需要符合预定义的 JSON 结构
- 需要验证 JSON 报告的字段完整性和类型正确性
- 自动化流程中需要确保数据交换格式的一致性

**适用场景**：
- 自动化报告生成与校验
- API 响应格式验证
- 配置文件 Schema 检查
- 数据管道中的数据格式标准化
- 科学计算结果的结构化输出验证

**不适用场景**：
- 非 JSON 格式的数据验证（XML、YAML 等）
- 复杂业务逻辑验证（仅格式验证）
- 性能关键型实时验证（考虑流式处理）

## 输入

- JSON Schema 定义文件（JSON 格式）
- 待验证的 JSON 数据或报告
- 校验规则配置（严格模式、错误处理策略）
- 上下文信息（任务 ID、时间戳等）

## 输出

- 校验结果（通过/失败）
- 结构化错误信息（字段路径、错误类型、预期值）
- 修复建议（针对常见错误模式）
- 校验报告（包含统计信息和历史记录）

## 流程节点

### Step 1：Schema 加载与解析
- **操作**：加载并解析 JSON Schema 定义文件
- **参数**：Schema 版本（Draft-04/07/2020-12）、引用解析策略
- **工具**：jsonschema 库、Schema 解析器
- **质量门禁**：Schema 必须符合 JSON Schema 规范

### Step 2：字段完整性检查
- **操作**：验证所有必填字段是否存在
- **参数**：required 字段列表、可选字段列表
- **工具**：字段遍历器、存在性检查器
- **质量门禁**：必填字段缺失必须报告具体字段路径

### Step 3：类型验证
- **操作**：验证每个字段的数据类型是否符合 Schema
- **参数**：类型映射表（string/number/integer/boolean/array/object/null）
- **工具**：类型检查器、类型转换器
- **质量门禁**：类型不匹配必须报告字段路径和实际类型

### Step 4：数组与对象约束验证
- **操作**：验证数组长度、对象属性、嵌套结构
- **参数**：minItems/maxItems/minProperties/maxProperties/patternProperties
- **工具**：约束验证器、递归检查器
- **质量门禁**：约束违反必须报告具体约束类型

### Step 5：身份字段匹配验证
- **操作**：验证任务 ID、名称等身份字段的一致性
- **参数**：身份字段列表、匹配规则（精确/正则/范围）
- **工具**：模式匹配器、身份验证器
- **质量门禁**：身份不匹配必须报告冲突字段

### Step 6：校验报告生成
- **操作**：汇总校验结果并生成结构化报告
- **参数**：报告模板、错误聚合策略、统计指标
- **工具**：报告生成器、模板引擎
- **质量门禁**：报告必须包含校验状态、错误详情和统计信息

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Schema 版本 | 2020-12 | [D1] | 当前推荐版本 |
| 严格模式 | true | [D2] | 启用所有约束检查 |
| 错误聚合 | 按字段分组 | [D3] | 便于批量修复 |
| 报告格式 | JSON | [D1] | 与输入格式一致 |
| 校验深度 | 无限递归 | [D2] | 验证嵌套结构 |

### 校准数值
以下数值来自典型实现，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 最大 Schema 复杂度 | 1000 节点 | [D3] | 避免性能问题 |
| 错误消息最大长度 | 200 字符 | [D3] | 保持可读性 |
| 嵌套深度限制 | 10 层 | [D3] | 防止栈溢出 |
| 批量校验大小 | 1000 条 | [D3] | 内存优化 |

## 边界与分流

**前提 1：JSON 数据格式正确**
- 不成立时：先执行 JSON 语法修复（括号匹配、逗号修正）

**前提 2：Schema 定义有效**
- 不成立时：先验证 Schema 本身是否符合 JSON Schema 规范

**前提 3：身份字段可访问**
- 不成立时：标记为"身份验证跳过"，仅执行格式校验

**前提 4：校验性能可接受**
- 不成立时：采用流式校验或分批处理策略

## 质量检查

- Schema 解析必须处理 $ref 引用
- 字段缺失错误必须包含完整路径
- 类型错误必须报告实际值和预期类型
- 校验结果必须可复现
- 错误消息必须人类可读

## 回退策略

1. **Schema 版本不兼容**：降级到 Draft-07 或使用兼容性转换器
2. **循环引用**：设置引用深度限制，标记为"需人工检查"
3. **性能瓶颈**：启用并行校验或采样校验
4. **错误信息过多**：按严重性过滤，仅报告关键错误

## 资源召回建议

当遇到以下情况时应召回本卡片：
- 程序输出 JSON 格式不符合预期
- 自动化报告校验失败
- API 响应格式验证错误
- 配置文件 Schema 检查失败
- 需要建立 JSON 数据质量标准

配套资源：
- `general-cli-fault-diagnosis`：用于诊断生成 JSON 的 CLI 工具故障
- `onescience-paper-repro`：用于处理论文中的 JSON 数据结构
- `onescience-data-standardizer`：用于数据格式标准化

## 补充证据

[D1] "JSON Schema官方文档", JSON Schema organization, 2020-12, URL: https://json-schema.org/documentation（accessed 2026-09-15，权威官方文档）
[D2] "Understanding JSON Schema", JSON Schema organization, 2020-12, URL: https://json-schema.org/understanding-json-schema/（accessed 2026-09-15，官方教程）
[D3] "Python jsonschema library documentation", Python Software Foundation, jsonschema 4.20.0, URL: https://python-jsonschema.readthedocs.io/（accessed 2026-09-15，官方库文档）

## 证据来源

[D1] "JSON Schema官方文档", JSON Schema organization, 2020-12, URL: https://json-schema.org/documentation
[D2] "Understanding JSON Schema", JSON Schema organization, 2020-12, URL: https://json-schema.org/understanding-json-schema/
[D3] "Python jsonschema library documentation", Python Software Foundation, jsonschema 4.20.0, URL: https://python-jsonschema.readthedocs.io/