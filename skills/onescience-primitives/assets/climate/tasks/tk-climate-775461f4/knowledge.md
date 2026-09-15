# 骨架任务：循环生成分析状态并滚动中期天气预报

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“循环生成分析状态并滚动中期天气预报”，完成从带时间和位置的原始观测、背景状态到全球分析场与后续多变量天气预报的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{CYCLE_CONFIG}、{FORECAST_HORIZON}、{FORECAST_OUTPUT_INTERVAL}、{CHECKPOINT_INTERVAL}执行循环生成分析状态并滚动中期天气预报，将带时间和位置的原始观测、背景状态转换为全球分析场与后续多变量天气预报。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {CYCLE_CONFIG} | required=True | type=str | var_name=分析循环配置 | hint=输入分析循环配置。 | default=None
- {FORECAST_HORIZON} | required=True | type=str | var_name=后续预报时效 | hint=输入后续预报时效。 | default=None
- {FORECAST_OUTPUT_INTERVAL} | required=True | type=str | var_name=预报输出间隔 | hint=输入预报输出间隔。 | default=None
- {CHECKPOINT_INTERVAL} | required=True | type=str | var_name=循环保存间隔 | hint=输入循环保存间隔。 | default=None

## 产出
- 中间状态与运行日志
- 循环生成分析状态并滚动中期天气预报结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 分析增量和循环状态不存在未解释的突变
- 同一次运行同时产出分析状态和从该状态起报的后续天气轨迹
- 核心计算未读取任务截止时间之后的数据
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-9612c6b3

## 复用场景
- E4
