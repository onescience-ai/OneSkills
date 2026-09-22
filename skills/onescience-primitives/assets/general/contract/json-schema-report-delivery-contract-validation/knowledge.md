# JSON Schema报告交付契约验证规范

## 适用范围
面向自动化工具链中结构化报告交付的验证场景，提供JSON Schema契约定义、必填字段校验、任务身份一致性判定与数组约束验证流程。适用于归因分析报告、数据处理报告、模型评估报告等需要按契约格式交付的JSON文档验证场景。

## 输入
- 待验证的JSON报告文档
- 目标JSON Schema定义（必填字段、类型约束、数组约束）
- 任务身份信息（task_id、task_name）
- 预期字段白名单

## 输出
- 验证结果（通过/失败）
- 错误详情列表（缺失字段、类型错误、约束违反、身份不一致）
- 修复建议

## 流程节点
1. **JSON解析检查** → 尝试解析JSON字符串，记录语法错误位置
2. **必填字段检查** → 验证所有必需顶层字段是否存在
3. **类型约束检查** → 验证每个字段的数据类型是否符合预期
4. **任务身份一致性** → 验证task_id和task是否与预期完全一致
5. **数组约束验证** → 验证数组字段的元素结构和约束条件
6. **额外字段检测** → 检测并报告未预期的顶层字段
7. **验证结果生成** → 汇总所有检查结果，生成验证报告

## 关键参数

### 通用判据（方法层，同类体系可参考）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 必填字段列表 | ["task_id", "task", "summary", "issues"] | [D1] 归因报告规范 | 顶层必填字段 |
| summary类型 | string (non-empty) | [D1] 归因报告规范 | 摘要必须是非空字符串 |
| issues类型 | array | [D1] 归因报告规范 | 问题列表必须是数组 |
| 身份匹配规则 | exact match | 报告契约 | task_id和task必须完全匹配 |
| 额外字段处理 | warning（不阻断验证） | 行业实践 | 额外字段应记录为警告 |

### 校准数值（以下数值来自归因报告实践，供量级校准；其他体系需以自身证据重新锚定）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| JSON解析成功率 | 100%（强模型） | [论文1] | 强模型在JSON格式正确性上表现优异 |
| 语义正确率 | ~80%（强模型） | [论文1] | 即使schema有效，语义正确率仍有缺口 |
| 硬schema准确率下降 | 19.7%→11.0% | [论文2] | 硬schema约束导致小模型答案准确率下降 |
| 结构有效性提升 | 61.5%→100.0% | [论文2] | 硬schema约束将结构有效性提升至100% |
| 错误检测覆盖率 | ≥95% | 行业实践 | 必须覆盖所有必填字段和类型约束 |

## 边界与分流
- **JSON语法错误**：记录精确错误位置（行号、列号）→ 终止验证
- **必填字段缺失**：记录缺失字段列表 → 标记为验证失败
- **类型错误**：记录期望类型与实际类型 → 标记为验证失败
- **身份不一致**：记录期望值与实际值 → 标记为验证失败
- **额外字段检测**：记录警告信息 → 继续验证不阻断
- **数组元素结构错误**：记录无效元素索引和字段 → 标记为验证失败
- **Schema有效性vs语义正确性**：Schema验证通过但内容语义错误 → 记录为"wrong-valid-schema"，需要领域验证层

## 质量检查
- [ ] JSON语法正确（无解析错误）
- [ ] 所有必填字段存在（task_id, task, summary, issues）
- [ ] 字段类型符合预期（string, array, non-empty）
- [ ] 任务身份一致（task_id和task完全匹配）
- [ ] 无意外的额外字段（或已记录警告）
- [ ] 数组元素结构正确（issues[].failed_check, issues[].error_detail存在）
- [ ] 验证结果格式完整（valid, errors, warnings）

## 回退策略
1. **JSON解析失败**：修正JSON语法错误后重新提交
2. **字段缺失**：添加缺失的必填字段
3. **类型错误**：将字段值转换为预期类型
4. **身份不一致**：修正task_id和task字段
5. **格式降级**：接受部分字段缺失但保留核心信息

## 资源召回建议
当以下场景出现时应召回本卡片：
- 结构化报告校验失败（字段缺失、类型错误）
- 归因分析输出不符合Schema契约
- 需要定义JSON报告的必填字段和约束
- 需要验证任务身份一致性
- 需要区分schema有效性与语义正确性
- 需要设计schema描述以避免与prompt指令冲突

配套资源：
- `json-schema-report-validation`（JSON Schema验证流程）
- `json-schema-report-contract`（JSON Schema报告契约）
- `cli-fault-classification-non-interactive`（CLI故障诊断）

## 补充证据（开源权威文档）
[D1] JSON Schema reference documentation, JSON Schema Organization, v2020-12, URL: https://json-schema.org/understanding-json-schema/reference (accessed 2026-09-22, 权威文档单源参考)

## 证据来源
[1] Schema validation and evaluation framework for extracted schemas in JSON databases, Belefqih et al., Scientific Reports, 2026, DOI: 10.1038/s41598-026-45554-6
[2] Validation of Modern JSON Schema: Formalization and Complexity, Attouche et al., Proceedings of the ACM on Programming Languages, 2024, DOI: 10.1145/3632891
[3] Blaze: Compiling JSON Schema for 10x Faster Validation, Viotti & Mior, Proceedings of the VLDB Endowment, 2025, DOI: 10.14778/3773749.3773764
[D1] JSON Schema Organization, 2020-12 Standard

## 批次补充（2026-09-22）

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