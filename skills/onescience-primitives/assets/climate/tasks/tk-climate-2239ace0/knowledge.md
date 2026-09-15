# 骨架任务：海洋状态和强迫资料及任务边界预检

- domain: climate
- 复用场景数: 6
- 实例任务数: 6

## 步骤描述（跨场景聚合去重）
- 界定“全球海表温度次季节—季节异常预报”的任务范围并执行“海洋状态和强迫资料及任务边界预检”，核验历史海温、海洋状态和遥相关前兆的来源、覆盖、有效时间和可用边界。
- 界定“全球涡旋分辨率三维海洋1—10日预报”的任务范围并执行“海洋状态和强迫资料及任务边界预检”，核验三维海洋分析场、海表温度和海面风的来源、覆盖、有效时间和可用边界。
- 界定“北极海冰1—6月概率预报”的任务范围并执行“海洋状态和强迫资料及任务边界预检”，核验历史海冰浓度、海气变量和季节信息的来源、覆盖、有效时间和可用边界。
- 界定“区域海表温度1—7日逐日预报”的任务范围并执行“海洋状态和强迫资料及任务边界预检”，核验历史日海表温度及可选海气强迫的来源、覆盖、有效时间和可用边界。
- 界定“海岸浴深重建与形态演变预报”的任务范围并执行“海洋状态和强迫资料及任务边界预检”，核验历史浴深测量、水动力和泥沙强迫的来源、覆盖、有效时间和可用边界。
- 界定“近岸有效波高—周期—波向短期预报”的任务范围并执行“海洋状态和强迫资料及任务边界预检”，核验初始海浪场、预报风场、边界波谱和水深的来源、覆盖、有效时间和可用边界。

## 执行 prompt（跨场景聚合去重）
- 面向“全球海表温度次季节—季节异常预报”，读取{OCEAN_STATE}、{SURFACE_FORCING}、{STATIC_OCEAN_DATA}、{START_TIME}、{TARGET_HORIZON}、{DATA_CUTOFF_TIME}并完成海洋状态和强迫资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“全球涡旋分辨率三维海洋1—10日预报”，读取{OCEAN_STATE}、{SURFACE_FORCING}、{STATIC_OCEAN_DATA}、{START_TIME}、{TARGET_HORIZON}、{DATA_CUTOFF_TIME}并完成海洋状态和强迫资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“北极海冰1—6月概率预报”，读取{OCEAN_STATE}、{SURFACE_FORCING}、{STATIC_OCEAN_DATA}、{START_TIME}、{TARGET_HORIZON}、{DATA_CUTOFF_TIME}并完成海洋状态和强迫资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“区域海表温度1—7日逐日预报”，读取{OCEAN_STATE}、{SURFACE_FORCING}、{STATIC_OCEAN_DATA}、{START_TIME}、{TARGET_HORIZON}、{DATA_CUTOFF_TIME}并完成海洋状态和强迫资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“海岸浴深重建与形态演变预报”，读取{OCEAN_STATE}、{SURFACE_FORCING}、{STATIC_OCEAN_DATA}、{START_TIME}、{TARGET_HORIZON}、{DATA_CUTOFF_TIME}并完成海洋状态和强迫资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“近岸有效波高—周期—波向短期预报”，读取{OCEAN_STATE}、{SURFACE_FORCING}、{STATIC_OCEAN_DATA}、{START_TIME}、{TARGET_HORIZON}、{DATA_CUTOFF_TIME}并完成海洋状态和强迫资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 输入槽（var/hint/default）
- {OCEAN_STATE} | required=True | type=str | var_name=海洋状态资料 | hint=输入海洋状态资料路径。 | default=None
- {SURFACE_FORCING} | required=False | type=str | var_name=海表强迫资料 | hint=输入海表强迫资料路径。 | default=None
- {STATIC_OCEAN_DATA} | required=False | type=str | var_name=静态海洋资料 | hint=输入地形掩膜等资料。 | default=None
- {START_TIME} | required=True | type=str | var_name=起始时刻 | hint=输入处理起始时刻。 | default=None
- {TARGET_HORIZON} | required=True | type=str | var_name=目标时效 | hint=输入目标时效或时段。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 产出
- 任务范围和资料截止时间表
- 输入完整性预检报告
- 输入数据与版本清单

## 质量门禁 quality_gate
- 任务区域、时段、变量和输出目标无歧义
- 所有必需输入均存在且路径、版本和来源可追溯
- 海陆掩膜、岸线、垂向层和海洋单位一致
- 缺测、重复和异常资料已记录且未擅自补造

## 可调资源（edge:resource，仅真实存在）
- datasets/CMEMS

## 实例任务（本骨架在各场景的实例化）
- it-064d3238
- it-8b91a4df
- it-d7fbe703
- it-df275048
- it-df8eb792
- it-ffe50890

## 复用场景
- E29
- E5
- E17
- E27
- E74
- E31
