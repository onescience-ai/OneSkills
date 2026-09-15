# 实例任务：搜索多目标可行航线 @ E100

- domain: climate
- 骨架: tk-climate-187ccc5b
- 场景: sc-975001b3 (E100)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E100
- 关联论文: A novel, data-driven heuristic framework for vessel weather routing | doi:

## 本实例步骤描述
按冻结配置执行“搜索多目标可行航线”，完成从风浪流预报、船舶性能、起终点与约束到优化航线、航时、能耗和风险的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{SEARCH_CONFIG}、{ARRIVAL_WINDOW}、{ALTERNATIVE_COUNT}执行搜索多目标可行航线，将风浪流预报、船舶性能、起终点与约束转换为优化航线、航时、能耗和风险。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {SEARCH_CONFIG} | required=True | type=str | var_name=搜索配置 | hint=输入航线搜索配置。 | default=None
- {ARRIVAL_WINDOW} | required=True | type=str | var_name=到达时间窗 | hint=输入允许到达时间窗。 | default=None
- {ALTERNATIVE_COUNT} | required=True | type=str | var_name=候选航线数 | hint=输入候选航线数量。 | default=5

## 本实例产出
- 搜索多目标可行航线结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 所有候选航线均满足禁航区和安全硬约束

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
