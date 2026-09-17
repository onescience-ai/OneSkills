# PINN 不可压缩 Navier-Stokes 正问题求解

## 适用范围

**触发条件**：
- 需要求解不可压缩层流 Navier-Stokes 方程的正问题（已知边界条件和几何，求流场）
- 已知域几何、边界条件（Dirichlet/Neumann）、初始条件或稳态假设
- 需要快速获得速度-压力或速度-涡量场，且可接受近似解

**适用场景**：
- 腔体驱动流（lid-driven cavity）在 Re=100~20000 范围
- 圆柱绕流（cylinder wake）在 Re=100~3900 范围
- Kovasznay 流、Beltrami 流等解析解基准验证
- 后向台阶流等复杂几何的层流问题
- 参数化扫描（如 Reynolds 数变化的流场预测）

**不适用场景**：
- 高速可压缩流动（Ma > 0.3）
- 强湍流直接数值模拟（DNS）
- 含自由表面或多相流问题
- 流固耦合或化学反应流

## 输入

- **几何描述**：计算域的参数化表示（坐标范围、障碍物位置等）
- **边界条件**：Dirichlet 条件（壁面速度）、Neumann 条件（出口压力梯度）、周期性条件
- **初始条件**：非稳态问题的 t=0 流场；稳态问题可省略
- **物理参数**：流体密度 ρ、动力粘度 μ（或运动粘度 ν）、Reynolds 数 Re
- **配点采样**：域内均匀/随机配点数量与分布策略

## 输出

- **解场**：速度分量 (u, v)、压力 p 或涡量 ω 在查询坐标上的值
- **PDE 残差场**：Navier-Stokes 方程残差在配点上的分布
- **边界残差**：边界条件满足程度的逐点误差
- **评估指标**：相对 L2 误差、最大点误差、PDE 残差范数、守恒误差

## 流程节点

### Step 1：问题定义与 NS 方程表述选择
- **操作**：确定使用 VP（速度-压力）或 VV（速度-涡量）表述
- **参数**：VP 输出 (u, v, p)，通过 ∇·u=0 约束得到压力；VV 输出 (u, v, ω)，压力通过 Poisson 方程后处理得到
- **质量门禁**：选定表述与问题物理特征匹配（VP 更通用，VV 适合涡量关键场景）[1]

### Step 2：网络架构与损失函数设计
- **操作**：构建全连接网络（通常4-8层，每层64-128神经元），设计复合损失函数
- **损失组成**：L = λ_data·L_data + λ_PDE·L_PDE + λ_BC·L_BC + λ_IC·L_IC
- **质量门禁**：损失项数 ≥ 3（数据/方程/边界），权重可调 [1][2]

### Step 3：配点采样与训练
- **操作**：在域内生成配点（拉丁超立方或均匀网格），执行 Adam/AdamW + L-BFGS 混合优化
- **参数**：配点数 10^3~10^5，学习率 1e-3（Adam）→ 1e-4（L-BFGS），epoch 10^3~10^5
- **质量门禁**：训练损失收敛至稳定值，验证损失不发散 [1][2]

### Step 4：解场恢复与后处理
- **操作**：在查询坐标上前向推理，使用自动微分计算导数，恢复完整流场
- **参数**：推理批大小按显存调整，导数阶数 = NS 方程最高阶导数
- **质量门禁**：解场导数均为有限值，残差分布无异常突变 [1]

### Step 5：验证与适用域判定
- **操作**：与解析解/DNS 数据/CFD 参考解对比，评估误差分布和物理约束
- **指标**：相对 L2 误差 < 0.1、PDE 残差范数 < 1e-4、守恒误差可接受
- **质量门禁**：统计与物理指标同时报告，最差样本可追溯 [1][2][7]

## 关键参数

### 通用判据

| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| 网络深度 | 4-8 层 | [1][2] | 全连接层，浅层适合简单流，深层适合复杂流 |
| 每层宽度 | 64-256 | [1][5] | 宽度增加可提升表达力但增加训练成本 |
| 激活函数 | tanh / swish | [1][7] | tanh 为默认选择，swish 可加速收敛 |
| 配点数 | 10^3 ~ 10^5 | [1][4] | 与问题复杂度和维数正相关 |
| 优化器 | Adam + L-BFGS | [1][2] | 两阶段混合优化是主流策略 |
| 学习率(Adam) | 1e-3 ~ 1e-4 | [1][2] | 初始阶段 |
| 学习率(L-BFGS) | 1e-4 ~ 1e-5 | [1] | 精调阶段 |
| 损失权重 | 动态/自适应 | [1][2] | 静态权重需手动调参，动态权重更鲁棒 |

### 校准数值

以下数值来自特定基准体系，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Kovasznay 流 Re | 20~80 | [2] | 经典解析解基准 |
| 腔体流 Re 范围 | 100~20000 | [1][4][5] | 从层流到转捩 |
| 圆柱绕流 Re | 100~3900 | [1][9] | 从稳定到涡脱落 |
| Beltrami 流维数 | 2D/3D | [2] | 有解析解的稳态/非稳态流 |
| 典型相对 L2 误差 | O(10^-4)~O(10^-1) | [5][8] | 取决于 Re 和方法 |
| SIMPLE-PINN Re=20000 耗时 | 448s | [4] | 完全无数据的腔体流求解 |

