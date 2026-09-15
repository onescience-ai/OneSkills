# 骨架任务：机制与性能定量分析

- domain: matchem
- 复用场景数: 5
- 实例任务数: 5

## 步骤描述（跨场景聚合去重）
- 建立组成/工艺-微结构-性能或反应关系。

## 执行 prompt（跨场景聚合去重）
- 在 {LOAD_OR_REACTION_CONDITION} 下计算性能、结构变化和机制证据，报告不确定性。

## 输入槽（var/hint/default）
- {LOAD_OR_REACTION_CONDITION} | required=True | type=object | var_name=载荷或反应条件 | hint=温度、应变率、环境、反应时间或电化学条件 | default={'temperature_K': 298}

## 产出
- 机制分析
- 量化指标

## 质量门禁 quality_gate
- 相关性与因果证据区分
- 统计样本量明确

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-0b7fab84
- it-2381ccb2
- it-596a2358
- it-c0c3540f
- it-f7249f8e

## 复用场景
- CrCoNi中高熵合金低温断裂韧性分析
- 复杂合金热稳定纳米颗粒扩散调控
- 激光粉末床熔融钥孔波动与孔隙形成分析
- 难熔高熵合金位错迁移与短程有序分析
- 高熵金属玻璃纳米颗粒电合成与电催化设计
