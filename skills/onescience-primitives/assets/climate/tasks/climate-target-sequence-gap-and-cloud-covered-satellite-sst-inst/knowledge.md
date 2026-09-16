# 实例任务：目标序列及缺口及任务边界预检 @ E69

- domain: climate
- 骨架: climate-target-sequence-gap-and-boundary-precheck-task
- 场景: climate-cloud-covered-satellite-sst-reconstruction-pixel-uncertainty-scenario (E69)
- step_id: s01
- depend: []

## 场景研究主体
- E69
- 关联论文: DINCAE 1.0: a convolutional neural network with error estimates to reconstruct sea surface temperature satellite observations | doi:

## 本实例步骤描述
界定“云遮卫星海表温度缺测重建与像元不确定性估计”的任务范围并执行“目标序列及缺口及任务边界预检”，核验带云缺测的卫星海温序列、质量标志和时空坐标的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“云遮卫星海表温度缺测重建与像元不确定性估计”，读取{INCOMPLETE_TARGET_DATA}、{AUXILIARY_DATA}、{GAP_MASK}、{TARGET_REGION_TIME}、{DATA_CUTOFF_TIME}并完成目标序列及缺口及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {INCOMPLETE_TARGET_DATA} | required=True | type=str | var_name=不完整目标序列 | hint=输入含缺口目标资料路径。 | default=None
- {AUXILIARY_DATA} | required=True | type=str | var_name=辅助驱动资料 | hint=输入辅助驱动资料路径。 | default=None
- {GAP_MASK} | required=True | type=str | var_name=时间空间缺口 | hint=输入待重建缺口掩膜。 | default=None
- {TARGET_REGION_TIME} | required=True | type=str | var_name=目标区域时段 | hint=输入区域和重建时段。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 目标序列、辅助资料和真实缺口掩膜可追溯

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
