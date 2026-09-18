# JSON Schema 报告交付契约

## 适用范围

本卡片服务于JSON格式报告的结构化验证与契约合规检查任务。适用于数据交换、API响应、配置文件、科学报告、归因分析输出等需要确保JSON数据符合预定Schema的场景。帮助开发者和数据工程师定义、验证和维护JSON数据的结构契约，确保数据交付的完整性和一致性。

## 输入

- JSON Schema定义文件（.json）
- 待验证的JSON数据
- 验证配置（strict模式、错误处理策略）
- 验证上下文（字段描述、业务规则）

## 输出

- 验证结果（通过/失败）
- 错误详情（缺失字段、类型不匹配、格式错误）
- 校验报告（符合Schema的字段列表、不符合项）
- 修复建议（如何调整数据以符合Schema）

## 流程节点

1. **Schema加载与解析** → 读取JSON Schema文件，构建验证规则树
2. **数据加载与预处理** → 读取JSON数据，处理编码和格式问题
3. **类型验证** → 检查字段类型是否符合Schema定义
4. **结构验证** → 检查必需字段、属性约束、数组长度
5. **格式验证** → 检查字符串格式（日期、邮箱、URI等）
6. **组合验证** → 使用allOf/anyOf/oneOf/not进行复杂约束验证
7. **条件验证** → 使用if/then/else进行条件字段验证
8. **结果生成与报告** → 生成详细的验证报告和修复建议

每步含：操作、参数、工具、质量门禁

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| type | string/number/boolean/null/object/array | [D2] | 字段基础类型定义 |
| required | ["field1", "field2"] | [D5] | 必需字段列表 |
| properties | { "field": schema } | [D5] | 对象属性定义 |
| items | schema | [D4] | 数组元素Schema |
| enum | [value1, value2] | [D7] | 枚举值约束 |
| const | value | [D8] | 固定值约束 |
| pattern | "regex" | [D6] | 字符串正则约束 |
| minimum/maximum | number | [D6] | 数值范围约束 |
| minLength/maxLength | number | [D6] | 字符串长度约束 |
| minItems/maxItems | number | [D4] | 数组长度约束 |
| additionalProperties | false/schema | [D5] | 额外属性控制 |
| allOf/anyOf/oneOf/not | [schema...] | [D7] | 组合约束 |
| if/then/else | schema | [D8] | 条件约束 |

### 校准数值

以下数值来自JSON Schema官方文档，供量级校准；其他Schema变体需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认行为 | 允许额外属性 | [D5] | 未设置additionalProperties时的默认行为 |
| 默认行为 | 属性可选 | [D5] | 未设置required时的默认行为 |
| 正则语法 | ECMA 262子集 | [D9] | JSON Schema支持的正则表达式语法 |
| 格式验证 | 可选启用 | [D3] | format关键字默认为注解，可配置为断言 |
| 嵌套限制 | 无硬性限制 | [D7] | 递归Schema可能导致性能问题 |

## 边界与分流

- **Schema版本不兼容**：不同JSON Schema版本（Draft 4/6/7/2019-09/2020-12）关键字可能不同，需确认版本
- **性能问题**：复杂组合Schema（allOf/anyOf/oneOf）可能显著增加验证时间
- **格式验证失败**：format关键字默认为注解，需显式启用格式断言
- **循环引用**：$ref和$recursiveRef可能导致无限递归，需设置深度限制
- **未知关键字**：Schema中包含未知关键字时，验证器通常忽略但不报错
- **空Schema**：{}匹配任何数据，可能掩盖验证缺失

## 质量检查

- 验证Schema本身是否为有效JSON
- 检查required字段是否在properties中定义
- 验证enum值是否唯一
- 检查minimum/maximum逻辑一致性
- 验证正则表达式语法正确性
- 检查嵌套Schema深度是否合理
- 验证$ref引用路径是否有效

## 回退策略

