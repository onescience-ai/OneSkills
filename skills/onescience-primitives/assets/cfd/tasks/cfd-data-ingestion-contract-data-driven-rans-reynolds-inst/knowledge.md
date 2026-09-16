# 实例任务：数据接入与契约核验 @ CFD_S073

- domain: cfd
- 骨架: cfd-data-ingestion-contract-validation-task
- 场景: cfd-data-driven-rans-reynolds-stress-eddy-viscosity-closure-scenario (CFD_S073)
- step_id: s01
- depend: []

## 场景研究主体
- CFD_S073
- 关联论文: Quantifying model form uncertainty in Reynolds-averaged turbulence models with Bayesian deep neural networks | doi:; Machine learning for RANS turbulence modeling of variable property flows | doi:; Deep Learning Methods for Reynolds-Averaged Navier–Stokes Simulations of Airfoil Flows | doi:; Data-driven nonlinear turbulent flow scaling with Buckingham Pi variables | doi:; Turbulence model augmented physics-informed neural networks for mean-flow reconstruction | doi:; Predictions of turbulent shear flows using deep neural networks | doi:; Machine-Learning-Augmented Predictive Modeling of Turbulent Separated Flows over Airfoils | doi:; Physics-informed machine learning approach for augmenting turbulence models_ A comprehensive framework | doi:; RANS turbulence model development using CFD-driven machine learning | doi:; From Bypass Transition to Flow Control and Data-Driven Turbulence Modeling_ An Input–Output Viewpoint | doi:; Perspectives on machine learning-augmented Reynolds-averaged and large eddy simulation models of turbulence | doi:; Discovering explicit Reynolds-averaged turbulence closures for turbulent separated flows through deep learni | doi:; FoilDiff_ A Hybrid Transformer Backbone for Diffusion-based Modelling of 2D Airfoil Flow Fields | doi:; A Symplectic Theory of Turbulence Closure_ Hidden Reservoir Dynamics, Endogenous Stochastic Transport, and Kraichnan Dual Cascades | doi:; A high-fidelity numerical database for free-stream transition | doi:; Learning Turbulence Closures with Physics-Informed Neural Networks for the Rayleigh-Taylor Transition to Turbulence | doi:; Towards bridging the gap between data-driven and theoretical turbulence closures in stratified flows | doi:; VATO_ A Vortex-Force-Aware Transformer Operator for Unsteady Separated Aerofoil Flows | doi:

## 本实例步骤描述
接入DNS与RANS配对湍流闭合数据，核验样本、变量、单位、网格坐标及许可。

## 本实例执行 prompt
读取{DATASET_PATH}中的{DATASET_NAME}，为“数据驱动RANS雷诺应力与涡黏闭合”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。

## 本实例输入槽
- {DATASET_PATH} | required=True | type=doc | var_name=数据集路径 | hint=目录或清单文件 | default=
- {DATASET_NAME} | required=True | type=str | var_name=数据集名称 | hint=来源与数据版本 | default=DNS与RANS配对湍流闭合数据
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
