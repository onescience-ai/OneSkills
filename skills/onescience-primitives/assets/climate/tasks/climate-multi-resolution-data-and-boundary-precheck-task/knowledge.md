# 骨架任务：粗细分辨率资料及任务边界预检

- domain: climate
- 复用场景数: 7
- 实例任务数: 7

## 步骤描述（跨场景聚合去重）
- 界定“CMIP6温度—降水区域气候统计降尺度”的任务范围并执行“粗细分辨率资料及任务边界预检”，核验CMIP6粗网格场、区域观测或再分析、地形、排放情景的来源、覆盖、有效时间和可用边界。
- 界定“NWP 24—240小时近地面多变量偏差订正”的任务范围并执行“粗细分辨率资料及任务边界预检”，核验原始NWP预报、起报分析、历史验证资料的来源、覆盖、有效时间和可用边界。
- 界定“中国0.05°历史—情景叶面积指数空间细化”的任务范围并执行“粗细分辨率资料及任务边界预检”，核验粗分辨率LAI、气候情景、土地覆盖和高分辨率参考的来源、覆盖、有效时间和可用边界。
- 界定“复杂地形区域100米风场同期空间降尺度”的任务范围并执行“粗细分辨率资料及任务边界预检”，核验粗网格风场、地形、陆海掩膜和辅助大气量的来源、覆盖、有效时间和可用边界。
- 界定“山区近实时雪水当量估计与网格订正”的任务范围并执行“粗细分辨率资料及任务边界预检”，核验当日雪盖、微波亮温、地形和背景SWE的来源、覆盖、有效时间和可用边界。
- 界定“粗分辨率降水到公里—亚小时尺度的概率降尺度”的任务范围并执行“粗细分辨率资料及任务边界预检”，核验粗网格小时降水、地形及可选环境场的来源、覆盖、有效时间和可用边界。
- 界定“粗网格大气场到公里尺度的同期概率降尺度”的任务范围并执行“粗细分辨率资料及任务边界预检”，核验粗网格大气状态、地形与静态地理量的来源、覆盖、有效时间和可用边界。

## 执行 prompt（跨场景聚合去重）
- 面向“CMIP6温度—降水区域气候统计降尺度”，读取{COARSE_INPUT}、{FINE_REFERENCE}、{TARGET_GRID}、{ANALYSIS_PERIOD}、{DATA_CUTOFF_TIME}并完成粗细分辨率资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“NWP 24—240小时近地面多变量偏差订正”，读取{COARSE_INPUT}、{FINE_REFERENCE}、{TARGET_GRID}、{ANALYSIS_PERIOD}、{DATA_CUTOFF_TIME}并完成粗细分辨率资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“中国0.05°历史—情景叶面积指数空间细化”，读取{COARSE_INPUT}、{FINE_REFERENCE}、{TARGET_GRID}、{ANALYSIS_PERIOD}、{DATA_CUTOFF_TIME}并完成粗细分辨率资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“复杂地形区域100米风场同期空间降尺度”，读取{COARSE_INPUT}、{FINE_REFERENCE}、{TARGET_GRID}、{ANALYSIS_PERIOD}、{DATA_CUTOFF_TIME}并完成粗细分辨率资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“山区近实时雪水当量估计与网格订正”，读取{COARSE_INPUT}、{FINE_REFERENCE}、{TARGET_GRID}、{ANALYSIS_PERIOD}、{DATA_CUTOFF_TIME}并完成粗细分辨率资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“粗分辨率降水到公里—亚小时尺度的概率降尺度”，读取{COARSE_PRECIPITATION}、{FINE_PRECIPITATION_REFERENCE}、{TARGET_GRID}、{TARGET_TIME_INTERVAL}、{DATA_CUTOFF_TIME}并完成粗细分辨率资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“粗网格大气场到公里尺度的同期概率降尺度”，读取{COARSE_ATMOSPHERIC_FIELDS}、{FINE_ANALYSIS_REFERENCE}、{TARGET_GRID}、{VALID_TIME_RANGE}、{DATA_CUTOFF_TIME}并完成粗细分辨率资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 输入槽（var/hint/default）
- {COARSE_INPUT} | required=True | type=str | var_name=粗分辨率输入 | hint=输入粗分辨率资料路径。 | default=None
- {FINE_REFERENCE} | required=True | type=str | var_name=高分辨率参考 | hint=输入高分辨率参考路径。 | default=None
- {TARGET_GRID} | required=True | type=str | var_name=公里级目标网格 | hint=输入公里级网格规格。 | default=None
- {ANALYSIS_PERIOD} | required=True | type=str | var_name=处理时段 | hint=输入处理起止时间。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None
- {COARSE_PRECIPITATION} | required=True | type=str | var_name=粗网格降水 | hint=输入粗网格降水路径。 | default=None
- {FINE_PRECIPITATION_REFERENCE} | required=True | type=str | var_name=细尺度降水参考 | hint=输入细尺度降水参考。 | default=None
- {TARGET_TIME_INTERVAL} | required=True | type=str | var_name=亚小时时间间隔 | hint=输入亚小时时间间隔。 | default=None
- {COARSE_ATMOSPHERIC_FIELDS} | required=True | type=str | var_name=粗网格大气场 | hint=输入粗网格大气场路径。 | default=None
- {FINE_ANALYSIS_REFERENCE} | required=True | type=str | var_name=细尺度分析参考 | hint=输入细尺度分析参考。 | default=None
- {VALID_TIME_RANGE} | required=True | type=str | var_name=同期有效时段 | hint=输入同期有效时段。 | default=None

