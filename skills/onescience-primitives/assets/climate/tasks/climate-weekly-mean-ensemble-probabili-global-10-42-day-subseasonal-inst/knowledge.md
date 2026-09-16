# 实例任务：汇总周平均与集合概率 @ E7

- domain: climate
- 骨架: climate-weekly-mean-ensemble-probability-task
- 场景: climate-global-10-42-day-subseasonal-multivariate-anomaly-forecast-scenario (E7)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E7
- 关联论文: FengWu-W2S_ A deep learning model for seamless weather-to-subseasonal forecast of global atmosphere | doi:; AIFS-SUBS- Extending Data-Driven Forecasting to Sub-Seasonal Timescales | doi:; A machine learning model that outperforms conventional global subseasonal forecast models | doi:

## 本实例步骤描述
按冻结配置执行“汇总周平均与集合概率”，完成从全球大气初态、海陆边界状态、目标周到周平均异常场、集合概率和气候模态诊断的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{OUTPUT_INTERVAL}、{ENSEMBLE_SIZE}执行汇总周平均与集合概率，将全球大气初态、海陆边界状态、目标周转换为周平均异常场、集合概率和气候模态诊断。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入结果输出间隔。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=1

## 本实例产出
- 汇总周平均与集合概率结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 滚动过程中未读取起报时间之后的观测或分析资料

## 可调资源（edge:resource，仅真实存在）
- datasets/cesm2-large-ensemble
- datasets/large-ensemble-testbed
- models/crpsexp-loss-function-for-ensemble-forecasting
- models/ensemble-empirical-mode-decomposition-eemd
- models/ensemble-model-output-statistics-emos-post-processing

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
