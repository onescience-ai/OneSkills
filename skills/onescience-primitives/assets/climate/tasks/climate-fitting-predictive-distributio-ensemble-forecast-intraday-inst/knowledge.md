# 实例任务：拟合预测分布或分位数 @ E24

- domain: climate
- 骨架: climate-fitting-predictive-distribution-quantiles-task
- 场景: climate-ensemble-forecast-intraday-to-days-ahead-solar-irradiance-scenario (E24)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E24
- 关联论文: Improving Model Chain Approaches for Probabilistic Solar Energy Forecasting through Post-processing and Machine Learning | doi:; Post-processing numerical weather prediction ensembles for probabilistic solar irradiance forecasting | doi:; Comparison of statistical post-processing methods for probabilistic NWP forecasts of solar radiation | doi:; Machine-learning-based probabilistic forecasting of solar irradiance in Chile | doi:

## 本实例步骤描述
按冻结配置执行“拟合预测分布或分位数”，完成从集合NWP辐射、历史观测与误差到校准辐照度分布、分位数和区间的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{CALIBRATION_CONFIG}、{OUTPUT_DISTRIBUTION}、{QUANTILES}执行拟合预测分布或分位数，将集合NWP辐射、历史观测与误差转换为校准辐照度分布、分位数和区间。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {CALIBRATION_CONFIG} | required=True | type=str | var_name=辐照度校准配置 | hint=输入辐照度校准配置。 | default=None
- {OUTPUT_DISTRIBUTION} | required=True | type=str | var_name=输出分布形式 | hint=输入分布或分位数形式。 | default=None
- {QUANTILES} | required=False | type=str | var_name=辐照度分位数 | hint=输入辐照度分位数。 | default=None

## 本实例产出
- 拟合预测分布或分位数结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 校准后分布、分位数或概率满足单调与取值约束
- 夜间零值、晴空上限和分位数单调性均满足约束

## 可调资源（edge:resource，仅真实存在）
- models/ensemble-model-output-statistics-emos-post-processing
- models/neural-network-based-nwp-model-calibration
- models/quantile-regression-forest-qrf-methods

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
