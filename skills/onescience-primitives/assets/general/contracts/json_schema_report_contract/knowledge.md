# JSON Schema报告交付契约

## 适用场景

当任务需要生成结构化报告并交付给下游消费者时，本契约规定报告的格式、校验规则和交付要求。适用于：
- 归因分析报告
- 任务执行报告
- 验证结果报告
- 诊断分析报告
- 评估结果报告

## 报告结构要求

### 1. 根节点要求

报告根节点必须是JSON对象，不能是数组、字符串、数字或null。

**错误示例**：
```json
[
  {"task_id": "1", "status": "success"}
]
```

**正确示例**：
```json
{
  "task_id": "1",
  "status": "success"
}
```

### 2. 必填字段

#### 2.1 任务身份字段

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `task_id` | string | 是 | 任务唯一标识符，必须与输入任务ID匹配 |
| `task_name` | string | 是 | 任务名称，必须与输入任务名称匹配 |
| `timestamp` | string | 是 | 报告生成时间戳，ISO 8601格式 |
| `version` | string | 是 | 报告版本号，语义化版本格式 |

#### 2.2 状态字段

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `status` | string | 是 | 任务执行状态：`success`、`partial`、`failed`、`blocked` |
| `summary` | string | 是 | 任务执行摘要，简要描述执行结果 |
| `execution_time_seconds` | number | 否 | 执行耗时（秒） |

#### 2.3 结果字段

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `issues` | array | 是 | 问题列表，至少包含一个元素 |
| `artifacts` | object | 否 | 产物信息，包含生成的文件和目录 |
| `observations` | object | 否 | 观察信息，包含执行过程中的观察记录 |

### 3. 问题对象结构

每个`issues`数组中的元素必须包含以下字段：

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `failed_check` | string | 是 | 失败的检查项名称 |
| `location` | string | 是 | 问题发生的位置（文件路径、函数名等） |
| `error_detail` | string | 是 | 详细的错误信息 |
| `error_propagation` | string | 否 | 错误传播路径和影响 |
| `capability_attributions` | array | 是 | 能力归因列表 |
| `responsibility_attribution` | string | 是 | 责任归属描述 |
| `optimization_plan` | array | 是 | 优化建议列表 |

#### 3.1 能力归因值

`capability_attributions`数组中的值必须是以下枚举之一：
- `结果生成错误`：报告生成过程中出现错误
- `数据处理错误`：数据预处理或转换错误
- `模型执行错误`：模型训练或推理错误
- `环境配置错误`：环境或配置问题
- `资源访问错误`：文件、网络或API访问错误
- `参数配置错误`：输入参数错误
- `依赖缺失错误`：缺少必要的依赖或资源

#### 3.2 优化建议结构

每个`optimization_plan`元素必须包含：

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `需补充的知识` | string | 是 | 需要补充的知识类型 |
| `知识缺失证据` | string | 是 | 证明知识缺失的证据 |
| `知识内容与边界` | string | 是 | 知识的内容和边界说明 |
| `应用动作` | string | 是 | 基于该知识应采取的动作 |
| `预期修复点` | string | 是 | 修复后的预期结果 |
| `验证方式` | string | 是 | 验证修复效果的方法 |

## 校验规则

### 1. Schema校验

