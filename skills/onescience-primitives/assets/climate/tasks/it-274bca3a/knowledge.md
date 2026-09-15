# 实例任务：水文强迫和流域资料及任务边界预检 @ E66

- domain: climate
- 骨架: tk-climate-14a78ebe
- 场景: sc-db022c00 (E66)
- step_id: s01
- depend: []

## 场景研究主体
- E66
- 关联论文: Hybrid Deep Learning for Week-Ahead Evapotranspiration Forecasting | doi:; Neural network approach to reference evapotranspiration modeling from limited climatic data in arid regions | doi:

## 本实例步骤描述
界定“有限气象变量驱动的未来7天参考蒸散发预报”的任务范围并执行“水文强迫和流域资料及任务边界预检”，核验温度湿度风速辐射观测与预报的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“有限气象变量驱动的未来7天参考蒸散发预报”，读取{RECENT_WEATHER_OBSERVATIONS}、{SEVEN_DAY_WEATHER_FORECAST}、{REFERENCE_ET_OBSERVATIONS}、{STATION_METADATA}、{FORECAST_START_DATE}、{DATA_CUTOFF_TIME}并完成水文强迫和流域资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {RECENT_WEATHER_OBSERVATIONS} | required=True | type=str | var_name=近期气象观测 | hint=输入近期气象观测路径。 | default=None
- {SEVEN_DAY_WEATHER_FORECAST} | required=True | type=str | var_name=未来7天天气预报 | hint=输入未来七天天气预报。 | default=None
- {REFERENCE_ET_OBSERVATIONS} | required=True | type=str | var_name=参考蒸散发实况 | hint=输入参考蒸散发实况。 | default=None
- {STATION_METADATA} | required=True | type=str | var_name=站点元数据 | hint=输入站点元数据路径。 | default=None
- {FORECAST_START_DATE} | required=True | type=str | var_name=预测起始日期 | hint=输入预测起始日期。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 气象强迫、流域边界和水文观测时空一致
- 近期观测、未来七天天气预报和参考蒸散实况分别登记

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
