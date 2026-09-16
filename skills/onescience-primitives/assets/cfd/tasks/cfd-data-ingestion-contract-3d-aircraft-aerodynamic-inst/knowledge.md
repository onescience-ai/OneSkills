# 实例任务：数据接入与契约核验 @ CFD_S035

- domain: cfd
- 骨架: cfd-data-ingestion-contract-validation-task
- 场景: cfd-3d-aircraft-aerodynamic-inverse-design-scenario (CFD_S035)
- step_id: s01
- depend: []

## 场景研究主体
- CFD_S035
- 关联论文: BlendedNet++_ A dataset and benchmark for field-resolved aerodynamics and inverse design of blended wing body aircraft | doi:; Inverse Design for Fluid-Structure Interactions using Graph Network Simulators | doi:; PIED_ Physics-Informed Experimental Design for Inverse Problems | doi:; 3DID_ Direct 3D Inverse Design for Aerodynamics with Physics-Aware Optimization | doi:

## 本实例步骤描述
接入三维机翼与融合翼身气动数据，核验样本、变量、单位、网格坐标及许可。

## 本实例执行 prompt
读取{DATASET_PATH}中的{DATASET_NAME}，为“三维航空器目标气动响应逆向设计”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。

## 本实例输入槽
- {DATASET_PATH} | required=True | type=doc | var_name=数据集路径 | hint=目录或清单文件 | default=
- {DATASET_NAME} | required=True | type=str | var_name=数据集名称 | hint=来源与数据版本 | default=三维机翼与融合翼身气动数据
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
