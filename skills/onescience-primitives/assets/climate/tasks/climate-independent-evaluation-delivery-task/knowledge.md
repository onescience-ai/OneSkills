# 骨架任务：独立评估与交付判定

- domain: climate
- 复用场景数: 9
- 实例任务数: 9

## 步骤描述（跨场景聚合去重）
- 使用冻结的独立资料和同协议基线完成分层评估、试运行汇总、交付判定和复现归档。

## 执行 prompt（跨场景聚合去重）
- {BASELINE_PRODUCTS}、{ACCEPTANCE_PROTOCOL}、{IMPROVEMENT_METRIC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结验收方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。使用{INDEPENDENT_VALIDATION_DATA}、{BASELINE_PRODUCTS}、{IMPROVEMENT_METRIC}和{ACCEPTANCE_PROTOCOL}比较原WRF与订正产品；按变量、区域、季节和提前期报告结果，未量化的显著提升不判PASS。
- {BASELINE_PRODUCTS}、{ACCEPTANCE_PROTOCOL}、{IMPROVEMENT_PROTOCOL}均为可选输入：未提供的规则或方案字段由agent依据s02冻结验收方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。使用{INDEPENDENT_VALIDATION_DATA}、{BASELINE_PRODUCTS}、{IMPROVEMENT_PROTOCOL}和{ACCEPTANCE_PROTOCOL}按深度、区域和提前期比较原预报与1 km产品，核验改善≥30%和表层误差。
- {BASELINE_PRODUCTS}、{ACCEPTANCE_PROTOCOL}、{INUNDATION_METRIC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结验收方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。使用{INDEPENDENT_VALIDATION_DATA}、{BASELINE_PRODUCTS}、{INUNDATION_METRIC}和{ACCEPTANCE_PROTOCOL}评估漫滩空间结果与运行时限；缺少精度门限时，不对空间性能指标判PASS。
- {BASELINE_PRODUCTS}、{ACCEPTANCE_PROTOCOL}、{OCEAN_METRIC_PROTOCOL}均为可选输入：未提供的规则或方案字段由agent依据s02冻结验收方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。使用{INDEPENDENT_VALIDATION_DATA}、{BASELINE_PRODUCTS}、{OCEAN_METRIC_PROTOCOL}和{ACCEPTANCE_PROTOCOL}按深度、区域、变量和提前期评估；重点核验7天海温RMSE<0.6℃。
- {BASELINE_PRODUCTS}、{ACCEPTANCE_PROTOCOL}、{RMSE_REDUCTION_PROTOCOL}均为可选输入：未提供的规则或方案字段由agent依据s02冻结验收方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。使用{INDEPENDENT_VALIDATION_DATA}、{BASELINE_PRODUCTS}、{RMSE_REDUCTION_PROTOCOL}和{ACCEPTANCE_PROTOCOL}评估；重点核验>100 cm过程RMSE相对业务模式降低10%及潮位误差门限。
- {BASELINE_PRODUCTS}、{ACCEPTANCE_PROTOCOL}、{WIND_ERROR_PROTOCOL}均为可选输入：未提供的规则或方案字段由agent依据s02冻结验收方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。使用{INDEPENDENT_VALIDATION_DATA}、{BASELINE_PRODUCTS}、{WIND_ERROR_PROTOCOL}和{ACCEPTANCE_PROTOCOL}按变量、区域和提前期评估；只对协议已由s02冻结且证据充分的风速误差、运行性能和交付项判定PASS。
- {BASELINE_PRODUCTS}、{ACCEPTANCE_PROTOCOL}均为可选输入：未提供的规则或方案字段由agent依据s02冻结验收方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。使用{INDEPENDENT_VALIDATION_DATA}、{BASELINE_PRODUCTS}和{ACCEPTANCE_PROTOCOL}对s04连续试运行产品按区域、波况、变量和提前期评估，并统计逐起报完整率、缺报和失败；EC/GFS身份或指标未由s02冻结时不得判定优于基线。
- {BASELINE_PRODUCTS}、{ACCEPTANCE_PROTOCOL}均为可选输入：未提供的规则或方案字段由agent依据s02冻结验收方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。使用{INDEPENDENT_VALIDATION_DATA}、{EC_GFS_PRODUCTS}、{BASELINE_PRODUCTS}和{ACCEPTANCE_PROTOCOL}对s04连续试运行产品按海域、波况、变量和提前期比较，并统计逐起报完整率、缺报和失败；未同时完成同期EC和GFS同协议比较时不得对该验收项判PASS。
- {BASELINE_PRODUCTS}、{ACCEPTANCE_PROTOCOL}均为可选输入：未提供的规则或方案字段由agent依据s02冻结验收方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。在{REPLAY_PERIOD}使用{INDEPENDENT_VALIDATION_DATA}、{BASELINE_PRODUCTS}和{ACCEPTANCE_PROTOCOL}执行严格历史回放，按资料可用性和提前期评估精度及小于1分钟时限。

## 输入槽（var/hint/default）
- {INDEPENDENT_VALIDATION_DATA} | required=True | type=str | var_name=独立验证资料 | hint=输入独立验证资料路径。 | default=None
- {BASELINE_PRODUCTS} | required=False | type=str | var_name=同协议基线产品 | hint=输入基线产品路径。 | default=None
- {ACCEPTANCE_PROTOCOL} | required=False | type=str | var_name=验收协议 | hint=输入指标公式和门限。 | default=None
- {IMPROVEMENT_PROTOCOL} | required=False | type=str | var_name=海温改善协议 | hint=输入30%改善计算规则。 | default=None
- {OCEAN_METRIC_PROTOCOL} | required=False | type=str | var_name=温盐流评估协议 | hint=输入各变量指标公式。 | default=None
- {REPLAY_PERIOD} | required=True | type=str | var_name=独立回放时段 | hint=输入历史回放起止时间。 | default=None
- {RMSE_REDUCTION_PROTOCOL} | required=False | type=str | var_name=RMSE改善协议 | hint=输入事件与RMSE计算规则。 | default=None
- {WIND_ERROR_PROTOCOL} | required=False | type=str | var_name=风速误差协议 | hint=输入风速误差计算规则。 | default=None
- {IMPROVEMENT_METRIC} | required=False | type=str | var_name=精度改善指标 | hint=输入改善指标与公式。 | default=None
- {EC_GFS_PRODUCTS} | required=True | type=str | var_name=同期EC与GFS产品 | hint=输入EC与GFS产品路径。 | default=None
- {INUNDATION_METRIC} | required=False | type=str | var_name=淹没评估指标 | hint=输入空间评估公式。 | default=None

## 产出
- 分区域分变量分时效评估报告
- 基线比较与试运行报告
- 逐项验收判定与完整交付清单

## 质量门禁 quality_gate
- 必要数据仍缺失或无法形成科学上可辩护唯一口径的项目未标记为PASS
- 模型与基线使用相同样本、区域、变量、网格和指标协议
- 每个性能结论均可定位到样本、公式、产品和日志证据
- 源代码、模型、产品、文档和复现包均可重新读取
- 独立验证资料未参与训练、调参或阈值选择

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/glorys12-global-ocean-reanalysis-dataset
- datasets/kling-gupta-efficiency-kge-metric
- datasets/lpma-airport-wind-observation-validation
- datasets/modis-myd13a3-ndvi-product
- datasets/ostia-sst-data
- datasets/smap-level-3-passive-soil-moisture-products
- datasets/snodas-swe-data-product
- datasets/southern-great-plains-sgp-observatory-wind-dataset
- models/multivariate-data-fusion-vector-wind-prediction
- models/narx-network-configurations-for-inundation-depth-forecasting
- models/random-forest-regression-for-vertical-wind-speed-extrapolation
- tools/glo12v4-operational-ocean-forecasting-system
- tools/multi-task-deep-learning-model-for-indian-ocean-dipole-prediction
- tools/urban-hydrological-hydraulic-model-chain-for-inundation-simulation
- tools/wenhai-global-ocean-forecast-system

## 实例任务（本骨架在各场景的实例化）
- climate-independent-evaluation-bohai-yellow-sea-fourcastnet-inst
- climate-independent-evaluation-bohai-yellow-sea-wave-inst
- climate-independent-evaluation-bohai-yellow-sea-wave-inst-2
- climate-independent-evaluation-bohai-yellow-sea-wrf-numeric-inst
- climate-independent-evaluation-nearshore-inundation-rapid-inst
- climate-independent-evaluation-north-sea-3d-sea-temperature-inst
- climate-independent-evaluation-north-sea-3d-temperature-inst
- climate-independent-evaluation-north-sea-storm-surge-inst
- climate-independent-evaluation-north-sea-storm-surge-inst-2

## 复用场景
- E103
- E104
- E101
- E102
- E107
- E108
- E105
- E106
- E109
