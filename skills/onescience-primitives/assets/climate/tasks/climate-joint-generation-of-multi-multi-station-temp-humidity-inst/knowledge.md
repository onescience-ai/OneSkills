# 实例任务：联合生成各站多变量序列 @ E41

- domain: climate
- 骨架: climate-joint-generation-of-multi-variable-station-sequences-task
- 场景: climate-multi-station-temp-humidity-wind-24to72h-joint-time-series-scenario (E41)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E41
- 关联论文: Sequence to Sequence Weather Forecasting with Long Short-Term Memory Recurrent Neural Networks | doi:; WSSM_ GEOGRAPHIC-ENHANCED HIERARCHICAL STATE-SPACE MODEL FOR GLOBAL STATION WEATHER FORECAST | doi:; S$^2$Transformer- Scalable Structured Transformers for Global Station Weather Forecasting | doi:

## 本实例步骤描述
按冻结配置执行“联合生成各站多变量序列”，完成从多站历史温湿风、站点位置与时间特征到各站未来逐时温度、湿度和风速序列的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{OUTPUT_INTERVAL}、{ENSEMBLE_SIZE}执行联合生成各站多变量序列，将多站历史温湿风、站点位置与时间特征转换为各站未来逐时温度、湿度和风速序列。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入结果输出间隔。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=1

## 本实例产出
- 联合生成各站多变量序列结果
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
