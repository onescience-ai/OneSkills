# 骨架任务：在给定强迫下多年自由积分

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“在给定强迫下多年自由积分”，完成从海温、太阳辐射、地形及初始大气状态到多年全球大气场、降水和能量水分通量的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{ENSEMBLE_SIZE}、{OUTPUT_FREQUENCY}执行在给定强迫下多年自由积分，将海温、太阳辐射、地形及初始大气状态转换为多年全球大气场、降水和能量水分通量。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=1
- {OUTPUT_FREQUENCY} | required=True | type=str | var_name=输出频率 | hint=输入结果输出频率。 | default=None

## 产出
- 中间状态与运行日志
- 在给定强迫下多年自由积分结果
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
- climate-multiyear-free-integration-given-boundary-forcing-inst

## 复用场景
- E57
