# 实例任务：天气暴露和目标观测及任务边界预检 @ E98

- domain: climate
- 骨架: climate-weather-exposure-target-observation-task-boundary-precheck-task
- 场景: climate-cultivar-location-uncertain-weather-yield-distribution-and-scenario (E98)
- step_id: s01
- depend: []

## 场景研究主体
- E98
- 关联论文: A data-driven simulation platform to predict cultivars’ performances under uncertain weather conditions | doi:

## 本实例步骤描述
界定“品种—地点不确定天气下产量分布与稳定性评估”的任务范围并执行“天气暴露和目标观测及任务边界预检”，核验多点田间试验、品种基因型、历史天气和生育期特征的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“品种—地点不确定天气下产量分布与稳定性评估”，读取{MULTISITE_YIELD_TRIALS}、{GENOTYPE_DATA}、{HISTORICAL_WEATHER}、{TARGET_LOCATIONS}、{ANALYSIS_PERIOD}并完成天气暴露和目标观测及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {MULTISITE_YIELD_TRIALS} | required=True | type=str | var_name=多点产量试验 | hint=输入多点产量试验路径。 | default=None
- {GENOTYPE_DATA} | required=True | type=str | var_name=品种基因型资料 | hint=输入品种基因型资料。 | default=None
- {HISTORICAL_WEATHER} | required=True | type=str | var_name=地点历史天气 | hint=输入地点历史天气路径。 | default=None
- {TARGET_LOCATIONS} | required=True | type=str | var_name=目标种植地点 | hint=输入目标地点清单。 | default=None
- {ANALYSIS_PERIOD} | required=True | type=str | var_name=试验分析时段 | hint=输入试验分析时段。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 天气、目标观测和背景协变量时空匹配
- 多点试验、品种基因型和地点历史天气均显式登记

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/integrated-multi-satellite-retrievals-for-gpm-imerg-precipitation-dataset
- datasets/ostia-sst-data
- datasets/sgp-c1-multi-source-boundary-layer-height-dataset
- datasets/snodas-swe-data-product
- datasets/south-korea-air-quality-and-weather-monitoring-dataset
- models/dust-event-forecasting-with-multi-task-deep-learning
- models/multivariate-data-fusion-vector-wind-prediction
- models/photovoltaic-yield-prediction
- models/radially-averaged-power-spectral-density-analysis
- tools/aardvark-weather-system
- tools/ai-global-medium-range-weather-forecasting-system-pangu-weather
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/fuxi-weather
- tools/gencast-global-probabilistic-weather-forecasting-model
- tools/multi-level-b-spline-analysis-mba
- tools/multi-task-deep-learning-model-for-indian-ocean-dipole-prediction

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
