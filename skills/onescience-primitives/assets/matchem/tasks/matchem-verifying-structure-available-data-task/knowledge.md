# 骨架任务：核验结构与可用资料

- domain: matchem
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 核对 C12/C13 结构、DFT 收敛状态、AIMD 数据、训练数据和历史资料，区分正式输入与参考资料。

## 执行 prompt（跨场景聚合去重）
- 审计 {C12_STRUCTURE}、{C13_STRUCTURE} 和 {HISTORICAL_DATA}，输出正式输入清单、异常排除项和待确认问题。

## 输入槽（var/hint/default）
- {C12_STRUCTURE} | required=True | type=doc | var_name=C12 初始结构 | hint=提供结构及来源说明 | default=
- {C13_STRUCTURE} | required=True | type=doc | var_name=C13 初始结构 | hint=提供结构及来源说明 | default=
- {HISTORICAL_DATA} | required=False | type=doc | var_name=历史数据资料 | hint=标明可用性和用途 | default=

## 产出
- 待确认清单
- 结构质量检查
- 输入审计报告

## 质量门禁 quality_gate
- 异常 AIMD 数据已标识
- 正式输入已确认
- 结构来源可追溯

## 可调资源（edge:resource，仅真实存在）
- datasets/matpl
- models/data-efficient-machine-learning-potentials-modeling-catalytic
- tools/molecular-structure-preparation

## 实例任务（本骨架在各场景的实例化）
- matchem-verifying-structure-available-co2-cu111-water-k-interface-inst

## 复用场景
- CO2_Cu111_12C13C_MACE_LAMMPS动力学验证
