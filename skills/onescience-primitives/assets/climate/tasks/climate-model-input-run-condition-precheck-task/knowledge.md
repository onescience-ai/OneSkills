# 骨架任务：模型输入与运行条件预检

- domain: climate
- 复用场景数: 9
- 实例任务数: 9

## 步骤描述（跨场景聚合去重）
- 核对模型实际输入的数据身份、版本、权限、资料截止时间、变量、时空覆盖和缺测，形成输入清单与数据阻断项。

## 执行 prompt（跨场景聚合去重）
- 读取{BATHYMETRY_COASTLINE}、{WIND_10M_FORECAST}和{WAVE_BOUNDARY_DATA}，以{TARGET_REGION}和{DATA_CUTOFF_TIME}核验存在性、权限、覆盖、网格、变量、时次、方向约定和缺测；仅列出数据阻断项。
- 读取{GLOBAL_FOURCASTNET_ASSET}、{REGIONAL_REANALYSIS_DATA}和{LARGE_SCALE_BOUNDARY_DATA}，以{TARGET_REGION}为范围、{DATA_CUTOFF_TIME}为资料截止时间，核验模型、数据和边界产品的存在性、权限、变量、版本、覆盖和缺测；仅列出数据阻断项。
- 读取{OCEAN_INITIAL_STATE}、{OCEAN_FORCING_DATA}、{OCEAN_BOUNDARY_DATA}和{BATHYMETRY_DATA}，以{DATA_CUTOFF_TIME}核验北海区覆盖、变量、层次、时次、边界、基准和缺测；缺少必需输入时标记BLOCKED。
- 读取{OCEAN_TEMPERATURE_FORECAST}、{FUSED_SST_OBSERVATION}和{ATMOSPHERIC_FORCING_FORECAST}，以{TARGET_REGION}和{DATA_CUTOFF_TIME}核验系统版本、起报、有效时刻、层次、网格、缺测和未来资料泄漏。
- 读取{OPERATIONAL_WAVE_FORECAST}和{WAVE_OBSERVATIONS}，以{DATA_CUTOFF_TIME}核验待订正产品身份、变量、起报、有效时刻、网格、观测覆盖和使用权限；若待订正产品来自EC或GFS须明确其身份。
- 读取{PREDICTED_COASTAL_WATER_LEVEL}、{TERRAIN_COAST_DEFENSE}和{ADMINISTRATIVE_BOUNDARIES}，以{TARGET_COASTAL_AREA}和{DATA_CUTOFF_TIME}核验存在性、权限、水位与高程基准、坐标、空间覆盖、有效时间、岸线、防护工程和行政边界；缺少任一必要输入或关键定义时标记BLOCKED。
- 读取{SCHEDULED_SURGE_FORECAST}、{REALTIME_TIDE_DATA}和{REALTIME_WEATHER_DATA}，以{RUN_TIME}和{DATA_CUTOFF_TIME}核验北海区数据时效、300 m网格、接口延迟、缺测及未来资料泄漏。
- 读取{STORM_SURGE_FORECAST}、{METEOROLOGICAL_FIELDS}、{PREVIOUS_DAY_SIMULATION}和{SURGE_OBSERVATIONS}，以{DATA_CUTOFF_TIME}核验北海区数据身份、300 m网格、起报、有效时刻、站点和未来资料泄漏。
- 读取{WRF_FORECAST_DATA}和{WRF_ERA5_REFERENCE}，以{TARGET_REGION}和{DATA_CUTOFF_TIME}核验预报与参考数据的存在性、权限、版本、变量、起报、有效时刻、网格和缺测；仅列出数据阻断项。

