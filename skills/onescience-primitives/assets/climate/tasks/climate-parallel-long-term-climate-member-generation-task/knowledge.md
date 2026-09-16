# 骨架任务：并行生成长期气候成员

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“并行生成长期气候成员”，完成从外部强迫、边界条件、随机种子和初始状态到长期气候集合、分布统计和极端重现期的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{ENSEMBLE_SIZE}、{OUTPUT_FREQUENCY}执行并行生成长期气候成员，将外部强迫、边界条件、随机种子和初始状态转换为长期气候集合、分布统计和极端重现期。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=20
- {OUTPUT_FREQUENCY} | required=True | type=str | var_name=输出频率 | hint=输入结果输出频率。 | default=None

## 产出
- 中间状态与运行日志
- 并行生成长期气候成员结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 核心计算未读取任务截止时间之后的数据
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯
- 长期积分无非物理漂移或未解释的数值突变

## 可调资源（edge:resource，仅真实存在）
- datasets/cesm2-large-ensemble
- datasets/large-ensemble-testbed
- models/crpsexp-loss-function-for-ensemble-forecasting
- models/ensemble-empirical-mode-decomposition-eemd
- models/ensemble-model-output-statistics-emos-post-processing

## 实例任务（本骨架在各场景的实例化）
- climate-parallel-long-term-climate-given-boundary-forcing-inst

## 复用场景
- E36
