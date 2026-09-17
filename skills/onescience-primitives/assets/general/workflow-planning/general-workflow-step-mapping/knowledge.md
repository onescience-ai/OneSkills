# OneScience 场景workflow步骤与executor步骤映射规则

## 适用范围

**触发条件**：
- orchestrator需要将场景workflow步骤映射为executor可执行步骤
- 需要确保场景步骤的输入输出契约传递到executor步骤
- 需要在execution-manifest.json中记录映射关系

**适用场景**：
- 所有OneScience任务的global_plan生成
- 场景步骤与executor步骤的对应关系定义
- 执行计划的可审计性保障

**不适用场景**：
- 直接执行单一executor的简单任务
- 不涉及场景workflow的任务

## 输入

- **场景workflow定义**：s01-s04步骤列表
- **executor能力视图**：各executor的输入输出契约
- **任务上下文**：具体任务的需求和约束

## 输出

- **映射关系**：每个场景步骤对应的executor步骤
- **execution-manifest.json**：包含step_mapping字段
- **契约传递**：输入输出参数的映射

## 流程节点

### Step 1：解析场景workflow步骤
- **操作**：读取场景定义，提取s01-s04步骤
- **参数**：步骤名称、输入输出契约、质量门禁
- **工具**：workflow配置文件
- **质量门禁**：步骤列表完整

### Step 2：匹配executor能力
- **操作**：为每个场景步骤选择合适的executor
- **参数**：executor能力视图、输入输出契约
- **工具**：能力匹配算法
- **质量门禁**：executor能力覆盖场景需求

### Step 3：定义映射关系
- **操作**：建立场景步骤到executor步骤的映射
- **参数**：
  - s01 → material modeling步骤
  - s02 → computation步骤
  - s03 → analysis步骤
  - s04 → recommendation步骤
- **工具**：映射定义
- **质量门禁**：映射关系完整且契约一致

### Step 4：生成execution-manifest
- **操作**：将映射关系写入execution-manifest.json
- **参数**：step_mapping字段
- **工具**：JSON生成
- **质量门禁**：step_mapping字段存在且格式正确

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| s01 | material modeling | [1] | 材料与工况建模 |
| s02 | computation | [1] | 计算执行 |
| s03 | analysis | [1] | 结果分析 |
| s04 | recommendation | [1] | 方案推荐 |
| step_mapping | executor步骤映射 | [1] | execution-manifest.json字段 |

## 边界与分流

**映射规则**：
- 每个场景步骤可映射为一个或多个executor步骤
- 输入输出契约必须传递到对应executor步骤
- 映射关系必须记录在step_mapping字段

**异常处理**：
- 若executor能力不足，可拆分为多个子步骤
- 若场景步骤与executor不匹配，标记MISMATCH
- 若契约不一致，调整executor参数

## 质量检查

- **映射完整性**：所有s01-s04步骤都有对应executor
- **契约一致性**：输入输出参数匹配
- **记录完整性**：step_mapping字段完整
- **可审计性**：映射关系可追溯

## 回退策略

- 若映射失败，使用通用executor覆盖
- 若契约不一致，调整参数或标记WARNING
- 若场景步骤无法映射，标记UNMAPPED

## 资源召回建议

**何时应召回本卡片**：
- orchestrator生成global_plan时
- 需要定义场景步骤与executor的映射
- 需要确保execution-manifest完整

**配套资源**：
- `matchem-blocked-trigger-rules`：输入验证
- `matchem-data-traceability`：数据质量
- `matchem-sslcs-unsupervised-discovery`：具体任务示例

## 证据来源

[1] "Unsupervised discovery of solid-state lithium ion conductors", Ying Zhang et al., Nature Communications, 2019, DOI: 10.1038/s41467-019-13214-1

[2] OneScience场景workflow定义规范：s01-s04步骤与executor映射要求
