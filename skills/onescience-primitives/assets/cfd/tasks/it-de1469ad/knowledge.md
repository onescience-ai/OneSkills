# 实例任务：数据接入与契约核验 @ CFD_S057

- domain: cfd
- 骨架: tk-cfd-54dc529a
- 场景: sc-27b63ea3 (CFD_S057)
- step_id: s01
- depend: []

## 场景研究主体
- CFD_S057
- 关联论文: Group Equivariant Fourier Neural Operators for Partial Differential Equations | doi:; DeltaPhi_ Physical States Residual Learning for Neural Operators in Data-Limited PDE Solving | doi:; Accelerating Data Generation for Neural Operators via Krylov Subspace Recycling | doi:; Equivariant Graph Neural Operator for Modeling 3D Dynamics | doi:; Guaranteed Approximation Bounds for Mixed-Precision Neural Operators | doi:; An Intrinsic Vector Heat Network | doi:; Random Grid Neural Processes for Parametric Partial Differential Equations | doi:; Globally injective and bijective neural operators | doi:; Spherical Fourier Neural Operators_ Learning Stable Dynamics on the Sphere | doi:; Can neural operators always be continuously discretized | doi:; Banach neural operator for Navier–Stokes equations | doi:; Fengbo_ a Clifford Neural Operator pipeline for 3D PDEs in Computational Fluid Dynamics | doi:; Generalized Spherical Neural Operators_ Green’s Function Formulation | doi:; Locally Subspace-Informed Neural Operators for Efficient Multiscale PDE Solving | doi:

## 本实例步骤描述
接入球面向量场与三维对称PDE数据，核验样本、变量、单位、网格坐标及许可。

## 本实例执行 prompt
读取{DATASET_PATH}中的{DATASET_NAME}，为“等变球面与Clifford神经算子学习”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。

## 本实例输入槽
- {DATASET_PATH} | required=True | type=doc | var_name=数据集路径 | hint=目录或清单文件 | default=
- {DATASET_NAME} | required=True | type=str | var_name=数据集名称 | hint=来源与数据版本 | default=球面向量场与三维对称PDE数据
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
