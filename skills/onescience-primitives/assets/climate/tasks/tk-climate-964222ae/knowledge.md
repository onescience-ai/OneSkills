# 骨架任务：输出校准后的温度分布

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“输出校准后的温度分布”，完成从原始集合成员、辅助预报量、站点历史观测到温度分布参数、分位数和预测区间的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{CALIBRATION_CONFIG}、{OUTPUT_DISTRIBUTION}、{QUANTILES}执行输出校准后的温度分布，将原始集合成员、辅助预报量、站点历史观测转换为温度分布参数、分位数和预测区间。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {CALIBRATION_CONFIG} | required=True | type=str | var_name=概率校准配置 | hint=输入概率校准配置。 | default=None
- {OUTPUT_DISTRIBUTION} | required=True | type=str | var_name=输出分布形式 | hint=输入分布或分位数形式。 | default=None
- {QUANTILES} | required=False | type=str | var_name=温度分位数 | hint=输入温度分位数清单。 | default=None

## 产出
- 中间状态与运行日志
- 资源和退出状态记录
- 输出校准后的温度分布结果

## 质量门禁 quality_gate
- 校准分布不得固定假设为20个离散成员
- 校准后分布、分位数或概率满足单调与取值约束
- 核心计算未读取任务截止时间之后的数据
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-408c64f4

## 复用场景
- E14
