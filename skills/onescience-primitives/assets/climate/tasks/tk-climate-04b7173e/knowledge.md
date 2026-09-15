# 骨架任务：污染气象资料及任务边界预检

- domain: climate
- 复用场景数: 4
- 实例任务数: 4

## 步骤描述（跨场景聚合去重）
- 界定“NWP与排放驱动的区域气溶胶0—72小时格点预报”的任务范围并执行“污染气象资料及任务边界预检”，核验污染站历史、NWP气象场、排放清单的来源、覆盖、有效时间和可用边界。
- 界定“城市站点PM2.5短期浓度预报”的任务范围并执行“污染气象资料及任务边界预检”，核验目标与邻站PM2.5历史、站点位置、气象预报的来源、覆盖、有效时间和可用边界。
- 界定“稀疏监测站驱动的城市污染浓度网格重建与短时预测”的任务范围并执行“污染气象资料及任务边界预检”，核验稀疏污染站序列、气象、道路和空间位置的来源、覆盖、有效时间和可用边界。
- 界定“近地面臭氧小时级多时效预报”的任务范围并执行“污染气象资料及任务边界预检”，核验臭氧监测历史、气象预报、可选CMAQ场的来源、覆盖、有效时间和可用边界。

## 执行 prompt（跨场景聚合去重）
- 面向“NWP与排放驱动的区域气溶胶0—72小时格点预报”，读取{AIR_QUALITY_DATA}、{METEOROLOGICAL_DATA}、{EMISSION_DATA}、{TARGET_REGION_TIME}、{DATA_CUTOFF_TIME}并完成污染气象资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“城市站点PM2.5短期浓度预报”，读取{AIR_QUALITY_DATA}、{METEOROLOGICAL_DATA}、{EMISSION_DATA}、{TARGET_REGION_TIME}、{DATA_CUTOFF_TIME}并完成污染气象资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“稀疏监测站驱动的城市污染浓度网格重建与短时预测”，读取{AIR_QUALITY_DATA}、{METEOROLOGICAL_DATA}、{EMISSION_DATA}、{TARGET_REGION_TIME}、{DATA_CUTOFF_TIME}并完成污染气象资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“近地面臭氧小时级多时效预报”，读取{AIR_QUALITY_DATA}、{METEOROLOGICAL_DATA}、{EMISSION_DATA}、{TARGET_REGION_TIME}、{DATA_CUTOFF_TIME}并完成污染气象资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 输入槽（var/hint/default）
- {AIR_QUALITY_DATA} | required=True | type=str | var_name=污染观测资料 | hint=输入污染观测资料路径。 | default=None
- {METEOROLOGICAL_DATA} | required=True | type=str | var_name=气象驱动资料 | hint=输入气象驱动资料路径。 | default=None
- {EMISSION_DATA} | required=False | type=str | var_name=排放与活动资料 | hint=输入排放资料路径。 | default=None
- {TARGET_REGION_TIME} | required=True | type=str | var_name=目标区域时段 | hint=输入区域和起止时间。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 产出
- 任务范围和资料截止时间表
- 输入完整性预检报告
- 输入数据与版本清单

## 质量门禁 quality_gate
- 任务区域、时段、变量和输出目标无歧义
- 所有必需输入均存在且路径、版本和来源可追溯
- 监测、气象和排放资料的可用时间边界明确
- 缺测、重复和异常资料已记录且未擅自补造

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-2c064af5
- it-51de693e
- it-9f542931
- it-f6dd477e

## 复用场景
- E99
- E42
- E60
- E44
