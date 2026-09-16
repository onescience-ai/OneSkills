# 实例任务：单细胞数据与任务定义 @ B76

- domain: bio
- 骨架: bio-single-cell-data-task-definition-task
- 场景: bio-single-cell-chromatin-accessibility-foundation-characterization-scenario (B76)
- step_id: s01
- depend: []

## 场景研究主体
- B76
- 关联论文: ChromFound: Towards A Universal Foundation Model for Single-Cell Chromatin Accessibility Data | doi:; CellxPert: Inference-Time MCMC Steering of a Multi-Omics Single-Cell Foundation Model for In-Silico Perturbation | doi:

## 本实例步骤描述
读取单细胞染色质可及性基础表征与注释的表达、染色质或空间多组学数据。

## 本实例执行 prompt
读取{CELL_DATA}的{DATA_LAYER}层，检查细胞、基因和空间坐标，使用{MODEL_NAME}建立单细胞染色质可及性基础表征与注释任务。

## 本实例输入槽
- {CELL_DATA} | required=True | type=doc | var_name=单细胞数据 | hint=输入H5AD或表达矩阵 | default=pbmc_atac.h5ad
- {MODEL_NAME} | required=True | type=enum | var_name=单细胞模型 | hint=选择场景使用的模型 | default=ChromFound
- {DATA_LAYER} | required=False | type=str | var_name=表达数据层 | hint=填写用于分析的数据层 | default=counts

## 本实例产出
- 标准化AnnData
- 特征与样本清单
- 任务配置

## 本实例质量门禁
- 细胞和基因标识唯一
- 计数矩阵维度一致
- 必要的元数据列存在

## 可调资源（edge:resource，仅真实存在）
- components/anndata
- datasets/cellxgene_census
- tools/pdb-structure-data-access
- tools/scanpy
- tools/simplefold-protein-structure-prediction-model-and-pipeline

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