## 产出
- 任务范围和资料截止时间表
- 输入完整性预检报告
- 输入数据与版本清单

## 质量门禁 quality_gate
- 任务区域、时段、变量和输出目标无歧义
- 所有必需输入均存在且路径、版本和来源可追溯
- 目标同时包含公里级空间细化和亚小时时间细化
- 粗细分辨率样本严格同期且坐标一致
- 粗细大气场具有相同有效时间且只做空间尺度转换
- 缺测、重复和异常资料已记录且未擅自补造

## 可调资源（edge:resource，仅真实存在）
- datasets/anttilope-precipitation-dataset
- datasets/data-infrastructure-observations-and-labels
- datasets/ERA5
- datasets/gedi-footprint-canopy-height-data
- datasets/integrated-multi-satellite-retrievals-for-gpm-imerg-precipitation-dataset
- datasets/ostia-sst-data
- datasets/precipitation-nowcasting-evaluation-metrics
- datasets/snodas-swe-data-product
- models/customized-deep-learning-for-precipitation-bias-correction-and-downscaling
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- models/pnpr-v2-passive-microwave-precipitation-retrieval-algorithm
- models/radially-averaged-power-spectral-density-analysis
- models/standardized-precipitation-evapotranspiration-index-spei
- tools/ai-global-medium-range-weather-forecasting-system-pangu-weather
- tools/deep-learning-precipitation-retrieval-model-and-evaluation
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/multi-level-b-spline-analysis-mba

## 实例任务（本骨架在各场景的实例化）
- climate-multi-resolution-data-and-china-0-05-historical-inst
- climate-multi-resolution-data-and-cmip6-temperature-precipitat-inst
- climate-multi-resolution-data-and-coarse-grid-atmospheric-inst
- climate-multi-resolution-data-and-coarse-resolution-precipitat-inst
- climate-multi-resolution-data-and-complex-terrain-region-100m-inst
- climate-multi-resolution-data-and-mountain-snow-water-equivale-inst
- climate-multi-resolution-data-and-nwp-24-240h-near-surface-inst

## 复用场景
- E38
- E53
- E93
- E89
- E40
- E15
- E55
