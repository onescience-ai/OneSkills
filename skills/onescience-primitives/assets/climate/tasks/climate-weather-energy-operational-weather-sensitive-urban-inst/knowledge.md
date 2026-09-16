# 实例任务：天气能源运行资料及任务边界预检 @ E20

- domain: climate
- 骨架: climate-weather-energy-operational-data-task-boundary-precheck-task
- 场景: climate-weather-sensitive-urban-electric-load-day-ahead-probabilistic-scenario (E20)
- step_id: s01
- depend: []

## 场景研究主体
- E20
- 关联论文: A gradient boosting approach to the Kaggle load forecasting competition | doi:; Hierarchical Probabilistic Forecasting of Electricity Demand With Smart Meter Data | doi:; Machine Learning Techniques for Predicting the Energy Consumption-Production and Its Uncertainties Driven by Meteorological Observations and Forecasts | doi:; Multi-Feature Data Fusion-Based Load Forecasting of Electric Vehicle Charging Stations Using a Deep Learning Model | doi:

## 本实例步骤描述
界定“天气敏感型城市电力负荷日前概率预报”的任务范围并执行“天气能源运行资料及任务边界预检”，核验历史负荷、天气预报、日历与用户层级的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“天气敏感型城市电力负荷日前概率预报”，读取{WEATHER_FORECAST}、{LOAD_HISTORY}、{CALENDAR_FEATURES}、{HIERARCHY_METADATA}、{FORECAST_START_TIME}、{DATA_CUTOFF_TIME}并完成天气能源运行资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {WEATHER_FORECAST} | required=True | type=str | var_name=日前天气预报 | hint=输入日前天气预报路径。 | default=None
- {LOAD_HISTORY} | required=True | type=str | var_name=历史电力负荷 | hint=输入历史负荷资料路径。 | default=None
- {CALENDAR_FEATURES} | required=True | type=str | var_name=日历特征 | hint=输入日历节假日特征。 | default=None
- {HIERARCHY_METADATA} | required=True | type=str | var_name=负荷层级信息 | hint=输入城市配电层级信息。 | default=None
- {FORECAST_START_TIME} | required=True | type=str | var_name=预测签发时间 | hint=输入预测签发时间。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 天气输入和设施观测在签发时均真实可用

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- datasets/south-korea-air-quality-and-weather-monitoring-dataset
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- tools/aardvark-weather-system
- tools/ai-global-medium-range-weather-forecasting-system-pangu-weather
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/fuxi-weather
- tools/gencast-global-probabilistic-weather-forecasting-model
- tools/wenhai-global-ocean-forecast-system

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
