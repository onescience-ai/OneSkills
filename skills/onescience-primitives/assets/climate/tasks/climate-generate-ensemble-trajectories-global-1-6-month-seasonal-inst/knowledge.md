# 实例任务：生成集合轨迹并汇总月季异常 @ E47

- domain: climate
- 骨架: climate-generate-ensemble-trajectories-and-summarize-anomalies-task
- 场景: climate-global-1-6-month-seasonal-ensemble-weather-climate-forecast-scenario (E47)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E47
- 关联论文: Skilful global seasonal predictions from a machine learning weather model trained on reanalysis data | doi:; Seasonal forecasting using the GenCast probabilistic machine learning model | doi:

## 本实例步骤描述
按冻结配置执行“生成集合轨迹并汇总月季异常”，完成从多个季节起报初态、边界状态、气候基准到月季尺度集合异常场与概率分布的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{OUTPUT_INTERVAL}、{ENSEMBLE_SIZE}执行生成集合轨迹并汇总月季异常，将多个季节起报初态、边界状态、气候基准转换为月季尺度集合异常场与概率分布。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入结果输出间隔。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=20

## 本实例产出
- 生成集合轨迹并汇总月季异常结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 滚动过程中未读取起报时间之后的观测或分析资料
- 每个1至6月预见期和集合成员均完整输出

## 可调资源（edge:resource，仅真实存在）
- datasets/cesm2-large-ensemble
- datasets/large-ensemble-testbed
- models/crpsexp-loss-function-for-ensemble-forecasting
- models/ensemble-empirical-mode-decomposition-eemd
- models/ensemble-model-output-statistics-emos-post-processing

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
