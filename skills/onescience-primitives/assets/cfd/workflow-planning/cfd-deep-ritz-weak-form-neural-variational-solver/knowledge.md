# Deep Ritz与弱形式神经变分求解

## 适用范围

**触发条件**：
- 需要求解椭圆方程或演化方程的变分问题
- 已有PDE的变分积分形式（能量泛函或弱形式残差积分）
- 希望用神经网络逼近PDE的解而非依赖传统有限元/有限差分网格

**适用场景**：
- 椭圆方程（如Poisson方程、Laplace方程）的变分求解
- 演化方程（如热传导方程、对流扩散方程）的弱形式求解
- 高维PDE（传统方法维度灾难）的神经网络求解
- 需要连续解表示（非离散网格）的应用
- 流体力学中椭圆/抛物型子问题的快速求解

**不适用场景**：
- 强间断、激波主导的双曲型方程（需特殊处理）
- 要求严格守恒律保证的工程仿真（需CFD复核）
- 变分形式未知或无法推导的PDE
- 域外工况（超出训练分布的几何、边界条件、参数范围）

## 输入

- 椭圆或演化方程的变分积分形式（能量泛函或弱形式残差）
- 计算域几何定义（边界、内部区域）
- 边界条件（Dirichlet/Neumann/Robin）
- 初始条件（演化方程）
- 方程参数（系数、源项等）

## 输出

- 神经网络逼近的PDE解场
- 逐点残差场（PDE残差、边界残差）
- 物理一致性评估报告
- 适用域判定（PASS/REJECT/BLOCKED）

## 流程节点

1. 数据接入与契约核验 → 2. 预处理与数据切分 → 3. 模型配置与训练 → 4. 方程求解与物理残差恢复 → 5. 任务验收与适用域判定

每步含详细操作、参数、工具和质量门禁，见 workflow 卡片 `cfd-deep-ritz-variational-pde-solver-workflow`。

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型类型 | Deep Ritz network, Weak-form neural solver | [1][2] | 两种主要的变分神经求解器 |
| 框架 | PyTorch | [3] | 默认实现框架 |
| 典型学习率 | 0.001 | [4] | 需根据问题调整 |
| 典型训练轮数 | 100+ | [4] | 需配合早停策略 |
| 验收指标 | relative_L2, PDE_residual, boundary_error, conservation_error | [5] | 多维度物理一致性验证 |
| 相对误差门限 | ≤ 0.1 | [5] | 默认放行阈值，可按精度需求调整 |

## 边界与分流

- **变分形式不可得**：若PDE无法推导出可用的变分积分形式，应转向强形式PINN求解（如标准Physics-Informed Neural Networks）
- **高维双曲问题**：若方程为主流场中的双曲型问题（激波、间断），Deep Ritz方法可能不稳定，建议使用特征线方法或弱对抗网络
- **域外工况**：若测试工况超出训练分布（不同几何/边界/参数），必须经CFD复核后才能使用
- **训练不收敛**：若训练损失震荡或不下降，检查变分形式推导是否正确、网络架构是否匹配问题规模

## 质量检查

- 训练验证损失均为有限值（非NaN/Inf）
- 最佳权重可重新加载
- 配置环境随机种子可复现
- 解场导数与残差均为有限值
- 边初值逐项满足门限
- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

## 回退策略

- Deep Ritz不收敛 → 尝试弱形式神经求解器（不同损失泛函）
- 两者均不收敛 → 回退到传统有限元方法（FEM）作为baseline
- 物理一致性不足 → 增加配点密度、调整网络深度、引入自适应采样
- 域外工况 → 必须经CFD复核，不可直接工程使用

## 资源召回建议

当需要求解椭圆/演化方程的变分问题时召回本卡。配套资源：
- workflow 卡片 `cfd-deep-ritz-variational-pde-solver-workflow`（完整工作流）
- task 卡片覆盖各步骤（数据接入、预处理、训练、求解、验收）
- onescience-runtime（执行环境）
- onescience-coder（代码生成）

## 证据来源

[1] "The Deep Ritz Method: A Deep Learning-Based Numerical Algorithm for Solving Variational Problems", E and Yu, 2017
[2] "Refined generalization analysis of the Deep Ritz Method and Physics-Informed Neural Networks", 2023
[3] "Error Analysis of Deep Ritz Methods for Elliptic Equations", 2021
[4] "Weak adversarial networks for high-dimensional partial differential equations", 2019
[5] "Learning from Integral Losses in Physics-Informed Neural Networks", 2024
[6] "Randomized Sparse Neural Galerkin Schemes for Solving Evolution Equations with Deep Networks", 2023
