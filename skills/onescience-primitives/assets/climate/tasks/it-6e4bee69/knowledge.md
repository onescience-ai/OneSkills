# 实例任务：天气能源运行资料及任务边界预检 @ E23

- domain: climate
- 骨架: tk-climate-f078dc43
- 场景: sc-6e705dff (E23)
- step_id: s01
- depend: []

## 场景研究主体
- E23
- 关联论文: A Deep Learning Approach to Solar-Irradiance Forecasting in Sky-Videos | doi:; IrradianceNet- Spatiotemporal deep learning model for satellite-derived solar irradiance short-term forecasting | doi:; Sky Imager-Based Forecast of Solar Irradiance Using Machine Learning | doi:; A regional solar forecasting approach using generative adversarial networks with solar irradiance maps | doi:

## 本实例步骤描述
界定“天空相机与卫星云图驱动的分钟至小时太阳辐照度临近预报”的任务范围并执行“天气能源运行资料及任务边界预检”，核验天空图像、卫星云图、历史辐照度的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“天空相机与卫星云图驱动的分钟至小时太阳辐照度临近预报”，读取{SKY_CAMERA_HISTORY}、{SATELLITE_CLOUD_HISTORY}、{IRRADIANCE_HISTORY}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{DATA_CUTOFF_TIME}并完成天气能源运行资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {SKY_CAMERA_HISTORY} | required=True | type=str | var_name=天空相机序列 | hint=输入天空相机序列路径。 | default=None
- {SATELLITE_CLOUD_HISTORY} | required=True | type=str | var_name=卫星云图序列 | hint=输入卫星云图序列路径。 | default=None
- {IRRADIANCE_HISTORY} | required=True | type=str | var_name=地面辐照度历史 | hint=输入地面辐照度历史。 | default=None
- {FORECAST_START_TIME} | required=True | type=str | var_name=起报时间 | hint=输入UTC起报时间。 | default=None
- {FORECAST_HORIZON} | required=True | type=str | var_name=分钟小时预见期 | hint=输入分钟至小时预见期。 | default=None
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
- 天空相机、卫星云图和地面辐照度均不晚于起报时间

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
