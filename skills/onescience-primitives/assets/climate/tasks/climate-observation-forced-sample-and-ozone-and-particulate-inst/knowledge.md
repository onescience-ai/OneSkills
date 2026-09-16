# 实例任务：观测强迫样本及任务边界预检 @ E45

- domain: climate
- 骨架: climate-observation-forced-sample-and-boundary-precheck-task
- 场景: climate-ozone-and-particulate-matter-historical-series-meteorological-scenario (E45)
- step_id: s01
- depend: []

## 场景研究主体
- E45
- 关联论文: A machine learning approach to quantify meteorological drivers of ozone pollution in China from 2015 to 2019 | doi:; Assessing the impact of clean air action on air quality trends in Beijing using a machine learning technique | doi:; Meteorology-driven variability of air pollution (PM1) revealed with explainable machine learning | doi:

## 本实例步骤描述
界定“臭氧与颗粒物历史序列的气象归一化和趋势归因”的任务范围并执行“观测强迫样本及任务边界预检”，核验历史污染观测、同期气象和时间特征的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“臭氧与颗粒物历史序列的气象归一化和趋势归因”，读取{POLLUTANT_SERIES}、{METEOROLOGICAL_DRIVERS}、{EMISSION_ACTIVITY_DATA}、{ANALYSIS_PERIOD}、{REFERENCE_PERIOD}并完成观测强迫样本及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {POLLUTANT_SERIES} | required=True | type=str | var_name=污染物历史序列 | hint=输入污染物历史序列。 | default=None
- {METEOROLOGICAL_DRIVERS} | required=True | type=str | var_name=同期气象驱动 | hint=输入同期气象资料路径。 | default=None
- {EMISSION_ACTIVITY_DATA} | required=False | type=str | var_name=排放活动资料 | hint=输入排放活动资料路径。 | default=None
- {ANALYSIS_PERIOD} | required=True | type=str | var_name=趋势分析时段 | hint=输入趋势分析起止时间。 | default=None
- {REFERENCE_PERIOD} | required=True | type=str | var_name=归一化参考期 | hint=输入归一化参考时段。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 目标观测、驱动资料和参照样本定义可追溯
- 污染物、气象和排放活动资料覆盖统一分析时段

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/manila-dengue-meteorological-dataset
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- models/radially-averaged-power-spectral-density-analysis
- models/random-forest-meteorological-normalization
- tools/multi-level-b-spline-analysis-mba

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
