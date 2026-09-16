# 骨架任务：致灾因子和事件标签及任务边界预检

- domain: climate
- 复用场景数: 9
- 实例任务数: 9

## 步骤描述（跨场景聚合去重）
- 界定“卫星影像与地面传感器融合的早期火情烟羽检测”的任务范围并执行“致灾因子和事件标签及任务边界预检”，核验卫星或摄像影像、温湿烟气传感器的来源、覆盖、有效时间和可用边界。
- 界定“台风与气压风场驱动的沿海风暴增水短期预报”的任务范围并执行“致灾因子和事件标签及任务边界预检”，核验风压预报、天文潮、历史水位、海岸地形的来源、覆盖、有效时间和可用边界。
- 界定“地形与下垫面驱动的静态洪水易发性制图”的任务范围并执行“致灾因子和事件标签及任务边界预检”，核验DEM、河网、土地覆盖、土壤、历史洪水样点的来源、覆盖、有效时间和可用边界。
- 界定“多时间窗降雨驱动的区域浅层滑坡概率临近预警”的任务范围并执行“致灾因子和事件标签及任务边界预检”，核验小时雨量历史、降雨预报、滑坡目录、易发性图的来源、覆盖、有效时间和可用边界。
- 界定“多源观测与天气预报驱动的沙尘事件提前预警”的任务范围并执行“致灾因子和事件标签及任务边界预检”，核验气象预报、气溶胶观测、地表与沙尘历史的来源、覆盖、有效时间和可用边界。
- 界定“天气驱动次日大面积野火危险概率预报”的任务范围并执行“致灾因子和事件标签及任务边界预检”，核验近期天气、土壤、植被、地形和人类活动特征的来源、覆盖、有效时间和可用边界。
- 界定“干雪雪崩危险等级日尺度预报”的任务范围并执行“致灾因子和事件标签及任务边界预检”，核验积雪状态、天气历史与预报、地形的来源、覆盖、有效时间和可用边界。
- 界定“气候与燃料异常驱动的季节野火发生概率预测”的任务范围并执行“致灾因子和事件标签及任务边界预检”，核验季节气候异常、燃料与植被状态、历史火点的来源、覆盖、有效时间和可用边界。
- 界定“海啸与大地测量观测驱动的快速淹没范围预报”的任务范围并执行“致灾因子和事件标签及任务边界预检”，核验海啸浮标、海平面与地壳形变观测的来源、覆盖、有效时间和可用边界。

## 执行 prompt（跨场景聚合去重）
- 面向“卫星影像与地面传感器融合的早期火情烟羽检测”，读取{HAZARD_DRIVERS}、{STATIC_CONDITIONS}、{EVENT_LABELS}、{TARGET_WINDOW}、{DATA_CUTOFF_TIME}并完成致灾因子和事件标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“台风与气压风场驱动的沿海风暴增水短期预报”，读取{HAZARD_DRIVERS}、{STATIC_CONDITIONS}、{EVENT_LABELS}、{TARGET_WINDOW}、{DATA_CUTOFF_TIME}并完成致灾因子和事件标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“地形与下垫面驱动的静态洪水易发性制图”，读取{DEM_DATA}、{RIVER_NETWORK}、{LAND_SURFACE_DATA}、{HISTORICAL_FLOOD_POINTS}、{MAPPING_EXTENT}并完成致灾因子和事件标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“多时间窗降雨驱动的区域浅层滑坡概率临近预警”，读取{HAZARD_DRIVERS}、{STATIC_CONDITIONS}、{EVENT_LABELS}、{TARGET_WINDOW}、{DATA_CUTOFF_TIME}并完成致灾因子和事件标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“多源观测与天气预报驱动的沙尘事件提前预警”，读取{GROUND_DUST_OBSERVATIONS}、{SATELLITE_AEROSOL_DATA}、{AEROSOL_BACKGROUND}、{WEATHER_FORECAST}、{FORECAST_START_TIME}、{FORECAST_HORIZON}并完成致灾因子和事件标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“天气驱动次日大面积野火危险概率预报”，读取{HAZARD_DRIVERS}、{STATIC_CONDITIONS}、{EVENT_LABELS}、{TARGET_WINDOW}、{DATA_CUTOFF_TIME}并完成致灾因子和事件标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“干雪雪崩危险等级日尺度预报”，读取{HAZARD_DRIVERS}、{STATIC_CONDITIONS}、{EVENT_LABELS}、{TARGET_WINDOW}、{DATA_CUTOFF_TIME}并完成致灾因子和事件标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“气候与燃料异常驱动的季节野火发生概率预测”，读取{HAZARD_DRIVERS}、{STATIC_CONDITIONS}、{EVENT_LABELS}、{TARGET_WINDOW}、{DATA_CUTOFF_TIME}并完成致灾因子和事件标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“海啸与大地测量观测驱动的快速淹没范围预报”，读取{HAZARD_DRIVERS}、{STATIC_CONDITIONS}、{EVENT_LABELS}、{TARGET_WINDOW}、{DATA_CUTOFF_TIME}并完成致灾因子和事件标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 输入槽（var/hint/default）
- {HAZARD_DRIVERS} | required=True | type=str | var_name=致灾驱动资料 | hint=输入致灾驱动资料路径。 | default=None
- {STATIC_CONDITIONS} | required=False | type=str | var_name=静态环境资料 | hint=输入地形和下垫面资料。 | default=None
- {EVENT_LABELS} | required=True | type=str | var_name=历史事件标签 | hint=输入历史事件标签路径。 | default=None
- {TARGET_WINDOW} | required=True | type=str | var_name=目标预警窗口 | hint=输入目标预警时间窗。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None
- {DEM_DATA} | required=True | type=str | var_name=数字高程资料 | hint=输入数字高程资料路径。 | default=None
- {RIVER_NETWORK} | required=True | type=str | var_name=河网资料 | hint=输入河网资料路径。 | default=None
- {LAND_SURFACE_DATA} | required=True | type=str | var_name=下垫面资料 | hint=输入土地覆盖土壤资料。 | default=None
- {HISTORICAL_FLOOD_POINTS} | required=True | type=str | var_name=历史洪水样点 | hint=输入历史洪水样点路径。 | default=None
- {MAPPING_EXTENT} | required=True | type=str | var_name=制图范围 | hint=输入长期易发性制图范围。 | default=None
- {GROUND_DUST_OBSERVATIONS} | required=True | type=str | var_name=地面沙尘观测 | hint=输入地面沙尘观测路径。 | default=None
- {SATELLITE_AEROSOL_DATA} | required=True | type=str | var_name=卫星气溶胶资料 | hint=输入卫星气溶胶资料。 | default=None
- {AEROSOL_BACKGROUND} | required=True | type=str | var_name=气溶胶背景场 | hint=输入气溶胶背景场路径。 | default=None
- {WEATHER_FORECAST} | required=True | type=str | var_name=天气预报资料 | hint=输入天气预报资料路径。 | default=None
- {FORECAST_START_TIME} | required=True | type=str | var_name=预警签发时间 | hint=输入预警签发时间。 | default=None
- {FORECAST_HORIZON} | required=True | type=str | var_name=预警时效 | hint=输入小时至日预警时效。 | default=None

