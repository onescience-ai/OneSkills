# 实例任务：循环生成分析状态并滚动中期天气预报 @ E4

- domain: climate
- 骨架: tk-climate-775461f4
- 场景: sc-84809286 (E4)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E4
- 关联论文: A data-to-forecast machine learning system for global weather | doi:; End-to-end data-driven weather prediction | doi:; GraphDOP_ Towards skilful data-driven medium-range weather forecasts learnt and initialised directly from observations | doi:

## 本实例步骤描述
按冻结配置执行“循环生成分析状态并滚动中期天气预报”，完成从带时间和位置的原始观测、背景状态到全球分析场与后续多变量天气预报的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{CYCLE_CONFIG}、{FORECAST_HORIZON}、{FORECAST_OUTPUT_INTERVAL}、{CHECKPOINT_INTERVAL}执行循环生成分析状态并滚动中期天气预报，将带时间和位置的原始观测、背景状态转换为全球分析场与后续多变量天气预报。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {CYCLE_CONFIG} | required=True | type=str | var_name=分析循环配置 | hint=输入分析循环配置。 | default=None
- {FORECAST_HORIZON} | required=True | type=str | var_name=后续预报时效 | hint=输入后续预报时效。 | default=None
- {FORECAST_OUTPUT_INTERVAL} | required=True | type=str | var_name=预报输出间隔 | hint=输入预报输出间隔。 | default=None
- {CHECKPOINT_INTERVAL} | required=True | type=str | var_name=循环保存间隔 | hint=输入循环保存间隔。 | default=None

## 本实例产出
- 循环生成分析状态并滚动中期天气预报结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 分析增量和循环状态不存在未解释的突变
- 同一次运行同时产出分析状态和从该状态起报的后续天气轨迹

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
