# 实例任务：1—10天确定性状态滚动 @ E1

- domain: climate
- 骨架: climate-1-10d-deterministic-state-rolling-task
- 场景: climate-global-analysis-driven-1-10-day-multivariate-deterministic-scenario (E1)
- step_id: s04
- depend: ['s02', 's03']

## 场景研究主体
- E1
- 关联论文: Learning skillful medium-range global weather forecasting | doi:; Accurate medium-range global weather forecasting with 3D neural networks | doi:; FourCastNet: A Global Data-driven High-resolution Weather Model using Adaptive Fourier Neural Operators | doi:; FengWu: Pushing the Skillful Global Medium-range Weather Forecast beyond 10 Days Lead | doi:; AIFS -- ECMWF's data-driven forecasting system | doi:

## 本实例步骤描述
按模型原生推进方式生成目标时段内的全球多变量确定性预报轨迹。

## 本实例执行 prompt
采用{ROLLOUT_STRATEGY}，以{OUTPUT_INTERVAL_HOURS}小时为间隔，把标准化初场推进至{LEAD_DAYS}天。按{SAVE_INTERMEDIATE_STATES}保存中间状态并固定{RANDOM_SEED}；逐步记录有效时刻、输入来源、输出形状、数值范围、耗时和资源占用。

## 本实例输入槽
- {ROLLOUT_STRATEGY} | required=True | type=str | var_name=状态推进策略 | hint=输入自回归或多时效推进。 | default=None
- {OUTPUT_INTERVAL_HOURS} | required=True | type=str | var_name=输出时间间隔 | hint=输入输出间隔，单位小时。 | default=6
- {SAVE_INTERMEDIATE_STATES} | required=False | type=str | var_name=保存中间状态 | hint=输入是否保存中间状态。 | default=true
- {RANDOM_SEED} | required=False | type=str | var_name=运行随机种子 | hint=输入随机种子。 | default=None

## 本实例产出
- 标准化全球确定性预报序列
- 中间状态检查点
- 推理日志与资源统计

## 本实例质量门禁
- 目标时段内预报时次完整且不存在重复、跳步或时间错位
- 所有输出的维度、变量顺序和坐标与模型契约一致
- 每一步输出均不存在NaN或Inf
- 滚动过程中未读取起报时间之后的分析或验证资料
- 断点续算未混用不同检查点、配置或预处理版本

## 可调资源（edge:resource，仅真实存在）
- datasets/random-forest-model-performance-evaluation
- models/ensemble-model-output-statistics-emos-post-processing
- models/importance-sampling-strategy-for-extreme-events
- models/random-forest-meteorological-normalization
- models/random-forest-regression-for-vertical-wind-speed-extrapolation
- models/weighted-long-short-term-memory-neural-network-extended-model-for-pm2-5-forecasting

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
