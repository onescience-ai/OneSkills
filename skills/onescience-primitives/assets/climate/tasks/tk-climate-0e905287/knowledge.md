# 骨架任务：分阶段估计物候日期和不确定性

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“分阶段估计物候日期和不确定性”，完成从植被指数、气象累计量、雪盖、地形和物候观测到各物候阶段年积日及置信区间的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{DECISION_THRESHOLD}、{UNCERTAINTY_CONFIG}执行分阶段估计物候日期和不确定性，将植被指数、气象累计量、雪盖、地形和物候观测转换为各物候阶段年积日及置信区间。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {DECISION_THRESHOLD} | required=False | type=str | var_name=判定阈值 | hint=输入分类或检测阈值。 | default=None
- {UNCERTAINTY_CONFIG} | required=False | type=str | var_name=不确定性配置 | hint=输入不确定性估计配置。 | default=None

## 产出
- 中间状态与运行日志
- 分阶段估计物候日期和不确定性结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 核心计算未读取任务截止时间之后的数据
- 目标区域和时段内结果完整且无重复或错位
- 输出坐标、分辨率、无效值和置信信息完整
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-0451d3db

## 复用场景
- E67
