# 实例任务：源观测和参考资料及任务边界预检 @ E63

- domain: climate
- 骨架: climate-source-obs-reference-data-boundary-task
- 场景: climate-ground-meteorological-driven-daily-total-solar-radiation-scenario (E63)
- step_id: s01
- depend: []

## 场景研究主体
- E63
- 关联论文: Artificial neural network model with different backpropagation algorithms and meteorological data for solar radiation prediction | doi:; Solar Radiation Prediction Using Different Machine Learning Algorithms and Implications for Extreme Climate Events | doi:; Global solar radiation prediction using artificial neural network models for New Zealand | doi:

## 本实例步骤描述
界定“地面气象要素驱动的日总太阳辐射估算”的任务范围并执行“源观测和参考资料及任务边界预检”，核验站点日温度、湿度、风速及可选时间特征的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“地面气象要素驱动的日总太阳辐射估算”，读取{SOURCE_OBSERVATIONS}、{AUXILIARY_DATA}、{TARGET_REGION_TIME}、{TARGET_VARIABLE}、{DATA_CUTOFF_TIME}并完成源观测和参考资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {SOURCE_OBSERVATIONS} | required=True | type=str | var_name=源观测资料 | hint=输入源观测资料路径。 | default=None
- {AUXILIARY_DATA} | required=False | type=str | var_name=辅助资料 | hint=输入辅助资料路径。 | default=None
- {TARGET_REGION_TIME} | required=True | type=str | var_name=目标区域时段 | hint=输入区域和观测时段。 | default=None
- {TARGET_VARIABLE} | required=True | type=str | var_name=目标诊断量 | hint=输入目标诊断量。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 源观测与辅助资料的有效时间和来源可追溯

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/lpma-airport-wind-observation-validation
- datasets/ostia-sst-data
- datasets/sgp-c1-multi-source-boundary-layer-height-dataset
- datasets/snodas-swe-data-product
- models/anomaly-numerical-correction-with-observations-ano
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
