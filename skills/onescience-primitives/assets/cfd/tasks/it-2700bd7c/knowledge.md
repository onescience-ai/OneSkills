# 实例任务：数据接入与契约核验 @ CFD_S003

- domain: cfd
- 骨架: tk-cfd-54dc529a
- 场景: sc-33189952 (CFD_S003)
- step_id: s01
- depend: []

## 场景研究主体
- CFD_S003
- 关联论文: A Kernel-based Resource-efficient Neural Surrogate for Multi-fidelity Prediction of Aerodynamic Field | doi:; AFBench_ A Large-scale Benchmark for Airfoil Design | doi:; Airfoil optimization using Design-by-Morphing with minimized design-space dimensionality | doi:; Predictive Criteria for Electrospray-Assisted Droplet Dynamics in Aerodynamic Flow Fields | doi:; AeroJEPA_ Learning Semantic Latent Representations for Scalable 3D Aerodynamic Field Modeling | doi:; AirfoilGen_ A valid-by-construction and performance-aware latent diffusion model for airfoil generation | doi:

## 本实例步骤描述
接入参数化翼型多工况与多保真数据，核验样本、变量、单位、网格坐标及许可。

## 本实例执行 prompt
读取{DATASET_PATH}中的{DATASET_NAME}，为“核方法与生成模型翼型跨工况场预测”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。

## 本实例输入槽
- {DATASET_PATH} | required=True | type=doc | var_name=数据集路径 | hint=目录或清单文件 | default=
- {DATASET_NAME} | required=True | type=str | var_name=数据集名称 | hint=来源与数据版本 | default=参数化翼型多工况与多保真数据
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
