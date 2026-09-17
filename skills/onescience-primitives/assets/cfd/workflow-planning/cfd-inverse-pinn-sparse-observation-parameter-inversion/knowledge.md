# 物理信息网络稀疏观测参数反演

## 适用范围

本卡片覆盖使用物理信息神经网络（PINN）及其变体从稀疏流场观测数据中推断未知PDE参数的完整工作流。适用于以下场景：
- 稀疏传感器布局下的流场参数反演
- 未知PDE系数（如扩散系数、粘度、边界条件参数）的估计
- 数据同化与物理约束融合的参数识别
- 流体系统中的逆问题求解

**不适用场景**：
- 完整观测流场的正问题求解（forward problem）
- 无物理约束的纯数据驱动回归
- 高维参数空间且缺乏物理先验的黑箱优化
- 域外工况需经CFD复核验证

## 输入

### 必需输入
1. **稀疏流场观测数据**：在有限空间/时间点采集的流场变量（速度、压力、温度等）
2. **PDE方程定义**：待反演参数所满足的控制方程（如Navier-Stokes方程、扩散方程）
3. **边界条件信息**：已知或部分已知的边界约束

### 可选输入
- 初始条件猜测
- 参数先验范围
- 额外物理约束（如守恒律）

## 输出

1. **反演参数估计**：推断的PDE参数值及其不确定性
2. **重建流场**：基于反演参数的完整流场预测
3. **物理残差场**：PDE方程在各配点的残差分布
4. **适用域报告**：模型可靠性的量化评估

## 流程节点

```
数据接入与契约核验(s01) → 预处理与数据切分(s02) → 模型配置与训练(s03) → 方程求解与物理残差恢复(s04) → 任务验收与适用域判定(s05)
```

### 各步骤概要

| 步骤 | 名称 | 核心任务 | 关键输出 |
|------|------|----------|----------|
| s01 | 数据接入与契约核验 | 核验样本、变量、单位、网格坐标 | dataset_manifest.json, data_contract.json |
| s02 | 预处理与数据切分 | 统一物理量表示，构造无泄漏切分 | train/validation/test_manifest.json, normalization.json |
| s03 | 模型配置与训练 | 训练Inverse PINN完成输入到目标映射 | best_checkpoint.pt, training_metrics.csv |
| s04 | 方程求解与物理残差恢复 | 恢复解场、导数、边界值与方程残差 | solution_fields/, pde_residuals/ |
| s05 | 任务验收与适用域判定 | 评估统计误差、物理约束、泛化能力 | evaluation.json, applicability_report.md |

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型类型 | Inverse PINN | [场景需求书] | 物理信息神经网络逆问题求解 |
| 模型类型 | Physics-informed data assimilation | [场景需求书] | 数据同化框架 |
| 训练框架 | PyTorch | [场景需求书] | 深度学习框架 |
| 默认epochs | 100 | [场景需求书] | 训练轮数 |
| 默认batch_size | 8 | [场景需求书] | 批量大小 |
| 默认learning_rate | 0.001 | [场景需求书] | 学习率 |
| early_stopping_patience | 15 | [场景需求书] | 早停耐心值 |
| 切分比例 | train:0.7, val:0.15, test:0.15 | [场景需求书] | 数据切分比例 |
| 相对误差门限 | 0.1 | [场景需求书] | 测试集放行阈值 |
| 无量纲化 | true | [场景需求书] | 统一跨工况量纲 |

## 边界与分流

1. **数据不足**：稀疏观测点数 < 参数敏感区域覆盖要求 → 需补充观测或引入强先验
2. **PDE定义不明确**：控制方程形式未知 → 转向方程发现任务（如PDE-FIND）
3. **训练不收敛**：物理损失与数据损失冲突 → 调整损失权重或网络架构
4. **域外工况**：测试工况超出训练分布 → 执行CFD复核验证
5. **多峰解**：参数空间存在多个局部最优 → 使用多起点优化或贝叶斯推断

## 质量检查

1. **数据完整性**：文件可读、样本可追溯、变量单位坐标定义完整
2. **切分有效性**：训练/验证/测试集无泄漏，仅用训练集计算变换统计量
3. **训练收敛性**：训练验证损失均为有限值，最佳权重可重新加载
4. **物理一致性**：解场导数与残差均为有限值，边初值满足门限
5. **泛化能力**：执行几何或工况外推测试，明确适用域限制

## 回退策略

1. **PINN训练失败** → 尝试传统优化方法（如遗传算法、粒子群）
2. **数据稀疏度过高** → 引入代理模型或降阶模型
3. **物理约束过强** → 放松权重或使用自适应权重调整
4. **计算资源不足** → 采用小规模子问题分解

## 资源召回建议

**何时召回本卡片**：
- 用户描述"稀疏观测参数反演"、"PDE参数估计"、"PINN逆问题"等任务
- 需要从有限观测推断流场参数
- 需要物理一致性约束的数据同化

**配套资源**：
- 相关论文：11篇（见metadata.evidence_papers）
- 数据集：稀疏流场观测数据
- 模型实现：Inverse PINN, Physics-informed data assimilation

## 证据来源

[1] Inferring flow parameters and turbulent configuration with physics-informed data assimilation and spectral nudging, 2018, URL: https://arxiv.org/abs/1804.07680
[2] CoPINN: Cognitive Physics-Informed Neural Networks, 2022
[3] Parameterized Physics-Informed Neural Networks for Parameterized PDEs, 2022
[4] RoPINN: Region Optimized Physics-Informed Neural Networks, 2022
[5] Multi-output physics-informed neural networks for forward and inverse PDE problems with uncertainties, 2022, URL: https://arxiv.org/abs/2202.01710
[6] Physics-informed learning of governing equations from scarce data, 2020, URL: https://arxiv.org/abs/2005.03448
[7] Surrogate modeling for fluid flows based on physics-constrained deep learning without simulation data, 2019, URL: https://arxiv.org/abs/1906.02382
[8] Physics informed deep learning (Part I): Data-driven solutions of nonlinear partial differential equations, 2017, URL: https://arxiv.org/abs/1711.10561
[9] Causal-PIK: Causality-based Physical Reasoning with a Physics-Informed Kernel, 2023
[10] DiffWind: Physics-Informed Differentiable Modeling of Wind-Driven Object Dynamics, 2023, URL: https://arxiv.org/abs/2311.15127
[11] Physics-informed learning under mixing: How physical knowledge speeds up learning, 2022
