# 骨架任务：起报范围与分析场预检

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 固定起报时间、预报时效和变量范围，核验全球分析场的时次、层次、单位、坐标、缺测与资料截止时间。

## 执行 prompt（跨场景聚合去重）
- 读取{INITIAL_ANALYSIS}，以{FORECAST_START_TIME}为起报时间、{LEAD_DAYS}天为目标时效，核验{VARIABLES_AND_LEVELS}和{DATA_CUTOFF_TIME}。逐项报告时次、层次、单位、网格、缺测和异常；发现未来资料泄漏、关键时次缺失或变量不兼容时停止并标记BLOCKED。

## 输入槽（var/hint/default）
- {INITIAL_ANALYSIS} | required=True | type=str | var_name=全球分析初场 | hint=输入ERA5或业务分析场路径。 | default=None
- {FORECAST_START_TIME} | required=True | type=str | var_name=起报时间 | hint=输入UTC起报时间。 | default=None
- {LEAD_DAYS} | required=True | type=str | var_name=预报步长 | hint=输入待预报的步长。 | default=1
- {VARIABLES_AND_LEVELS} | required=True | type=str | var_name=变量与层次 | hint=输入变量名称和气压层。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 产出
- 分析初场预检报告
- 变量—层次—单位矩阵
- 输入文件与资料截止时间清单

## 质量门禁 quality_gate
- 必需变量、层次、单位和坐标均可识别
- 所有动态输入的有效时间均不晚于起报时间
- 缺测、重复时次和异常值已记录且未擅自补造
- 输入时次数量满足所选模型的单时次或双时次要求

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

## 实例任务（本骨架在各场景的实例化）
- climate-forecast-range-and-analysis-global-analysis-driven-1-10-inst

## 复用场景
- E1
