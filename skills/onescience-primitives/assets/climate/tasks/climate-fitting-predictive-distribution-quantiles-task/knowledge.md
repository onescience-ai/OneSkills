# 骨架任务：拟合预测分布或分位数

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“拟合预测分布或分位数”，完成从集合NWP辐射、历史观测与误差到校准辐照度分布、分位数和区间的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{CALIBRATION_CONFIG}、{OUTPUT_DISTRIBUTION}、{QUANTILES}执行拟合预测分布或分位数，将集合NWP辐射、历史观测与误差转换为校准辐照度分布、分位数和区间。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {CALIBRATION_CONFIG} | required=True | type=str | var_name=辐照度校准配置 | hint=输入辐照度校准配置。 | default=None
- {OUTPUT_DISTRIBUTION} | required=True | type=str | var_name=输出分布形式 | hint=输入分布或分位数形式。 | default=None
- {QUANTILES} | required=False | type=str | var_name=辐照度分位数 | hint=输入辐照度分位数。 | default=None

## 产出
- 中间状态与运行日志
- 拟合预测分布或分位数结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 夜间零值、晴空上限和分位数单调性均满足约束
- 校准后分布、分位数或概率满足单调与取值约束
- 核心计算未读取任务截止时间之后的数据
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- models/ensemble-model-output-statistics-emos-post-processing
- models/neural-network-based-nwp-model-calibration
- models/quantile-regression-forest-qrf-methods

## 实例任务（本骨架在各场景的实例化）
- climate-fitting-predictive-distributio-ensemble-forecast-intraday-inst

## 复用场景
- E24
