# 骨架任务：航次资料和航行约束及任务边界预检

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 界定“海洋天气与航行约束驱动的船舶气象航线优化”的任务范围并执行“航次资料和航行约束及任务边界预检”，核验风浪流预报、船舶性能、起终点与约束的来源、覆盖、有效时间和可用边界。

## 执行 prompt（跨场景聚合去重）
- 面向“海洋天气与航行约束驱动的船舶气象航线优化”，读取{WEATHER_FORECAST}、{VESSEL_PERFORMANCE}、{VOYAGE_ENDPOINTS}、{NAVIGATION_CONSTRAINTS}、{FORECAST_ISSUE_TIME}并完成航次资料和航行约束及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 输入槽（var/hint/default）
- {WEATHER_FORECAST} | required=True | type=str | var_name=海洋天气预报 | hint=输入风浪流预报路径。 | default=None
- {VESSEL_PERFORMANCE} | required=True | type=str | var_name=船舶性能参数 | hint=输入船舶性能参数。 | default=None
- {VOYAGE_ENDPOINTS} | required=True | type=str | var_name=航次起终点 | hint=输入航次起点和终点。 | default=None
- {NAVIGATION_CONSTRAINTS} | required=True | type=str | var_name=航行约束 | hint=输入禁航和安全约束。 | default=None
- {FORECAST_ISSUE_TIME} | required=True | type=str | var_name=预报签发时间 | hint=输入预报签发时间。 | default=None

## 产出
- 任务范围和资料截止时间表
- 输入完整性预检报告
- 输入数据与版本清单

## 质量门禁 quality_gate
- 任务区域、时段、变量和输出目标无歧义
- 天气预报、船舶参数和航行约束均对应同一航次
- 所有必需输入均存在且路径、版本和来源可追溯
- 缺测、重复和异常资料已记录且未擅自补造

## 可调资源（edge:resource，仅真实存在）
- datasets/CMEMS

## 实例任务（本骨架在各场景的实例化）
- it-6ef79863

## 复用场景
- E100
