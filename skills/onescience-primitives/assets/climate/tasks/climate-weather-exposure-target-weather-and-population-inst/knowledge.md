# 实例任务：天气暴露和目标观测及任务边界预检 @ E62

- domain: climate
- 骨架: climate-weather-exposure-target-observation-task-boundary-precheck-task
- 场景: climate-weather-and-population-change-driven-urban-monthly-daily-water-scenario (E62)
- step_id: s01
- depend: []

## 场景研究主体
- E62
- 关联论文: Short-Term Urban Water Demand Prediction Considering Weather Factors | doi:; A Method for Predicting Long-Term Municipal Water Demands Under Climate Change | doi:; Urban Water Demand Prediction for a City That Suffers from Climate Change and Population Growth- Gauteng Province Case Study | doi:

## 本实例步骤描述
界定“天气与人口变化驱动的城市月日用水需求预测”的任务范围并执行“天气暴露和目标观测及任务边界预检”，核验历史用水、天气、日历、人口与政策情景的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“天气与人口变化驱动的城市月日用水需求预测”，读取{WEATHER_EXPOSURE}、{TARGET_OBSERVATIONS}、{CONTEXT_FEATURES}、{ANALYSIS_PERIOD}、{DATA_CUTOFF_TIME}并完成天气暴露和目标观测及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {WEATHER_EXPOSURE} | required=True | type=str | var_name=天气暴露资料 | hint=输入天气暴露资料路径。 | default=None
- {TARGET_OBSERVATIONS} | required=True | type=str | var_name=目标观测资料 | hint=输入目标观测资料路径。 | default=None
- {CONTEXT_FEATURES} | required=False | type=str | var_name=背景协变量 | hint=输入背景协变量路径。 | default=None
- {ANALYSIS_PERIOD} | required=True | type=str | var_name=分析预测时段 | hint=输入处理起止时间。 | default=None
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

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/lpma-airport-wind-observation-validation
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- datasets/south-korea-air-quality-and-weather-monitoring-dataset
- models/anomaly-numerical-correction-with-observations-ano
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- models/radially-averaged-power-spectral-density-analysis
- tools/aardvark-weather-system
- tools/ai-global-medium-range-weather-forecasting-system-pangu-weather
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/fuxi-weather
- tools/gencast-global-probabilistic-weather-forecasting-model
- tools/multi-level-b-spline-analysis-mba

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
