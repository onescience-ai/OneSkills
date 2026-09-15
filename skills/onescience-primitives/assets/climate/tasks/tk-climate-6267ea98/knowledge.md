# 骨架任务：目标序列及缺口及任务边界预检

- domain: climate
- 复用场景数: 4
- 实例任务数: 4

## 步骤描述（跨场景聚合去重）
- 界定“AVHRR—MODIS连续NDVI历史序列融合重建”的任务范围并执行“目标序列及缺口及任务边界预检”，核验重叠期AVHRR与MODIS NDVI、质量标志和时空特征的来源、覆盖、有效时间和可用边界。
- 界定“GRACE缺测期全球陆地水储量异常重建”的任务范围并执行“目标序列及缺口及任务边界预检”，核验GRACE观测、气候驱动、陆面状态的来源、覆盖、有效时间和可用边界。
- 界定“云遮卫星海表温度缺测重建与像元不确定性估计”的任务范围并执行“目标序列及缺口及任务边界预检”，核验带云缺测的卫星海温序列、质量标志和时空坐标的来源、覆盖、有效时间和可用边界。
- 界定“全球海洋pCO2稀疏观测时空扩展”的任务范围并执行“目标序列及缺口及任务边界预检”，核验稀疏海气pCO2观测、海温、盐度和生物地球化学辅助场的来源、覆盖、有效时间和可用边界。

## 执行 prompt（跨场景聚合去重）
- 面向“AVHRR—MODIS连续NDVI历史序列融合重建”，读取{INCOMPLETE_TARGET_DATA}、{AUXILIARY_DATA}、{GAP_MASK}、{TARGET_REGION_TIME}、{DATA_CUTOFF_TIME}并完成目标序列及缺口及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“GRACE缺测期全球陆地水储量异常重建”，读取{GRACE_TWSA_SERIES}、{CLIMATE_LAND_DRIVERS}、{GAP_MASK}、{REFERENCE_PERIOD}、{TARGET_GRID}并完成目标序列及缺口及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“云遮卫星海表温度缺测重建与像元不确定性估计”，读取{INCOMPLETE_TARGET_DATA}、{AUXILIARY_DATA}、{GAP_MASK}、{TARGET_REGION_TIME}、{DATA_CUTOFF_TIME}并完成目标序列及缺口及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“全球海洋pCO2稀疏观测时空扩展”，读取{INCOMPLETE_TARGET_DATA}、{AUXILIARY_DATA}、{GAP_MASK}、{TARGET_REGION_TIME}、{DATA_CUTOFF_TIME}并完成目标序列及缺口及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 输入槽（var/hint/default）
- {INCOMPLETE_TARGET_DATA} | required=True | type=str | var_name=不完整目标序列 | hint=输入含缺口目标资料路径。 | default=None
- {AUXILIARY_DATA} | required=True | type=str | var_name=辅助驱动资料 | hint=输入辅助驱动资料路径。 | default=None
- {GAP_MASK} | required=True | type=str | var_name=时间空间缺口 | hint=输入待重建缺口掩膜。 | default=None
- {TARGET_REGION_TIME} | required=True | type=str | var_name=目标区域时段 | hint=输入区域和重建时段。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None
- {GRACE_TWSA_SERIES} | required=True | type=str | var_name=GRACE水储量序列 | hint=输入GRACE水储量路径。 | default=None
- {CLIMATE_LAND_DRIVERS} | required=True | type=str | var_name=气候陆面驱动 | hint=输入气候陆面资料路径。 | default=None
- {REFERENCE_PERIOD} | required=True | type=str | var_name=异常基准期 | hint=输入异常基准时段。 | default=None
- {TARGET_GRID} | required=True | type=str | var_name=目标网格 | hint=输入目标网格规格。 | default=None

## 产出
- 任务范围和资料截止时间表
- 输入完整性预检报告
- 输入数据与版本清单

## 质量门禁 quality_gate
- GRACE水储量序列、异常基准期和真实缺口明确
- 任务区域、时段、变量和输出目标无歧义
- 所有必需输入均存在且路径、版本和来源可追溯
- 目标序列、辅助资料和真实缺口掩膜可追溯
- 缺测、重复和异常资料已记录且未擅自补造

## 可调资源（edge:resource，仅真实存在）
- datasets/CMEMS

## 实例任务（本骨架在各场景的实例化）
- it-2da670bf
- it-a2ef7c5c
- it-b45c3ffd
- it-ceaa1c8c

## 复用场景
- E91
- E49
- E69
- E13
