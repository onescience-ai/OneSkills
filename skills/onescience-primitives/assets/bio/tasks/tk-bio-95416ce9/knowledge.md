# 骨架任务：单细胞数据与任务定义

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 读取Geneformer与scGPT单细胞知识可解释性比较的表达、染色质或空间多组学数据。
- 读取MCMC引导的多组学单细胞扰动预测的表达、染色质或空间多组学数据。
- 读取scGPT造血细胞表征与谱系结构解析的表达、染色质或空间多组学数据。
- 读取单细胞到空间转录组的缺失表达恢复的表达、染色质或空间多组学数据。
- 读取单细胞染色质可及性基础表征与注释的表达、染色质或空间多组学数据。
- 读取因果潜扩散的未见扰动响应预测的表达、染色质或空间多组学数据。
- 读取多模态推理增强的遗传扰动虚拟细胞预测的表达、染色质或空间多组学数据。
- 读取空间转录组与蛋白组图基础表征的表达、染色质或空间多组学数据。
- 读取空间转录组区域识别与组织架构解析的表达、染色质或空间多组学数据。
- 读取跨细胞类型与剂量的扰动响应预测的表达、染色质或空间多组学数据。

## 执行 prompt（跨场景聚合去重）
- 读取{CELL_DATA}的{DATA_LAYER}层，检查细胞、基因和空间坐标，使用{MODEL_NAME}建立Geneformer与scGPT单细胞知识可解释性比较任务。
- 读取{CELL_DATA}的{DATA_LAYER}层，检查细胞、基因和空间坐标，使用{MODEL_NAME}建立MCMC引导的多组学单细胞扰动预测任务。
- 读取{CELL_DATA}的{DATA_LAYER}层，检查细胞、基因和空间坐标，使用{MODEL_NAME}建立scGPT造血细胞表征与谱系结构解析任务。
- 读取{CELL_DATA}的{DATA_LAYER}层，检查细胞、基因和空间坐标，使用{MODEL_NAME}建立单细胞到空间转录组的缺失表达恢复任务。
- 读取{CELL_DATA}的{DATA_LAYER}层，检查细胞、基因和空间坐标，使用{MODEL_NAME}建立单细胞染色质可及性基础表征与注释任务。
- 读取{CELL_DATA}的{DATA_LAYER}层，检查细胞、基因和空间坐标，使用{MODEL_NAME}建立因果潜扩散的未见扰动响应预测任务。
- 读取{CELL_DATA}的{DATA_LAYER}层，检查细胞、基因和空间坐标，使用{MODEL_NAME}建立多模态推理增强的遗传扰动虚拟细胞预测任务。
- 读取{CELL_DATA}的{DATA_LAYER}层，检查细胞、基因和空间坐标，使用{MODEL_NAME}建立空间转录组与蛋白组图基础表征任务。
- 读取{CELL_DATA}的{DATA_LAYER}层，检查细胞、基因和空间坐标，使用{MODEL_NAME}建立空间转录组区域识别与组织架构解析任务。
- 读取{CELL_DATA}的{DATA_LAYER}层，检查细胞、基因和空间坐标，使用{MODEL_NAME}建立跨细胞类型与剂量的扰动响应预测任务。

## 输入槽（var/hint/default）
- {CELL_DATA} | required=True | type=doc | var_name=单细胞数据 | hint=输入H5AD或表达矩阵 | default=Parse_filtered.h5ad
- {MODEL_NAME} | required=True | type=enum | var_name=单细胞模型 | hint=选择场景使用的模型 | default=STATE
- {DATA_LAYER} | required=False | type=str | var_name=表达数据层 | hint=填写用于分析的数据层 | default=counts

## 产出
- 任务配置
- 标准化AnnData
- 特征与样本清单

## 质量门禁 quality_gate
- 必要的元数据列存在
- 细胞和基因标识唯一
- 计数矩阵维度一致

## 可调资源（edge:resource，仅真实存在）
- components/anndata
- tools/scanpy

## 实例任务（本骨架在各场景的实例化）
- it-228b3231
- it-26e3aad7
- it-3d26fad2
- it-5ea42b9f
- it-9538dedb
- it-b29214fa
- it-c1677eca
- it-c943a0c1
- it-d48d45da
- it-df4aacd6

## 复用场景
- B72
- B75
- B71
- B77
- B76
- B79
- B74
- B80
- B78
- B73
