# 扩散与随机过程时空场概率预测场景

## 适用范围

本卡服务的问题类：面向随机或混沌PDE（偏微分方程）产生的时空数据，利用扩散模型（Diffusion model）与随机过程模型（Stochastic process model）完成概率预测，产出可复现的模型、任务结果、物理一致性评估和适用域报告。适用于流体力学中具有随机性或混沌特性的PDE时空场建模与预测任务，包括但不限于湍流模拟、随机扩散场预测、混沌动力系统状态估计等。不适用于确定性PDE的确定性场预测（无需概率输出）、稳态问题、或无PDE背景的纯统计时序预测。

## 场景目标

1. 接入随机或混沌PDE时空数据，完成数据契约核验与质量审计。
2. 对数据进行预处理、无量纲化与无泄漏切分。
3. 训练扩散模型与随机过程模型，完成指定输入到目标物理量的概率映射。
4. 在独立测试集上批量推理，恢复原始物理单位与网格。
5. 评估统计误差、物理约束满足度、泛化能力与适用域，给出PASS/REJECT/BLOCKED判定。

## 模型与工具

| 资源类型 | 名称 | 用途 |
|---------|------|------|
| 模型 | Diffusion model | 基于扩散过程的生成式时空场概率预测 |
| 模型 | Stochastic process model | 基于随机过程的动力学建模与概率预测 |
| 框架 | PyTorch（默认） | 模型训练与推理框架 |
| HPC | 待确认 | 视数据规模与模型复杂度决定 |

## 适用与不适用

- **适用**：随机/混沌PDE时空数据；需要概率分布输出（不确定性量化）的场景；流体扩散、湍流、多相流随机场等。
- **不适用**：确定性PDE的确定性解预测；无PDE背景的纯统计时序；稳态/平衡态问题；域外工况未经CFD复核直接使用。

## 工作流概览

```
s01 数据接入与契约核验 → s02 预处理与数据切分 → s03 模型配置与训练 → s04 批量推理与物理恢复 → s05 任务验收与适用域判定
```

各步骤的详细输入、输出、质量门禁与执行方法参见配套任务卡：
- s01: [cfd-pde-data-intake-contract-validation](../../task/cfd-pde-data-intake-contract-validation/)
- s02: [cfd-pde-preprocessing-data-splitting](../../task/cfd-pde-preprocessing-data-splitting/)
- s03: [cfd-diffusion-stochastic-model-training](../../task/cfd-diffusion-stochastic-model-training/)
- s04: [cfd-pde-batch-inference-physical-recovery](../../task/cfd-pde-batch-inference-physical-recovery/)
- s05: [cfd-probabilistic-prediction-acceptance-applicability](../../task/cfd-probabilistic-prediction-acceptance-applicability/)

## 关键参数

### 通用判据

| 判据 | 说明 | 来源 |
|------|------|------|
| 相对L2误差门限 | 默认≤0.1，超出为REJECT | [场景需求书CFD_S021] |
| 守恒残差 | 物理守恒量偏差须为有限值 | [场景需求书CFD_S021] |
| 边界误差 | 边界条件满足度须报告 | [场景需求书CFD_S021] |
| OOD测试 | 几何或工况外推测试必须执行 | [场景需求书CFD_S021] |

### 校准数值

以下数值来自CFD_S021场景需求书，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 训练轮数 | 100 | [场景需求书CFD_S021] | 默认epochs |
| 批大小 | 8 | [场景需求书CFD_S021] | 默认batch_size |
| 学习率 | 0.001 | [场景需求书CFD_S021] | 默认学习率 |
| 随机种子 | 42 | [场景需求书CFD_S021] | 可复现性种子 |
| 早停耐心 | 15 | [场景需求书CFD_S021] | early_stopping_patience |
| 切分比例 | 70/15/15 | [场景需求书CFD_S021] | train/val/test |

## 边界与分流

- 数据文件不可读或样本不可追溯 → 返回BLOCKED，不得编造数据。
- 输入目标变量单位坐标不完整 → 返回BLOCKED，列出缺项。
- 测试集泄漏检测失败 → 强制止止，重新切分。
- 域外工况发现 → 必须经CFD复核，不得仅凭平均误差宣称工程可用。
- 模型权重加载失败 → BLOCKED，检查checkpoint结构兼容性。
- 推理结果含NaN/Inf → REJECT，排查数值稳定性。

## 质量检查

- 数据文件可读且样本可追溯（s01）
- 三份切分的对象轨迹互斥（s02）
- 训练验证损失均为有限值（s03）
- 最佳权重可重新加载（s03）
- 预测无NaN/Inf且形状单位正确（s04）
- 统计与物理指标同时报告（s05）
- 最差样本可追溯（s05）
- 结论含适用域限制与复核建议（s05）

## 回退策略

- 数据接入失败 → 检查路径与格式，补充元数据后重试。
- 训练不收敛 → 调整学习率、批大小或模型架构，记录失败原因。
- 推理精度不足 → 检查数据预处理一致性，评估模型是否欠拟合。
- 适用域判定为REJECT → 分析失败模式，建议域外工况复核方案。

## 资源召回建议

当任务涉及以下关键词时召回本卡：
- 扩散模型 + PDE + 概率预测
- 随机过程 + 时空场 + 概率预测
- 混沌PDE + 不确定性量化
- Diffusion model + spatiotemporal forecasting
- Stochastic process + physics prediction

配套资源：
- 任务卡（5张）覆盖各步骤细节
- 工作流卡 cfd-diffusion-stochastic-pde-probability-prediction-workflow

## 证据来源

[1] DYffusion: A Dynamics-informed Diffusion Model for Spatiotemporal Forecasting（场景需求书CFD_S021引用）
[2] Predicting the Energy Landscape of Stochastic Dynamical System via Physics-informed Self-supervised Learning（场景需求书CFD_S021引用）
[3] Diffusion-Based Hierarchical Graph Neural Networks for Simulating Nonlinear Solid Mechanics, arXiv:2506.06045（场景需求书CFD_S021引用）
[4] Neural MJD: Neural Non-Stationary Merton Jump Diffusion for Time Series Prediction, arXiv:2506.04542（场景需求书CFD_S021引用）
[5] PGODE: Towards High-quality System Dynamics Modeling（场景需求书CFD_S021引用）
[6] Deep Stochastic Processes via Functional Markov Transition Operators（场景需求书CFD_S021引用）
[7] Dynamic Tensor Decomposition via Neural Diffusion-Reaction Processes（场景需求书CFD_S021引用）
[8] Learning Efficient Surrogate Dynamic Models with Graph Spline Networks（场景需求书CFD_S021引用）
[9] Deep learning for physical processes: Incorporating prior scientific knowledge, arXiv:1711.07970（场景需求书CFD_S021引用）
