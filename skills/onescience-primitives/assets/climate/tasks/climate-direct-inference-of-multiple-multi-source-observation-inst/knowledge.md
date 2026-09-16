# 实例任务：直接推理多个目标提前量 @ E8

- domain: climate
- 骨架: climate-direct-inference-of-multiple-target-lead-times-task
- 场景: climate-multi-source-observation-driven-regional-3to12h-quantitative-scenario (E8)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E8
- 关联论文: Deep learning for twelve hour precipitation forecasts | doi:; MetNet-3_ A state-of-the-art neural weather model available in Google products | doi:

## 本实例步骤描述
按冻结配置执行“直接推理多个目标提前量”，完成从近期雷达卫星序列、站点观测、区域分析场到3—12小时降水率场、累积降水和概率的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{EVENT_THRESHOLDS}、{ENSEMBLE_SIZE}执行直接推理多个目标提前量，将近期雷达卫星序列、站点观测、区域分析场转换为3—12小时降水率场、累积降水和概率。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {EVENT_THRESHOLDS} | required=True | type=str | var_name=事件阈值 | hint=输入事件判定阈值。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=1

## 本实例产出
- 直接推理多个目标提前量结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 每个目标提前量均生成且未使用未来观测

## 可调资源（edge:resource，仅真实存在）
- datasets/cesm2-large-ensemble
- datasets/large-ensemble-testbed
- models/crpsexp-loss-function-for-ensemble-forecasting
- models/dust-event-forecasting-with-multi-task-deep-learning
- models/ensemble-empirical-mode-decomposition-eemd
- models/ensemble-model-output-statistics-emos-post-processing
- tools/ecmwf-hres

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
