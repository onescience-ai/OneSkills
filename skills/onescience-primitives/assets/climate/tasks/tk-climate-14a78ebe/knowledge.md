# 骨架任务：水文强迫和流域资料及任务边界预检

- domain: climate
- 复用场景数: 11
- 实例任务数: 11

## 步骤描述（跨场景聚合去重）
- 界定“CMIP6气候情景驱动的流域径流长期投影”的任务范围并执行“水文强迫和流域资料及任务边界预检”，核验历史水文气象、CMIP6情景、流域属性的来源、覆盖、有效时间和可用边界。
- 界定“城市积水点未来数小时淹没深度多步预报”的任务范围并执行“水文强迫和流域资料及任务边界预检”，核验实时雨量水位、短临降水、排水状态的来源、覆盖、有效时间和可用边界。
- 界定“多源气象强迫驱动的多流域日径流连续模拟”的任务范围并执行“水文强迫和流域资料及任务边界预检”，核验多源逐日气象强迫、流域静态属性、历史流量的来源、覆盖、有效时间和可用边界。
- 界定“有限气象变量驱动的未来7天参考蒸散发预报”的任务范围并执行“水文强迫和流域资料及任务边界预检”，核验温度湿度风速辐射观测与预报的来源、覆盖、有效时间和可用边界。
- 界定“次季节土壤湿度干旱概率预报”的任务范围并执行“水文强迫和流域资料及任务边界预检”，核验初始土壤湿度、气象预报、陆面属性的来源、覆盖、有效时间和可用边界。
- 界定“气候情景驱动的地下水位长期投影”的任务范围并执行“水文强迫和流域资料及任务边界预检”，核验历史地下水位、气象与抽水信息、气候情景的来源、覆盖、有效时间和可用边界。
- 界定“气候模态驱动的水库月入库流量预报”的任务范围并执行“水文强迫和流域资料及任务边界预检”，核验月入流、气象历史、气候模态指数的来源、覆盖、有效时间和可用边界。
- 界定“气象预报驱动的小时至十日河流流量与洪峰预报”的任务范围并执行“水文强迫和流域资料及任务边界预检”，核验实时雨量流量、流域状态、未来气象预报的来源、覆盖、有效时间和可用边界。
- 界定“流域气象干旱指数的月季尺度预报”的任务范围并执行“水文强迫和流域资料及任务边界预检”，核验历史气象序列、气候因子的来源、覆盖、有效时间和可用边界。
- 界定“遥感土壤湿度公里级空间降尺度与时序重建”的任务范围并执行“水文强迫和流域资料及任务边界预检”，核验卫星土壤湿度、植被地表温度、地形土壤属性的来源、覆盖、有效时间和可用边界。
- 界定“降雨与管网状态驱动的合流制溢流事件预报”的任务范围并执行“水文强迫和流域资料及任务边界预检”，核验降雨预报、管网水位流量、泵闸运行的来源、覆盖、有效时间和可用边界。

