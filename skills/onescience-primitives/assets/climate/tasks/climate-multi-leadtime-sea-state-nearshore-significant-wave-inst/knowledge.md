# 实例任务：生成多提前期确定性或集合海况 @ E31

- domain: climate
- 骨架: climate-multi-leadtime-sea-state-task
- 场景: climate-nearshore-significant-wave-height-period-direction-short-term-scenario (E31)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E31
- 关联论文: A machine learning framework to forecast wave conditions | doi:; SPATIAL AND TEMPORAL DEEP LEARNING OF WEATHER FORECASTFOR 11 DAY WAVE PREDICTION | doi:; Machine Learning Prediction of Wave Characteristics: Comparison between Semi-Empirical Approaches and DT Model | doi:

## 本实例步骤描述
按冻结配置执行“生成多提前期确定性或集合海况”，完成从初始海浪场、预报风场、边界波谱和水深到多时效波高、周期及波向的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{OUTPUT_INTERVAL}、{ENSEMBLE_SIZE}执行生成多提前期确定性或集合海况，将初始海浪场、预报风场、边界波谱和水深转换为多时效波高、周期及波向。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入结果输出间隔。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=1

## 本实例产出
- 生成多提前期确定性或集合海况结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 输出在岸线、深水区和强梯度区无异常跳变

## 可调资源（edge:resource，仅真实存在）
- datasets/cesm2-large-ensemble
- datasets/large-ensemble-testbed
- models/crpsexp-loss-function-for-ensemble-forecasting
- models/ensemble-empirical-mode-decomposition-eemd
- models/ensemble-model-output-statistics-emos-post-processing

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
