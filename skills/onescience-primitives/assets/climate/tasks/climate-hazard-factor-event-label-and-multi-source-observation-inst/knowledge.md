# 实例任务：致灾因子和事件标签及任务边界预检 @ E92

- domain: climate
- 骨架: climate-hazard-factor-event-label-and-boundary-precheck-task
- 场景: climate-multi-source-observation-and-weather-forecast-driven-dust-event-scenario (E92)
- step_id: s01
- depend: []

## 场景研究主体
- E92
- 关联论文: Deep multi-task learning for early warnings of dust events implemented for the Middle East | doi:

## 本实例步骤描述
界定“多源观测与天气预报驱动的沙尘事件提前预警”的任务范围并执行“致灾因子和事件标签及任务边界预检”，核验气象预报、气溶胶观测、地表与沙尘历史的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“多源观测与天气预报驱动的沙尘事件提前预警”，读取{GROUND_DUST_OBSERVATIONS}、{SATELLITE_AEROSOL_DATA}、{AEROSOL_BACKGROUND}、{WEATHER_FORECAST}、{FORECAST_START_TIME}、{FORECAST_HORIZON}并完成致灾因子和事件标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {GROUND_DUST_OBSERVATIONS} | required=True | type=str | var_name=地面沙尘观测 | hint=输入地面沙尘观测路径。 | default=None
- {SATELLITE_AEROSOL_DATA} | required=True | type=str | var_name=卫星气溶胶资料 | hint=输入卫星气溶胶资料。 | default=None
- {AEROSOL_BACKGROUND} | required=True | type=str | var_name=气溶胶背景场 | hint=输入气溶胶背景场路径。 | default=None
- {WEATHER_FORECAST} | required=True | type=str | var_name=天气预报资料 | hint=输入天气预报资料路径。 | default=None
- {FORECAST_START_TIME} | required=True | type=str | var_name=预警签发时间 | hint=输入预警签发时间。 | default=None
- {FORECAST_HORIZON} | required=True | type=str | var_name=预警时效 | hint=输入小时至日预警时效。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 事件定义、预警窗口和资料截止时间明确
- 地面、卫星、背景场和天气预报资料均显式登记

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/in-situ-and-satellite-matchup-dataset-for-chlorophyll-a-retrieval
- datasets/integrated-multi-satellite-retrievals-for-gpm-imerg-precipitation-dataset
- datasets/lpma-airport-wind-observation-validation
- datasets/machine-learning-modeling-plant-phenology-coupling-satellite
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- datasets/south-korea-air-quality-and-weather-monitoring-dataset
- models/anomaly-numerical-correction-with-observations-ano
- models/dust-event-forecasting-with-multi-task-deep-learning
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- tools/aardvark-weather-system
- tools/aerosol-chemical-speciation-monitor-acsm
- tools/ai-global-medium-range-weather-forecasting-system-pangu-weather
- tools/anni-nh3-v2-1-satellite-ammonia-retrieval-algorithm-and-reanalysis-dataset
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/fuxi-weather
- tools/gencast-global-probabilistic-weather-forecasting-model
- tools/wenhai-global-ocean-forecast-system

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
