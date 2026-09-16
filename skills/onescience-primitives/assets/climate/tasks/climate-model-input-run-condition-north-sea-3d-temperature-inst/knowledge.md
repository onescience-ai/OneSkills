# 实例任务：模型输入与运行条件预检 @ E104

- domain: climate
- 骨架: climate-model-input-run-condition-precheck-task
- 场景: climate-north-sea-3d-temperature-salinity-current-intelligent-forecast-scenario (E104)
- step_id: s01
- depend: []

## 场景研究主体
- E104
- 关联论文: LangYa: a large AI model for global ocean forecasting | doi:

## 本实例步骤描述
核对模型实际输入的数据身份、版本、权限、资料截止时间、变量、时空覆盖和缺测，形成输入清单与数据阻断项。

## 本实例执行 prompt
读取{OCEAN_INITIAL_STATE}、{OCEAN_FORCING_DATA}、{OCEAN_BOUNDARY_DATA}和{BATHYMETRY_DATA}，以{DATA_CUTOFF_TIME}核验北海区覆盖、变量、层次、时次、边界、基准和缺测；缺少必需输入时标记BLOCKED。

## 本实例输入槽
- {OCEAN_INITIAL_STATE} | required=True | type=str | var_name=三维海洋初始场 | hint=输入温盐流初始场路径。 | default=None
- {OCEAN_FORCING_DATA} | required=True | type=str | var_name=海洋外部强迫 | hint=输入气象潮汐强迫路径。 | default=None
- {OCEAN_BOUNDARY_DATA} | required=True | type=str | var_name=开放边界数据 | hint=输入区域边界场路径。 | default=None
- {BATHYMETRY_DATA} | required=True | type=str | var_name=海底地形数据 | hint=输入海底地形路径。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 输入时空变量与缺测检查报告
- 数据缺失、权限和契约阻断项

## 本实例质量门禁
- 输入文件存在、可读、获准使用且来源和版本可追溯
- 输入的区域、时段、网格、变量、单位、坐标和资料截止时间已逐项核对
- 未来资料、模型开发资料和独立验证资料的用途已隔离
- 输入数据中的缺失、冲突和异常未被推测值覆盖

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/glorys12-global-ocean-reanalysis-dataset
- datasets/ostia-sst-data
- datasets/sgp-c1-multi-source-boundary-layer-height-dataset
- datasets/snodas-swe-data-product
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- models/tucker-thresholding-method-for-boundary-layer-height-estimation
- tools/glo12v4-operational-ocean-forecasting-system
- tools/multi-task-deep-learning-model-for-indian-ocean-dipole-prediction
- tools/wenhai-global-ocean-forecast-system

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