## 输入槽（var/hint/default）
- {OCEAN_TEMPERATURE_FORECAST} | required=True | type=str | var_name=海温数值预报 | hint=输入三维海温预报路径。 | default=None
- {FUSED_SST_OBSERVATION} | required=True | type=str | var_name=融合海表温度观测 | hint=输入融合SST观测路径。 | default=None
- {ATMOSPHERIC_FORCING_FORECAST} | required=True | type=str | var_name=气象强迫预报 | hint=输入气温降水风场路径。 | default=None
- {TARGET_REGION} | required=True | type=str | var_name=目标区域 | hint=输入渤黄海区域边界。 | default=渤黄海区域
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None
- {OCEAN_INITIAL_STATE} | required=True | type=str | var_name=三维海洋初始场 | hint=输入温盐流初始场路径。 | default=None
- {OCEAN_FORCING_DATA} | required=True | type=str | var_name=海洋外部强迫 | hint=输入气象潮汐强迫路径。 | default=None
- {OCEAN_BOUNDARY_DATA} | required=True | type=str | var_name=开放边界数据 | hint=输入区域边界场路径。 | default=None
- {BATHYMETRY_DATA} | required=True | type=str | var_name=海底地形数据 | hint=输入海底地形路径。 | default=None
- {SCHEDULED_SURGE_FORECAST} | required=True | type=str | var_name=定时风暴潮预报 | hint=输入已发布预报路径。 | default=None
- {REALTIME_TIDE_DATA} | required=True | type=str | var_name=实时逐小时潮位 | hint=输入实时潮位数据路径。 | default=None
- {REALTIME_WEATHER_DATA} | required=True | type=str | var_name=实时逐小时气象 | hint=输入实时气象数据路径。 | default=None
- {RUN_TIME} | required=True | type=str | var_name=模型运行时刻 | hint=输入本次运行UTC时间。 | default=None
- {STORM_SURGE_FORECAST} | required=True | type=str | var_name=风暴潮数值预报 | hint=输入当天网格预报路径。 | default=None
- {METEOROLOGICAL_FIELDS} | required=True | type=str | var_name=气象场 | hint=输入气象驱动场路径。 | default=None
- {PREVIOUS_DAY_SIMULATION} | required=True | type=str | var_name=前日模拟结果 | hint=输入前一天模拟路径。 | default=None
- {SURGE_OBSERVATIONS} | required=True | type=str | var_name=风暴潮观测数据 | hint=输入可用观测数据路径。 | default=None
- {GLOBAL_FOURCASTNET_ASSET} | required=True | type=str | var_name=全球FourCastNet工件 | hint=输入模型与配置路径。 | default=None
- {REGIONAL_REANALYSIS_DATA} | required=True | type=str | var_name=区域再分析数据 | hint=输入WRF-ERA5等数据路径。 | default=None
- {LARGE_SCALE_BOUNDARY_DATA} | required=True | type=str | var_name=大区域边界产品 | hint=输入边界产品路径。 | default=None
- {WRF_FORECAST_DATA} | required=True | type=str | var_name=WRF预报数据 | hint=输入WRF历史预报路径。 | default=None
- {WRF_ERA5_REFERENCE} | required=True | type=str | var_name=WRF-ERA5参考数据 | hint=输入再分析参考路径。 | default=None
- {OPERATIONAL_WAVE_FORECAST} | required=True | type=str | var_name=业务海浪预报 | hint=输入业务模式产品路径。 | default=None
- {WAVE_OBSERVATIONS} | required=True | type=str | var_name=海浪观测历史 | hint=输入观测与历史数据路径。 | default=None
- {BATHYMETRY_COASTLINE} | required=True | type=str | var_name=地形岸线数据 | hint=输入海底地形岸线路径。 | default=None
- {WIND_10M_FORECAST} | required=True | type=str | var_name=10米风场 | hint=输入风速风向数据路径。 | default=None
- {WAVE_BOUNDARY_DATA} | required=True | type=str | var_name=海浪边界场 | hint=输入大区域海浪产品。 | default=None
- {PREDICTED_COASTAL_WATER_LEVEL} | required=True | type=str | var_name=预测沿岸潮位 | hint=输入沿岸潮位预报路径。 | default=None
- {TARGET_COASTAL_AREA} | required=True | type=str | var_name=目标近岸区域 | hint=输入目标区域边界。 | default=None
- {TERRAIN_COAST_DEFENSE} | required=True | type=str | var_name=地形岸线防护数据 | hint=输入地形岸线工程路径。 | default=None
- {ADMINISTRATIVE_BOUNDARIES} | required=True | type=str | var_name=行政区划数据 | hint=输入行政边界数据路径。 | default=None

