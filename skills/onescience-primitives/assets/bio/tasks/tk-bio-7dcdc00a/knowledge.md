# 骨架任务：基因组输入与坐标规范化

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 读取DNA语言模型生物任务基准评测的DNA、区间、变异或表观信号。
- 读取单纯形流匹配的调控DNA序列设计的DNA、区间、变异或表观信号。
- 读取双向等变长程DNA序列建模的DNA、区间、变异或表观信号。
- 读取基因组语言模型中转录因子特征的因果解析的DNA、区间、变异或表观信号。
- 读取多物种DNA序列表征与下游分类的DNA、区间、变异或表观信号。
- 读取水稻育种变异功能效应优先级预测的DNA、区间、变异或表观信号。
- 读取百万碱基上下文基因组建模与序列设计的DNA、区间、变异或表观信号。
- 读取组蛋白修饰驱动的基因表达预测的DNA、区间、变异或表观信号。
- 读取细胞类型特异调控DNA条件生成的DNA、区间、变异或表观信号。
- 读取长DNA区间多组学轨迹与变异效应预测的DNA、区间、变异或表观信号。

## 执行 prompt（跨场景聚合去重）
- 读取{GENOMICS_INPUT}，相对{REFERENCE_GENOME}校验序列和坐标，使用{MODEL_NAME}建立DNA语言模型生物任务基准评测任务。
- 读取{GENOMICS_INPUT}，相对{REFERENCE_GENOME}校验序列和坐标，使用{MODEL_NAME}建立单纯形流匹配的调控DNA序列设计任务。
- 读取{GENOMICS_INPUT}，相对{REFERENCE_GENOME}校验序列和坐标，使用{MODEL_NAME}建立双向等变长程DNA序列建模任务。
- 读取{GENOMICS_INPUT}，相对{REFERENCE_GENOME}校验序列和坐标，使用{MODEL_NAME}建立基因组语言模型中转录因子特征的因果解析任务。
- 读取{GENOMICS_INPUT}，相对{REFERENCE_GENOME}校验序列和坐标，使用{MODEL_NAME}建立多物种DNA序列表征与下游分类任务。
- 读取{GENOMICS_INPUT}，相对{REFERENCE_GENOME}校验序列和坐标，使用{MODEL_NAME}建立水稻育种变异功能效应优先级预测任务。
- 读取{GENOMICS_INPUT}，相对{REFERENCE_GENOME}校验序列和坐标，使用{MODEL_NAME}建立百万碱基上下文基因组建模与序列设计任务。
- 读取{GENOMICS_INPUT}，相对{REFERENCE_GENOME}校验序列和坐标，使用{MODEL_NAME}建立组蛋白修饰驱动的基因表达预测任务。
- 读取{GENOMICS_INPUT}，相对{REFERENCE_GENOME}校验序列和坐标，使用{MODEL_NAME}建立细胞类型特异调控DNA条件生成任务。
- 读取{GENOMICS_INPUT}，相对{REFERENCE_GENOME}校验序列和坐标，使用{MODEL_NAME}建立长DNA区间多组学轨迹与变异效应预测任务。

## 输入槽（var/hint/default）
- {GENOMICS_INPUT} | required=True | type=doc | var_name=基因组输入 | hint=输入序列区间或变异 | default=chr22_interval.csv
- {MODEL_NAME} | required=True | type=enum | var_name=基因组模型 | hint=选择场景使用的模型 | default=AlphaGenome
- {REFERENCE_GENOME} | required=False | type=enum | var_name=参考基因组 | hint=选择坐标参考版本 | default=hg38

## 产出
- 任务配置
- 坐标检查报告
- 标准化基因组输入

## 质量门禁 quality_gate
- 坐标位于参考范围
- 样本标识唯一
- 等位基因方向一致

## 可调资源（edge:resource，仅真实存在）
- models/proteinmpnn

## 实例任务（本骨架在各场景的实例化）
- it-0457f530
- it-0d57e2f6
- it-27bedc16
- it-31e4adbe
- it-63d10f0d
- it-a0affaba
- it-a2ff58fe
- it-c2d95510
- it-d7e25731
- it-f371f71d

## 复用场景
- B65
- B70
- B64
- B66
- B63
- B69
- B62
- B68
- B67
- B61
