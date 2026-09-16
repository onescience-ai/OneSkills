# 实例任务：观测和背景场及任务边界预检 @ E4

- domain: climate
- 骨架: climate-observation-background-field-and-boundary-precheck-task
- 场景: climate-multi-source-raw-observation-driven-global-analysis-forecast-scenario (E4)
- step_id: s01
- depend: []

## 场景研究主体
- E4
- 关联论文: A data-to-forecast machine learning system for global weather | doi:; End-to-end data-driven weather prediction | doi:; GraphDOP_ Towards skilful data-driven medium-range weather forecasts learnt and initialised directly from observations | doi:

## 本实例步骤描述
界定“多源原始观测驱动的全球分析—预报闭环”的任务范围并执行“观测和背景场及任务边界预检”，核验带时间和位置的原始观测、背景状态的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“多源原始观测驱动的全球分析—预报闭环”，读取{OBSERVATION_DATA}、{BACKGROUND_STATE}、{ANALYSIS_TIME}、{ASSIMILATION_WINDOW}、{DATA_CUTOFF_TIME}并完成观测和背景场及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {OBSERVATION_DATA} | required=True | type=str | var_name=原始观测资料 | hint=输入原始观测资料路径。 | default=None
- {BACKGROUND_STATE} | required=True | type=str | var_name=背景状态 | hint=输入背景状态路径。 | default=None
- {ANALYSIS_TIME} | required=True | type=str | var_name=分析时刻 | hint=输入目标分析时刻。 | default=None
- {ASSIMILATION_WINDOW} | required=True | type=str | var_name=同化时间窗 | hint=输入同化时间窗。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 观测可用时间、质控标志和误差配置可追溯

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/lpma-airport-wind-observation-validation
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- datasets/southern-great-plains-sgp-observatory-wind-dataset
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- models/radially-averaged-power-spectral-density-analysis
- models/random-forest-regression-for-vertical-wind-speed-extrapolation
- tools/multi-level-b-spline-analysis-mba

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
