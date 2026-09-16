# 实例任务：重建当前污染格点并滚动生成短时预测 @ E60

- domain: climate
- 骨架: climate-reconstruct-pollution-grid-roll-short-term-prediction-task
- 场景: climate-sparse-monitoring-station-driven-urban-pollution-grid-scenario (E60)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E60
- 关联论文: Spatiotemporal deep learning model for citywide air pollution interpolation and prediction | doi:; PM10 and PM2.5 real-time prediction models using an interpolated convolutional neural network | doi:

## 本实例步骤描述
按冻结配置执行“重建当前污染格点并滚动生成短时预测”，完成从稀疏污染站序列、气象、道路和空间位置到城市连续污染格点、短时预测及不确定性的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{FORECAST_HORIZON}、{SPATIAL_GRID}执行重建当前污染格点并滚动生成短时预测，将稀疏污染站序列、气象、道路和空间位置转换为城市连续污染格点、短时预测及不确定性。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {FORECAST_HORIZON} | required=False | type=str | var_name=预测时效 | hint=输入目标预测时效。 | default=None
- {SPATIAL_GRID} | required=True | type=str | var_name=输出网格 | hint=输入输出网格规格。 | default=None

## 本实例产出
- 重建当前污染格点并滚动生成短时预测结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 输出浓度或柱含量满足物理范围和掩膜约束

## 可调资源（edge:resource，仅真实存在）
- datasets/spatial-generalization-benchmarks-for-hydrologic-models
- models/spatial-and-temporal-deep-learning-models-for-fire-prediction
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/wenhai-global-ocean-forecast-system

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
