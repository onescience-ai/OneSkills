# 实例任务：天气能源运行资料及任务边界预检 @ E25

- domain: climate
- 骨架: tk-climate-f078dc43
- 场景: sc-1e3c4752 (E25)
- step_id: s01
- depend: []

## 场景研究主体
- E25
- 关联论文: Spatio-Temporal Graph Neural Networks for Multi-Site PV Power Forecasting | doi:; Photovoltaic yield prediction using an irradiance forecast model based on multiple neural networks | doi:; Short-Term Power Generation Forecasting of a Photovoltaic Plant Based on PSO-BP and GA-BP Neural Networks | doi:; Solar PV power forecasting at Yarmouk University using machine learning techniques | doi:

## 本实例步骤描述
界定“多站光伏电站0—48小时功率联合预报”的任务范围并执行“天气能源运行资料及任务边界预检”，核验多站历史功率、天气预报、电站容量属性的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“多站光伏电站0—48小时功率联合预报”，读取{WEATHER_INPUT}、{ASSET_METADATA}、{POWER_HISTORY}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{DATA_CUTOFF_TIME}并完成天气能源运行资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {WEATHER_INPUT} | required=True | type=str | var_name=天气输入资料 | hint=输入天气观测预报路径。 | default=None
- {ASSET_METADATA} | required=True | type=str | var_name=能源设施信息 | hint=输入设施与容量信息。 | default=None
- {POWER_HISTORY} | required=False | type=str | var_name=历史功率负荷 | hint=输入历史功率负荷路径。 | default=None
- {FORECAST_START_TIME} | required=True | type=str | var_name=起报时间 | hint=输入UTC起报时间。 | default=None
- {FORECAST_HORIZON} | required=True | type=str | var_name=预测时效 | hint=输入目标预测时效。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 天气输入和设施观测在签发时均真实可用

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