报告必须通过JSON Schema校验。基本校验规则：

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["task_id", "task_name", "timestamp", "version", "status", "summary", "issues"],
  "properties": {
    "task_id": {
      "type": "string",
      "minLength": 1
    },
    "task_name": {
      "type": "string",
      "minLength": 1
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "status": {
      "type": "string",
      "enum": ["success", "partial", "failed", "blocked"]
    },
    "summary": {
      "type": "string",
      "minLength": 1
    },
    "issues": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["failed_check", "location", "error_detail", "capability_attributions", "responsibility_attribution", "optimization_plan"],
        "properties": {
          "failed_check": {"type": "string"},
          "location": {"type": "string"},
          "error_detail": {"type": "string"},
          "error_propagation": {"type": "string"},
          "capability_attributions": {
            "type": "array",
            "items": {
              "type": "string",
              "enum": ["结果生成错误", "数据处理错误", "模型执行错误", "环境配置错误", "资源访问错误", "参数配置错误", "依赖缺失错误"]
            }
          },
          "responsibility_attribution": {"type": "string"},
          "optimization_plan": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["需补充的知识", "知识缺失证据", "知识内容与边界", "应用动作", "预期修复点", "验证方式"],
              "properties": {
                "需补充的知识": {"type": "string"},
                "知识缺失证据": {"type": "string"},
                "知识内容与边界": {"type": "string"},
                "应用动作": {"type": "string"},
                "预期修复点": {"type": "string"},
                "验证方式": {"type": "string"}
              }
            }
          }
        }
      }
    }
  }
}
```

### 2. 身份一致性校验

报告中的`task_id`和`task_name`必须与输入任务的身份信息完全匹配。

### 3. 数组约束校验

- `issues`数组必须至少包含一个元素
- `capability_attributions`数组必须至少包含一个元素
- `optimization_plan`数组必须至少包含一个元素

## 校验流程

### 1. 输出前校验

在生成报告后、交付前，必须执行以下校验：

1. **JSON格式校验**：确保输出是有效的JSON
2. **Schema校验**：使用上述JSON Schema进行校验
3. **身份一致性校验**：验证task_id和task_name
4. **数组约束校验**：验证必填数组字段
5. **枚举值校验**：验证所有枚举字段的值

### 2. 校验失败处理

校验失败时，应：

1. 记录具体的校验错误信息
2. 尝试自动修复（如补充缺失字段、修正格式）
3. 如果无法自动修复，返回校验失败状态和详细错误信息
4. 不交付不符合契约的报告

### 3. 校验工具

建议使用以下工具进行校验：

- Python: `jsonschema`库
- Node.js: `ajv`库
- 在线工具: JSON Schema Validator

## 交付要求

### 1. 交付格式

报告必须以JSON格式交付，编码为UTF-8。

### 2. 交付方式

根据下游消费者需求，支持以下交付方式：

1. **直接输出**：在命令行或API响应中直接输出JSON
2. **文件交付**：写入JSON文件到指定路径
3. **消息队列**：通过消息队列发送
4. **数据库存储**：存储到数据库的JSON字段

### 3. 交付验证

交付后，下游消费者应验证：

1. JSON格式正确
2. 必填字段存在
3. 字段类型正确
4. 身份信息匹配
5. 业务逻辑合理

## 边界说明

本契约专注于报告的格式和交付规范，不涉及：
- 报告内容的科学正确性（由领域专家技能保证）
- 业务逻辑的合理性（由任务执行技能保证）
- 数据的准确性（由数据处理技能保证）

本契约只保证报告格式符合规范，内容可被下游系统正确解析和处理。

## 归因分析报告校验案例（新增）

### 案例：任务70归因分析报告校验失败

**错误表现**：
- 报告校验错误：缺少顶层字段: ['issues', 'summary', 'task', 'task_id']
- 包含额外顶层字段: ['error', 'sessionID', 'timestamp', 'type']
- task_id 与任务索引不一致
- task 与任务 name 不一致
- summary 必须是非空字符串
- issues 必须是数组

**诊断方法**：
1. 检查报告JSON结构是否符合Schema
2. 验证必填字段是否存在
3. 核对task_id和task字段与任务索引的一致性
4. 检查字段类型是否正确

**修复建议**：
- 在输出前执行Schema预校验
- 使用模板确保字段格式正确
- 实现自动身份信息注入
- 添加输出格式断言检查

**验证方式**：
- 使用report-schema.json校验最终输出
- 执行错配字段反例测试

## 证据来源
[1] 基于通用JSON Schema最佳实践和报告交付经验总结
[2] 基于归因分析报告校验案例分析
[3] 基于任务70归因报告中的JSON Schema校验案例总结（新增）