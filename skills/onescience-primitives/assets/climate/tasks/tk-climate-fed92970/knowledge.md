# 骨架任务：生成日前负荷分布并协调层级汇总

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“生成日前负荷分布并协调层级汇总”，完成从历史负荷、天气预报、日历与用户层级到日前负荷点值、分位数和区间的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{QUANTILES}、{RECONCILIATION_CONFIG}执行生成日前负荷分布并协调层级汇总，将历史负荷、天气预报、日历与用户层级转换为日前负荷点值、分位数和区间。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=负荷预测配置 | hint=输入负荷预测配置。 | default=None
- {QUANTILES} | required=True | type=str | var_name=负荷分位数 | hint=输入负荷分位数清单。 | default=None
- {RECONCILIATION_CONFIG} | required=True | type=str | var_name=层级协调配置 | hint=输入层级协调配置。 | default=None

## 产出
- 中间状态与运行日志
- 生成日前负荷分布并协调层级汇总结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 先生成各层级日前负荷分布再执行层级一致性协调
- 功率、负荷或辐照度输出满足物理边界
- 核心计算未读取任务截止时间之后的数据
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-9f3db1d7

## 复用场景
- E20
