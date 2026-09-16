# 实例任务：模型输入与运行条件预检 @ E106

- domain: climate
- 骨架: climate-model-input-run-condition-precheck-task
- 场景: climate-bohai-yellow-sea-wave-intelligent-forecast-scenario (E106)
- step_id: s01
- depend: []

## 场景研究主体
- E106
- 关联论文: Ocean Wave Forecasting With Deep Learning as Alternative to Conventional Models | doi:

## 本实例步骤描述
核对模型实际输入的数据身份、版本、权限、资料截止时间、变量、时空覆盖和缺测，形成输入清单与数据阻断项。

## 本实例执行 prompt
读取{BATHYMETRY_COASTLINE}、{WIND_10M_FORECAST}和{WAVE_BOUNDARY_DATA}，以{TARGET_REGION}和{DATA_CUTOFF_TIME}核验存在性、权限、覆盖、网格、变量、时次、方向约定和缺测；仅列出数据阻断项。

## 本实例输入槽
- {BATHYMETRY_COASTLINE} | required=True | type=str | var_name=地形岸线数据 | hint=输入海底地形岸线路径。 | default=None
- {WIND_10M_FORECAST} | required=True | type=str | var_name=10米风场 | hint=输入风速风向数据路径。 | default=None
- {WAVE_BOUNDARY_DATA} | required=True | type=str | var_name=海浪边界场 | hint=输入大区域海浪产品。 | default=None
- {TARGET_REGION} | required=True | type=str | var_name=目标区域 | hint=输入渤黄海区域边界。 | default=渤黄海区域
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
- datasets/lpma-airport-wind-observation-validation
- datasets/ostia-sst-data
- datasets/sgp-c1-multi-source-boundary-layer-height-dataset
- datasets/snodas-swe-data-product
- datasets/southern-great-plains-sgp-observatory-wind-dataset
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- models/random-forest-regression-for-vertical-wind-speed-extrapolation
- models/tucker-thresholding-method-for-boundary-layer-height-estimation
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/wenhai-global-ocean-forecast-system

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
