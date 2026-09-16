# 骨架任务：拟合基因型、环境及互作响应模型

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“拟合基因型、环境及互作响应模型”，完成从多点田间试验、品种基因型、历史天气和生育期特征到品种—地点产量分布及稳定性排序的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RESPONSE_CONFIG}、{WEATHER_SAMPLING_CONFIG}、{UNCERTAINTY_CONFIG}执行拟合基因型、环境及互作响应模型，将多点田间试验、品种基因型、历史天气和生育期特征转换为品种—地点产量分布及稳定性排序。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RESPONSE_CONFIG} | required=True | type=str | var_name=互作响应配置 | hint=输入互作响应配置。 | default=None
- {WEATHER_SAMPLING_CONFIG} | required=True | type=str | var_name=天气抽样配置 | hint=输入历史天气抽样配置。 | default=None
- {UNCERTAINTY_CONFIG} | required=True | type=str | var_name=不确定性配置 | hint=输入不确定性估计配置。 | default=None

## 产出
- 中间状态与运行日志
- 拟合基因型、环境及互作响应模型结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 基因型环境互作与天气抽样不确定性分别传播
- 核心计算未读取任务截止时间之后的数据
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯
- 预测关系与因果归因声明严格区分

## 可调资源（edge:resource，仅真实存在）
- datasets/south-korea-air-quality-and-weather-monitoring-dataset
- models/importance-sampling-strategy-for-extreme-events
- tools/aardvark-weather-system
- tools/ai-global-medium-range-weather-forecasting-system-pangu-weather
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/fuxi-weather
- tools/gencast-global-probabilistic-weather-forecasting-model

## 实例任务（本骨架在各场景的实例化）
- climate-fitting-genotype-environment-cultivar-location-uncertain-inst

## 复用场景
- E98
