# 骨架任务：预报实况样本及任务边界预检

- domain: climate
- 复用场景数: 2
- 实例任务数: 2

## 步骤描述（跨场景聚合去重）
- 界定“站点温度集合预报概率校准”的任务范围并执行“预报实况样本及任务边界预检”，核验原始集合成员、辅助预报量、站点历史观测的来源、覆盖、有效时间和可用边界。
- 界定“集合数值预报的日内至日前太阳辐照度概率后处理”的任务范围并执行“预报实况样本及任务边界预检”，核验集合NWP辐射、历史观测与误差的来源、覆盖、有效时间和可用边界。

## 执行 prompt（跨场景聚合去重）
- 面向“站点温度集合预报概率校准”，读取{RAW_ENSEMBLE_FORECAST}、{STATION_OBSERVATIONS}、{STATION_METADATA}、{CALIBRATION_PERIOD}、{DATA_CUTOFF_TIME}并完成预报实况样本及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“集合数值预报的日内至日前太阳辐照度概率后处理”，读取{RAW_IRRADIANCE_ENSEMBLE}、{IRRADIANCE_OBSERVATIONS}、{SITE_METADATA}、{CALIBRATION_PERIOD}、{DATA_CUTOFF_TIME}并完成预报实况样本及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 输入槽（var/hint/default）
- {RAW_ENSEMBLE_FORECAST} | required=True | type=str | var_name=原始温度集合 | hint=输入原始温度集合路径。 | default=None
- {STATION_OBSERVATIONS} | required=True | type=str | var_name=同期站点实况 | hint=输入同期站点实况路径。 | default=None
- {STATION_METADATA} | required=True | type=str | var_name=站点元数据 | hint=输入站点元数据路径。 | default=None
- {CALIBRATION_PERIOD} | required=True | type=str | var_name=校准时段 | hint=输入校准起止时间。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None
- {RAW_IRRADIANCE_ENSEMBLE} | required=True | type=str | var_name=原始辐照度集合 | hint=输入辐照度集合路径。 | default=None
- {IRRADIANCE_OBSERVATIONS} | required=True | type=str | var_name=同期辐照度实况 | hint=输入辐照度实况路径。 | default=None
- {SITE_METADATA} | required=True | type=str | var_name=站点元数据 | hint=输入站点元数据路径。 | default=None

## 产出
- 任务范围和资料截止时间表
- 输入完整性预检报告
- 输入数据与版本清单

## 质量门禁 quality_gate
- 任务区域、时段、变量和输出目标无歧义
- 原始集合成员与站点实况按起报和有效时间一一配对
- 原始预报与同期实况按起报和有效时间准确配对
- 所有必需输入均存在且路径、版本和来源可追溯
- 缺测、重复和异常资料已记录且未擅自补造
- 输入是辐照度集合与同期辐照度实况而非功率数据

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-06f9e873
- it-e878a70c

## 复用场景
- E14
- E24
