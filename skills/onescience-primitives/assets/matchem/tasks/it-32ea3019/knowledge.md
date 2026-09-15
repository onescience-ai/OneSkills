# 实例任务：缺陷模型与对照定义 @ 锂还原室温氧化物缺陷调控

- domain: matchem
- 骨架: tk-matchem-4da9d8ad
- 场景: sc-c5d0df7d (锂还原室温氧化物缺陷调控)
- step_id: s01
- depend: []

## 场景研究主体
- 锂还原室温氧化物缺陷调控
- 关联论文: Tuning defects in oxides at room temperature by lithium reduction | doi:

## 本实例步骤描述
生成母体和缺陷候选并固定浓度/边界。

## 本实例执行 prompt
根据 {HOST_STRUCTURE} 和 {DEFECT_SET} 建立缺陷候选，定义对照和电荷/化学势参考。

## 本实例输入槽
- {HOST_STRUCTURE} | required=True | type=doc | var_name=母体结构 | hint=CIF/POSCAR、晶面、层数或样品信 | default=CIF/POSCAR
- {DEFECT_SET} | required=True | type=list[str] | var_name=缺陷候选 | hint=空位、掺杂、边缘、晶界或辐照缺陷及浓度。 | default=['specified defects']

## 本实例产出
- 缺陷结构集
- 参考态说明

## 本实例质量门禁
- 缺陷浓度与超胞一致
- 电荷补偿明确

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
