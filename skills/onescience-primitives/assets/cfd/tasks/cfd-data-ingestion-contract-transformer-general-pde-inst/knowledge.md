# 实例任务：数据接入与契约核验 @ CFD_S052

- domain: cfd
- 骨架: cfd-data-ingestion-contract-validation-task
- 场景: cfd-transformer-general-pde-operator-pretrain-finetune-scenario (CFD_S052)
- step_id: s01
- depend: []

## 场景研究主体
- CFD_S052
- 关联论文: PDE-Transformer_ Efficient and Versatile Transformers for Physics Simulations | doi:; Curvature-aware Graph Attention for PDEs on Manifolds | doi:; Neural Interpretable PDEs_ Harmonizing Fourier Insights with Attention for Scalable and Interpretable Physics Di | doi:; Unisolver_ PDE-Conditional Transformers Towards Universal Neural PDE Solvers | doi:; S-Crescendo_ A Nested Transformer Weaving Framework for Scalable Nonlinear System in S-Domain Representation | doi:; FUSE_ Fast Unified Simulation and Estimation for PDEs | doi:; DPOT_ Auto-Regressive Denoising Operator Transformer for Large-Scale PDE Pre-Training | doi:; Universal Physics Transformers_ A Framework For Efficiently Scaling Neural Operators | doi:; Positional Knowledge is All You Need_ Position-induced Transformer (PiT) for Operator Learning | doi:; Choose a Transformer_ Fourier or Galerkin | doi:

## 本实例步骤描述
接入多方程多网格预训练数据，核验样本、变量、单位、网格坐标及许可。

## 本实例执行 prompt
读取{DATASET_PATH}中的{DATASET_NAME}，为“Transformer通用PDE算子预训练与微调”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。

## 本实例输入槽
- {DATASET_PATH} | required=True | type=doc | var_name=数据集路径 | hint=目录或清单文件 | default=
- {DATASET_NAME} | required=True | type=str | var_name=数据集名称 | hint=来源与数据版本 | default=多方程多网格预训练数据
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
- models/transformer

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
