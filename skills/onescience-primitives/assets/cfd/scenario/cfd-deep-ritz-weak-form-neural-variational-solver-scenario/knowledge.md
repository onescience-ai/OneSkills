# 场景：CFD_S044

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Deep Ritz network', 'Weak-form neural solver']
- 工具: []

## 研究意图（agent_task_prompt）
（源场景未提供）

## 客户端请求
- task_title: 
- request: 
- scientific_context: 
- desired_outcome: 
- executor_role: 

## 问题与适用性
面向椭圆与演化方程变分积分数据完成Deep Ritz与弱形式神经变分求解。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 方程求解与物理残差恢复
- s05 任务验收与适用域判定

## 关联论文
- Refined generalization analysis of the Deep Ritz Method and Physics-Informed Neural Networks | doi:
- PINP_ Physics-Informed Neural Predictor with latent estimation of fluid flows | doi:
- Gradient Alignment in Physics-informed Neural Networks_ A Second-Order Optimization Perspective | doi:
- Learning from Integral Losses in Physics-Informed Neural Networks | doi:
- Efficient Error Certification for Physics-Informed Neural Networks | doi:
- Solving Poisson Equations using Neural Walk-on-Spheres | doi:
- Characteristic Neural Ordinary Differential Equation | doi:
- Entropy-dissipation Informed Neural Network for McKean-Vlasov Type PDEs | doi:
- Randomized Sparse Neural Galerkin Schemes for Solving Evolution Equations with Deep Networks | doi:
- Physics-informed neural networks for the shallow-water equations on the sphere | doi:
- Characterizing possible failure modes in physics-informed neural networks | doi:
- Error Analysis of Deep Ritz Methods for Elliptic Equations | doi:
- Adaptive activation functions accelerate convergence in deep and physics-informed neural networks | doi:
- Weak adversarial networks for high-dimensional partial differential equations | doi:
- The Deep Ritz Method_ A Deep Learning-Based Numerical Algorithm for Solving Variational Problems | doi:
- The neural particle method – An updated Lagrangian physics informed neural network for computational fluid d | doi:
- Composing Partial Differential Equations with Physics-Aware Neural Networks | doi:
- Physics-informed Neural Networks for Functional Differential Equations_ Cylindrical Approximation and Its Co | doi:
- FlashPDE_ A Drop-In Fused Triton Operator Library for Neural PDE Solvers | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
