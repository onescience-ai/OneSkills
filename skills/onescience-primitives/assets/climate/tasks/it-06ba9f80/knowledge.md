# 实例任务：起报资料及任务边界预检 @ E39

- domain: climate
- 骨架: tk-climate-b71baabb
- 场景: sc-8131edae (E39)
- step_id: s01
- depend: []

## 场景研究主体
- E39
- 关联论文: EarthNet2021- A large-scale dataset and challenge for Earth surface forecasting as a guided video prediction task | doi:; Enhanced prediction of vegetation responses to extreme drought using deep learning and Earth observation data | doi:; Deep Learning for Vegetation Health Forecasting- A Case Study in Kenya | doi:

## 本实例步骤描述
界定“卫星—天气驱动地表反射率与植被绿度短期预报”的任务范围并执行“起报资料及任务边界预检”，核验历史多光谱影像、天气驱动和静态地形的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“卫星—天气驱动地表反射率与植被绿度短期预报”，读取{SURFACE_HISTORY}、{WEATHER_DRIVERS}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{DATA_CUTOFF_TIME}并完成起报资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {SURFACE_HISTORY} | required=True | type=str | var_name=反射率绿度历史 | hint=输入反射率绿度序列。 | default=None
- {WEATHER_DRIVERS} | required=True | type=str | var_name=天气驱动资料 | hint=输入天气驱动资料路径。 | default=None
- {FORECAST_START_TIME} | required=True | type=str | var_name=起报时间 | hint=输入UTC起报时间。 | default=None
- {FORECAST_HORIZON} | required=True | type=str | var_name=周尺度预见期 | hint=输入周尺度预见期。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 所有动态输入的有效时间均不晚于资料截止时间
- 卫星历史序列和天气驱动均不晚于起报时间

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
