# 实例任务：污染气象资料及任务边界预检 @ E42

- domain: climate
- 骨架: climate-pollution-met-data-boundary-precheck-task
- 场景: climate-urban-station-pm25-short-term-concentration-forecast-scenario (E42)
- step_id: s01
- depend: []

## 场景研究主体
- E42
- 关联论文: An improved deep learning model for predicting daily PM2.5 concentration | doi:; Dynamically pre-trained deep recurrent neural networks using environmental monitoring data for predicting PM2.5 | doi:; PM2.5 forecasting for an urban area based on deep learning and decomposition method | doi:

## 本实例步骤描述
界定“城市站点PM2.5短期浓度预报”的任务范围并执行“污染气象资料及任务边界预检”，核验目标与邻站PM2.5历史、站点位置、气象预报的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“城市站点PM2.5短期浓度预报”，读取{AIR_QUALITY_DATA}、{METEOROLOGICAL_DATA}、{EMISSION_DATA}、{TARGET_REGION_TIME}、{DATA_CUTOFF_TIME}并完成污染气象资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {AIR_QUALITY_DATA} | required=True | type=str | var_name=污染观测资料 | hint=输入污染观测资料路径。 | default=None
- {METEOROLOGICAL_DATA} | required=True | type=str | var_name=气象驱动资料 | hint=输入气象驱动资料路径。 | default=None
- {EMISSION_DATA} | required=False | type=str | var_name=排放与活动资料 | hint=输入排放资料路径。 | default=None
- {TARGET_REGION_TIME} | required=True | type=str | var_name=目标区域时段 | hint=输入区域和起止时间。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 监测、气象和排放资料的可用时间边界明确

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/manila-dengue-meteorological-dataset
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- datasets/south-korea-air-quality-and-weather-monitoring-dataset
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- models/random-forest-meteorological-normalization

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