## 产出
- 任务范围和资料截止时间表
- 输入完整性预检报告
- 输入数据与版本清单

## 质量门禁 quality_gate
- 事件定义、预警窗口和资料截止时间明确
- 任务区域、时段、变量和输出目标无歧义
- 地形、河网、下垫面和历史洪水样点均为必需输入
- 地面、卫星、背景场和天气预报资料均显式登记
- 所有必需输入均存在且路径、版本和来源可追溯
- 缺测、重复和异常资料已记录且未擅自补造

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/gleam-v3-8a-global-land-evaporation-dataset
- datasets/in-situ-and-satellite-matchup-dataset-for-chlorophyll-a-retrieval
- datasets/integrated-multi-satellite-retrievals-for-gpm-imerg-precipitation-dataset
- datasets/international-soil-moisture-network-ismn
- datasets/lpma-airport-wind-observation-validation
- datasets/machine-learning-modeling-plant-phenology-coupling-satellite
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- datasets/south-korea-air-quality-and-weather-monitoring-dataset
- datasets/southern-great-plains-sgp-observatory-wind-dataset
- models/anomaly-numerical-correction-with-observations-ano
- models/dust-event-forecasting-with-multi-task-deep-learning
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- models/narx-network-configurations-for-inundation-depth-forecasting
- models/neural-network-based-nwp-model-calibration
- models/neural-network-soil-moisture-downscaling
- models/random-forest-regression-for-vertical-wind-speed-extrapolation
- models/weighted-long-short-term-memory-neural-network-extended-model-for-pm2-5-forecasting
- tools/aardvark-weather-system
- tools/aerosol-chemical-speciation-monitor-acsm
- tools/ai-global-medium-range-weather-forecasting-system-pangu-weather
- tools/anni-nh3-v2-1-satellite-ammonia-retrieval-algorithm-and-reanalysis-dataset
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/fuxi-weather
- tools/gencast-global-probabilistic-weather-forecasting-model
- tools/matlab-neural-network-toolbox
- tools/wenhai-global-ocean-forecast-system

## 实例任务（本骨架在各场景的实例化）
- climate-hazard-factor-event-label-and-climate-fuel-anomaly-driven-inst
- climate-hazard-factor-event-label-and-dry-snow-avalanche-danger-inst
- climate-hazard-factor-event-label-and-multi-source-observation-inst
- climate-hazard-factor-event-label-and-multi-time-window-rainfall-inst
- climate-hazard-factor-event-label-and-satellite-and-ground-sensor-inst
- climate-hazard-factor-event-label-and-terrain-and-underlying-inst
- climate-hazard-factor-event-label-and-tsunami-geodetic-observation-inst
- climate-hazard-factor-event-label-and-typhoon-and-pressure-wind-inst
- climate-hazard-factor-event-label-and-weather-driven-next-day-inst

## 复用场景
- E22
- E11
- E76
- E51
- E92
- E37
- E32
- E70
- E90
