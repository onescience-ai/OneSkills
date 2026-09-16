# 骨架任务：逐时效预测臭氧浓度

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“逐时效预测臭氧浓度”，完成从臭氧监测历史、气象预报、可选CMAQ场到小时臭氧浓度、MDA8和超标概率的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{FORECAST_HORIZON}、{SPATIAL_GRID}执行逐时效预测臭氧浓度，将臭氧监测历史、气象预报、可选CMAQ场转换为小时臭氧浓度、MDA8和超标概率。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {FORECAST_HORIZON} | required=False | type=str | var_name=预测时效 | hint=输入目标预测时效。 | default=None
- {SPATIAL_GRID} | required=True | type=str | var_name=输出网格 | hint=输入输出网格规格。 | default=None

## 产出
- 中间状态与运行日志
- 资源和退出状态记录
- 逐时效预测臭氧浓度结果

## 质量门禁 quality_gate
- 核心计算未读取任务截止时间之后的数据
- 目标区域和时段内结果完整且无重复或错位
- 输出浓度或柱含量满足物理范围和掩膜约束
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- datasets/spatial-generalization-benchmarks-for-hydrologic-models
- models/spatial-and-temporal-deep-learning-models-for-fire-prediction
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/wenhai-global-ocean-forecast-system

## 实例任务（本骨架在各场景的实例化）
- climate-predict-ozone-concentration-near-surface-ozone-hourly-inst

## 复用场景
- E44
