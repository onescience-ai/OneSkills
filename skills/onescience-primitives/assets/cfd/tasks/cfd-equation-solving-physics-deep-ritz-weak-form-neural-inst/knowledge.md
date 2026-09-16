# 实例任务：方程求解与物理残差恢复 @ CFD_S044

- domain: cfd
- 骨架: cfd-equation-solving-physics-residual-restoration-task
- 场景: cfd-deep-ritz-weak-form-neural-variational-solver-scenario (CFD_S044)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- CFD_S044
- 关联论文: Refined generalization analysis of the Deep Ritz Method and Physics-Informed Neural Networks | doi:; PINP_ Physics-Informed Neural Predictor with latent estimation of fluid flows | doi:; Gradient Alignment in Physics-informed Neural Networks_ A Second-Order Optimization Perspective | doi:; Learning from Integral Losses in Physics-Informed Neural Networks | doi:; Efficient Error Certification for Physics-Informed Neural Networks | doi:; Solving Poisson Equations using Neural Walk-on-Spheres | doi:; Characteristic Neural Ordinary Differential Equation | doi:; Entropy-dissipation Informed Neural Network for McKean-Vlasov Type PDEs | doi:; Randomized Sparse Neural Galerkin Schemes for Solving Evolution Equations with Deep Networks | doi:; Physics-informed neural networks for the shallow-water equations on the sphere | doi:; Characterizing possible failure modes in physics-informed neural networks | doi:; Error Analysis of Deep Ritz Methods for Elliptic Equations | doi:; Adaptive activation functions accelerate convergence in deep and physics-informed neural networks | doi:; Weak adversarial networks for high-dimensional partial differential equations | doi:; The Deep Ritz Method_ A Deep Learning-Based Numerical Algorithm for Solving Variational Problems | doi:; The neural particle method – An updated Lagrangian physics informed neural network for computational fluid d | doi:; Composing Partial Differential Equations with Physics-Aware Neural Networks | doi:; Physics-informed Neural Networks for Functional Differential Equations_ Cylindrical Approximation and Its Co | doi:; FlashPDE_ A Drop-In Fused Triton Operator Library for Neural PDE Solvers | doi:

## 本实例步骤描述
在查询配点或网格上恢复解场、导数、边界值与方程残差。

## 本实例执行 prompt
加载{CHECKPOINT}，在测试参数、边界和查询坐标上求解目标PDE，使用自动微分或离散算子恢复导数、通量和方程残差。保存解场与残差场；禁止只依据训练损失判定方程已求解。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=通过训练门限权重 | default=best_checkpoint.pt
- {DEVICE} | required=True | type=str | var_name=计算设备 | hint=CPU或CUDA设备 | default=cuda
- {BATCH_SIZE} | required=False | type=int | var_name=推理批大小 | hint=按显存调整批量 | default=8

## 本实例产出
- solution_fields/
- pde_residuals/
- boundary_residuals.csv

## 本实例质量门禁
- 解场导数与残差均为有限值
- 边初值逐项满足门限
- 独立数值解或解析解可对照

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
