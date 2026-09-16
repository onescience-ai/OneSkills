# 实例任务：输出校准后的温度分布 @ E14

- domain: climate
- 骨架: climate-output-calibrated-temperature-distribution-task
- 场景: climate-station-temperature-ensemble-forecast-probability-calibration-scenario (E14)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E14
- 关联论文: Neural Networks for Postprocessing Ensemble Weather Forecasts | doi:; From research to applications – examples of operational ensemble post-processing in France using machine learning | doi:; A Composite-Loss Graph Neural Network for the Multivariate Post-Processing of Ensemble Weather Forecasts | doi:; Ensemble weather forecast post-processing with a flexible probabilistic neural network approach | doi:

## 本实例步骤描述
按冻结配置执行“输出校准后的温度分布”，完成从原始集合成员、辅助预报量、站点历史观测到温度分布参数、分位数和预测区间的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{CALIBRATION_CONFIG}、{OUTPUT_DISTRIBUTION}、{QUANTILES}执行输出校准后的温度分布，将原始集合成员、辅助预报量、站点历史观测转换为温度分布参数、分位数和预测区间。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {CALIBRATION_CONFIG} | required=True | type=str | var_name=概率校准配置 | hint=输入概率校准配置。 | default=None
- {OUTPUT_DISTRIBUTION} | required=True | type=str | var_name=输出分布形式 | hint=输入分布或分位数形式。 | default=None
- {QUANTILES} | required=False | type=str | var_name=温度分位数 | hint=输入温度分位数清单。 | default=None

## 本实例产出
- 输出校准后的温度分布结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 校准后分布、分位数或概率满足单调与取值约束
- 校准分布不得固定假设为20个离散成员

## 可调资源（edge:resource，仅真实存在）
- models/ensemble-model-output-statistics-emos-post-processing
- models/neural-network-based-nwp-model-calibration
- models/quantile-regression-forest-qrf-methods

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
