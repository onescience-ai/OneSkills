# 骨架任务：联合生成多时效功率

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“联合生成多时效功率”，完成从多站历史功率、天气预报、电站容量属性到逐站多时效光伏功率的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{QUANTILES}、{OUTPUT_INTERVAL}执行联合生成多时效功率，将多站历史功率、天气预报、电站容量属性转换为逐站多时效光伏功率。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {QUANTILES} | required=False | type=str | var_name=概率分位数 | hint=输入概率分位数清单。 | default=None
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入结果输出间隔。 | default=None

## 产出
- 中间状态与运行日志
- 联合生成多时效功率结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 功率、负荷或辐照度输出满足物理边界
- 核心计算未读取任务截止时间之后的数据
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-9877efd8

## 复用场景
- E25
