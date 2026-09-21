# 可复现可审计研究任务标准

## 适用范围

面向任意科研计算任务（论文复现/模型训练/仿真/数据分析），当任务要求"完成一项可复现、可审计的研究任务"时，本卡定义具体的可复现性要求、可审计性要求、执行产物规范和科学严谨性标准。适用于避免因任务理解偏差导致执行方案不满足基本科研规范。

## 输入

- 任务目标（来自用户请求）
- 任务约束（数据来源要求、验证要求、报告要求）
- 执行环境信息（计算资源、软件版本、依赖配置）

## 输出

- 完整执行产物（代码、数据、模型、报告），符合 required_files 规范
- execution_manifest（含决策日志、技能调用日志、专家召回日志）
- 可复现性自检报告（代码/数据/环境完整性检查）

## 流程节点

1. 任务理解 → 方案制定 → 执行实施 → 产物验证 → 自检报告 → 归档
   - 每步含操作、参数、工具、质量门禁

## 关键参数

### 通用判据（方法层，同类体系可参考，逐条带证据编号）

| 维度 | 要求 | 来源 | 说明 |
|------|------|------|------|
| 可复现性-代码 | 所有执行代码必须实际运行（非模拟/占位），代码版本可追溯 | [1][3] | 禁止使用模拟数据代替真实数据 |
| 可复现性-数据 | 训练/验证/测试数据来源可追溯，数据获取脚本可执行 | [1][2] | 禁止使用合成数据代替真实科学数据 |
| 可复现性-环境 | 记录完整依赖列表（requirements.txt/conda.yaml）和软件版本 | [1][3] | 确保他人可重建执行环境 |
| 可审计性-决策日志 | 每个关键决策（模型选择、数据来源、参数设定）需记录理由和依据 | [2][5] | 决策需基于领域知识而非"简化执行" |
| 可审计性-执行日志 | 所有技能调用、专家召回、错误恢复需记录在 execution_manifest 中 | [2][4] | 日志必须反映实际执行，非事后补写 |
| 科学严谨性 | 使用真实数据而非模拟数据；选择符合任务要求的模型架构 | [1][2] | "快速演示"不构成简化执行的正当理由 |

### 校准数值（体系专属值，引语写明"以下数值来自特定体系，供量级校准；其他体系需以自身证据重新锚定"）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 代码可执行率 | 100%（所有步骤必须可实际运行） | [1] | 零容忍占位代码 |
| 数据可追溯率 | 100%（每条数据必须有来源标注） | [1] | 包括训练集、验证集、测试集 |
| 决策记录覆盖率 | 100%（所有 branch_point 决策必须记录） | [2] | 含选择理由和备选方案 |

## 边界与分流

- 若任务明确允许使用模拟数据（如纯架构演示），需在 execution_manifest 中记录 explicit_allowance
- 若数据获取受限（如付费数据库），需记录 blocked_reason 而非自动降级为模拟数据
- 若模型选择不符合任务要求（如基础模型任务选择线性回归），需记录 violation_reason 并请求人工确认

## 质量检查

- execution_manifest 必须包含 decision_log、skill_invocations、expert_recall 三个子项
- decision_log 中每个条目必须有 rationale（选择理由）
- skill_invocations 中每个条目必须有 status（实际执行状态，非 "模拟执行"）
- 所有产物文件必须实际存在于文件系统中

## 回退策略

- 若无法获取真实数据，记录 blocked_reason 并请求用户提供数据或授权使用替代数据源
- 若模型架构不符合任务要求，记录 violation_reason 并请求人工确认是否继续

## 资源召回建议

- 当任何科研计算任务开始执行时召回本卡作为基础规范
- 配套资源：技能调用规范卡、专家技能召回融合卡

## 证据来源

[1] Semmelrock H, et al. "Reproducibility in machine-learning-based research: Overview, barriers, and drivers." AI Magazine, 2025, DOI: 10.1002/aaai.70002
[2] Miller T. "Controlled Agentic AI Systems: A Governance-Driven Architecture for Auditable and Reproducible Decision Pipelines." Machine Learning and Knowledge Extraction, 2026, DOI: 10.3390/make8050125
[3] Zhang Z, Valeo C. "Agentic SWMM: Auditable and Reproducible Stormwater Modelling Workflow." AI for Engineering, 2026, DOI: 10.3390/aieng1010005
[4] Sejfuli-Ramadani N, et al. "A Reproducible Blockchain-Anchored Proof-of-Charge Platform for Auditable EV Charging Receipts." Future Internet, 2026, DOI: 10.3390/fi18080423
[5] Djidrovski I. "P30-36 ToxMCP: Auditable, Reproducible Workflows for NAM-Based Toxicology and Risk Assessment." Toxicology Letters, 2026, DOI: 10.1016/j.toxlet.2026.112783