- Schema验证失败时，提供详细的错误位置和修复建议
- 格式验证不通过时，提供格式转换工具或正则修正建议
- 组合验证复杂时，拆分为多个简单Schema逐步验证
- 循环引用时，使用$recursiveRef或重构Schema结构
- 性能不足时，优化Schema结构或使用增量验证

## 资源召回建议

- 当需要定义JSON数据结构契约时召回本卡片
- 当需要验证JSON数据是否符合Schema时召回本卡片
- 当需要诊断JSON验证失败原因时召回本卡片
- 配套资源：JSON Schema官方文档、JSON验证器库（ajv、jsonschema等）

## 补充证据（开源文档）

[D1] JSON Schema reference, JSON Schema, 2020-12, URL: https://json-schema.org/understanding-json-schema/（accessed_at 2026-09-17，交叉验证）
[D2] JSON Schema - Type-specific Keywords, JSON Schema, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/type（accessed_at 2026-09-17，交叉验证）
[D3] JSON Schema - Schema annotations and comments, JSON Schema, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/metadata（accessed_at 2026-09-17，交叉验证）
[D4] JSON Schema - array, JSON Schema, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/array（accessed_at 2026-09-17，交叉验证）
[D5] JSON Schema - object, JSON Schema, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/object（accessed_at 2026-09-17，交叉验证）
[D6] JSON Schema - string, JSON Schema, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/string（accessed_at 2026-09-17，交叉验证）
[D7] JSON Schema - Boolean JSON Schema combination, JSON Schema, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/combining（accessed_at 2026-09-17，交叉验证）
[D8] JSON Schema - Conditional schema validation, JSON Schema, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/conditionals（accessed_at 2026-09-17，交叉验证）
[D9] JSON Schema - Regular Expressions, JSON Schema, 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/regular_expressions（accessed_at 2026-09-17，交叉验证）

## 证据来源

[1] JSON Schema官方参考文档
[2] JSON Schema类型关键字文档
[3] JSON Schema注解与评论文档
[4] JSON Schema数组验证文档
[5] JSON Schema对象验证文档
[6] JSON Schema字符串验证文档
[7] JSON Schema组合验证文档
[8] JSON Schema条件验证文档
[9] JSON Schema正则表达式文档

[D10] jsonschema - Python JSON Schema implementation, Python Software Foundation, version 4.26.0, URL: https://python-jsonschema.readthedocs.io/en/stable/（accessed_at 2026-09-17，交叉验证）

## 批次补充（2026-09-17：任务274案例补充）

### 实际应用案例

基于归因分析任务（任务ID：274，干雪雪崩危险等级日尺度预报）的JSON Schema报告交付契约案例：

#### JSON Schema报告交付契约案例
- **故障现象**：最终响应缺失、无法解析或字段校验失败
- **故障分类**：Schema验证失败
- **错误详情**：
  - 缺少顶层必填字段：`['issues', 'summary', 'task', 'task_id']`
  - 包含额外顶层字段（additionalProperties违规）：`['error', 'sessionID', 'timestamp', 'type']`
  - task_id与任务索引不一致（身份校验失败）
  - task与任务name不一致（身份校验失败）
  - summary必须是非空字符串（类型/格式校验失败）
  - issues必须是数组（类型校验失败）
- **修复方法**：
  - 在输出前按契约校验报告，确保所有必填字段存在
  - 移除Schema未定义的额外字段
  - 确保task_id与任务索引一致、task与任务name一致
- **预期修复点**：report.json可解析且与任务身份一致
- **验证方式**：以report-schema.json校验最终输出并执行错配字段反例测试

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 缺失必填字段 | 4 | 任务274案例 | issues, summary, task, task_id |
| 额外字段数 | 4 | 任务274案例 | error, sessionID, timestamp, type |
| 身份校验失败项 | 2 | 任务274案例 | task_id不匹配、task不匹配 |

## 批次补充 2026-09-17（归因分析任务58案例：Python jsonschema库集成）

### Python jsonschema 库验证实现

