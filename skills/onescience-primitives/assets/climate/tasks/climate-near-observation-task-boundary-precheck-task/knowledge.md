# 骨架任务：临近观测及任务边界预检

- domain: climate
- 复用场景数: 6
- 实例任务数: 6

## 步骤描述（跨场景聚合去重）
- 界定“地面气象要素驱动的0—30分钟雷电临近预报”的任务范围并执行“临近观测及任务边界预检”，核验近期地面气象观测、站点位置、历史雷电标签的来源、覆盖、有效时间和可用边界。
- 界定“多源观测驱动的区域3—12小时定量降水预报”的任务范围并执行“临近观测及任务边界预检”，核验近期雷达卫星序列、站点观测、区域分析场的来源、覆盖、有效时间和可用边界。
- 界定“天气雷达驱动的0—2小时冰雹概率临近预报”的任务范围并执行“临近观测及任务边界预检”，核验雷达回波序列、可选环境场、冰雹标签的来源、覆盖、有效时间和可用边界。
- 界定“天气雷达驱动的对流阵风临近预报”的任务范围并执行“临近观测及任务边界预检”，核验雷达反射率序列、地面阵风记录、可选环境场的来源、覆盖、有效时间和可用边界。
- 界定“机场雾和低能见度事件短时概率预报”的任务范围并执行“临近观测及任务边界预检”，核验机场温湿风、能见度历史、NWP或CAMS预报的来源、覆盖、有效时间和可用边界。
- 界定“雷达与环境场驱动的0—6小时闪电发生临近预报”的任务范围并执行“临近观测及任务边界预检”，核验雷达体扫、闪电历史、对流环境场的来源、覆盖、有效时间和可用边界。

## 执行 prompt（跨场景聚合去重）
- 面向“地面气象要素驱动的0—30分钟雷电临近预报”，读取{RECENT_OBSERVATIONS}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{TARGET_VARIABLES}、{DATA_CUTOFF_TIME}并完成临近观测及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“多源观测驱动的区域3—12小时定量降水预报”，读取{RECENT_OBSERVATIONS}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{TARGET_VARIABLES}、{DATA_CUTOFF_TIME}并完成临近观测及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“天气雷达驱动的0—2小时冰雹概率临近预报”，读取{RECENT_OBSERVATIONS}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{TARGET_VARIABLES}、{DATA_CUTOFF_TIME}并完成临近观测及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“天气雷达驱动的对流阵风临近预报”，读取{RECENT_OBSERVATIONS}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{TARGET_VARIABLES}、{DATA_CUTOFF_TIME}并完成临近观测及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“机场雾和低能见度事件短时概率预报”，读取{RECENT_OBSERVATIONS}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{TARGET_VARIABLES}、{DATA_CUTOFF_TIME}并完成临近观测及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“雷达与环境场驱动的0—6小时闪电发生临近预报”，读取{RADAR_HISTORY}、{CONVECTIVE_ENVIRONMENT}、{LIGHTNING_HISTORY}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{DATA_CUTOFF_TIME}并完成临近观测及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 输入槽（var/hint/default）
- {RECENT_OBSERVATIONS} | required=True | type=str | var_name=近期观测序列 | hint=输入连续观测序列路径。 | default=None
- {FORECAST_START_TIME} | required=True | type=str | var_name=起报时间 | hint=输入UTC起报时间。 | default=None
- {FORECAST_HORIZON} | required=True | type=str | var_name=预报时效 | hint=输入0至6小时预报时效。 | default=None
- {TARGET_VARIABLES} | required=True | type=str | var_name=目标变量 | hint=输入目标变量清单。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None
- {RADAR_HISTORY} | required=True | type=str | var_name=雷达历史序列 | hint=输入雷达历史序列路径。 | default=None
- {CONVECTIVE_ENVIRONMENT} | required=True | type=str | var_name=对流环境场 | hint=输入对流环境场路径。 | default=None
- {LIGHTNING_HISTORY} | required=True | type=str | var_name=闪电历史观测 | hint=输入闪电历史观测路径。 | default=None

## 产出
- 任务范围和资料截止时间表
- 输入完整性预检报告
- 输入数据与版本清单

## 质量门禁 quality_gate
- 任务区域、时段、变量和输出目标无歧义
- 所有必需输入均存在且路径、版本和来源可追溯
- 所有观测帧均不晚于起报时间且时间顺序连续
- 缺测、重复和异常资料已记录且未擅自补造
- 雷达、环境场和历史闪电均不晚于起报时间

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/lpma-airport-wind-observation-validation
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- datasets/uk-radar-composite-dataset
- models/anomaly-numerical-correction-with-observations-ano
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/wenhai-global-ocean-forecast-system

## 实例任务（本骨架在各场景的实例化）
- climate-near-observation-task-airport-fog-low-visibility-inst
- climate-near-observation-task-ground-meteorological-inst
- climate-near-observation-task-multi-source-observation-inst
- climate-near-observation-task-radar-and-environmental-inst
- climate-near-observation-task-weather-radar-convective-inst
- climate-near-observation-task-weather-radar-hail-probabili-inst

## 复用场景
- E52
- E8
- E83
- E85
- E33
- E72
