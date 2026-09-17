# CLI JSON Schema报告交付契约验证

## 适用范围
适用于所有CLI工具产出的JSON格式结构化报告，包括归因分析报告、任务执行结果、元数据输出等。当报告需要符合预定义Schema契约时，本卡片提供校验框架与故障诊断方法。

不适用于：非JSON格式输出（XML、CSV、YAML）；实时流式输出；二进制格式数据。

## 输入
- 待校验的JSON输出内容或文件路径
- 目标JSON Schema定义（必填字段、类型约束、数组约束等）
- 任务元数据（task_id、task名称等，用于身份一致性验证）

## 输出
- 校验结果（通过/失败）
- 失败详情（缺失字段、类型错误、额外字段等）
- 修复建议

## 流程节点
1. JSON解析 → 2. 必填字段校验 → 3. 类型约束检查 → 4. 任务身份一致性 → 5. 数组约束确认 → 6. 额外字段检测

### 节点1：JSON解析
- **操作**：尝试解析JSON字符串或文件
- **参数**：JSON内容
- **工具**：json.loads() / json.load()
- **质量门禁**：必须捕获JSONDecodeError并报告解析失败原因

### 节点2：必填字段校验
- **操作**：检查Schema中required数组指定的字段是否存在
- **参数**：JSON对象、required数组
- **工具**：集合差集运算
- **质量门禁**：缺失字段必须逐一列出

### 节点3：类型约束检查
- **操作**：验证每个字段的类型是否符合Schema定义
- **参数**：JSON对象、properties定义
- **工具**：类型检查函数
- **质量门禁**：类型不匹配必须指出期望类型与实际类型

### 节点4：任务身份一致性
- **操作**：验证task_id和task字段与预期值匹配
- **参数**：JSON对象中的task_id/task、预期值
- **工具**：字符串比较
- **质量门禁**：不匹配时必须明确指出差异

### 节点5：数组约束确认
- **操作**：验证数组字段的minItems、maxItems、items类型
- **参数**：JSON数组、Schema数组约束
- **工具**：长度检查、元素类型检查
- **质量门禁**：数组越界或类型错误必须明确报告

### 节点6：额外字段检测
- **操作**：检查是否存在Schema未定义的额外字段
- **参数**：JSON对象、Schema properties
- **工具**：集合差集运算
- **质量门禁**：额外字段必须列出（取决于Schema是否允许additionalProperties）

## 关键参数

### 通用判据（方法层）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| required字段缺失 | 校验失败 | [D1] JSON Schema object | 必填字段未出现时返回错误 |
| 类型不匹配 | 校验失败 | [D1] JSON Schema object | 字段值类型与Schema定义不符 |
| 数组越界 | 校验失败 | [D1] JSON Schema object | 数组长度超出minItems/maxItems |
| 额外字段（additionalProperties:false） | 校验失败 | [D1] JSON Schema object | 出现Schema未定义的字段 |
| JSON解析失败 | 校验失败 | JSON规范 | 输入不是合法JSON语法 |

### 校准数值
以下数值来自归因报告契约，供量级校准；其他系统需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 必填字段 | issues, summary, task, task_id | 归因报告契约 | 归因报告的顶层必填字段 |
| task_id类型 | 字符串 | 归因报告契约 | 必须与任务索引一致 |
| task类型 | 字符串 | 归因报告契约 | 必须与任务name一致 |
| summary类型 | 非空字符串 | 归因报告契约 | 不允许空字符串 |
| issues类型 | 数组 | 归因报告契约 | 必须是数组类型 |

## 边界与分流
- **JSON解析失败**：检查输入是否为空、编码是否正确、是否为截断输出
- **必填字段缺失**：检查CLI输出逻辑是否遗漏字段生成
- **类型不匹配**：检查数值是否被错误序列化为字符串，或反之
- **任务身份不匹配**：检查CLI是否正确传递了task_id和task参数
- **数组为空但required非空**：检查业务逻辑是否允许空结果

## 质量检查
- JSON解析无语法错误
- 所有required字段均存在
- 字段类型符合Schema定义
- task_id与任务索引一致
- task与任务name一致
- summary为非空字符串
- issues为数组类型
- 无未定义的额外字段（如Schema要求严格）

## 回退策略
- JSON解析失败时：尝试修复常见问题（尾部逗号、编码问题）后重试
- Schema文件缺失时：使用最小必填字段集进行基础校验
- 部分字段校验失败时：输出已通过字段和失败字段列表，便于定位

## 资源召回建议
当遇到以下情况时召回本卡片：
- CLI输出JSON格式报告
- 报告校验失败（字段缺失、类型错误）
- 需要验证结构化输出契约
- 归因分析报告生成失败
- 需要定义JSON Schema约束

配套资源：
- cli-noninteractive-fault-diagnosis：CLI非交互执行与故障分类

## 补充证据（权威文档）
[D1] JSON Schema - object, JSON Schema Organization, Draft 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/object（accessed_at 2026-09-17，官方权威文档）
[D2] JSON Schema - boolean, JSON Schema Organization, Draft 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/boolean（accessed_at 2026-09-17，官方权威文档）

## 证据来源
[1] JSON Schema - object, Understanding JSON Schema
[2] JSON Schema - boolean, Understanding JSON Schema
