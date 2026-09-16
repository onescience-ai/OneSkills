# 实例任务：缺陷模型与对照定义 @ 磷烯单层缺陷工程与空气稳定化

- domain: matchem
- 骨架: matchem-defect-model-and-control-definition-task
- 场景: matchem-phosphorene-monolayer-defect-engineering-air-stability-scenario (磷烯单层缺陷工程与空气稳定化)
- step_id: s01
- depend: []

## 场景研究主体
- 磷烯单层缺陷工程与空气稳定化
- 关联论文: Producing air-stable monolayers of phosphorene and their defect engineering | doi:

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
- models/dft-calculation-of-defect-formation-energy
- tools/molecular-structure-preparation

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
