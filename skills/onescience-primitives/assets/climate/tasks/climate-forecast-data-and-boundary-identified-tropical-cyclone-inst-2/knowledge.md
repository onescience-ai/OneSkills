# 实例任务：起报资料及任务边界预检 @ E30

- domain: climate
- 骨架: climate-forecast-data-and-boundary-precheck-task
- 场景: climate-identified-tropical-cyclone-track-forecast-24-120h-scenario (E30)
- step_id: s01
- depend: []

## 场景研究主体
- E30
- 关联论文: Tropical Cyclone Track Forecasting Using Fused Deep Learning From Aligned Reanalysis Data | doi:; Dual-Branched Spatio-Temporal Fusion Network for Multihorizon Tropical Cyclone Track Forecast | doi:; Forecasting tropical cyclone tracks in the northwestern Pacific based on a deep-learning model | doi:

## 本实例步骤描述
界定“已识别热带气旋24—120小时路径预报”的任务范围并执行“起报资料及任务边界预检”，核验气旋历史位置、强度元数据、风暴中心环境场的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“已识别热带气旋24—120小时路径预报”，读取{INITIAL_DATA}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{TARGET_VARIABLES}、{DATA_CUTOFF_TIME}并完成起报资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {INITIAL_DATA} | required=True | type=str | var_name=历史与初始数据 | hint=输入历史和初始数据路径。 | default=None
- {FORECAST_START_TIME} | required=True | type=str | var_name=起报时间 | hint=输入UTC起报时间。 | default=None
- {FORECAST_HORIZON} | required=True | type=str | var_name=预报时效 | hint=输入目标预报时效。 | default=None
- {TARGET_VARIABLES} | required=True | type=str | var_name=目标变量 | hint=输入目标变量清单。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 所有动态输入的有效时间均不晚于资料截止时间

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/wenhai-global-ocean-forecast-system

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
