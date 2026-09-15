# 实例任务：生成日前负荷分布并协调层级汇总 @ E20

- domain: climate
- 骨架: tk-climate-fed92970
- 场景: sc-bae97f9f (E20)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E20
- 关联论文: A gradient boosting approach to the Kaggle load forecasting competition | doi:; Hierarchical Probabilistic Forecasting of Electricity Demand With Smart Meter Data | doi:; Machine Learning Techniques for Predicting the Energy Consumption-Production and Its Uncertainties Driven by Meteorological Observations and Forecasts | doi:; Multi-Feature Data Fusion-Based Load Forecasting of Electric Vehicle Charging Stations Using a Deep Learning Model | doi:

## 本实例步骤描述
按冻结配置执行“生成日前负荷分布并协调层级汇总”，完成从历史负荷、天气预报、日历与用户层级到日前负荷点值、分位数和区间的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{QUANTILES}、{RECONCILIATION_CONFIG}执行生成日前负荷分布并协调层级汇总，将历史负荷、天气预报、日历与用户层级转换为日前负荷点值、分位数和区间。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=负荷预测配置 | hint=输入负荷预测配置。 | default=None
- {QUANTILES} | required=True | type=str | var_name=负荷分位数 | hint=输入负荷分位数清单。 | default=None
- {RECONCILIATION_CONFIG} | required=True | type=str | var_name=层级协调配置 | hint=输入层级协调配置。 | default=None

## 本实例产出
- 生成日前负荷分布并协调层级汇总结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 功率、负荷或辐照度输出满足物理边界
- 先生成各层级日前负荷分布再执行层级一致性协调

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
