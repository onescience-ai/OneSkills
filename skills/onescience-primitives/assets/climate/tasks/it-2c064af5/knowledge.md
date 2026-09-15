# 实例任务：污染气象资料及任务边界预检 @ E44

- domain: climate
- 骨架: tk-climate-04b7173e
- 场景: sc-055f5820 (E44)
- step_id: s01
- depend: []

## 场景研究主体
- E44
- 关联论文: A novel CMAQ-CNN hybrid model to forecast hourly surface-ozone concentrations 14 days in advance | doi:; IntelliO3-ts v1.0- a neural network approach to predict near-surface ozone concentrations in Germany | doi:; A neural network model for short term prediction of surface ozone at Pone | doi:

## 本实例步骤描述
界定“近地面臭氧小时级多时效预报”的任务范围并执行“污染气象资料及任务边界预检”，核验臭氧监测历史、气象预报、可选CMAQ场的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“近地面臭氧小时级多时效预报”，读取{AIR_QUALITY_DATA}、{METEOROLOGICAL_DATA}、{EMISSION_DATA}、{TARGET_REGION_TIME}、{DATA_CUTOFF_TIME}并完成污染气象资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {AIR_QUALITY_DATA} | required=True | type=str | var_name=污染观测资料 | hint=输入污染观测资料路径。 | default=None
- {METEOROLOGICAL_DATA} | required=True | type=str | var_name=气象驱动资料 | hint=输入气象驱动资料路径。 | default=None
- {EMISSION_DATA} | required=False | type=str | var_name=排放与活动资料 | hint=输入排放资料路径。 | default=None
- {TARGET_REGION_TIME} | required=True | type=str | var_name=目标区域时段 | hint=输入区域和起止时间。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 监测、气象和排放资料的可用时间边界明确

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
