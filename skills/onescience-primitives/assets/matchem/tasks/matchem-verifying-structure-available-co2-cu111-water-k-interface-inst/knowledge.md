# 实例任务：核验结构与可用资料 @ CO2_Cu111_12C13C_MACE_LAMMPS动力学验证

- domain: matchem
- 骨架: matchem-verifying-structure-available-data-task
- 场景: matchem-co2-cu111-water-k-interface-12c-13c-kinetics-verification-scenario (CO2_Cu111_12C13C_MACE_LAMMPS动力学验证)
- step_id: s01
- depend: []

## 场景研究主体
- CO2_Cu111_12C13C_MACE_LAMMPS动力学验证
- 关联论文: （源场景未提供）

## 本实例步骤描述
核对 C12/C13 结构、DFT 收敛状态、AIMD 数据、训练数据和历史资料，区分正式输入与参考资料。

## 本实例执行 prompt
审计 {C12_STRUCTURE}、{C13_STRUCTURE} 和 {HISTORICAL_DATA}，输出正式输入清单、异常排除项和待确认问题。

## 本实例输入槽
- {C12_STRUCTURE} | required=True | type=doc | var_name=C12 初始结构 | hint=提供结构及来源说明 | default=
- {C13_STRUCTURE} | required=True | type=doc | var_name=C13 初始结构 | hint=提供结构及来源说明 | default=
- {HISTORICAL_DATA} | required=False | type=doc | var_name=历史数据资料 | hint=标明可用性和用途 | default=

## 本实例产出
- 输入审计报告
- 结构质量检查
- 待确认清单

## 本实例质量门禁
- 结构来源可追溯
- 异常 AIMD 数据已标识
- 正式输入已确认

## 可调资源（edge:resource，仅真实存在）
- datasets/matpl
- models/data-efficient-machine-learning-potentials-modeling-catalytic
- tools/molecular-structure-preparation

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
