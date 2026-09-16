# 骨架任务：生成多个未来时效概率场

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“生成多个未来时效概率场”，完成从雷达回波序列、可选环境场、冰雹标签到分时效冰雹概率格点与风险对象的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{EVENT_THRESHOLDS}、{ENSEMBLE_SIZE}执行生成多个未来时效概率场，将雷达回波序列、可选环境场、冰雹标签转换为分时效冰雹概率格点与风险对象。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {EVENT_THRESHOLDS} | required=True | type=str | var_name=事件阈值 | hint=输入事件判定阈值。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=20

## 产出
- 中间状态与运行日志
- 生成多个未来时效概率场结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 核心计算未读取任务截止时间之后的数据
- 每个目标提前量均生成且未使用未来观测
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- datasets/cesm2-large-ensemble
- datasets/large-ensemble-testbed
- models/crpsexp-loss-function-for-ensemble-forecasting
- models/dust-event-forecasting-with-multi-task-deep-learning
- models/ensemble-empirical-mode-decomposition-eemd
- models/ensemble-model-output-statistics-emos-post-processing
- tools/ecmwf-hres

## 实例任务（本骨架在各场景的实例化）
- climate-multi-leadtime-probability-weather-radar-hail-probabili-inst

## 复用场景
- E83