基于 Python jsonschema 官方文档 [D10]，补充 JSON Schema 报告交付契约在 Python 生态中的具体实现：

#### 核心验证 API
- `jsonschema.validate(instance, schema)` — 验证通过无返回，失败抛出 `ValidationError`
- `jsonschema.Draft202012Validator(schema)` — 创建惰性验证器，支持 `iter_errors()` 逐条报告所有错误
- 支持 Draft 3/4/6/7/2019-09/2020-12 全版本

#### ValidationError 关键属性
| 属性 | 说明 | 来源 |
|------|------|------|
| `.message` | 错误描述文本 | [D10] |
| `.validator` | 失败的关键字（如 "required", "type"） | [D10] |
| `.validator_value` | Schema 中该关键字的期望值 | [D10] |
| `.instance` | 验证失败的实际数据 | [D10] |
| `.path` | 失败位置在实例中的路径 | [D10] |
| `.schema_path` | 失败位置在 Schema 中的路径 | [D10] |

#### 报告交付前验证流程（CLI集成）
```python
from jsonschema import validate, ValidationError

schema = {
    "type": "object",
    "required": ["task_id", "task", "summary", "issues"],
    "properties": {
        "task_id": {"type": "string"},
        "task": {"type": "string"},
        "summary": {"type": "string", "minLength": 1},
        "issues": {"type": "array"}
    },
    "additionalProperties": False
}

try:
    validate(instance=report_json, schema=schema)
except ValidationError as e:
    # e.message: " 'task_id' is a required property"
    # e.validator: "required"
    # e.path: []  (顶层)
    classify_and_fix(e)
```

#### 常见校验失败模式
| 失败模式 | 错误关键字 | 修复方向 | 来源 |
|----------|-----------|----------|------|
| 缺失必填字段 | `required` | 补齐缺失字段 | [D10] |
| 类型不匹配 | `type` | 修正字段类型 | [D10] |
| 额外属性 | `additionalProperties` | 移除未声明字段 | [D10] |
| 数组长度违规 | `minItems`/`maxItems` | 调整数组元素数 | [D10] |
| 字符串格式违规 | `pattern`/`format` | 修正正则或格式 | [D10] |

#### 校准数值（Python jsonschema 场景，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| format 默认行为 | 注解（非断言） | [D10] | 需安装额外依赖启用格式断言 |
| 惰性验证 | iter_errors() | [D10] | 可一次收集所有错误而非首个即停 |
| 嵌套深度 | 无硬性限制 | [D10] | 复杂Schema可能影响性能 |

## 批次补充 2026-09-17（归因分析任务395案例：CLI执行与报告契约故障）

### 案例描述

任务395（钙钛矿太阳能电池氧诱导碘缺陷退化分析）的归因分析智能体未能交付有效的结构化报告，故障模式与任务274高度相似：

- **故障现象**：CLI进程退出码为1，报告校验错误：缺少顶层字段 `['issues', 'summary', 'task', 'task_id']`；包含额外顶层字段 `['error', 'sessionID', 'timestamp', 'type']`；task_id与任务索引不一致；task与任务name不一致。
- **故障分类**：CLI非交互执行失败 + JSON Schema报告交付契约违反
- **根因分析**：
  1. CLI进程未正常退出（退出码1），可能由参数错误、认证失败、沙箱隔离或超时引起
  2. 输出报告不符合预定义Schema，缺少必填字段且包含未声明字段
- **修复方法**：
  1. 修正CLI启动配置，确保命令参数、认证、沙箱设置正确
  2. 在输出前使用JSON Schema校验报告，确保字段完整性和身份一致性
- **验证方式**：使用成功、非零退出和超时用例验证状态及日志；以report-schema.json校验最终输出并执行错配字段反例测试

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 缺失必填字段 | 4 | 任务395案例 | issues, summary, task, task_id |
| 额外字段数 | 4 | 任务395案例 | error, sessionID, timestamp, type |
| 身份校验失败项 | 2 | 任务395案例 | task_id不匹配、task不匹配 |
| 退出码 | 1 | 任务395案例 | 通用错误，catchall for general errors |

