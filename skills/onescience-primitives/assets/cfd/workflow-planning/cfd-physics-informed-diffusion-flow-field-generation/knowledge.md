# 物理信息扩散模型流场分布生成

## 适用范围

面向流场条件数据与物理残差数据，使用物理信息扩散模型（Physics-Informed Diffusion Model）完成流场分布生成的任务。该方法将扩散模型的生成能力与物理约束（Navier-Stokes 方程残差、守恒律、边界条件）相结合，在生成多样流场样本的同时保证物理一致性。适用于不可压/可压缩层流与湍流、翼型绕流、管道流、城市风场等CFD场景。域外几何或工况超出训练覆盖范围时，需经传统 CFD 复核后方可采信。

本卡服务的问题类：给定条件流场（如边界条件、几何参数、工况），生成满足物理约束的流场分布样本，替代或加速高成本 CFD 仿真以获取统计量（RMS、两点相关等）。

## 输入

- 条件流场数据：包括边界条件、几何参数、工况参数、初始场
- 物理残差数据：Navier-Stokes 方程残差、连续性方程残差、能量方程残差等
- 数据契约：变量名、单位、网格拓扑、坐标系定义
- 来源：CFD 仿真结果、实验数据或混合来源

## 输出

- 可复现的扩散模型 checkpoint
- 多样流场样本集（含采样轨迹与随机种子记录）
- 物理一致性评估报告（边界残差、守恒误差、方程残差）
- 适用域报告（含几何/工况外推测试结论与 CFD 复核建议）

## 流程节点

数据接入与契约核验 → 预处理与数据切分 → 模型配置与训练 → 条件采样与物理一致性筛选 → 任务验收与适用域判定

### 数据接入与契约核验
- 操作：读取数据集，检查文件可读性、样本数、输入/目标变量、单位、坐标系、网格拓扑、时间/工况范围、缺失值和使用许可
- 质量门禁：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏

### 预处理与数据切分
- 操作：统一物理量表示，按几何、工况或时间构造无泄漏切分；执行归一化或无量纲化
- 质量门禁：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏

### 模型配置与训练
- 操作：加载切分数据与统计量，训练 Physics-informed diffusion model；记录代码版本、依赖、随机种子、逐轮指标与最佳权重
- 质量门禁：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现

### 条件采样与物理一致性筛选
- 操作：对每个测试条件生成多随机种子样本，恢复物理量后计算边界、守恒与方程残差，剔除不合格样本
- 质量门禁：样本条件与随机种子可追溯；多样性和真实性同时评价；物理筛选前后统计均报告

### 任务验收与适用域判定
- 操作：按统计与物理指标评价结果，给出 PASS/REJECT/BLOCKED；执行几何或工况外推测试并明确适用域
- 质量门禁：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议

## 关键参数

### 通用判据（方法层，同类体系可参考）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 物理约束类型 | Navier-Stokes 残差 + 守恒律 + 边界条件 | [场景需求书] | 核心物理信息来源 |
| 物理筛选策略 | 残差阈值剔除 + 分布覆盖评估 | [1][2][3] | 禁止单样本代表整体 |
| 多样性评价 | 多随机种子采样 + 分布距离指标 | [1][4][5] | 需同时报告筛选前后统计 |
| 适用域判定 | 几何/工况外推测试 + OOD 检测 | [场景需求书] | 不得仅凭平均误差宣称可用 |

### 校准数值（以下数值来自特定体系，供量级校准；其他体系需以自身证据重新锚定）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 训练框架 | PyTorch | [场景需求书] | 默认框架 |
| 默认 epochs | 100 | [场景需求书] | 可调整 |
| 默认 batch_size | 8 | [场景需求书] | 按显存调整 |
| 默认 learning_rate | 0.001 | [场景需求书] | 可调整 |
| early_stopping_patience | 15 | [场景需求书] | 防过拟合 |
| 相对误差门限 MAX_RELATIVE_L2 | 0.1 | [场景需求书] | 默认阈值 |
| train/val/test 比例 | 0.7/0.15/0.15 | [场景需求书] | 按几何/轨迹切分 |

## 边界与分流

- 数据不可读或缺少必填输入 → 返回 BLOCKED 并列出缺项，不得编造数据
- 物理残差数据缺失 → 降级为纯数据驱动扩散模型，但需在报告中明确标注物理一致性未经验证
- 域外几何/工况 → 外推测试必须执行，结论中须包含适用域限制与 CFD 复核建议
- 训练不收敛（损失为 NaN/Inf） → 检查数据质量与超参数，必要时降级为较小模型或更保守学习率
- 单个漂亮样本出现 → 禁止以此代表整体性能，必须报告多样本统计

## 质量检查

- 逐变量误差（相对 L2）是否低于门限
- 边界残差是否满足物理约束
- 守恒律/方程残差是否在可接受范围
- 最差样本是否可追溯
- 推理成本是否在可接受范围

## 回退策略

- 扩散模型训练失败 → 回退到传统 PINN 或纯数据驱动模型
- 物理筛选过于严格导致样本不足 → 放宽残差阈值并标注置信度降级
- 域外工况无法通过验收 → 转为 CFD 仿真或 hybrid 方案

## 资源召回建议

- 需要了解扩散模型在 CFD 中的基础架构时召回本卡
- 需要完整的从数据到验收的端到端工作流时召回本卡
- 需要了解物理一致性验证方法时召回下游 task 卡
- 配套资源：cfd-physics-informed-diffusion-pipeline（工作流级）、cfd-diffusion-conditional-sampling-physics-filter（采样筛选 task 卡）

## 证据来源

[1] Physics-Informed Diffusion Models, 2024
[2] Learning Distributions of Complex Fluid Simulations with Diffusion Graph Networks, Lino, Pfaff, Thuerey, ICLR 2025, arXiv:2504.02843
[3] Self-Augmented Diffusion Guidance for Physics-Informed Generation, Osaka, Takeishi, Yairi, 2026, arXiv:2608.26748
[4] Learning Flow Distributions via Projection-Constrained Diffusion on Manifolds, Trupin, Ghosh, Jangid, 2026, arXiv:2602.17773
[5] Uni-Flow: a unified autoregressive-diffusion model for complex multiscale flows, Xue et al., 2026, arXiv:2602.15592
[6] How well can Diffusion Models learn Lagrangian-Tracer Statistics in Non-reciprocal Turbulence, Jha, Maji, Pandit, 2026, arXiv:2608.27378
[7] Conditional diffusion denoising probabilistic model for super-resolution of ABL LES, Sallam, Fürth, 2026, arXiv:2604.26776
[8] Improved Sampling Of Diffusion Models In Fluid Dynamics With Tweedie's Formula, 2024
