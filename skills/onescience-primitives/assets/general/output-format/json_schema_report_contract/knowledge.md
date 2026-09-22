# JSON Schema 报告交付契约规范

## 适用范围

适用于需要通过CLI或API交付结构化JSON报告的自动化任务。本知识定义报告的必填字段、身份验证机制、数组约束及输出格式标准，确保报告可被下游系统正确解析、验证和路由。典型应用场景包括：归因分析报告、质量检查报告、结构化测试结果、API响应契约。

不适用于：非结构化文本输出、二进制文件、流式数据、实时日志。

## 输入

- 任务上下文：task_id（任务编号）、task（任务名称）
- 任务产物：待封装为JSON格式的分析结果、检查结果或执行状态
- Schema定义：report-schema.json（可选，用于运行时校验）

## 输出

符合契约的JSON报告，包含以下必填结构：

```json
{
  "task_id": "string",
  "task": "string",
  "summary": "string (non-empty)",
  "issues": "array"
}
```

验证标准：
- JSON可解析（valid JSON）
- 包含所有必填顶层字段
- task_id与任务索引一致
- task与任务name一致
- summary为非空字符串
- issues为数组类型

## 流程节点

### 1. 报告组装

1. 收集任务执行结果和诊断信息
2. 按契约格式组织字段
3. 填充task_id和task身份信息
4. 生成summary摘要（确保非空）
5. 组装issues数组（即使为空也必须存在）

### 2. 身份验证

1. 校验task_id与任务索引一致
2. 校验task与任务name一致
3. 不一致时记录为报告错误

### 3. 结构校验

1. 使用JSON Schema校验必填字段
2. 校验字段类型和约束
3. 检查是否存在额外顶层字段
4. 记录校验错误

### 4. 输出交付

1. 将校验通过的报告写入report.json
2. 记录交付状态（成功/失败）
3. 保留诊断证据

## 关键参数

### 必填字段表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| task_id | string | 与任务索引一致 | 任务唯一标识 |
| task | string | 与任务name一致 | 任务名称 |
| summary | string | non-empty | 任务摘要 |
| issues | array | 必须存在 | 问题列表（可为空数组） |

### 禁止字段

以下顶层字段不应出现在报告中：
- error（应通过issues记录）
- sessionID（应由系统管理）
- timestamp（应由系统管理）
- type（报告类型由结构隐含）

### JSON Schema 示例

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["task_id", "task", "summary", "issues"],
  "properties": {
    "task_id": {"type": "string"},
    "task": {"type": "string"},
    "summary": {"type": "string", "minLength": 1},
    "issues": {"type": "array", "items": {"type": "object"}}
  },
  "additionalProperties": false
}
```

## 边界与分流

- **字段缺失**：必填字段缺失 → 报告校验失败，记录缺失字段列表
- **身份不匹配**：task_id/task与任务上下文不一致 → 记录身份错配错误
- **额外字段**：存在禁止的顶层字段 → 记录警告，不影响核心校验
- **数组为空**：issues为空数组 → 合法，表示无问题
- **Schema不可用**：无report-schema.json时 → 使用内置必填字段列表校验

## 质量检查

- 验证点1：JSON可解析（json.loads成功）
- 验证点2：必填字段完整且类型正确
- 验证点3：task_id与任务索引一致
- 验证点4：summary非空
- 验证点5：无额外顶层字段（或仅允许白名单字段）
- 失败处理：任一检查失败 → 标记报告为无效，保留诊断证据

## 回退策略

- Schema校验工具不可用 → 使用内置字段检查
- JSON格式错误 → 记录原始输出，尝试修复或标记失败
- 身份信息缺失 → 从任务上下文推断，标记为"待确认"

## 资源召回建议

当遇到以下场景时召回本卡片：
- CLI工具输出JSON报告校验失败
- 归因分析报告结构不符合Schema
- API响应格式需要标准化
- 自动化流水线中JSON输出需要契约验证

配套资源：
- cli_fault_classification：CLI执行故障诊断
- json_schema_validation：JSON Schema验证工具

## 证据来源

[1] Validation of Modern JSON Schema: Formalization and Complexity, Lyes Attouche et al., Proceedings of the ACM on Programming Languages, 2024, DOI: 10.1145/3632891
[2] Schema validation and evaluation framework for extracted schemas in JSON databases, Saad Belefqih et al., Scientific Reports, 2026, DOI: 10.1038/s41598-026-45554-6
[3] Witness Generation for JSON Schema, Lyes Attouche et al., Proceedings of the VLDB Endowment, 2022, DOI: 10.14778/3565838.3565852
[4] Blaze: Compiling JSON Schema for 10x Faster Validation, Juan Cruz Viotti et al., Proceedings of the VLDB Endowment, 2025, DOI: 10.14778/3773749.3773764
[5] Improving Api Test Accuracy through Schema Validation and Real-time Json Assertions in Jenkins Pipelines, Udayan Verma, International Journal on Science and Technology, 2025, DOI: 10.71097/ijsat.v16.i3.10656