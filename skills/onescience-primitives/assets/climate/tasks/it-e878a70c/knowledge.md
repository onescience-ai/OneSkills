# 实例任务：预报实况样本及任务边界预检 @ E14

- domain: climate
- 骨架: tk-climate-928305e3
- 场景: sc-e61aa5dd (E14)
- step_id: s01
- depend: []

## 场景研究主体
- E14
- 关联论文: Neural Networks for Postprocessing Ensemble Weather Forecasts | doi:; From research to applications – examples of operational ensemble post-processing in France using machine learning | doi:; A Composite-Loss Graph Neural Network for the Multivariate Post-Processing of Ensemble Weather Forecasts | doi:; Ensemble weather forecast post-processing with a flexible probabilistic neural network approach | doi:

## 本实例步骤描述
界定“站点温度集合预报概率校准”的任务范围并执行“预报实况样本及任务边界预检”，核验原始集合成员、辅助预报量、站点历史观测的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“站点温度集合预报概率校准”，读取{RAW_ENSEMBLE_FORECAST}、{STATION_OBSERVATIONS}、{STATION_METADATA}、{CALIBRATION_PERIOD}、{DATA_CUTOFF_TIME}并完成预报实况样本及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {RAW_ENSEMBLE_FORECAST} | required=True | type=str | var_name=原始温度集合 | hint=输入原始温度集合路径。 | default=None
- {STATION_OBSERVATIONS} | required=True | type=str | var_name=同期站点实况 | hint=输入同期站点实况路径。 | default=None
- {STATION_METADATA} | required=True | type=str | var_name=站点元数据 | hint=输入站点元数据路径。 | default=None
- {CALIBRATION_PERIOD} | required=True | type=str | var_name=校准时段 | hint=输入校准起止时间。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 原始预报与同期实况按起报和有效时间准确配对
- 原始集合成员与站点实况按起报和有效时间一一配对

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
