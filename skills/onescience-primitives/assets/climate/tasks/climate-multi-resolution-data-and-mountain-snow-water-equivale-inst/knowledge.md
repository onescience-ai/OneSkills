# 实例任务：粗细分辨率资料及任务边界预检 @ E40

- domain: climate
- 骨架: climate-multi-resolution-data-and-boundary-precheck-task
- 场景: climate-mountain-snow-water-equivalent-nrt-estimation-scenario (E40)
- step_id: s01
- depend: []

## 场景研究主体
- E40
- 关联论文: Using machine learning for real-time estimates of snow water equivalent in the watersheds of Afghanistan | doi:; Application of machine learning techniques for regional bias correction of snow water equivalent estimates in Ontario, Canada | doi:; Improving gridded snow water equivalent products in British Columbia, Canada- multi-source data fusion by neural network models | doi:

## 本实例步骤描述
界定“山区近实时雪水当量估计与网格订正”的任务范围并执行“粗细分辨率资料及任务边界预检”，核验当日雪盖、微波亮温、地形和背景SWE的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“山区近实时雪水当量估计与网格订正”，读取{COARSE_INPUT}、{FINE_REFERENCE}、{TARGET_GRID}、{ANALYSIS_PERIOD}、{DATA_CUTOFF_TIME}并完成粗细分辨率资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {COARSE_INPUT} | required=True | type=str | var_name=粗分辨率输入 | hint=输入粗分辨率资料路径。 | default=None
- {FINE_REFERENCE} | required=True | type=str | var_name=高分辨率参考 | hint=输入高分辨率参考路径。 | default=None
- {TARGET_GRID} | required=True | type=str | var_name=目标网格 | hint=输入目标网格规格。 | default=None
- {ANALYSIS_PERIOD} | required=True | type=str | var_name=处理时段 | hint=输入处理起止时间。 | default=None
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

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- models/radially-averaged-power-spectral-density-analysis
- tools/multi-level-b-spline-analysis-mba

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
