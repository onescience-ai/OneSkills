# 骨架任务：源观测和参考资料及任务边界预检

- domain: climate
- 复用场景数: 6
- 实例任务数: 6

## 步骤描述（跨场景聚合去重）
- 界定“地面气象要素驱动的日总太阳辐射估算”的任务范围并执行“源观测和参考资料及任务边界预检”，核验站点日温度、湿度、风速及可选时间特征的来源、覆盖、有效时间和可用边界。
- 界定“多要素分析场驱动的天气锋面检测与矢量化”的任务范围并执行“源观测和参考资料及任务边界预检”，核验表面温湿压风分析场、人工锋面标签的来源、覆盖、有效时间和可用边界。
- 界定“天气雷达体扫驱动的实时定量降水估计”的任务范围并执行“源观测和参考资料及任务边界预检”，核验雷达多仰角反射率、雨量计观测、质量标识的来源、覆盖、有效时间和可用边界。
- 界定“激光雷达—探空融合的边界层高度反演”的任务范围并执行“源观测和参考资料及任务边界预检”，核验激光雷达后向散射剖面、探空、地面气象的来源、覆盖、有效时间和可用边界。
- 界定“雷达—卫星—雨量计多模态同期定量降水估计”的任务范围并执行“源观测和参考资料及任务边界预检”，核验雷达观测、卫星云图、雨量计及地理特征的来源、覆盖、有效时间和可用边界。
- 界定“静止气象卫星驱动的对流初生识别”的任务范围并执行“源观测和参考资料及任务边界预检”，核验多时次多光谱卫星云图、对流初生标签的来源、覆盖、有效时间和可用边界。

## 执行 prompt（跨场景聚合去重）
- 面向“地面气象要素驱动的日总太阳辐射估算”，读取{SOURCE_OBSERVATIONS}、{AUXILIARY_DATA}、{TARGET_REGION_TIME}、{TARGET_VARIABLE}、{DATA_CUTOFF_TIME}并完成源观测和参考资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“多要素分析场驱动的天气锋面检测与矢量化”，读取{SOURCE_OBSERVATIONS}、{AUXILIARY_DATA}、{TARGET_REGION_TIME}、{TARGET_VARIABLE}、{DATA_CUTOFF_TIME}并完成源观测和参考资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“天气雷达体扫驱动的实时定量降水估计”，读取{RADAR_VOLUME}、{RAIN_GAUGE_DATA}、{RADAR_SCAN_TIME}、{TARGET_REGION}、{DATA_CUTOFF_TIME}并完成源观测和参考资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“激光雷达—探空融合的边界层高度反演”，读取{SOURCE_OBSERVATIONS}、{AUXILIARY_DATA}、{TARGET_REGION_TIME}、{TARGET_VARIABLE}、{DATA_CUTOFF_TIME}并完成源观测和参考资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“雷达—卫星—雨量计多模态同期定量降水估计”，读取{RADAR_VOLUME}、{SATELLITE_OBSERVATIONS}、{RAIN_GAUGE_DATA}、{TARGET_PERIOD}、{DATA_CUTOFF_TIME}并完成源观测和参考资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“静止气象卫星驱动的对流初生识别”，读取{SOURCE_OBSERVATIONS}、{AUXILIARY_DATA}、{TARGET_REGION_TIME}、{TARGET_VARIABLE}、{DATA_CUTOFF_TIME}并完成源观测和参考资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 输入槽（var/hint/default）
- {SOURCE_OBSERVATIONS} | required=True | type=str | var_name=源观测资料 | hint=输入源观测资料路径。 | default=None
- {AUXILIARY_DATA} | required=False | type=str | var_name=辅助资料 | hint=输入辅助资料路径。 | default=None
- {TARGET_REGION_TIME} | required=True | type=str | var_name=目标区域时段 | hint=输入区域和观测时段。 | default=None
- {TARGET_VARIABLE} | required=True | type=str | var_name=目标诊断量 | hint=输入目标诊断量。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None
- {RADAR_VOLUME} | required=True | type=str | var_name=雷达体扫资料 | hint=输入雷达体扫资料路径。 | default=None
- {RAIN_GAUGE_DATA} | required=True | type=str | var_name=雨量计资料 | hint=输入雨量计资料路径。 | default=None
- {RADAR_SCAN_TIME} | required=True | type=str | var_name=雷达扫描时刻 | hint=输入雷达扫描时刻。 | default=None
- {TARGET_REGION} | required=True | type=str | var_name=目标区域 | hint=输入目标区域范围。 | default=None
- {SATELLITE_OBSERVATIONS} | required=True | type=str | var_name=卫星观测资料 | hint=输入卫星观测资料路径。 | default=None
- {TARGET_PERIOD} | required=True | type=str | var_name=目标估计时段 | hint=输入目标估计时段。 | default=None

## 产出
- 任务范围和资料截止时间表
- 输入完整性预检报告
- 输入数据与版本清单

## 质量门禁 quality_gate
- 任务区域、时段、变量和输出目标无歧义
- 所有必需输入均存在且路径、版本和来源可追溯
- 源观测与辅助资料的有效时间和来源可追溯
- 缺测、重复和异常资料已记录且未擅自补造
- 输入限定为雷达体扫和雨量计校准资料且不要求卫星资料
- 雷达、卫星和雨量计三种模态均为必需输入

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-058e4023
- it-5a9948be
- it-6ed02fbe
- it-d320bee9
- it-f224351a
- it-fe2c050d

## 复用场景
- E63
- E97
- E34
- E61
- E21
- E80
