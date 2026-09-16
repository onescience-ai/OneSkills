# 实例任务：机制与性能定量分析 @ 难熔高熵合金位错迁移与短程有序分析

- domain: matchem
- 骨架: matchem-mechanism-performance-quantitative-analysis-task
- 场景: matchem-refractory-high-entropy-alloy-dislocation-migration-and-short-scenario (难熔高熵合金位错迁移与短程有序分析)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- 难熔高熵合金位错迁移与短程有序分析
- 关联论文: Atomistic simulations of dislocation mobility in refractory high-entropy alloys and the effect of chemical short-range order | doi:

## 本实例步骤描述
建立组成/工艺-微结构-性能或反应关系。

## 本实例执行 prompt
在 {LOAD_OR_REACTION_CONDITION} 下计算性能、结构变化和机制证据，报告不确定性。

## 本实例输入槽
- {LOAD_OR_REACTION_CONDITION} | required=True | type=object | var_name=载荷或反应条件 | hint=温度、应变率、环境、反应时间或电化学条件 | default={'temperature_K': 298}

## 本实例产出
- 量化指标
- 机制分析

## 本实例质量门禁
- 相关性与因果证据区分
- 统计样本量明确

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
