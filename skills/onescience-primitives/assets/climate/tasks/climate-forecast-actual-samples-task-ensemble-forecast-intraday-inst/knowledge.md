# 实例任务：预报实况样本及任务边界预检 @ E24

- domain: climate
- 骨架: climate-forecast-actual-samples-task-boundary-precheck-task
- 场景: climate-ensemble-forecast-intraday-to-days-ahead-solar-irradiance-scenario (E24)
- step_id: s01
- depend: []

## 场景研究主体
- E24
- 关联论文: Improving Model Chain Approaches for Probabilistic Solar Energy Forecasting through Post-processing and Machine Learning | doi:; Post-processing numerical weather prediction ensembles for probabilistic solar irradiance forecasting | doi:; Comparison of statistical post-processing methods for probabilistic NWP forecasts of solar radiation | doi:; Machine-learning-based probabilistic forecasting of solar irradiance in Chile | doi:

## 本实例步骤描述
界定“集合数值预报的日内至日前太阳辐照度概率后处理”的任务范围并执行“预报实况样本及任务边界预检”，核验集合NWP辐射、历史观测与误差的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“集合数值预报的日内至日前太阳辐照度概率后处理”，读取{RAW_IRRADIANCE_ENSEMBLE}、{IRRADIANCE_OBSERVATIONS}、{SITE_METADATA}、{CALIBRATION_PERIOD}、{DATA_CUTOFF_TIME}并完成预报实况样本及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {RAW_IRRADIANCE_ENSEMBLE} | required=True | type=str | var_name=原始辐照度集合 | hint=输入辐照度集合路径。 | default=None
- {IRRADIANCE_OBSERVATIONS} | required=True | type=str | var_name=同期辐照度实况 | hint=输入辐照度实况路径。 | default=None
- {SITE_METADATA} | required=True | type=str | var_name=站点元数据 | hint=输入站点元数据路径。 | default=None
- {CALIBRATION_PERIOD} | required=True | type=str | var_name=校准时段 | hint=输入校准起止时间。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 原始预报与同期实况按起报和有效时间准确配对
- 输入是辐照度集合与同期辐照度实况而非功率数据

## 可调资源（edge:resource，仅真实存在）
- datasets/cesm2-large-ensemble
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/large-ensemble-testbed
- datasets/lpma-airport-wind-observation-validation
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- models/anomaly-numerical-correction-with-observations-ano
- models/crpsexp-loss-function-for-ensemble-forecasting
- models/dynamic-pre-training-for-time-series-dynpt
- models/ensemble-empirical-mode-decomposition-eemd
- models/ensemble-model-output-statistics-emos-post-processing
- models/multivariate-data-fusion-vector-wind-prediction
- models/neural-network-based-nwp-model-calibration

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
