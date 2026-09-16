# 实例任务：临近观测及任务边界预检 @ E72

- domain: climate
- 骨架: climate-near-observation-task-boundary-precheck-task
- 场景: climate-radar-and-environmental-field-driven-0-6-hour-lightning-scenario (E72)
- step_id: s01
- depend: []

## 场景研究主体
- E72
- 关联论文: FlashBench- A lightning nowcasting framework based on the hybrid deep learning and physics-based dynamical models | doi:

## 本实例步骤描述
界定“雷达与环境场驱动的0—6小时闪电发生临近预报”的任务范围并执行“临近观测及任务边界预检”，核验雷达体扫、闪电历史、对流环境场的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“雷达与环境场驱动的0—6小时闪电发生临近预报”，读取{RADAR_HISTORY}、{CONVECTIVE_ENVIRONMENT}、{LIGHTNING_HISTORY}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{DATA_CUTOFF_TIME}并完成临近观测及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {RADAR_HISTORY} | required=True | type=str | var_name=雷达历史序列 | hint=输入雷达历史序列路径。 | default=None
- {CONVECTIVE_ENVIRONMENT} | required=True | type=str | var_name=对流环境场 | hint=输入对流环境场路径。 | default=None
- {LIGHTNING_HISTORY} | required=True | type=str | var_name=闪电历史观测 | hint=输入闪电历史观测路径。 | default=None
- {FORECAST_START_TIME} | required=True | type=str | var_name=起报时间 | hint=输入UTC起报时间。 | default=None
- {FORECAST_HORIZON} | required=True | type=str | var_name=预报时效 | hint=输入0至6小时预报时效。 | default=None
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
- 雷达、环境场和历史闪电均不晚于起报时间

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- datasets/uk-radar-composite-dataset
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/wenhai-global-ocean-forecast-system

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
