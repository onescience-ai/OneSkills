# 实例任务：天气能源运行资料及任务边界预检 @ E26

- domain: climate
- 骨架: climate-weather-energy-operational-data-task-boundary-precheck-task
- 场景: climate-complex-terrain-wind-farm-hub-height-short-term-wind-speed-scenario (E26)
- step_id: s01
- depend: []

## 场景研究主体
- E26
- 关联论文: A machine learning model for hub-height short-term wind speed prediction | doi:; Estimating hub-height wind speed based on a machine learning algorithm- implications for wind energy assessment | doi:; Terrain-aware Deep Learning for Wind Energy Applications- From Kilometer-scale Forecasts to Fine Wind Fields | doi:; The importance of round-robin validation when assessing machine-learning-based vertical extrapolation of wind speeds | doi:

## 本实例步骤描述
界定“复杂地形风电场轮毂高度短期风速预报”的任务范围并执行“天气能源运行资料及任务边界预检”，核验近地面风、NWP、地形、轮毂高度的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“复杂地形风电场轮毂高度短期风速预报”，读取{NEAR_SURFACE_OBSERVATIONS}、{NWP_WIND_FORECAST}、{TERRAIN_DATA}、{TURBINE_LOCATIONS}、{FORECAST_START_TIME}、{FORECAST_HORIZON}并完成天气能源运行资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {NEAR_SURFACE_OBSERVATIONS} | required=True | type=str | var_name=近地面风观测 | hint=输入近地面风观测路径。 | default=None
- {NWP_WIND_FORECAST} | required=True | type=str | var_name=公里级风场预报 | hint=输入公里级风场预报。 | default=None
- {TERRAIN_DATA} | required=True | type=str | var_name=高分辨率地形 | hint=输入高分辨率地形路径。 | default=None
- {TURBINE_LOCATIONS} | required=True | type=str | var_name=风机位置与高度 | hint=输入风机位置轮毂高度。 | default=None
- {FORECAST_START_TIME} | required=True | type=str | var_name=起报时间 | hint=输入UTC起报时间。 | default=None
- {FORECAST_HORIZON} | required=True | type=str | var_name=短期预报时效 | hint=输入短期预报时效。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 天气输入和设施观测在签发时均真实可用
- 近地面风、公里风场、地形和轮毂高度均显式登记

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/lpma-airport-wind-observation-validation
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- datasets/southern-great-plains-sgp-observatory-wind-dataset
- models/anomaly-numerical-correction-with-observations-ano
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- models/random-forest-regression-for-vertical-wind-speed-extrapolation
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/wenhai-global-ocean-forecast-system

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
