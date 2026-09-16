# 实例任务：致灾因子和事件标签及任务边界预检 @ E76

- domain: climate
- 骨架: climate-hazard-factor-event-label-and-boundary-precheck-task
- 场景: climate-terrain-and-underlying-surface-driven-static-flood-scenario (E76)
- step_id: s01
- depend: []

## 场景研究主体
- E76
- 关联论文: Investigating the Role of the Key Conditioning Factors in Flood Susceptibility Mapping Through Machine Learning Approaches | doi:

## 本实例步骤描述
界定“地形与下垫面驱动的静态洪水易发性制图”的任务范围并执行“致灾因子和事件标签及任务边界预检”，核验DEM、河网、土地覆盖、土壤、历史洪水样点的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“地形与下垫面驱动的静态洪水易发性制图”，读取{DEM_DATA}、{RIVER_NETWORK}、{LAND_SURFACE_DATA}、{HISTORICAL_FLOOD_POINTS}、{MAPPING_EXTENT}并完成致灾因子和事件标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {DEM_DATA} | required=True | type=str | var_name=数字高程资料 | hint=输入数字高程资料路径。 | default=None
- {RIVER_NETWORK} | required=True | type=str | var_name=河网资料 | hint=输入河网资料路径。 | default=None
- {LAND_SURFACE_DATA} | required=True | type=str | var_name=下垫面资料 | hint=输入土地覆盖土壤资料。 | default=None
- {HISTORICAL_FLOOD_POINTS} | required=True | type=str | var_name=历史洪水样点 | hint=输入历史洪水样点路径。 | default=None
- {MAPPING_EXTENT} | required=True | type=str | var_name=制图范围 | hint=输入长期易发性制图范围。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 事件定义、预警窗口和资料截止时间明确
- 地形、河网、下垫面和历史洪水样点均为必需输入

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/gleam-v3-8a-global-land-evaporation-dataset
- datasets/international-soil-moisture-network-ismn
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- models/multivariate-data-fusion-vector-wind-prediction
- models/narx-network-configurations-for-inundation-depth-forecasting
- models/neural-network-based-nwp-model-calibration
- models/neural-network-soil-moisture-downscaling
- models/weighted-long-short-term-memory-neural-network-extended-model-for-pm2-5-forecasting
- tools/matlab-neural-network-toolbox

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
