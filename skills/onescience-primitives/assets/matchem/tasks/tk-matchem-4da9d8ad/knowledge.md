# 骨架任务：缺陷模型与对照定义

- domain: matchem
- 复用场景数: 4
- 实例任务数: 4

## 步骤描述（跨场景聚合去重）
- 生成母体和缺陷候选并固定浓度/边界。

## 执行 prompt（跨场景聚合去重）
- 根据 {HOST_STRUCTURE} 和 {DEFECT_SET} 建立缺陷候选，定义对照和电荷/化学势参考。

## 输入槽（var/hint/default）
- {HOST_STRUCTURE} | required=True | type=doc | var_name=母体结构 | hint=CIF/POSCAR、晶面、层数或样品信 | default=CIF/POSCAR
- {DEFECT_SET} | required=True | type=list[str] | var_name=缺陷候选 | hint=空位、掺杂、边缘、晶界或辐照缺陷及浓度。 | default=['specified defects']

## 产出
- 参考态说明
- 缺陷结构集

## 质量门禁 quality_gate
- 电荷补偿明确
- 缺陷浓度与超胞一致

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-32ea3019
- it-4c1a48f2
- it-ce2e0645
- it-fe9b212c

## 复用场景
- MoS2单层原子缺陷工程
- hBN单光子发射原子缺陷设计
- 磷烯单层缺陷工程与空气稳定化
- 锂还原室温氧化物缺陷调控
