# 骨架任务：重建时间缺口和历史序列

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“重建时间缺口和历史序列”，完成从GRACE观测、气候驱动、陆面状态到连续陆地水储量异常及不确定性的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RECONSTRUCTION_CONFIG}、{OBSERVED_VALUE_POLICY}、{UNCERTAINTY_CONFIG}执行重建时间缺口和历史序列，将GRACE观测、气候驱动、陆面状态转换为连续陆地水储量异常及不确定性。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RECONSTRUCTION_CONFIG} | required=True | type=str | var_name=水储量重建配置 | hint=输入水储量重建配置。 | default=None
- {OBSERVED_VALUE_POLICY} | required=True | type=str | var_name=观测值保持规则 | hint=输入观测值保持规则。 | default=None
- {UNCERTAINTY_CONFIG} | required=False | type=str | var_name=不确定性配置 | hint=输入不确定性估计配置。 | default=None

## 产出
- 中间状态与运行日志
- 资源和退出状态记录
- 重建时间缺口和历史序列结果

## 质量门禁 quality_gate
- 有观测月份保持原值且仅填补指定缺口
- 核心计算未读取任务截止时间之后的数据
- 目标区域和时段内结果完整且无重复或错位
- 观测位置保持原值且缺口结果无拼接突变
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- datasets/gtws-mlrec-machine-learning-based-global-terrestrial-water-storage-anomaly-reconstruction-dataset-and-workflow
- models/swe-reconstruction-using-energy-balance-model

## 实例任务（本骨架在各场景的实例化）
- climate-reconstruct-time-gap-historica-grace-gap-terrestrial-water-inst

## 复用场景
- E49
