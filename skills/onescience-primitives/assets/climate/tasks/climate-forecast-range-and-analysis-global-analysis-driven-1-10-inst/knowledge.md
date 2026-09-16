# 实例任务：起报范围与分析场预检 @ E1

- domain: climate
- 骨架: climate-forecast-range-and-analysis-field-precheck-task
- 场景: climate-global-analysis-driven-1-10-day-multivariate-deterministic-scenario (E1)
- step_id: s01
- depend: []

## 场景研究主体
- E1
- 关联论文: Learning skillful medium-range global weather forecasting | doi:; Accurate medium-range global weather forecasting with 3D neural networks | doi:; FourCastNet: A Global Data-driven High-resolution Weather Model using Adaptive Fourier Neural Operators | doi:; FengWu: Pushing the Skillful Global Medium-range Weather Forecast beyond 10 Days Lead | doi:; AIFS -- ECMWF's data-driven forecasting system | doi:

## 本实例步骤描述
固定起报时间、预报时效和变量范围，核验全球分析场的时次、层次、单位、坐标、缺测与资料截止时间。

## 本实例执行 prompt
读取{INITIAL_ANALYSIS}，以{FORECAST_START_TIME}为起报时间、{LEAD_DAYS}天为目标时效，核验{VARIABLES_AND_LEVELS}和{DATA_CUTOFF_TIME}。逐项报告时次、层次、单位、网格、缺测和异常；发现未来资料泄漏、关键时次缺失或变量不兼容时停止并标记BLOCKED。

## 本实例输入槽
- {INITIAL_ANALYSIS} | required=True | type=str | var_name=全球分析初场 | hint=输入ERA5或业务分析场路径。 | default=None
- {FORECAST_START_TIME} | required=True | type=str | var_name=起报时间 | hint=输入UTC起报时间。 | default=None
- {LEAD_DAYS} | required=True | type=str | var_name=预报步长 | hint=输入待预报的步长。 | default=1
- {VARIABLES_AND_LEVELS} | required=True | type=str | var_name=变量与层次 | hint=输入变量名称和气压层。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入文件与资料截止时间清单
- 变量—层次—单位矩阵
- 分析初场预检报告

## 本实例质量门禁
- 所有动态输入的有效时间均不晚于起报时间
- 输入时次数量满足所选模型的单时次或双时次要求
- 必需变量、层次、单位和坐标均可识别
- 缺测、重复时次和异常值已记录且未擅自补造

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/ostia-sst-data
- datasets/smap-level-3-passive-soil-moisture-products
- datasets/snodas-swe-data-product
- models/1d-cnn-based-groundwater-level-prediction
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- models/radially-averaged-power-spectral-density-analysis
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/multi-level-b-spline-analysis-mba
- tools/wenhai-global-ocean-forecast-system

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
