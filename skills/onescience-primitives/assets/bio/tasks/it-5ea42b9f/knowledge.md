# 实例任务：单细胞数据与任务定义 @ B71

- domain: bio
- 骨架: tk-bio-95416ce9
- 场景: sc-628ab0d9 (B71)
- step_id: s01
- depend: []

## 场景研究主体
- B71
- 关联论文: Discovery of a Hematopoietic Manifold in scGPT Yields a Method for Extracting Performant Algorithms from Biological Foundation Model Internals | doi:; Sparse autoencoders reveal organized biological knowledge but minimal regulatory logic in single-cell foundation models: a comparative atlas of Geneformer and scGPT | doi:; scGPT: toward building a foundation model for single-cell multi-omics using generative AI | doi:

## 本实例步骤描述
读取scGPT造血细胞表征与谱系结构解析的表达、染色质或空间多组学数据。

## 本实例执行 prompt
读取{CELL_DATA}的{DATA_LAYER}层，检查细胞、基因和空间坐标，使用{MODEL_NAME}建立scGPT造血细胞表征与谱系结构解析任务。

## 本实例输入槽
- {CELL_DATA} | required=True | type=doc | var_name=单细胞数据 | hint=输入H5AD或表达矩阵 | default=hematopoiesis.h5ad
- {MODEL_NAME} | required=True | type=enum | var_name=单细胞模型 | hint=选择场景使用的模型 | default=scGPT
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
- tools/scanpy

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
