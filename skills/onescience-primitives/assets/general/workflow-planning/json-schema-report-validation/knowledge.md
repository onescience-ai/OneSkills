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
| schema_validity_rate | 100% (strong models) | [1] | Schema 约束可保证结构有效性 |
| semantic_success_rate | ~80% (strong models) | [1] | 即使 schema 有效，语义正确率仍有缺口 |
| constraint_tax_accuracy_drop | 19.7%→11.0% | [2] | 硬 schema 约束导致小模型答案准确率下降 |
| schema_validity_gain | 61.5%→100.0% | [2] | 硬 schema 约束将结构有效性提升至 100% |
| wrong_valid_rate | 49.5%→88.9% | [2] | 硬约束下"结构正确但语义错误"的比例上升 |

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

### Schema 有效性 vs 语义正确性场景
- Schema 验证通过但内容语义错误 → 记录为"wrong-valid-schema" → 需要领域验证层
- 小模型在硬 schema 约束下准确率下降 → 采用"先自由推理、后约束打包"策略 [2]
- Schema 描述与 prompt 指令冲突 → 保持单一事实来源，避免 prompt/schema 漂移 [3]

## 质量检查

- [ ] JSON 语法正确
- [ ] 所有必填字段存在
- [ ] 字段类型符合预期
- [ ] 任务身份一致
- [ ] 无意外的额外字段
- [ ] 数组元素结构正确
- [ ] Schema 有效性与语义正确性分别报告（[1][2]）
- [ ] 避免 prompt/schema 指令漂移（[3]）

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
- 需要区分 schema 有效性与语义正确性（[1][2]）
- 需要设计 schema 描述以避免与 prompt 指令冲突（[3]）

## 补充证据（开源权威文档）

[D1] JSON Schema reference documentation, JSON Schema Organization, v2020-12, URL: https://json-schema.org/understanding-json-schema/reference（accessed_at 2026-09-17，权威文档单源参考）

## 证据来源

[1] When JSON Is Not Enough: Semantic Reliability of Schema-Constrained LLM Ordering Agents, Yin Li, arXiv 2026, DOI: 10.48550/arXiv.2607.18261v1
[2] The Constraint Tax: Measuring Validity-Correctness Tradeoffs in Structured Outputs for Small Language Models, Jaideep Ray, arXiv 2026, DOI: 10.48550/arXiv.2605.26128v1
[3] Your Prompt Is Not the Only Prompt: How Much Do LLMs Weight Structured-Output Schema Descriptions?, Sin-Ying Lin, arXiv 2026, DOI: 10.48550/arXiv.2608.08254v1

## 批次补充（2026-09-17）

本次修改引入 3 篇 2026 年学术论文，揭示了 Schema 验证的关键工程警告：(1) schema 有效性不等于语义正确性 [1]，最强模型在 100% schema 有效时语义成功率仅约 80%；(2) 硬 schema 约束对小模型造成"约束税"，准确率从 19.7% 降至 11.0% [2]；(3) schema 描述可覆盖 prompt 指令，需保持单一事实来源 [3]。建议在 Schema 验证之上增加领域语义验证层。

## 批次补充 2026-09-21（onescience-knowledge-harvester）

### 归因报告Schema验证应用场景

本次补充将JSON Schema验证流程应用于归因报告交付场景，提供具体的验证规范和修复流程。

**归因报告Schema规范**：

| 字段 | 类型 | 必填 | 约束条件 |
|------|------|------|----------|
| task_id | string/int | 是 | 必须与任务索引一致 |
| task | string | 是 | 必须与任务名称一致 |
| summary | string | 是 | 非空字符串 |
| issues | array | 是 | 可为空数组，不可为null |
| issues[].failed_check | string | 是 | 非空，描述失败检查项 |
| issues[].error_detail | string | 是 | 非空，包含错误详情 |
| issues[].location | string | 否 | 故障位置描述 |
| issues[].capability_attributions | array | 否 | 能力归因列表 |
| issues[].optimization_plan | array | 否 | 优化计划列表 |

**验证流程**：

1. **JSON解析检查**
   ```python
   try:
       data = json.loads(json_string)
   except json.JSONDecodeError as e:
       # 记录行号、列号、字符位置
   ```
   - 验证点：JSON语法正确性
   - 失败处理：记录精确错误位置，终止验证

2. **必填字段检查**
   ```python
   required = ["task_id", "task", "summary", "issues"]
   missing = [f for f in required if f not in data]
   ```
   - 验证点：所有必填字段存在
   - 失败处理：记录缺失字段列表

3. **类型约束检查**
   - task_id: string或int
   - task: string，非空
   - summary: string，非空
   - issues: array，可为空

4. **任务身份一致性**
   ```python
   assert data["task_id"] == expected_task_id
   assert data["task"] == expected_task_name
   ```
   - 验证点：task_id和task与预期完全一致
   - 失败处理：记录期望值与实际值

5. **数组约束验证**
   - issues数组元素必须是对象
   - 每个元素必须包含failed_check和error_detail
   - 可选字段：location、capability_attributions、optimization_plan

**验证结果格式**：

```json
{
  "valid": true/false,
  "errors": [
    {
      "type": "missing_field|type_error|identity_mismatch",
      "field": "field_name",
      "expected": "expected_value",
      "actual": "actual_value",
      "message": "错误描述"
    }
  ],
  "warnings": ["额外字段警告列表"]
}
```

**修复流程**：

| 错误类型 | 修复策略 | 优先级 |
|----------|----------|--------|
| JSON语法错误 | 修正语法后重新提交 | 高 |
| 必填字段缺失 | 添加缺失字段 | 高 |
| 类型错误 | 转换为预期类型 | 中 |
| 身份不一致 | 修正task_id/task | 高 |
| 额外字段 | 记录警告，继续验证 | 低 |