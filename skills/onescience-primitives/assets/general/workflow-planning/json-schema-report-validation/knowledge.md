# JSON Schema 结构化报告验证流程

## 适用范围

面向自动化工具链中结构化报告交付的验证场景，提供 JSON Schema 契约定义、字段校验、类型约束检查与任务身份一致性判定流程。适用于归因分析报告、数据处理报告、模型评估报告等需要按契约格式交付的 JSON 文档。

## 输入

- 待验证的 JSON 报告文档
- 目标 JSON Schema 定义（必填字段、类型约束、数组约束）
- 任务身份信息（task_id、task_name）

## 输出

- 验证结果（通过/失败）
- 错误详情列表（缺失字段、类型错误、约束违反）
- 修复建议

## 流程节点

### 节点1：JSON 解析与基础校验

```python
import json
try:
    data = json.loads(json_string)
except json.JSONDecodeError as e:
    # 记录解析错误：行号、列号、错误位置
```

- 操作：尝试解析 JSON 字符串
- 质量门禁：必须通过 JSON 语法检查
- 错误处理：记录精确的解析失败位置

### 节点2：必填字段校验

检查顶层字段是否存在：
- `task_id`：任务编号（字符串/整数）
- `task`：任务名称（字符串）
- `summary`：摘要（非空字符串）
- `issues`：问题列表（数组）

- 校验规则：
  - 字段必须存在（非 undefined/null）
  - `summary` 不能为空字符串
  - `issues` 必须是数组类型（即使为空数组）
- 错误模式：`缺少顶层字段: ['field1', 'field2']`

### 节点3：类型约束检查

| 字段 | 预期类型 | 约束条件 |
|------|----------|----------|
| task_id | string/int | 必须匹配任务索引 |
| task | string | 必须与任务 name 一致 |
| summary | string | 非空 |
| issues | array | 可为空数组，不可为 null |
| issues[].failed_check | string | 非空 |
| issues[].error_detail | string | 非空 |

- 校验规则：
  - 严格类型匹配（不允许类型隐式转换）
  - 字符串不可为空或仅含空白
  - 数组元素类型一致性

### 节点4：任务身份一致性判定

```python
assert data["task_id"] == expected_task_id, f"task_id 不匹配: {data['task_id']} vs {expected_task_id}"
assert data["task"] == expected_task_name, f"task 不匹配: {data['task']} vs {expected_task_name}"
```

- 校验规则：
  - `task_id` 必须与任务索引完全一致
  - `task` 必须与任务名称完全一致（区分大小写）
  - 不一致时记录错配详情

### 节点5：额外字段检测

检测并报告未预期的顶层字段：
- 预期字段白名单：`["task_id", "task", "summary", "issues"]`
- 额外字段应记录为警告（不阻断验证）
- 错误模式：`包含额外顶层字段: ['error', 'sessionID', 'timestamp', 'type']`

### 节点6：数组约束验证

针对 `issues` 数组的内部约束：
- 每个元素必须是对象
- 必填子字段：`failed_check`、`error_detail`
- 可选子字段：`location`、`capability_attributions`、`optimization_plan`

## 关键参数

| 参数 | 预期值 | 来源 | 说明 |
|------|--------|------|------|
| required_fields | ["task_id", "task", "summary", "issues"] | [D1] | 顶层必填字段 |
| summary_type | string (non-empty) | [D1] | 摘要必须是非空字符串 |
| issues_type | array | [D1] | 问题列表必须是数组 |
| identity_match | exact | 报告契约 | task_id 和 task 必须完全匹配 |

## 边界与分流

### 解析失败场景
- JSON 语法错误 → 记录位置信息 → 终止验证
- 编码问题 → 尝试 UTF-8 解码

### 字段缺失场景
- 必填字段缺失 → 记录缺失字段列表 → 标记为失败
- 可选字段缺失 → 跳过相关校验 → 继续验证

### 类型错误场景
- 类型不匹配 → 记录期望类型与实际类型 → 标记为失败
- null 值 → 检查字段是否允许 null

### 身份不一致场景
- task_id 不匹配 → 记录期望值与实际值 → 标记为失败
- task 不匹配 → 记录期望值与实际值 → 标记为失败

## 质量检查

- [ ] JSON 语法正确
- [ ] 所有必填字段存在
- [ ] 字段类型符合预期
- [ ] 任务身份一致
- [ ] 无意外的额外字段
- [ ] 数组元素结构正确

## 回退策略

1. **解析修复**：修正 JSON 语法错误后重新提交
2. **字段补全**：添加缺失的必填字段
3. **类型修正**：将字段值转换为预期类型
4. **身份对齐**：修正 task_id 和 task 字段
5. **格式降级**：接受部分字段缺失但保留核心信息

## 资源召回建议

当以下场景出现时应召回本卡片：
- 结构化报告校验失败（字段缺失、类型错误）
- 归因分析输出不符合 Schema 契约
- 需要定义 JSON 报告的必填字段和约束
- 需要验证任务身份一致性

## 补充证据（开源权威文档）

[D1] JSON Schema reference documentation, JSON Schema Organization, v2020-12, URL: https://json-schema.org/understanding-json-schema/reference（accessed_at 2026-09-17，权威文档单源参考）

## 证据来源

[无论文证据，本卡基于权威技术文档生成]