## 执行 prompt（跨场景聚合去重）
- 面向“CMIP6气候情景驱动的流域径流长期投影”，读取{METEOROLOGICAL_FORCING}、{BASIN_ATTRIBUTES}、{HYDROLOGICAL_OBSERVATIONS}、{SIMULATION_PERIOD}、{DATA_CUTOFF_TIME}并完成水文强迫和流域资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“城市积水点未来数小时淹没深度多步预报”，读取{METEOROLOGICAL_FORCING}、{BASIN_ATTRIBUTES}、{HYDROLOGICAL_OBSERVATIONS}、{SIMULATION_PERIOD}、{DATA_CUTOFF_TIME}并完成水文强迫和流域资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“多源气象强迫驱动的多流域日径流连续模拟”，读取{METEOROLOGICAL_FORCING}、{BASIN_ATTRIBUTES}、{HYDROLOGICAL_OBSERVATIONS}、{SIMULATION_PERIOD}、{DATA_CUTOFF_TIME}并完成水文强迫和流域资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“有限气象变量驱动的未来7天参考蒸散发预报”，读取{RECENT_WEATHER_OBSERVATIONS}、{SEVEN_DAY_WEATHER_FORECAST}、{REFERENCE_ET_OBSERVATIONS}、{STATION_METADATA}、{FORECAST_START_DATE}、{DATA_CUTOFF_TIME}并完成水文强迫和流域资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“次季节土壤湿度干旱概率预报”，读取{METEOROLOGICAL_FORCING}、{BASIN_ATTRIBUTES}、{HYDROLOGICAL_OBSERVATIONS}、{SIMULATION_PERIOD}、{DATA_CUTOFF_TIME}并完成水文强迫和流域资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“气候情景驱动的地下水位长期投影”，读取{METEOROLOGICAL_FORCING}、{BASIN_ATTRIBUTES}、{HYDROLOGICAL_OBSERVATIONS}、{SIMULATION_PERIOD}、{DATA_CUTOFF_TIME}并完成水文强迫和流域资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“气候模态驱动的水库月入库流量预报”，读取{METEOROLOGICAL_FORCING}、{BASIN_ATTRIBUTES}、{HYDROLOGICAL_OBSERVATIONS}、{SIMULATION_PERIOD}、{DATA_CUTOFF_TIME}并完成水文强迫和流域资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“气象预报驱动的小时至十日河流流量与洪峰预报”，读取{METEOROLOGICAL_FORCING}、{BASIN_ATTRIBUTES}、{HYDROLOGICAL_OBSERVATIONS}、{SIMULATION_PERIOD}、{DATA_CUTOFF_TIME}并完成水文强迫和流域资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“流域气象干旱指数的月季尺度预报”，读取{METEOROLOGICAL_FORCING}、{BASIN_ATTRIBUTES}、{HYDROLOGICAL_OBSERVATIONS}、{SIMULATION_PERIOD}、{DATA_CUTOFF_TIME}并完成水文强迫和流域资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“遥感土壤湿度公里级空间降尺度与时序重建”，读取{COARSE_SOIL_MOISTURE}、{FINE_SCALE_COVARIATES}、{FINE_REFERENCE}、{GAP_MASK}、{TARGET_GRID}并完成水文强迫和流域资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“降雨与管网状态驱动的合流制溢流事件预报”，读取{METEOROLOGICAL_FORCING}、{BASIN_ATTRIBUTES}、{HYDROLOGICAL_OBSERVATIONS}、{SIMULATION_PERIOD}、{DATA_CUTOFF_TIME}并完成水文强迫和流域资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 输入槽（var/hint/default）
- {METEOROLOGICAL_FORCING} | required=True | type=str | var_name=气象强迫资料 | hint=输入气象强迫资料路径。 | default=None
- {BASIN_ATTRIBUTES} | required=True | type=str | var_name=流域属性资料 | hint=输入流域属性资料路径。 | default=None
- {HYDROLOGICAL_OBSERVATIONS} | required=False | type=str | var_name=水文观测资料 | hint=输入水文观测资料路径。 | default=None
- {SIMULATION_PERIOD} | required=True | type=str | var_name=模拟预报时段 | hint=输入处理起止时间。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None
- {RECENT_WEATHER_OBSERVATIONS} | required=True | type=str | var_name=近期气象观测 | hint=输入近期气象观测路径。 | default=None
- {SEVEN_DAY_WEATHER_FORECAST} | required=True | type=str | var_name=未来7天天气预报 | hint=输入未来七天天气预报。 | default=None
- {REFERENCE_ET_OBSERVATIONS} | required=True | type=str | var_name=参考蒸散发实况 | hint=输入参考蒸散发实况。 | default=None
- {STATION_METADATA} | required=True | type=str | var_name=站点元数据 | hint=输入站点元数据路径。 | default=None
- {FORECAST_START_DATE} | required=True | type=str | var_name=预测起始日期 | hint=输入预测起始日期。 | default=None
- {COARSE_SOIL_MOISTURE} | required=True | type=str | var_name=粗网格土壤湿度 | hint=输入粗网格土壤湿度。 | default=None
- {FINE_SCALE_COVARIATES} | required=True | type=str | var_name=细尺度辅助变量 | hint=输入地表地形辅助资料。 | default=None
- {FINE_REFERENCE} | required=True | type=str | var_name=细尺度参考资料 | hint=输入细尺度参考路径。 | default=None
- {GAP_MASK} | required=False | type=str | var_name=时间缺口掩膜 | hint=输入时间缺口掩膜。 | default=None
- {TARGET_GRID} | required=True | type=str | var_name=公里级目标网格 | hint=输入公里级网格规格。 | default=None

## 产出
- 任务范围和资料截止时间表
- 输入完整性预检报告
- 输入数据与版本清单

## 质量门禁 quality_gate
- 任务区域、时段、变量和输出目标无歧义
- 所有必需输入均存在且路径、版本和来源可追溯
- 气象强迫、流域边界和水文观测时空一致
- 粗网格土壤湿度、细尺度参考和缺口掩膜分别登记
- 缺测、重复和异常资料已记录且未擅自补造
- 近期观测、未来七天天气预报和参考蒸散实况分别登记

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-274bca3a
- it-4079c45f
- it-4234d454
- it-45a1aaf9
- it-52823eff
- it-621db62e
- it-822e7d5f
- it-a6e123ff
- it-c337d512
- it-c7c4588d
- it-cd3b0b74

## 复用场景
- E28
- E64
- E10
- E66
- E46
- E87
- E65
- E6
- E18
- E16
- E82
