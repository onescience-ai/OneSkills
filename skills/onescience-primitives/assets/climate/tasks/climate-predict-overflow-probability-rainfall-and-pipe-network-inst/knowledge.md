# 实例任务：预测溢流概率与体量 @ E82

- domain: climate
- 骨架: climate-predict-overflow-probability-volume-task
- 场景: climate-rainfall-and-pipe-network-state-driven-combined-sewer-overflow-scenario (E82)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E82
- 关联论文: A Committee Evolutionary Neural Network for the Prediction of Combined Sewer Overflows | doi:

## 本实例步骤描述
按冻结配置执行“预测溢流概率与体量”，完成从降雨预报、管网水位流量、泵闸运行到溢流概率、开始时间和体量的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{INITIAL_STATE}、{ENSEMBLE_SIZE}执行预测溢流概率与体量，将降雨预报、管网水位流量、泵闸运行转换为溢流概率、开始时间和体量。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {INITIAL_STATE} | required=False | type=str | var_name=初始水文状态 | hint=输入初始水文状态路径。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=1

## 本实例产出
- 预测溢流概率与体量结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 水量、状态范围和洪峰时序不存在非物理异常

## 可调资源（edge:resource，仅真实存在）
- datasets/cesm2-large-ensemble
- datasets/large-ensemble-testbed
- models/crpsexp-loss-function-for-ensemble-forecasting
- models/ensemble-empirical-mode-decomposition-eemd
- models/ensemble-model-output-statistics-emos-post-processing

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
