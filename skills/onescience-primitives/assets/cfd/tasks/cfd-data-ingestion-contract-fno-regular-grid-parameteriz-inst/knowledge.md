# 实例任务：数据接入与契约核验 @ CFD_S048

- domain: cfd
- 骨架: cfd-data-ingestion-contract-validation-task
- 场景: cfd-fno-regular-grid-parameterized-pde-operator-learning-scenario (CFD_S048)
- step_id: s01
- depend: []

## 场景研究主体
- CFD_S048
- 关联论文: Tucker-FNO_ Tensor Tucker-Fourier Neural Operator and its Universal Approximation Theory | doi:; Fourier Neural Operator for Parametric Partial Differential Equations | doi:; Factorized Fourier Neural Operators | doi:; Maximal Update Parametrization and Zero-Shot Hyperparameter Transfer for Fourier Neural Operators | doi:; Sensitivity-Constrained Fourier Neural Operators for Forward and Inverse Problems in Parametric Differential Equations | doi:; Beyond Regular Grids_ Fourier-Based Neural Operators on Arbitrary Domains | doi:; Domain Agnostic Fourier Neural Operators | doi:; U-FNO_ An Enhanced Fourier Neural Operator-Based Deep-Learning Model for Multiphase Flow | doi:; Understanding the Expressivity and Trainability of Fourier Neural Operator_ A Mean-Field Perspective | doi:; Spectral-Refiner_ Accurate Fine-Tuning of Spatiotemporal Fourier Neural Operator for Turbulent Flows | doi:; Extending Fourier Neural Operators for Modeling Parameterized and Coupled PDEs | doi:; Evaluation of State-of-the-Art Deep Learning Architectures for Aerodynamical Predictions | doi:

## 本实例步骤描述
接入Darcy与Navier-Stokes规则网格数据，核验样本、变量、单位、网格坐标及许可。

## 本实例执行 prompt
读取{DATASET_PATH}中的{DATASET_NAME}，为“FNO规则网格参数化PDE算子学习”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。

## 本实例输入槽
- {DATASET_PATH} | required=True | type=doc | var_name=数据集路径 | hint=目录或清单文件 | default=
- {DATASET_NAME} | required=True | type=str | var_name=数据集名称 | hint=来源与数据版本 | default=Darcy与Navier-Stokes规则网格数据
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
- models/fno

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