## 批次补充 2026-09-17（归因分析任务75案例：CLI执行与报告契约故障）

### 案例描述

任务75（空间转录组与蛋白组图基础表征）的归因分析智能体未能交付有效的结构化报告，故障模式与任务274、任务395高度相似：

- **故障现象**：CLI进程退出码为1，报告校验错误：缺少顶层字段 `['issues', 'summary', 'task', 'task_id']`；包含额外顶层字段 `['error', 'sessionID', 'timestamp', 'type']`；task_id与任务索引不一致；task与任务name不一致。
- **故障分类**：CLI非交互执行失败 + JSON Schema报告交付契约违反
- **根因分析**：
  1. CLI进程未正常退出（退出码1），可能由参数错误、认证失败、沙箱隔离或超时引起
  2. 输出报告不符合预定义Schema，缺少必填字段且包含未声明字段
- **修复方法**：
  1. 修正CLI启动配置，确保命令参数、认证、沙箱设置正确
  2. 在输出前使用JSON Schema校验报告，确保字段完整性和身份一致性
- **验证方式**：使用成功、非零退出和超时用例验证状态及日志；以report-schema.json校验最终输出并执行错配字段反例测试

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 缺失必填字段 | 4 | 任务75案例 | issues, summary, task, task_id |
| 额外字段数 | 4 | 任务75案例 | error, sessionID, timestamp, type |
| 身份校验失败项 | 2 | 任务75案例 | task_id不匹配、task不匹配 |
| 退出码 | 1 | 任务75案例 | 通用错误，catchall for general errors |

## 批次补充 2026-09-17（归因分析任务281案例：CLI执行与报告契约故障）

### 案例描述

任务281（气候情景驱动的地下水位长期投影）的归因分析智能体未能交付有效的结构化报告，故障模式与任务274、任务395、任务75高度相似：

- **故障现象**：CLI进程退出码为1，报告校验错误：缺少顶层字段 `['issues', 'summary', 'task', 'task_id']`；包含额外顶层字段 `['error', 'sessionID', 'timestamp', 'type']`；task_id与任务索引不一致；task与任务name不一致。
- **故障分类**：CLI非交互执行失败 + JSON Schema报告交付契约违反
- **根因分析**：
  1. CLI进程未正常退出（退出码1），可能由参数错误、认证失败、沙箱隔离或超时引起
  2. 输出报告不符合预定义Schema，缺少必填字段且包含未声明字段
- **修复方法**：
  1. 修正CLI启动配置，确保命令参数、认证、沙箱设置正确
  2. 在输出前使用JSON Schema校验报告，确保字段完整性和身份一致性
- **验证方式**：使用成功、非零退出和超时用例验证状态及日志；以report-schema.json校验最终输出并执行错配字段反例测试

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 缺失必填字段 | 4 | 任务281案例 | issues, summary, task, task_id |
| 额外字段数 | 4 | 任务281案例 | error, sessionID, timestamp, type |
| 身份校验失败项 | 2 | 任务281案例 | task_id不匹配、task不匹配 |
| 退出码 | 1 | 任务281案例 | 通用错误，catchall for general errors |

## 批次补充 2026-09-17（归因分析任务292案例：CLI执行与报告契约故障）

### 案例描述

任务292（渤黄海海浪智能预报模型）的归因分析智能体未能交付有效的结构化报告，故障模式与任务274、任务395、任务75、任务281高度相似：

- **故障现象**：CLI进程退出码为1，报告校验错误：缺少顶层字段 `['issues', 'summary', 'task', 'task_id']`；包含额外顶层字段 `['error', 'sessionID', 'timestamp', 'type']`；task_id与任务索引不一致；task与任务name不一致。
- **故障分类**：CLI非交互执行失败 + JSON Schema报告交付契约违反
- **根因分析**：
  1. CLI进程未正常退出（退出码1），可能由参数错误、认证失败、沙箱隔离或超时引起
  2. 输出报告不符合预定义Schema，缺少必填字段且包含未声明字段
