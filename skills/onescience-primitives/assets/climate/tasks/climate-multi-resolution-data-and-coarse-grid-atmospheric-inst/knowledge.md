# 实例任务：粗细分辨率资料及任务边界预检 @ E55

- domain: climate
- 骨架: climate-multi-resolution-data-and-boundary-precheck-task
- 场景: climate-coarse-grid-atmospheric-field-to-kilometer-scale-concurrent-scenario (E55)
- step_id: s01
- depend: []

## 场景研究主体
- E55
- 关联论文: Residual Corrective Diffusion Modeling for Km-scale Atmospheric Downscaling | doi:; A deep learning approach for improving spatiotemporal resolution of numerical weather prediction forecasts | doi:

## 本实例步骤描述
界定“粗网格大气场到公里尺度的同期概率降尺度”的任务范围并执行“粗细分辨率资料及任务边界预检”，核验粗网格大气状态、地形与静态地理量的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“粗网格大气场到公里尺度的同期概率降尺度”，读取{COARSE_ATMOSPHERIC_FIELDS}、{FINE_ANALYSIS_REFERENCE}、{TARGET_GRID}、{VALID_TIME_RANGE}、{DATA_CUTOFF_TIME}并完成粗细分辨率资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {COARSE_ATMOSPHERIC_FIELDS} | required=True | type=str | var_name=粗网格大气场 | hint=输入粗网格大气场路径。 | default=None
- {FINE_ANALYSIS_REFERENCE} | required=True | type=str | var_name=细尺度分析参考 | hint=输入细尺度分析参考。 | default=None
- {TARGET_GRID} | required=True | type=str | var_name=公里级目标网格 | hint=输入公里级网格规格。 | default=None
- {VALID_TIME_RANGE} | required=True | type=str | var_name=同期有效时段 | hint=输入同期有效时段。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 粗细分辨率样本严格同期且坐标一致
- 粗细大气场具有相同有效时间且只做空间尺度转换

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- models/radially-averaged-power-spectral-density-analysis
- tools/ai-global-medium-range-weather-forecasting-system-pangu-weather
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/multi-level-b-spline-analysis-mba

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
