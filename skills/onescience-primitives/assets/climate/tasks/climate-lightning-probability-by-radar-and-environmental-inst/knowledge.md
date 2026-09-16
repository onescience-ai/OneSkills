# 实例任务：生成各提前期闪电发生概率场 @ E72

- domain: climate
- 骨架: climate-lightning-probability-by-leadtime-task
- 场景: climate-radar-and-environmental-field-driven-0-6-hour-lightning-scenario (E72)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E72
- 关联论文: FlashBench- A lightning nowcasting framework based on the hybrid deep learning and physics-based dynamical models | doi:

## 本实例步骤描述
按冻结配置执行“生成各提前期闪电发生概率场”，完成从雷达体扫、闪电历史、对流环境场到分时效闪电概率和位置栅格的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{LEAD_TIMES}、{EVENT_THRESHOLDS}执行生成各提前期闪电发生概率场，将雷达体扫、闪电历史、对流环境场转换为分时效闪电概率和位置栅格。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=闪电预报配置 | hint=输入闪电预报配置。 | default=None
- {LEAD_TIMES} | required=True | type=str | var_name=目标提前期 | hint=输入目标提前期清单。 | default=None
- {EVENT_THRESHOLDS} | required=True | type=str | var_name=闪电概率阈值 | hint=输入闪电概率阈值。 | default=None

## 本实例产出
- 生成各提前期闪电发生概率场结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 每个目标提前量均生成且未使用未来观测
- 每个目标提前期均生成闪电发生概率场

## 可调资源（edge:resource，仅真实存在）
- models/dust-event-forecasting-with-multi-task-deep-learning
- models/dynamic-pre-training-for-time-series-dynpt
- tools/ecmwf-hres

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
