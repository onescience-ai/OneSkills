# 实例任务：拟合基因型、环境及互作响应模型 @ E98

- domain: climate
- 骨架: climate-fitting-genotype-environment-interaction-response-models-task
- 场景: climate-cultivar-location-uncertain-weather-yield-distribution-and-scenario (E98)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E98
- 关联论文: A data-driven simulation platform to predict cultivars’ performances under uncertain weather conditions | doi:

## 本实例步骤描述
按冻结配置执行“拟合基因型、环境及互作响应模型”，完成从多点田间试验、品种基因型、历史天气和生育期特征到品种—地点产量分布及稳定性排序的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RESPONSE_CONFIG}、{WEATHER_SAMPLING_CONFIG}、{UNCERTAINTY_CONFIG}执行拟合基因型、环境及互作响应模型，将多点田间试验、品种基因型、历史天气和生育期特征转换为品种—地点产量分布及稳定性排序。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RESPONSE_CONFIG} | required=True | type=str | var_name=互作响应配置 | hint=输入互作响应配置。 | default=None
- {WEATHER_SAMPLING_CONFIG} | required=True | type=str | var_name=天气抽样配置 | hint=输入历史天气抽样配置。 | default=None
- {UNCERTAINTY_CONFIG} | required=True | type=str | var_name=不确定性配置 | hint=输入不确定性估计配置。 | default=None

## 本实例产出
- 拟合基因型、环境及互作响应模型结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 预测关系与因果归因声明严格区分
- 基因型环境互作与天气抽样不确定性分别传播

## 可调资源（edge:resource，仅真实存在）
- datasets/south-korea-air-quality-and-weather-monitoring-dataset
- models/importance-sampling-strategy-for-extreme-events
- tools/aardvark-weather-system
- tools/ai-global-medium-range-weather-forecasting-system-pangu-weather
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/fuxi-weather
- tools/gencast-global-probabilistic-weather-forecasting-model

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
