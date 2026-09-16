# 实例任务：天气暴露和目标观测及任务边界预检 @ E58

- domain: climate
- 骨架: climate-weather-exposure-target-observation-task-boundary-precheck-task
- 场景: climate-growing-season-county-corn-yield-advance-forecast-scenario (E58)
- step_id: s01
- depend: []

## 场景研究主体
- E58
- 关联论文: Forecasting Corn Yield With Machine Learning Ensembles | doi:; Maize yield forecasting by linear regression and artificial neural networks in Jilin, China | doi:

## 本实例步骤描述
界定“生长季县域玉米产量提前预报”的任务范围并执行“天气暴露和目标观测及任务边界预检”，核验截至签发日天气、土壤、种植管理和历史产量的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“生长季县域玉米产量提前预报”，读取{COUNTY_YIELD_HISTORY}、{KNOWN_WEATHER_TO_ISSUE}、{SOIL_MANAGEMENT_DATA}、{ISSUE_DATE}、{TARGET_HARVEST_YEAR}、{DATA_CUTOFF_TIME}并完成天气暴露和目标观测及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {COUNTY_YIELD_HISTORY} | required=True | type=str | var_name=县域历史产量 | hint=输入县域历史产量路径。 | default=None
- {KNOWN_WEATHER_TO_ISSUE} | required=True | type=str | var_name=签发日前天气 | hint=输入签发日前天气路径。 | default=None
- {SOIL_MANAGEMENT_DATA} | required=True | type=str | var_name=土壤管理资料 | hint=输入土壤管理资料路径。 | default=None
- {ISSUE_DATE} | required=True | type=str | var_name=预测签发日 | hint=输入产量预测签发日。 | default=None
- {TARGET_HARVEST_YEAR} | required=True | type=str | var_name=目标收获年份 | hint=输入目标收获年份。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 天气、目标观测和背景协变量时空匹配
- 任何签发日之后的实况天气不得作为本次预测输入

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/international-soil-moisture-network-ismn
- datasets/ismn-and-nasa-power-datasets-for-soil-moisture-prediction
- datasets/ostia-sst-data
- datasets/smap-level-3-passive-soil-moisture-products
- datasets/snodas-swe-data-product
- datasets/south-korea-air-quality-and-weather-monitoring-dataset
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- models/neural-network-soil-moisture-downscaling
- models/photovoltaic-yield-prediction
- tools/aardvark-weather-system
- tools/ai-global-medium-range-weather-forecasting-system-pangu-weather
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/fuxi-weather
- tools/gencast-global-probabilistic-weather-forecasting-model

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
