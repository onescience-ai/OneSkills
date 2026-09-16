# 实例任务：生成未来指数轨迹或集合 @ E9

- domain: climate
- 骨架: climate-future-index-trajectory-ensemble-task
- 场景: climate-enso-index-6-24-month-probabilistic-forecast-scenario (E9)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E9
- 关联论文: Efficient inference and learning of a generative model for ENSO predictions from large multi-model datasets | doi:; Temporal Convolutional Networks for the Advance Prediction of ENSO | doi:; Combined dynamical-deep learning ENSO forecasts | doi:; Deep learning for skillful long-lead ENSO forecasts | doi:

## 本实例步骤描述
按冻结配置执行“生成未来指数轨迹或集合”，完成从过去海温与海洋—大气状态序列到Niño3.4指数集合、厄尔尼诺和拉尼娜概率的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{OUTPUT_INTERVAL}、{ENSEMBLE_SIZE}执行生成未来指数轨迹或集合，将过去海温与海洋—大气状态序列转换为Niño3.4指数集合、厄尔尼诺和拉尼娜概率。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入结果输出间隔。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=20

## 本实例产出
- 生成未来指数轨迹或集合结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 滚动过程中未读取起报时间之后的观测或分析资料

## 可调资源（edge:resource，仅真实存在）
- datasets/cesm2-large-ensemble
- datasets/CMEMS
- datasets/large-ensemble-testbed
- models/crpsexp-loss-function-for-ensemble-forecasting
- models/ensemble-empirical-mode-decomposition-eemd
- models/ensemble-model-output-statistics-emos-post-processing

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
