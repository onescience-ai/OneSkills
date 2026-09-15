# 实例任务：预处理与数据切分 @ CFD_S073

- domain: cfd
- 骨架: tk-cfd-446c2dc0
- 场景: sc-e7605c6c (CFD_S073)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- CFD_S073
- 关联论文: Quantifying model form uncertainty in Reynolds-averaged turbulence models with Bayesian deep neural networks | doi:; Machine learning for RANS turbulence modeling of variable property flows | doi:; Deep Learning Methods for Reynolds-Averaged Navier–Stokes Simulations of Airfoil Flows | doi:; Data-driven nonlinear turbulent flow scaling with Buckingham Pi variables | doi:; Turbulence model augmented physics-informed neural networks for mean-flow reconstruction | doi:; Predictions of turbulent shear flows using deep neural networks | doi:; Machine-Learning-Augmented Predictive Modeling of Turbulent Separated Flows over Airfoils | doi:; Physics-informed machine learning approach for augmenting turbulence models_ A comprehensive framework | doi:; RANS turbulence model development using CFD-driven machine learning | doi:; From Bypass Transition to Flow Control and Data-Driven Turbulence Modeling_ An Input–Output Viewpoint | doi:; Perspectives on machine learning-augmented Reynolds-averaged and large eddy simulation models of turbulence | doi:; Discovering explicit Reynolds-averaged turbulence closures for turbulent separated flows through deep learni | doi:; FoilDiff_ A Hybrid Transformer Backbone for Diffusion-based Modelling of 2D Airfoil Flow Fields | doi:; A Symplectic Theory of Turbulence Closure_ Hidden Reservoir Dynamics, Endogenous Stochastic Transport, and Kraichnan Dual Cascades | doi:; A high-fidelity numerical database for free-stream transition | doi:; Learning Turbulence Closures with Physics-Informed Neural Networks for the Rayleigh-Taylor Transition to Turbulence | doi:; Towards bridging the gap between data-driven and theoretical turbulence closures in stratified flows | doi:; VATO_ A Vortex-Force-Aware Transformer Operator for Unsteady Separated Aerofoil Flows | doi:

## 本实例步骤描述
统一物理量与表示，按几何、工况或时间构造无泄漏切分。

## 本实例执行 prompt
依据s01契约完成质控、重采样或图构建、掩膜、归一化或无量纲化。按{SPLIT_CONFIG}以几何、完整轨迹或物理工况为单位切分，不得把同一轨迹的帧随机打散。为{TARGET_FIELDS}保存统计量与可逆变换。

## 本实例输入槽
- {SPLIT_CONFIG} | required=True | type=object | var_name=切分配置 | hint=按对象工况切分 | default={'train': 0.7, 'validation': 0.15, 'test': 0.15, 'seed': 42, 'group_by': 'geometry_or_trajectory'}
- {TARGET_FIELDS} | required=True | type=list[str] | var_name=目标变量 | hint=待预测物理量 | default=['按data_contract.json填写']
- {NONDIMENSIONALIZE} | required=False | type=bool | var_name=是否无量纲化 | hint=统一跨工况量纲 | default=True

## 本实例产出
- train_manifest.json
- validation_manifest.json
- test_manifest.json
- normalization.json

## 本实例质量门禁
- 三份切分的对象轨迹互斥
- 仅用训练集计算变换统计量
- 边界与掩膜语义未破坏

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
