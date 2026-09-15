# 实例任务：航次资料和航行约束及任务边界预检 @ E100

- domain: climate
- 骨架: tk-climate-88579ae4
- 场景: sc-975001b3 (E100)
- step_id: s01
- depend: []

## 场景研究主体
- E100
- 关联论文: A novel, data-driven heuristic framework for vessel weather routing | doi:

## 本实例步骤描述
界定“海洋天气与航行约束驱动的船舶气象航线优化”的任务范围并执行“航次资料和航行约束及任务边界预检”，核验风浪流预报、船舶性能、起终点与约束的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“海洋天气与航行约束驱动的船舶气象航线优化”，读取{WEATHER_FORECAST}、{VESSEL_PERFORMANCE}、{VOYAGE_ENDPOINTS}、{NAVIGATION_CONSTRAINTS}、{FORECAST_ISSUE_TIME}并完成航次资料和航行约束及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {WEATHER_FORECAST} | required=True | type=str | var_name=海洋天气预报 | hint=输入风浪流预报路径。 | default=None
- {VESSEL_PERFORMANCE} | required=True | type=str | var_name=船舶性能参数 | hint=输入船舶性能参数。 | default=None
- {VOYAGE_ENDPOINTS} | required=True | type=str | var_name=航次起终点 | hint=输入航次起点和终点。 | default=None
- {NAVIGATION_CONSTRAINTS} | required=True | type=str | var_name=航行约束 | hint=输入禁航和安全约束。 | default=None
- {FORECAST_ISSUE_TIME} | required=True | type=str | var_name=预报签发时间 | hint=输入预报签发时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 天气预报、船舶参数和航行约束均对应同一航次

## 可调资源（edge:resource，仅真实存在）
- datasets/CMEMS

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
