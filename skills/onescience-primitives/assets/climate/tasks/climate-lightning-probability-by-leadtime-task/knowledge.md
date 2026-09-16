# 骨架任务：生成各提前期闪电发生概率场

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“生成各提前期闪电发生概率场”，完成从雷达体扫、闪电历史、对流环境场到分时效闪电概率和位置栅格的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{LEAD_TIMES}、{EVENT_THRESHOLDS}执行生成各提前期闪电发生概率场，将雷达体扫、闪电历史、对流环境场转换为分时效闪电概率和位置栅格。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=闪电预报配置 | hint=输入闪电预报配置。 | default=None
- {LEAD_TIMES} | required=True | type=str | var_name=目标提前期 | hint=输入目标提前期清单。 | default=None
- {EVENT_THRESHOLDS} | required=True | type=str | var_name=闪电概率阈值 | hint=输入闪电概率阈值。 | default=None

## 产出
- 中间状态与运行日志
- 生成各提前期闪电发生概率场结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 核心计算未读取任务截止时间之后的数据
- 每个目标提前期均生成闪电发生概率场
- 每个目标提前量均生成且未使用未来观测
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- models/dust-event-forecasting-with-multi-task-deep-learning
- models/dynamic-pre-training-for-time-series-dynpt
- tools/ecmwf-hres

## 实例任务（本骨架在各场景的实例化）
- climate-lightning-probability-by-radar-and-environmental-inst

## 复用场景
- E72