- **修复方法**：
  1. 修正CLI启动配置，确保命令参数、认证、沙箱设置正确
  2. 在输出前使用JSON Schema校验报告，确保字段完整性和身份一致性
- **验证方式**：使用成功、非零退出和超时用例验证状态及日志；以report-schema.json校验最终输出并执行错配字段反例测试

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 缺失必填字段 | 4 | 任务292案例 | issues, summary, task, task_id |
| 额外字段数 | 4 | 任务292案例 | error, sessionID, timestamp, type |
| 身份校验失败项 | 2 | 任务292案例 | task_id不匹配、task不匹配 |
| 退出码 | 1 | 任务292案例 | 通用错误，catchall for general errors |

## 批次补充 2026-09-17（归因分析任务243案例：CLI执行与报告契约故障）

### 案例描述

任务243（印度洋偶极子多季节指数预测）的归因分析智能体未能交付有效的结构化报告，故障模式与之前案例高度相似：

- **故障现象**：CLI进程退出码为1，报告校验错误：缺少顶层字段 `['issues', 'summary', 'task', 'task_id']`；包含额外顶层字段 `['error', 'sessionID', 'timestamp', 'type']`；task_id与任务索引不一致；task与任务name不一致。
- **故障分类**：CLI非交互执行失败 + JSON Schema报告交付契约违反
- **根因分析**：
  1. CLI进程未正常退出（退出码1），可能由参数错误、认证失败、沙箱隔离或超时引起
  2. 输出报告不符合预定义Schema，缺少必填字段且包含未声明字段
- **修复方法**：
  1. 修正CLI启动配置，确保命令参数、认证、沙箱设置正确
  2. 在输出前使用JSON Schema校验报告，确保字段完整性和身份一致性
- **验证方式**：使用成功、非零退出和超时用例验证状态及日志；以report-schema.json校验最终输出并执行错配字段反例测试

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 缺失必填字段 | 4 | 任务243案例 | issues, summary, task, task_id |
| 额外字段数 | 4 | 任务243案例 | error, sessionID, timestamp, type |
| 身份校验失败项 | 2 | 任务243案例 | task_id不匹配、task不匹配 |
| 退出码 | 1 | 任务243案例 | 通用错误，catchall for general errors |

## 批次补充 2026-09-18（归因分析任务256案例：CLI执行与报告契约故障）

### 案例描述

任务256（多源原始观测驱动的全球分析—预报闭环）的归因分析智能体未能交付有效的结构化报告，故障模式与之前案例高度相似：

- **故障现象**：CLI进程退出码为1，报告校验错误：缺少顶层字段 `['issues', 'summary', 'task', 'task_id']`；包含额外顶层字段 `['error', 'sessionID', 'timestamp', 'type']`；task_id与任务索引不一致；task与任务name不一致。
- **故障分类**：CLI非交互执行失败 + JSON Schema报告交付契约违反
- **根因分析**：
  1. CLI进程未正常退出（退出码1），可能由参数错误、认证失败、沙箱隔离或超时引起
  2. 输出报告不符合预定义Schema，缺少必填字段且包含未声明字段
- **修复方法**：
  1. 修正CLI启动配置，确保命令参数、认证、沙箱设置正确
  2. 在输出前使用JSON Schema校验报告，确保字段完整性和身份一致性
- **验证方式**：使用成功、非零退出和超时用例验证状态及日志；以report-schema.json校验最终输出并执行错配字段反例测试

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 缺失必填字段 | 4 | 任务256案例 | issues, summary, task, task_id |
| 额外字段数 | 4 | 任务256案例 | error, sessionID, timestamp, type |
| 身份校验失败项 | 2 | 任务256案例 | task_id不匹配、task不匹配 |
| 退出码 | 1 | 任务256案例 | 通用错误，catchall for general errors |

