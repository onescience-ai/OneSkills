# 实例任务：临近观测及任务边界预检 @ E33

- domain: climate
- 骨架: climate-near-observation-task-boundary-precheck-task
- 场景: climate-airport-fog-low-visibility-short-term-probability-forecast-scenario (E33)
- step_id: s01
- depend: []

## 场景研究主体
- E33
- 关联论文: Machine learning regression and classification methods for fog events prediction | doi:; Deep learning ensembles for accurate fog-related low-visibility events forecasting | doi:; Enhancing multivariate post-processed visibility predictions utilizing CAMS forecasts | doi:

## 本实例步骤描述
界定“机场雾和低能见度事件短时概率预报”的任务范围并执行“临近观测及任务边界预检”，核验机场温湿风、能见度历史、NWP或CAMS预报的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“机场雾和低能见度事件短时概率预报”，读取{RECENT_OBSERVATIONS}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{TARGET_VARIABLES}、{DATA_CUTOFF_TIME}并完成临近观测及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {RECENT_OBSERVATIONS} | required=True | type=str | var_name=近期观测序列 | hint=输入连续观测序列路径。 | default=None
- {FORECAST_START_TIME} | required=True | type=str | var_name=起报时间 | hint=输入UTC起报时间。 | default=None
- {FORECAST_HORIZON} | required=True | type=str | var_name=临近预报时效 | hint=输入临近预报时效。 | default=None
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
- 所有观测帧均不晚于起报时间且时间顺序连续

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/lpma-airport-wind-observation-validation
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- models/anomaly-numerical-correction-with-observations-ano
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/wenhai-global-ocean-forecast-system

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
