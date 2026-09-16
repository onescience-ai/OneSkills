# 骨架任务：构造生育期特征并生成县域产量分布

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“构造生育期特征并生成县域产量分布”，完成从截至签发日天气、土壤、种植管理和历史产量到县域玉米单产及不确定性的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{FORECAST_CONFIG}、{FUTURE_WEATHER_POLICY}、{UNCERTAINTY_CONFIG}执行构造生育期特征并生成县域产量分布，将截至签发日天气、土壤、种植管理和历史产量转换为县域玉米单产及不确定性。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {FORECAST_CONFIG} | required=True | type=str | var_name=产量预测配置 | hint=输入产量预测配置。 | default=None
- {FUTURE_WEATHER_POLICY} | required=True | type=str | var_name=未来天气规则 | hint=输入未来天气使用规则。 | default=None
- {UNCERTAINTY_CONFIG} | required=True | type=str | var_name=不确定性配置 | hint=输入不确定性估计配置。 | default=None

## 产出
- 中间状态与运行日志
- 构造生育期特征并生成县域产量分布结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 核心计算未读取任务截止时间之后的数据
- 核心运行必须生成县域产量点估计和不确定性分布
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯
- 预测关系与因果归因声明严格区分

## 可调资源（edge:resource，仅真实存在）
- datasets/south-korea-air-quality-and-weather-monitoring-dataset
- tools/aardvark-weather-system
- tools/ai-global-medium-range-weather-forecasting-system-pangu-weather
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/fuxi-weather
- tools/gencast-global-probabilistic-weather-forecasting-model
- tools/wenhai-global-ocean-forecast-system

## 实例任务（本骨架在各场景的实例化）
- climate-constructing-growth-stage-growing-season-county-corn-inst

## 复用场景
- E58