## 批次补充 2026-09-18（归因分析任务CFD_S045案例：JSON语法错误型报告交付故障）

### 案例描述

任务CFD_S045（符号与稀疏物理学习控制方程发现）的归因分析智能体未能交付有效的结构化报告。与其他案例不同，本案例的故障发生在 **JSON 解析阶段**而非 Schema 验证阶段：

- **故障现象**：CLI进程退出码为1，报告校验错误：报告根节点不是 JSON 对象；JSON 语法错误：Expecting ',' delimiter: line 1 column 6273 (char 6272)
- **故障分类**：JSON 语法错误（解析阶段失败，未到达 Schema 校验）
- **根因分析**：
  1. 输出内容在字符位置 6272 处存在 JSON 语法错误（缺少逗号分隔符），导致解析器无法构建有效 JSON 对象
  2. 该错误类型不同于 Schema 验证失败——数据甚至无法被解析为 JSON，因此 Schema 校验不会执行
- **修复方法**：
  1. 检查输出序列化逻辑，确保所有对象属性间有正确的逗号分隔
  2. 在输出前使用 `json.dumps()` 或等效工具验证 JSON 格式，而非仅做 Schema 校验
  3. 对长 JSON 输出增加格式完整性预检（如括号/引号匹配检查）
- **验证方式**：使用 `json.loads()` 对最终输出做语法验证；以 report-schema.json 校验最终输出并执行错配字段反例测试

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 故障子类型 | JSON语法错误 | CFD_S045案例 | 不同于Schema验证失败，属于解析阶段 |
| 错误位置 | line 1 column 6273 (char 6272) | CFD_S045案例 | 字符级定位，报告根节点非JSON对象 |
| 错误关键字 | Expecting ',' delimiter | CFD_S045案例 | 缺少逗号分隔符 |
| 退出码 | 1 | CFD_S045案例 | 通用错误，catchall for general errors |

### 故障模式区分

本案例揭示了一个重要的故障层级区分：

| 故障阶段 | 错误类型 | 校验层级 | 本案例状态 |
|----------|---------|---------|-----------|
| 解析阶段 | JSON语法错误 | json.loads() | ❌ 失败 |
| Schema阶段 | 字段缺失/类型不匹配 | jsonschema.validate() | 未到达 |
| 语义阶段 | 身份不一致 | 自定义逻辑 | 未到达 |

## 批次补充 2026-09-18（归因分析任务232案例：CLI执行与报告契约故障）

### 案例描述

任务232（全球航空危险云微物理要素1—7天预报）的归因分析智能体未能交付有效的结构化报告，故障模式与之前案例高度相似：

- **故障现象**：CLI进程退出码为1，报告校验错误：缺少顶层字段 `['issues', 'summary', 'task', 'task_id']`；包含额外顶层字段 `['error', 'sessionID', 'timestamp', 'type']`；task_id与任务索引不一致；task与任务name不一致。
- **故障分类**：CLI非交互执行失败 + JSON Schema报告交付契约违反
- **根因分析**：
  1. CLI进程未正常退出（退出码1），可能由参数错误、认证失败、沙箱隔离或超时引起
  2. 输出报告不符合预定义Schema，缺少必填字段且包含未声明字段
- **修复方法**：
  1. 修正CLI启动配置，确保命令参数、认证、沙箱设置正确
  2. 在输出前使用JSON Schema校验报告，确保字段完整性和身份一致性
- **验证方式**：使用成功、非零退出和超时用例验证状态及日志；以report-schema.json校验最终输出并执行错配字段反例测试

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 缺失必填字段 | 4 | 任务232案例 | issues, summary, task, task_id |
| 额外字段数 | 4 | 任务232案例 | error, sessionID, timestamp, type |
| 身份校验失败项 | 2 | 任务232案例 | task_id不匹配、task不匹配 |
| 退出码 | 1 | 任务232案例 | 通用错误，catchall for general errors |