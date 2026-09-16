# 实例任务：数据接入与契约核验 @ CFD_S044

- domain: cfd
- 骨架: cfd-data-ingestion-contract-validation-task
- 场景: cfd-deep-ritz-weak-form-neural-variational-solver-scenario (CFD_S044)
- step_id: s01
- depend: []

## 场景研究主体
- CFD_S044
- 关联论文: Refined generalization analysis of the Deep Ritz Method and Physics-Informed Neural Networks | doi:; PINP_ Physics-Informed Neural Predictor with latent estimation of fluid flows | doi:; Gradient Alignment in Physics-informed Neural Networks_ A Second-Order Optimization Perspective | doi:; Learning from Integral Losses in Physics-Informed Neural Networks | doi:; Efficient Error Certification for Physics-Informed Neural Networks | doi:; Solving Poisson Equations using Neural Walk-on-Spheres | doi:; Characteristic Neural Ordinary Differential Equation | doi:; Entropy-dissipation Informed Neural Network for McKean-Vlasov Type PDEs | doi:; Randomized Sparse Neural Galerkin Schemes for Solving Evolution Equations with Deep Networks | doi:; Physics-informed neural networks for the shallow-water equations on the sphere | doi:; Characterizing possible failure modes in physics-informed neural networks | doi:; Error Analysis of Deep Ritz Methods for Elliptic Equations | doi:; Adaptive activation functions accelerate convergence in deep and physics-informed neural networks | doi:; Weak adversarial networks for high-dimensional partial differential equations | doi:; The Deep Ritz Method_ A Deep Learning-Based Numerical Algorithm for Solving Variational Problems | doi:; The neural particle method – An updated Lagrangian physics informed neural network for computational fluid d | doi:; Composing Partial Differential Equations with Physics-Aware Neural Networks | doi:; Physics-informed Neural Networks for Functional Differential Equations_ Cylindrical Approximation and Its Co | doi:; FlashPDE_ A Drop-In Fused Triton Operator Library for Neural PDE Solvers | doi:

## 本实例步骤描述
接入椭圆与演化方程变分积分数据，核验样本、变量、单位、网格坐标及许可。

## 本实例执行 prompt
读取{DATASET_PATH}中的{DATASET_NAME}，为“Deep Ritz与弱形式神经变分求解”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。

## 本实例输入槽
- {DATASET_PATH} | required=True | type=doc | var_name=数据集路径 | hint=目录或清单文件 | default=
- {DATASET_NAME} | required=True | type=str | var_name=数据集名称 | hint=来源与数据版本 | default=椭圆与演化方程变分积分数据
- {DATA_CONTRACT} | required=False | type=object | var_name=数据契约 | hint=变量单位网格定义 | default={'input_fields': [], 'target_fields': [], 'units': {}, 'coordinates': 'dataset_native'}

## 本实例产出
- dataset_manifest.json
- data_contract.json
- data_audit.md

## 本实例质量门禁
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
