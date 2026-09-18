# OneScience场景workflow步骤与executor步骤映射规则

## 适用范围

面向OneScience框架中场景定义的领域工作流步骤（s01-s04）与executor可执行步骤之间的映射需求，确保场景约束能够正确传递到具体执行环节。适用于材料计算、科学模拟等需要场景驱动执行的任务编排，包括晶体结构预测、固态电解质筛选、电化学模拟等场景。不适用于纯文档生成或无场景定义的通用任务。

## 输入

| 输入项 | 格式 | 来源 | 预处理要求 |
|--------|------|------|------------|
| 场景workflow定义 | JSON/YAML | 场景配置文件 | 提取s01-s04步骤描述和输入输出契约 |
| executor能力视图 | JSON | executor注册信息 | 确认每个executor的输入输出接口 |
| 任务上下文 | JSON | orchestrator传递 | 包含用户目标、约束条件、相关产物 |

## 输出

| 输出项 | 格式 | 验证标准 |
|--------|------|----------|
| 步骤映射关系 | JSON | 每个场景步骤对应一个或多个executor步骤 |
| 输入输出契约 | JSON | executor步骤的输入输出与场景步骤一致 |
| execution-manifest.json | JSON | 包含step_mapping字段，记录映射关系 |

## 流程节点

### 节点1：场景步骤解析
- **操作**：解析场景workflow定义，提取s01-s04步骤描述、输入输出契约
- **参数**：场景workflow文件路径
- **工具**：JSON/YAML解析器
- **质量门禁**：场景步骤完整性验证，确保所有s01-s04步骤已定义

### 节点2：executor能力匹配
- **操作**：根据场景步骤的输入输出需求，匹配合适的executor
- **参数**：executor能力视图、场景步骤输入输出契约
- **工具**：能力匹配算法
- **质量门禁**：每个场景步骤至少匹配一个executor，输入输出接口兼容

### 节点3：步骤映射生成
- **操作**：将场景步骤映射为executor可执行步骤，生成映射关系
- **参数**：场景步骤、executor步骤、输入输出契约
- **工具**：映射生成器
- **质量门禁**：映射关系完整性，输入输出契约一致性

### 节点4：manifest生成
- **操作**：生成execution-manifest.json，包含step_mapping字段
- **参数**：映射关系、步骤执行顺序、依赖关系
- **工具**：manifest生成器
- **质量门禁**：manifest格式正确，step_mapping字段完整

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 场景步骤定义 | s01-s04 | 场景配置 | 领域工作流步骤编号 |
| 映射粒度 | 1:1或1:N | 框架规则 | 一个场景步骤可映射为一个或多个executor步骤 |
| 契约一致性 | 必须保持 | 框架规则 | executor步骤的输入输出必须与场景步骤一致 |
| 映射记录 | step_mapping字段 | 框架规则 | 必须记录在execution-manifest.json中 |

### 校准数值（来自固态电解质研究场景）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| s01 | material modeling | [1] | 材料与工况建模步骤 |
| s02 | computation | [1] | 结构或电化学响应获取步骤 |
| s03 | analysis | [1] | 性能分析步骤 |
| s04 | recommendation | [1] | 推荐方案生成步骤 |

## 边界与分流

### 前提不成立时的改道方案

| 前提 | 不成立条件 | 改道方案 |
|------|------------|----------|
| 场景步骤已定义 | 场景workflow缺失s01-s04定义 | 使用通用研究流程，但需在manifest中标注场景约束缺失 |
| executor能力匹配 | 无合适executor可匹配 | 使用通用executor，但需在manifest中标注能力降级 |
| 输入输出契约一致 | executor接口与场景需求不匹配 | 进行接口适配，或标记PARTIAL状态 |

### 异常处理

- **场景步骤与executor步骤命名不一致**：在manifest中建立明确的映射关系
- **场景约束无法追溯到具体步骤**：在manifest中添加约束追溯字段
- **步骤执行顺序与场景定义不符**：调整executor步骤顺序，确保场景约束满足

## 质量检查

| 检查点 | 标准 | 失败处理 |
|--------|------|----------|
| 步骤映射完整性 | 每个场景步骤都有对应executor步骤 | 补充缺失的映射关系 |
| 契约一致性 | executor输入输出与场景需求一致 | 调整executor接口或标记PARTIAL |
| manifest格式 | JSON格式正确，包含step_mapping字段 | 重新生成manifest |
| 约束可追溯性 | 场景约束可追溯到具体executor步骤 | 添加约束追溯字段 |

## 回退策略

1. **场景步骤缺失**：使用通用研究流程，但需在manifest中标注场景约束缺失
2. **executor能力不足**：使用通用executor，但需在manifest中标注能力降级
3. **契约不一致**：进行接口适配，或标记PARTIAL状态

## 资源召回建议

- 何时召回本卡片：当orchestrator需要将场景workflow步骤映射为executor可执行步骤时，或当execution-manifest.json需要生成step_mapping字段时
- 配套资源：场景workflow定义、executor能力视图、输入输出契约定义

## 补充证据（开源文档/用户自有，可选）

无

## 证据来源

[1] Zhang, Y., He, X., Chen, Z., et al. Unsupervised discovery of solid-state lithium ion conductors. Nature Communications, 10(1), 5260 (2019). DOI: 10.1038/s41467-019-13214-1
[2] 任务369归因报告中的证据：场景s01-s04与execution-manifest中step-1到step-6无明确映射关系