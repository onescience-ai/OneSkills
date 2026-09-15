# 实例任务：数据接入与契约核验 @ CFD_S058

- domain: cfd
- 骨架: tk-cfd-54dc529a
- 场景: sc-c9e18696 (CFD_S058)
- step_id: s01
- depend: []

## 场景研究主体
- CFD_S058
- 关联论文: NUNO_ A General Framework for Learning Parametric PDEs with Non-Uniform Data | doi:; Reference Neural Operators_ Learning the Smooth Dependence of Solutions of PDEs on Geometric Deformations | doi:; Geometry-Informed Neural Operator for Large-Scale 3D PDEs | doi:; From Cheap Geometry to Expensive Physics_ A Physics-agnostic Pretraining Framework for Neural Operators | doi:; Operator Learning with Domain Decomposition for Geometry Generalization in PDE Solving | doi:; DD-RNO_ A Domain-Decomposed Routed Neural Operator for Airfoil Flow Prediction | doi:; Geometry-Aware Anisotropic Boundary Correction for Aerodynamic Simulation | doi:; Striding Across Reynolds Numbers_ Representation Geometry in Neural PDE Generalisation | doi:

## 本实例步骤描述
接入非均匀采样与变形几何PDE数据，核验样本、变量、单位、网格坐标及许可。

## 本实例执行 prompt
读取{DATASET_PATH}中的{DATASET_NAME}，为“域分解与非均匀几何神经算子学习”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。

## 本实例输入槽
- {DATASET_PATH} | required=True | type=doc | var_name=数据集路径 | hint=目录或清单文件 | default=
- {DATASET_NAME} | required=True | type=str | var_name=数据集名称 | hint=来源与数据版本 | default=非均匀采样与变形几何PDE数据
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
