# 骨架任务：天气能源运行资料及任务边界预检

- domain: climate
- 复用场景数: 4
- 实例任务数: 4

## 步骤描述（跨场景聚合去重）
- 界定“复杂地形风电场轮毂高度短期风速预报”的任务范围并执行“天气能源运行资料及任务边界预检”，核验近地面风、NWP、地形、轮毂高度的来源、覆盖、有效时间和可用边界。
- 界定“多站光伏电站0—48小时功率联合预报”的任务范围并执行“天气能源运行资料及任务边界预检”，核验多站历史功率、天气预报、电站容量属性的来源、覆盖、有效时间和可用边界。
- 界定“天气敏感型城市电力负荷日前概率预报”的任务范围并执行“天气能源运行资料及任务边界预检”，核验历史负荷、天气预报、日历与用户层级的来源、覆盖、有效时间和可用边界。
- 界定“天空相机与卫星云图驱动的分钟至小时太阳辐照度临近预报”的任务范围并执行“天气能源运行资料及任务边界预检”，核验天空图像、卫星云图、历史辐照度的来源、覆盖、有效时间和可用边界。

## 执行 prompt（跨场景聚合去重）
- 面向“复杂地形风电场轮毂高度短期风速预报”，读取{NEAR_SURFACE_OBSERVATIONS}、{NWP_WIND_FORECAST}、{TERRAIN_DATA}、{TURBINE_LOCATIONS}、{FORECAST_START_TIME}、{FORECAST_HORIZON}并完成天气能源运行资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“多站光伏电站0—48小时功率联合预报”，读取{WEATHER_INPUT}、{ASSET_METADATA}、{POWER_HISTORY}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{DATA_CUTOFF_TIME}并完成天气能源运行资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“天气敏感型城市电力负荷日前概率预报”，读取{WEATHER_FORECAST}、{LOAD_HISTORY}、{CALENDAR_FEATURES}、{HIERARCHY_METADATA}、{FORECAST_START_TIME}、{DATA_CUTOFF_TIME}并完成天气能源运行资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“天空相机与卫星云图驱动的分钟至小时太阳辐照度临近预报”，读取{SKY_CAMERA_HISTORY}、{SATELLITE_CLOUD_HISTORY}、{IRRADIANCE_HISTORY}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{DATA_CUTOFF_TIME}并完成天气能源运行资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 输入槽（var/hint/default）
- {NEAR_SURFACE_OBSERVATIONS} | required=True | type=str | var_name=近地面风观测 | hint=输入近地面风观测路径。 | default=None
- {NWP_WIND_FORECAST} | required=True | type=str | var_name=公里级风场预报 | hint=输入公里级风场预报。 | default=None
- {TERRAIN_DATA} | required=True | type=str | var_name=高分辨率地形 | hint=输入高分辨率地形路径。 | default=None
- {TURBINE_LOCATIONS} | required=True | type=str | var_name=风机位置与高度 | hint=输入风机位置轮毂高度。 | default=None
- {FORECAST_START_TIME} | required=True | type=str | var_name=起报时间 | hint=输入UTC起报时间。 | default=None
- {FORECAST_HORIZON} | required=True | type=str | var_name=分钟小时预见期 | hint=输入分钟至小时预见期。 | default=None
- {WEATHER_INPUT} | required=True | type=str | var_name=天气输入资料 | hint=输入天气观测预报路径。 | default=None
- {ASSET_METADATA} | required=True | type=str | var_name=能源设施信息 | hint=输入设施与容量信息。 | default=None
- {POWER_HISTORY} | required=False | type=str | var_name=历史功率负荷 | hint=输入历史功率负荷路径。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None
- {WEATHER_FORECAST} | required=True | type=str | var_name=日前天气预报 | hint=输入日前天气预报路径。 | default=None
- {LOAD_HISTORY} | required=True | type=str | var_name=历史电力负荷 | hint=输入历史负荷资料路径。 | default=None
- {CALENDAR_FEATURES} | required=True | type=str | var_name=日历特征 | hint=输入日历节假日特征。 | default=None
- {HIERARCHY_METADATA} | required=True | type=str | var_name=负荷层级信息 | hint=输入城市配电层级信息。 | default=None
- {SKY_CAMERA_HISTORY} | required=True | type=str | var_name=天空相机序列 | hint=输入天空相机序列路径。 | default=None
- {SATELLITE_CLOUD_HISTORY} | required=True | type=str | var_name=卫星云图序列 | hint=输入卫星云图序列路径。 | default=None
- {IRRADIANCE_HISTORY} | required=True | type=str | var_name=地面辐照度历史 | hint=输入地面辐照度历史。 | default=None

## 产出
- 任务范围和资料截止时间表
- 输入完整性预检报告
- 输入数据与版本清单

## 质量门禁 quality_gate
- 任务区域、时段、变量和输出目标无歧义
- 天气输入和设施观测在签发时均真实可用
- 天空相机、卫星云图和地面辐照度均不晚于起报时间
- 所有必需输入均存在且路径、版本和来源可追溯
- 缺测、重复和异常资料已记录且未擅自补造
- 近地面风、公里风场、地形和轮毂高度均显式登记

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-1d050954
- it-6e4bee69
- it-a20c5762
- it-fbb86a6d

## 复用场景
- E26
- E25
- E20
- E23
