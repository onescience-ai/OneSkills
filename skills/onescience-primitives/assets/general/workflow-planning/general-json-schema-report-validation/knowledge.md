# JSON Schema报告交付契约验证

## 适用范围

**触发条件**：
- 自动化系统输出需要符合预定义的JSON Schema契约
- API接口响应需要验证格式正确性
- 数据管道中需要确保数据完整性

**适用场景**：
- 自动化测试报告生成和验证
- API接口响应格式检查
- 数据处理流水线的质量控制
- 配置文件验证和错误检测

**不适用场景**：
- 非JSON格式的数据验证
- 实时流数据处理
- 复杂业务逻辑验证（仅限格式验证）

## 输入

**输入数据格式**：
- JSON Schema定义文件（标准JSON格式）
- 待验证的JSON数据
- 验证选项（严格模式、忽略额外属性等）

**来源**：
- 用户提供的Schema文件
- 系统生成的输出数据
- 配置文件和接口规范

**预处理要求**：
- Schema文件必须符合JSON Schema规范
- 待验证数据必须是有效JSON格式
- 验证选项需要明确指定

## 输出

**输出产物**：
- 验证结果报告（通过/失败）
- 错误详情（字段路径、错误类型、错误消息）
- 修复建议和示例

**格式**：
- 结构化验证报告（JSON格式）
- 分级错误严重程度（error/warning/info）

**验证标准**：
- 验证准确率 ≥ 99%
- 错误定位精确到字段路径
- 修复建议可执行

## 流程节点

### Step 1：Schema解析
- **操作**：加载和解析JSON Schema定义
- **参数**：Schema文件路径、Schema版本（Draft 4/6/7/2019-09/2020-12）
- **工具**：JSON Schema解析器、版本检测器
- **质量门禁**：Schema语法正确，版本兼容

### Step 2：类型验证
- **操作**：检查数据类型是否符合Schema定义
- **参数**：type关键字（string/number/integer/boolean/array/object/null）
- **工具**：类型检查器、类型转换器
- **质量门禁**：类型匹配准确率100%

### Step 3：必填字段验证
- **操作**：检查required数组中的字段是否存在
- **参数**：required关键字、字段存在性检查
- **工具**：字段检查器、缺失字段报告器
- **质量门禁**：必填字段检查准确率100%

### Step 4：数组约束验证
- **操作**：验证数组长度、唯一性、元素类型
- **参数**：minItems/maxItems/uniqueItems/items/prefixItems
- **工具**：数组验证器、长度检查器
- **质量门禁**：数组约束检查准确率 ≥ 99%

### Step 5：格式验证
- **操作**：验证字符串格式（date-time/email/uri等）
- **参数**：format关键字、格式验证器
- **工具**：格式验证库、正则表达式引擎
- **质量门禁**：格式验证准确率 ≥ 95%

### Step 6：额外属性处理
- **操作**：检查additionalProperties/unevaluatedProperties
- **参数**：额外属性策略（允许/禁止/类型限制）
- **工具**：属性检查器、模式匹配器
- **质量门禁**：额外属性检查准确率100%

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Schema版本 | Draft 2020-12 | [D1] | 最新稳定版本 |
| 类型关键字 | string/number/integer/boolean/array/object/null | [D2] | JSON Schema基本类型 |
| 必填字段 | required数组 | [D3] | 必须包含的所有字段 |
| 数组约束 | minItems/maxItems/uniqueItems | [D4] | 数组长度和唯一性约束 |
| 格式验证 | format关键字 | [D2] | 语义格式验证（可选） |

### 校准数值

以下数值来自JSON Schema官方文档，供量级校准；其他系统需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Draft 4 | required至少1个字符串 | [D3] | 早期版本要求 |
| Draft 6+ | required可为空数组 | [D3] | 新版本更灵活 |
| additionalProperties | 默认允许额外属性 | [D3] | 需显式禁止 |
| unevaluatedProperties | Draft 2019-09+ | [D3] | 跨子Schema属性检查 |

## 边界与分流

**前提1：Schema文件有效**
- 不成立时：Schema语法错误或版本不兼容
- 改道方案：使用Schema验证器检查Schema本身

**前提2：输入数据是有效JSON**
- 不成立时：JSON语法错误或编码问题
- 改道方案：使用JSON解析器预处理

**前提3：验证器支持目标Schema版本**
- 不成立时：验证器版本过旧
- 改道方案：升级验证器或使用兼容模式

**前提4：格式验证库可用**
- 不成立时：缺少格式验证依赖
- 改道方案：跳过格式验证或安装依赖

## 质量检查

**验证点**：
- Schema解析正确性
- 类型匹配准确性
- 必填字段检查完整性
- 数组约束验证准确性
- 格式验证覆盖率

**阈值**：
- 验证准确率 ≥ 99%
- 错误定位精确到字段路径
- 修复建议可执行性100%

**失败处理**：
- Schema解析失败时回退到基础JSON验证
- 格式验证失败时标记为警告而非错误

## 回退策略

**降级方案**：
1. 当高级Schema特性不支持时，使用基础验证
2. 当格式验证库缺失时，跳过格式检查
3. 当验证器版本过旧时，使用兼容模式

**预防措施**：
- 在CI/CD中添加Schema验证步骤
- 使用Schema版本管理工具
- 定期更新验证器依赖

## 资源召回建议

**何时召回本卡片**：
- 用户需要验证JSON输出格式
- API接口响应格式检查
- 数据管道质量控制
- 配置文件验证

**配套资源**：
- general-cli-fault-diagnosis：CLI执行故障诊断
- JSON Schema验证工具库
- Schema版本管理工具

## 补充证据

[D1] "JSON Schema reference", JSON Schema Organization, 2020-12, URL: https://json-schema.org/understanding-json-schema/（accessed 2026-09-17，权威文档）

[D2] "Type-specific Keywords", JSON Schema Organization, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/type（accessed 2026-09-17，权威文档）

[D3] "object", JSON Schema Organization, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/object（accessed 2026-09-17，权威文档）

[D4] "array", JSON Schema Organization, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/array（accessed 2026-09-17，权威文档）

## 证据来源

[1] Lyes Attouche, Mohamed-Amine Baazizi, Dario Colazzo, Giorgio Ghelli, Carlo Sartiani, Stefanie Scherzinger. "Validation of Modern JSON Schema: Formalization and Complexity." arXiv:2307.10034, 2023.
[2] Juan Cruz Viotti, Michael J. Mior. "Blaze: Compiling JSON Schema for 10x Faster Validation." arXiv:2503.02770, 2025.
[3] Oleg Solozobov. "Decision Trace Schema for Governance Evidence in Real-Time Risk Systems." arXiv:2604.09296, 2026.
[4] Edwin Sundberg, Thea Ekmark, Workneh Yilma Ayele. "Validating API Design Requirements for Interoperability (S.E.O.R.A)." arXiv:2511.17836, 2025.
[5] "JSON Schema reference", JSON Schema Organization, 2020-12, URL: https://json-schema.org/understanding-json-schema/
[6] "Type-specific Keywords", JSON Schema Organization, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/type
[7] "object", JSON Schema Organization, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/object
[8] "array", JSON Schema Organization, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/array