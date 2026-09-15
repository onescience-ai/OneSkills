# 实例任务：海洋状态和强迫资料及任务边界预检 @ E5

- domain: climate
- 骨架: tk-climate-2239ace0
- 场景: sc-9a86054e (E5)
- step_id: s01
- depend: []

## 场景研究主体
- E5
- 关联论文: XiHe: A Data-Driven Model for Global Ocean Eddy-Resolving Forecasting | doi:; GLONET_ Mercator's end-to-end neural Global Ocean forecasting system | doi:; Forecasting the eddying ocean with a deep neural network | doi:

## 本实例步骤描述
界定“全球涡旋分辨率三维海洋1—10日预报”的任务范围并执行“海洋状态和强迫资料及任务边界预检”，核验三维海洋分析场、海表温度和海面风的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“全球涡旋分辨率三维海洋1—10日预报”，读取{OCEAN_STATE}、{SURFACE_FORCING}、{STATIC_OCEAN_DATA}、{START_TIME}、{TARGET_HORIZON}、{DATA_CUTOFF_TIME}并完成海洋状态和强迫资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {OCEAN_STATE} | required=True | type=str | var_name=海洋状态资料 | hint=输入海洋状态资料路径。 | default=None
- {SURFACE_FORCING} | required=False | type=str | var_name=海表强迫资料 | hint=输入海表强迫资料路径。 | default=None
- {STATIC_OCEAN_DATA} | required=False | type=str | var_name=静态海洋资料 | hint=输入地形掩膜等资料。 | default=None
- {START_TIME} | required=True | type=str | var_name=起始时刻 | hint=输入处理起始时刻。 | default=None
- {TARGET_HORIZON} | required=True | type=str | var_name=目标时效 | hint=输入目标时效或时段。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 海陆掩膜、岸线、垂向层和海洋单位一致

## 可调资源（edge:resource，仅真实存在）
- datasets/CMEMS

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