## 产出
- 数据缺失、权限和契约阻断项
- 输入数据与版本清单
- 输入时空变量与缺测检查报告

## 质量门禁 quality_gate
- 未来资料、模型开发资料和独立验证资料的用途已隔离
- 输入数据中的缺失、冲突和异常未被推测值覆盖
- 输入文件存在、可读、获准使用且来源和版本可追溯
- 输入的区域、时段、网格、变量、单位、坐标和资料截止时间已逐项核对

## 可调资源（edge:resource，仅真实存在）
- datapipes/exploring-deep-learning-capabilities-surge-predictions-coastal
- datasets/cesm2-large-ensemble
- datasets/data-infrastructure-observations-and-labels
- datasets/ERA5
- datasets/gedi-footprint-canopy-height-data
- datasets/gleam-v3-8a-global-land-evaporation-dataset
- datasets/global-canopy-height-map-2020
- datasets/glorys12-global-ocean-reanalysis-dataset
- datasets/gtws-mlrec-machine-learning-based-global-terrestrial-water-storage-anomaly-reconstruction-dataset-and-workflow
- datasets/large-ensemble-testbed
- datasets/lpma-airport-wind-observation-validation
- datasets/manila-dengue-meteorological-dataset
- datasets/ostia-sst-data
- datasets/sgp-c1-multi-source-boundary-layer-height-dataset
- datasets/smap-level-3-passive-soil-moisture-products
- datasets/snodas-swe-data-product
- datasets/south-korea-air-quality-and-weather-monitoring-dataset
- datasets/southern-great-plains-sgp-observatory-wind-dataset
- models/1d-cnn-based-groundwater-level-prediction
- models/anomaly-numerical-correction-with-observations-ano
- models/dynamic-pre-training-for-time-series-dynpt
- models/fourcastnet
- models/multivariate-data-fusion-vector-wind-prediction
- models/radially-averaged-power-spectral-density-analysis
- models/random-forest-meteorological-normalization
- models/random-forest-regression-for-vertical-wind-speed-extrapolation
- models/tucker-thresholding-method-for-boundary-layer-height-estimation
- tools/aardvark-weather-system
- tools/ai-global-medium-range-weather-forecasting-system-pangu-weather
- tools/anni-nh3-v2-1-satellite-ammonia-retrieval-algorithm-and-reanalysis-dataset
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/fuxi-weather
- tools/gencast-global-probabilistic-weather-forecasting-model
- tools/glo12v4-operational-ocean-forecasting-system
- tools/lhasa-v2-global-rainfall-triggered-landslide-probabilistic-nowcast-model
- tools/multi-level-b-spline-analysis-mba
- tools/multi-task-deep-learning-model-for-indian-ocean-dipole-prediction
- tools/urban-hydrological-hydraulic-model-chain-for-inundation-simulation
- tools/wenhai-global-ocean-forecast-system

## 实例任务（本骨架在各场景的实例化）
- climate-model-input-run-condition-bohai-yellow-sea-fourcastnet-inst
- climate-model-input-run-condition-bohai-yellow-sea-wave-inst
- climate-model-input-run-condition-bohai-yellow-sea-wave-inst-2
- climate-model-input-run-condition-bohai-yellow-sea-wrf-numeric-inst
- climate-model-input-run-condition-nearshore-inundation-rapid-inst
- climate-model-input-run-condition-north-sea-3d-sea-temperature-inst
- climate-model-input-run-condition-north-sea-3d-temperature-inst
- climate-model-input-run-condition-north-sea-storm-surge-inst
- climate-model-input-run-condition-north-sea-storm-surge-inst-2

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
