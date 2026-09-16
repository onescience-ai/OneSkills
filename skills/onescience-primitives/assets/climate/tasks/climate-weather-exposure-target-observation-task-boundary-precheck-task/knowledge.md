# 骨架任务：天气暴露和目标观测及任务边界预检

- domain: climate
- 复用场景数: 4
- 实例任务数: 4

## 步骤描述（跨场景聚合去重）
- 界定“品种—地点不确定天气下产量分布与稳定性评估”的任务范围并执行“天气暴露和目标观测及任务边界预检”，核验多点田间试验、品种基因型、历史天气和生育期特征的来源、覆盖、有效时间和可用边界。
- 界定“天气与人口变化驱动的城市月日用水需求预测”的任务范围并执行“天气暴露和目标观测及任务边界预检”，核验历史用水、天气、日历、人口与政策情景的来源、覆盖、有效时间和可用边界。
- 界定“气象驱动的周尺度登革热发病量预报”的任务范围并执行“天气暴露和目标观测及任务边界预检”，核验气象历史与预报、病例序列、季节人口信息的来源、覆盖、有效时间和可用边界。
- 界定“生长季县域玉米产量提前预报”的任务范围并执行“天气暴露和目标观测及任务边界预检”，核验截至签发日天气、土壤、种植管理和历史产量的来源、覆盖、有效时间和可用边界。

## 执行 prompt（跨场景聚合去重）
- 面向“品种—地点不确定天气下产量分布与稳定性评估”，读取{MULTISITE_YIELD_TRIALS}、{GENOTYPE_DATA}、{HISTORICAL_WEATHER}、{TARGET_LOCATIONS}、{ANALYSIS_PERIOD}并完成天气暴露和目标观测及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“天气与人口变化驱动的城市月日用水需求预测”，读取{WEATHER_EXPOSURE}、{TARGET_OBSERVATIONS}、{CONTEXT_FEATURES}、{ANALYSIS_PERIOD}、{DATA_CUTOFF_TIME}并完成天气暴露和目标观测及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“气象驱动的周尺度登革热发病量预报”，读取{WEATHER_EXPOSURE}、{TARGET_OBSERVATIONS}、{CONTEXT_FEATURES}、{ANALYSIS_PERIOD}、{DATA_CUTOFF_TIME}并完成天气暴露和目标观测及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“生长季县域玉米产量提前预报”，读取{COUNTY_YIELD_HISTORY}、{KNOWN_WEATHER_TO_ISSUE}、{SOIL_MANAGEMENT_DATA}、{ISSUE_DATE}、{TARGET_HARVEST_YEAR}、{DATA_CUTOFF_TIME}并完成天气暴露和目标观测及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 输入槽（var/hint/default）
- {MULTISITE_YIELD_TRIALS} | required=True | type=str | var_name=多点产量试验 | hint=输入多点产量试验路径。 | default=None
- {GENOTYPE_DATA} | required=True | type=str | var_name=品种基因型资料 | hint=输入品种基因型资料。 | default=None
- {HISTORICAL_WEATHER} | required=True | type=str | var_name=地点历史天气 | hint=输入地点历史天气路径。 | default=None
- {TARGET_LOCATIONS} | required=True | type=str | var_name=目标种植地点 | hint=输入目标地点清单。 | default=None
- {ANALYSIS_PERIOD} | required=True | type=str | var_name=分析预测时段 | hint=输入处理起止时间。 | default=None
- {WEATHER_EXPOSURE} | required=True | type=str | var_name=天气暴露资料 | hint=输入天气暴露资料路径。 | default=None
- {TARGET_OBSERVATIONS} | required=True | type=str | var_name=目标观测资料 | hint=输入目标观测资料路径。 | default=None
- {CONTEXT_FEATURES} | required=False | type=str | var_name=背景协变量 | hint=输入背景协变量路径。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None
- {COUNTY_YIELD_HISTORY} | required=True | type=str | var_name=县域历史产量 | hint=输入县域历史产量路径。 | default=None
- {KNOWN_WEATHER_TO_ISSUE} | required=True | type=str | var_name=签发日前天气 | hint=输入签发日前天气路径。 | default=None
- {SOIL_MANAGEMENT_DATA} | required=True | type=str | var_name=土壤管理资料 | hint=输入土壤管理资料路径。 | default=None
- {ISSUE_DATE} | required=True | type=str | var_name=预测签发日 | hint=输入产量预测签发日。 | default=None
- {TARGET_HARVEST_YEAR} | required=True | type=str | var_name=目标收获年份 | hint=输入目标收获年份。 | default=None

## 产出
- 任务范围和资料截止时间表
- 输入完整性预检报告
- 输入数据与版本清单

## 质量门禁 quality_gate
- 任何签发日之后的实况天气不得作为本次预测输入
- 任务区域、时段、变量和输出目标无歧义
- 多点试验、品种基因型和地点历史天气均显式登记
- 天气、目标观测和背景协变量时空匹配
- 所有必需输入均存在且路径、版本和来源可追溯
- 缺测、重复和异常资料已记录且未擅自补造

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/integrated-multi-satellite-retrievals-for-gpm-imerg-precipitation-dataset
- datasets/international-soil-moisture-network-ismn
- datasets/ismn-and-nasa-power-datasets-for-soil-moisture-prediction
- datasets/lpma-airport-wind-observation-validation
- datasets/ostia-sst-data
- datasets/sgp-c1-multi-source-boundary-layer-height-dataset
- datasets/smap-level-3-passive-soil-moisture-products
- datasets/snodas-swe-data-product
- datasets/south-korea-air-quality-and-weather-monitoring-dataset
- models/anomaly-numerical-correction-with-observations-ano
- models/dust-event-forecasting-with-multi-task-deep-learning
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- models/neural-network-soil-moisture-downscaling
- models/photovoltaic-yield-prediction
- models/radially-averaged-power-spectral-density-analysis
- tools/aardvark-weather-system
- tools/ai-global-medium-range-weather-forecasting-system-pangu-weather
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/fuxi-weather
- tools/gencast-global-probabilistic-weather-forecasting-model
- tools/multi-level-b-spline-analysis-mba
- tools/multi-task-deep-learning-model-for-indian-ocean-dipole-prediction

## 实例任务（本骨架在各场景的实例化）
- climate-weather-exposure-target-cultivar-location-uncertain-inst
- climate-weather-exposure-target-growing-season-county-corn-inst
- climate-weather-exposure-target-weather-and-population-inst
- climate-weather-exposure-target-weather-driven-weekly-inst

## 复用场景
- E98
- E62
- E43
- E58
