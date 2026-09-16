# 骨架任务：搜索多目标可行航线

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“搜索多目标可行航线”，完成从风浪流预报、船舶性能、起终点与约束到优化航线、航时、能耗和风险的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{SEARCH_CONFIG}、{ARRIVAL_WINDOW}、{ALTERNATIVE_COUNT}执行搜索多目标可行航线，将风浪流预报、船舶性能、起终点与约束转换为优化航线、航时、能耗和风险。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {SEARCH_CONFIG} | required=True | type=str | var_name=搜索配置 | hint=输入航线搜索配置。 | default=None
- {ARRIVAL_WINDOW} | required=True | type=str | var_name=到达时间窗 | hint=输入允许到达时间窗。 | default=None
- {ALTERNATIVE_COUNT} | required=True | type=str | var_name=候选航线数 | hint=输入候选航线数量。 | default=5

## 产出
- 中间状态与运行日志
- 搜索多目标可行航线结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 所有候选航线均满足禁航区和安全硬约束
- 核心计算未读取任务截止时间之后的数据
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- datasets/lpma-airport-wind-observation-validation
- datasets/southern-great-plains-sgp-observatory-wind-dataset
- models/multivariate-data-fusion-vector-wind-prediction
- models/random-forest-regression-for-vertical-wind-speed-extrapolation

## 实例任务（本骨架在各场景的实例化）
- climate-searching-multi-objective-marine-weather-navigation-inst

## 复用场景
- E100
