# 实例任务：数据接入与契约核验 @ CFD_S074

- domain: cfd
- 骨架: cfd-data-ingestion-contract-validation-task
- 场景: cfd-hypersonic-transonic-boundary-layer-turbulence-surrogate-scenario (CFD_S074)
- step_id: s01
- depend: []

## 场景研究主体
- CFD_S074
- 关联论文: Data-Driven Turbulence Modeling Approach for Cold-Wall Hypersonic Boundary Layers | doi:; Gaussian processes at the Helm(holtz)_ A more fluid model for ocean currents | doi:; Scalable Transformer for PDE Surrogate Modeling | doi:; Aeroelastic Reduced-Order Model Differential Equations in Transonic Buffeting Flow | doi:; Compact representation of transonic airfoil buffet flows with observable-augmented machine learning | doi:; SuperWing_ a comprehensive transonic wing dataset for data-driven aerodynamic design | doi:; Neural Differential Equations for Oscillatory Flows in Aeroelasticity Applied to Transonic Buffet | doi:; SMART_ Scalable Mesh-free Aerodynamic Simulations from Raw Geometries using a Transformer-based Surrogate Model | doi:

## 本实例步骤描述
接入高超声速冷壁与跨声速机翼CFD数据，核验样本、变量、单位、网格坐标及许可。

## 本实例执行 prompt
读取{DATASET_PATH}中的{DATASET_NAME}，为“高超声速与跨声速边界层湍流代理”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。

## 本实例输入槽
- {DATASET_PATH} | required=True | type=doc | var_name=数据集路径 | hint=目录或清单文件 | default=
- {DATASET_NAME} | required=True | type=str | var_name=数据集名称 | hint=来源与数据版本 | default=高超声速冷壁与跨声速机翼CFD数据
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
