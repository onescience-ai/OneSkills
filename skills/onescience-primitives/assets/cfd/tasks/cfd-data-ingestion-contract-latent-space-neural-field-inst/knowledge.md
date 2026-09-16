# 实例任务：数据接入与契约核验 @ CFD_S054

- domain: cfd
- 骨架: cfd-data-ingestion-contract-validation-task
- 场景: cfd-latent-space-neural-field-continuous-pde-operator-learning-scenario (CFD_S054)
- step_id: s01
- depend: []

## 场景研究主体
- CFD_S054
- 关联论文: Latent Neural Operator for Solving Forward and Inverse PDE Problems | doi:; Discretization-invariance_ On the Discretization Mismatch Errors in Neural Operators | doi:; Neural Emulator Superiority_ When Machine Learning for PDEs Surpasses its Training Data | doi:; Implicit Representations via Operator Learning | doi:; Neural operators meet conjugate gradients_ The FCG-NO method for efficient PDE solving | doi:; GNOT_ A General Neural Operator Transformer for Operator Learning | doi:; General Covariance Data Augmentation for Neural PDE Solvers | doi:; Operator Learning with Neural Fields_ Tackling PDEs on General Geometries | doi:; Solving High-Dimensional PDEs with Latent Spectral Models | doi:; Meta-Auto-Decoder for Solving Parametric Partial Differential Equations | doi:; A Bregman Proximal Viewpoint on Neural Operators | doi:; GridMix_ Exploring Spatial Modulation for Neural Fields in PDE Modeling | doi:; Quantitative Approximation for Neural Operators in Nonlinear Parabolic Equations | doi:; Disentangled Representation Learning for Parametric Partial Differential Equations | doi:; Accelerating Bayesian inverse design in computational fluid dynamics using neural operators | doi:

## 本实例步骤描述
接入连续坐标与压缩潜空间PDE数据，核验样本、变量、单位、网格坐标及许可。

## 本实例执行 prompt
读取{DATASET_PATH}中的{DATASET_NAME}，为“潜空间与神经场连续PDE算子学习”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。

## 本实例输入槽
- {DATASET_PATH} | required=True | type=doc | var_name=数据集路径 | hint=目录或清单文件 | default=
- {DATASET_NAME} | required=True | type=str | var_name=数据集名称 | hint=来源与数据版本 | default=连续坐标与压缩潜空间PDE数据
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