## 边界与分流

| 前提 | 不成立时改道 |
|------|-------------|
| 流动为层流或弱转捩 | 转向 RANS/LES 湍流模型或 DNS + PINN 混合方法 |
| 几何简单、边界条件明确 | 考虑域分解 PINN（DDM-PINN）或 hp-VPINN 处理复杂几何 |
| 需要高精度定量结果 | 转向传统 CFD（FVM/FEM）或 PINN 作为初值+CFD 精修 |
| 计算资源有限 | 使用轻量级网络或 Transfer Learning + 已有低 Re 解 |

## 质量检查

| 检查项 | 阈值 | 失败处理 |
|--------|------|----------|
| PDE 残差范数 | < 1e-4 | 增加配点数或调整损失权重 |
| 相对 L2 误差 | < 0.1 | 增加网络深度/宽度或使用 L-BFGS 精调 |
| 边界条件满足度 | 逐点误差 < 1e-3 | 增加边界配点权重或改用硬边界条件 |
| 守恒误差（质量/动量） | < 5% | 检查配点分布或增加约束项 |
| 训练稳定性 | 损失无发散 | 降低学习率或使用梯度裁剪 |

## 回退策略

- 训练不收敛：降低学习率 → 减少网络复杂度 → 检查配点分布 → 使用域分解
- 边界误差过大：增加边界配点 → 使用硬边界条件 → 调整边界损失权重
- 泛化能力不足：增加训练工况覆盖 → 使用迁移学习 → 扩充配点范围

## 资源召回建议

- 需要选择 NS 方程表述时召回 `cfd-pinn-ns-formulation-selection`
- 需要设计损失权重策略时召回 `cfd-pinn-loss-weighting-strategies`
- 需要处理边界条件时召回 `cfd-pinn-boundary-condition-enforcement`
- 需要验证结果时召回 `cfd-pinn-solution-validation`
- 需要执行完整工作流时召回 `cfd-pinn-incompressible-ns-forward-workflow`

## 证据来源

[1] Jin X, Cai S, Li H, Karniadakis GE. "NSFnets (Navier-Stokes Flow nets): Physics-informed neural networks for the incompressible Navier-Stokes equations", Journal of Computational Physics, 2020, DOI: 10.1016/j.jcp.2020.109951
[2] Xiang Z, Peng W, Zheng X, Zhao X, Yao W. "Self-adaptive loss balanced Physics-informed neural networks for the incompressible Navier-Stokes equations", Neurocomputing, 2022, DOI: 10.1016/j.neucom.2022.05.015
[3] Anandh T, Ghose D, Tyagi A, Gupta A, Sarkar S, Ganesan S. "An efficient hp-Variational PINNs framework for incompressible Navier-Stokes equations", arXiv:2409.04143, 2024
[4] Wei C, Fan Y, Ooi CC, Wong JC, Wang H, Chiu PH. "Bridging CFD Algorithm and Physics-Informed Learning: SIMPLE-PINN for Incompressible Navier-Stokes Equations", arXiv:2603.24013, 2026
[5] Pal R, Mukherjee S, Dutta U, Choudhury A. "Solving Navier-Stokes Equations Using Data-free PINNs With Hard Boundary Conditions", arXiv:2511.14497, 2025
[6] Su Z, Liu Y, Pan S, Li Z, Shen C. "Finite Volume Physical Informed Neural Network (FV-PINN) with Reduced Derivative Order for Incompressible Flows", arXiv:2411.17095, 2024
[7] Andre-Sloan S, Kumar D, Frangi AF, Mukherjee A. "Generalization Bounds for Physics-Informed Neural Networks for the Incompressible Navier-Stokes Equations", arXiv:2603.23072, 2026
[8] Sun D, Chen J, Wang X, Tang J. "UniPINN: A Unified PINN Framework for Multi-task Learning of Diverse Navier-Stokes Equations", arXiv:2603.10466, 2026
[9] Goraya S, Sobh N, Masud A. "Error Estimates and Physics Informed Augmentation of Neural Networks for Thermally Coupled Incompressible Navier Stokes Equations", arXiv:2209.02977, 2022
[10] Roy N, Dürr R, Bück A, Sundar S. "Finite difference physics-informed neural networks enable improved solution accuracy of the Navier-Stokes equations", arXiv:2501.00014, 2025
[11] Liu D, Li X, Yang R. "Error Analysis of Tr-PINNs Algorithm for 2D Incompressible Navier-Stokes Equations", arXiv:2606.06268, 2026
[12] Çibik A. "An Artificial-Compressibility Physics-Informed Neural Network for the Unsteady Incompressible Navier-Stokes Equations", arXiv:2608.04191, 2026
