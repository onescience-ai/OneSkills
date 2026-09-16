# 骨架任务：观测强迫样本及任务边界预检

- domain: climate
- 复用场景数: 2
- 实例任务数: 2

## 步骤描述（跨场景聚合去重）
- 界定“日降水场中的人为气候变化指纹检测”的任务范围并执行“观测强迫样本及任务边界预检”，核验气候模式大集合日降水、观测日降水的来源、覆盖、有效时间和可用边界。
- 界定“臭氧与颗粒物历史序列的气象归一化和趋势归因”的任务范围并执行“观测强迫样本及任务边界预检”，核验历史污染观测、同期气象和时间特征的来源、覆盖、有效时间和可用边界。

## 执行 prompt（跨场景聚合去重）
- 面向“日降水场中的人为气候变化指纹检测”，读取{OBSERVED_DAILY_PRECIPITATION}、{FORCED_CLIMATE_SAMPLES}、{NATURAL_CLIMATE_SAMPLES}、{ANALYSIS_PERIOD}、{REFERENCE_PERIOD}并完成观测强迫样本及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“臭氧与颗粒物历史序列的气象归一化和趋势归因”，读取{POLLUTANT_SERIES}、{METEOROLOGICAL_DRIVERS}、{EMISSION_ACTIVITY_DATA}、{ANALYSIS_PERIOD}、{REFERENCE_PERIOD}并完成观测强迫样本及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 输入槽（var/hint/default）
- {OBSERVED_DAILY_PRECIPITATION} | required=True | type=str | var_name=观测日降水场 | hint=输入观测日降水场路径。 | default=None
- {FORCED_CLIMATE_SAMPLES} | required=True | type=str | var_name=历史强迫样本 | hint=输入历史强迫样本路径。 | default=None
- {NATURAL_CLIMATE_SAMPLES} | required=True | type=str | var_name=自然强迫样本 | hint=输入自然强迫样本路径。 | default=None
- {ANALYSIS_PERIOD} | required=True | type=str | var_name=趋势分析时段 | hint=输入趋势分析起止时间。 | default=None
- {REFERENCE_PERIOD} | required=True | type=str | var_name=归一化参考期 | hint=输入归一化参考时段。 | default=None
- {POLLUTANT_SERIES} | required=True | type=str | var_name=污染物历史序列 | hint=输入污染物历史序列。 | default=None
- {METEOROLOGICAL_DRIVERS} | required=True | type=str | var_name=同期气象驱动 | hint=输入同期气象资料路径。 | default=None
- {EMISSION_ACTIVITY_DATA} | required=False | type=str | var_name=排放活动资料 | hint=输入排放活动资料路径。 | default=None

## 产出
- 任务范围和资料截止时间表
- 输入完整性预检报告
- 输入数据与版本清单

## 质量门禁 quality_gate
- 任务区域、时段、变量和输出目标无歧义
- 所有必需输入均存在且路径、版本和来源可追溯
- 污染物、气象和排放活动资料覆盖统一分析时段
- 目标观测、驱动资料和参照样本定义可追溯
- 缺测、重复和异常资料已记录且未擅自补造
- 观测、历史强迫和自然强迫样本使用一致日降水定义

## 可调资源（edge:resource，仅真实存在）
- datasets/anttilope-precipitation-dataset
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/integrated-multi-satellite-retrievals-for-gpm-imerg-precipitation-dataset
- datasets/manila-dengue-meteorological-dataset
- datasets/ostia-sst-data
- datasets/precipitation-nowcasting-evaluation-metrics
- datasets/snodas-swe-data-product
- models/customized-deep-learning-for-precipitation-bias-correction-and-downscaling
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- models/pnpr-v2-passive-microwave-precipitation-retrieval-algorithm
- models/radially-averaged-power-spectral-density-analysis
- models/random-forest-meteorological-normalization
- models/standardized-precipitation-evapotranspiration-index-spei
- tools/deep-learning-precipitation-retrieval-model-and-evaluation
- tools/multi-level-b-spline-analysis-mba

## 实例任务（本骨架在各场景的实例化）
- climate-observation-forced-sample-and-daily-precipitation-field-inst
- climate-observation-forced-sample-and-ozone-and-particulate-inst

## 复用场景
- E94
- E45
