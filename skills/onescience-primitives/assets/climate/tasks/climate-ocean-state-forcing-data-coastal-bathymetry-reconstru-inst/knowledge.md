# 实例任务：海洋状态和强迫资料及任务边界预检 @ E74

- domain: climate
- 骨架: climate-ocean-state-forcing-data-boundary-precheck-task
- 场景: climate-coastal-bathymetry-reconstruction-morphological-evolution-scenario (E74)
- step_id: s01
- depend: []

## 场景研究主体
- E74
- 关联论文: Advancing bathymetric reconstruction and forecasting using deep learning | doi:

## 本实例步骤描述
界定“海岸浴深重建与形态演变预报”的任务范围并执行“海洋状态和强迫资料及任务边界预检”，核验历史浴深测量、水动力和泥沙强迫的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“海岸浴深重建与形态演变预报”，读取{OCEAN_STATE}、{SURFACE_FORCING}、{STATIC_OCEAN_DATA}、{START_TIME}、{TARGET_HORIZON}、{DATA_CUTOFF_TIME}并完成海洋状态和强迫资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {OCEAN_STATE} | required=True | type=str | var_name=海洋状态资料 | hint=输入海洋状态资料路径。 | default=None
- {SURFACE_FORCING} | required=False | type=str | var_name=海表强迫资料 | hint=输入海表强迫资料路径。 | default=None
- {STATIC_OCEAN_DATA} | required=False | type=str | var_name=静态海洋资料 | hint=输入地形掩膜等资料。 | default=None
- {START_TIME} | required=True | type=str | var_name=起始时刻 | hint=输入处理起始时刻。 | default=None
- {TARGET_HORIZON} | required=True | type=str | var_name=目标时效 | hint=输入目标时效或时段。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 海陆掩膜、岸线、垂向层和海洋单位一致

## 可调资源（edge:resource，仅真实存在）
- datasets/CMEMS
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/glorys12-global-ocean-reanalysis-dataset
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- tools/glo12v4-operational-ocean-forecasting-system
- tools/multi-task-deep-learning-model-for-indian-ocean-dipole-prediction
- tools/wenhai-global-ocean-forecast-system

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
