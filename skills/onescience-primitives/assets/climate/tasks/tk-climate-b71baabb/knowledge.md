# 骨架任务：起报资料及任务边界预检

- domain: climate
- 复用场景数: 12
- 实例任务数: 12

## 步骤描述（跨场景聚合去重）
- 界定“ENSO指数6—24个月概率预测”的任务范围并执行“起报资料及任务边界预检”，核验过去海温与海洋—大气状态序列的来源、覆盖、有效时间和可用边界。
- 界定“MJO与季节内振荡10—30天位相预报”的任务范围并执行“起报资料及任务边界预检”，核验热带风场、温度和对流异常历史的来源、覆盖、有效时间和可用边界。
- 界定“全球10—42天次季节多变量异常预报”的任务范围并执行“起报资料及任务边界预检”，核验全球大气初态、海陆边界状态、目标周的来源、覆盖、有效时间和可用边界。
- 界定“全球1—15天集合概率天气预报”的任务范围并执行“起报资料及任务边界预检”，核验全球分析场、随机扰动配置、目标时效的来源、覆盖、有效时间和可用边界。
- 界定“全球1—6个月季节集合天气—气候预测”的任务范围并执行“起报资料及任务边界预检”，核验多个季节起报初态、边界状态、气候基准的来源、覆盖、有效时间和可用边界。
- 界定“全球航空危险云微物理要素1—7天预报”的任务范围并执行“起报资料及任务边界预检”，核验全球大气初态、云微物理状态、目标时效的来源、覆盖、有效时间和可用边界。
- 界定“区域短中期极端风速格点预报”的任务范围并执行“起报资料及任务边界预检”，核验历史区域风场、环境气象场、强风事件标签的来源、覆盖、有效时间和可用边界。
- 界定“卫星—天气驱动地表反射率与植被绿度短期预报”的任务范围并执行“起报资料及任务边界预检”，核验历史多光谱影像、天气驱动和静态地形的来源、覆盖、有效时间和可用边界。
- 界定“印度洋偶极子多季节指数预测”的任务范围并执行“起报资料及任务边界预检”，核验印度洋—太平洋海温、热含量和风场的来源、覆盖、有效时间和可用边界。
- 界定“多站点温湿风24—72小时联合时序预报”的任务范围并执行“起报资料及任务边界预检”，核验多站历史温湿风、站点位置与时间特征的来源、覆盖、有效时间和可用边界。
- 界定“已识别热带气旋12—72小时强度预报”的任务范围并执行“起报资料及任务边界预检”，核验气旋强度历史、海温、环境大气场的来源、覆盖、有效时间和可用边界。
- 界定“已识别热带气旋24—120小时路径预报”的任务范围并执行“起报资料及任务边界预检”，核验气旋历史位置、强度元数据、风暴中心环境场的来源、覆盖、有效时间和可用边界。

## 执行 prompt（跨场景聚合去重）
- 面向“ENSO指数6—24个月概率预测”，读取{INITIAL_DATA}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{TARGET_VARIABLES}、{DATA_CUTOFF_TIME}并完成起报资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“MJO与季节内振荡10—30天位相预报”，读取{INITIAL_DATA}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{TARGET_VARIABLES}、{DATA_CUTOFF_TIME}并完成起报资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“全球10—42天次季节多变量异常预报”，读取{INITIAL_DATA}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{TARGET_VARIABLES}、{DATA_CUTOFF_TIME}并完成起报资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“全球1—15天集合概率天气预报”，读取{INITIAL_DATA}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{TARGET_VARIABLES}、{DATA_CUTOFF_TIME}并完成起报资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“全球1—6个月季节集合天气—气候预测”，读取{INITIAL_COUPLED_STATE}、{FORECAST_START_DATE}、{LEAD_MONTHS}、{TARGET_VARIABLES}、{DATA_CUTOFF_TIME}并完成起报资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“全球航空危险云微物理要素1—7天预报”，读取{INITIAL_DATA}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{TARGET_VARIABLES}、{DATA_CUTOFF_TIME}并完成起报资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“区域短中期极端风速格点预报”，读取{INITIAL_DATA}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{TARGET_VARIABLES}、{DATA_CUTOFF_TIME}并完成起报资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“卫星—天气驱动地表反射率与植被绿度短期预报”，读取{SURFACE_HISTORY}、{WEATHER_DRIVERS}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{DATA_CUTOFF_TIME}并完成起报资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“印度洋偶极子多季节指数预测”，读取{INITIAL_DATA}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{TARGET_VARIABLES}、{DATA_CUTOFF_TIME}并完成起报资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“多站点温湿风24—72小时联合时序预报”，读取{INITIAL_DATA}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{TARGET_VARIABLES}、{DATA_CUTOFF_TIME}并完成起报资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“已识别热带气旋12—72小时强度预报”，读取{INITIAL_DATA}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{TARGET_VARIABLES}、{DATA_CUTOFF_TIME}并完成起报资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“已识别热带气旋24—120小时路径预报”，读取{INITIAL_DATA}、{FORECAST_START_TIME}、{FORECAST_HORIZON}、{TARGET_VARIABLES}、{DATA_CUTOFF_TIME}并完成起报资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 输入槽（var/hint/default）
- {INITIAL_DATA} | required=True | type=str | var_name=历史与初始数据 | hint=输入历史和初始数据路径。 | default=None
- {FORECAST_START_TIME} | required=True | type=str | var_name=起报时间 | hint=输入UTC起报时间。 | default=None
- {FORECAST_HORIZON} | required=True | type=str | var_name=预报时效 | hint=输入目标预报时效。 | default=None
- {TARGET_VARIABLES} | required=True | type=str | var_name=目标变量 | hint=输入目标变量清单。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None
- {INITIAL_COUPLED_STATE} | required=True | type=str | var_name=大气海洋初态 | hint=输入大气海洋初态路径。 | default=None
- {FORECAST_START_DATE} | required=True | type=str | var_name=起报日期 | hint=输入UTC起报日期。 | default=None
- {LEAD_MONTHS} | required=True | type=str | var_name=月预见期 | hint=输入1至6月预见期。 | default=None
- {SURFACE_HISTORY} | required=True | type=str | var_name=反射率绿度历史 | hint=输入反射率绿度序列。 | default=None
- {WEATHER_DRIVERS} | required=True | type=str | var_name=天气驱动资料 | hint=输入天气驱动资料路径。 | default=None

## 产出
- 任务范围和资料截止时间表
- 输入完整性预检报告
- 输入数据与版本清单

## 质量门禁 quality_gate
- 任务区域、时段、变量和输出目标无歧义
- 初始大气海洋状态和起报日对应同一业务时刻
- 卫星历史序列和天气驱动均不晚于起报时间
- 所有动态输入的有效时间均不晚于资料截止时间
- 所有必需输入均存在且路径、版本和来源可追溯
- 缺测、重复和异常资料已记录且未擅自补造

## 可调资源（edge:resource，仅真实存在）
- datasets/CMEMS

## 实例任务（本骨架在各场景的实例化）
- it-06ba9f80
- it-0da87c62
- it-0faec149
- it-1e4abea0
- it-2ec4de88
- it-3c2b620c
- it-5b300d7a
- it-636c3673
- it-912e6edb
- it-ae4b5712
- it-b74420ea
- it-d8b6003c

## 复用场景
- E9
- E19
- E7
- E3
- E47
- E88
- E95
- E39
- E78
- E41
- E50
- E30
