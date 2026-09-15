# 骨架任务：1—10天确定性状态滚动

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按模型原生推进方式生成目标时段内的全球多变量确定性预报轨迹。

## 执行 prompt（跨场景聚合去重）
- 采用{ROLLOUT_STRATEGY}，以{OUTPUT_INTERVAL_HOURS}小时为间隔，把标准化初场推进至{LEAD_DAYS}天。按{SAVE_INTERMEDIATE_STATES}保存中间状态并固定{RANDOM_SEED}；逐步记录有效时刻、输入来源、输出形状、数值范围、耗时和资源占用。

## 输入槽（var/hint/default）
- {ROLLOUT_STRATEGY} | required=True | type=str | var_name=状态推进策略 | hint=输入自回归或多时效推进。 | default=None
- {OUTPUT_INTERVAL_HOURS} | required=True | type=str | var_name=输出时间间隔 | hint=输入输出间隔，单位小时。 | default=6
- {SAVE_INTERMEDIATE_STATES} | required=False | type=str | var_name=保存中间状态 | hint=输入是否保存中间状态。 | default=true
- {RANDOM_SEED} | required=False | type=str | var_name=运行随机种子 | hint=输入随机种子。 | default=None

## 产出
- 中间状态检查点
- 推理日志与资源统计
- 标准化全球确定性预报序列

## 质量门禁 quality_gate
- 所有输出的维度、变量顺序和坐标与模型契约一致
- 断点续算未混用不同检查点、配置或预处理版本
- 每一步输出均不存在NaN或Inf
- 滚动过程中未读取起报时间之后的分析或验证资料
- 目标时段内预报时次完整且不存在重复、跳步或时间错位

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-0784aab3

## 复用场景
- E1
