# 骨架任务：核验结构与可用资料

- domain: matchem
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 建立或复用 C12/C13 共用的优化原胞，核验初始几何、固定索引和 VASP 收敛。

## 执行 prompt（跨场景聚合去重）
- 核验 {OPTIMIZED_PRIMITIVE_CELL}、{C12_STRUCTURE}、{C13_STRUCTURE} 和 {HISTORICAL_DATA} 中的已有资料。没有合格复用原胞时，在已确认的计算范围内构建并用 VASP 优化，交付共用原胞和收敛证据。

## 输入槽（var/hint/default）
- {OPTIMIZED_PRIMITIVE_CELL} | required=False | type=doc | var_name=共用优化原胞 | hint=提供同体系同约束原胞和同次收敛证据 | default=
- {C12_STRUCTURE} | required=False | type=doc | var_name=C12 初始结构 | hint=已有结构及来源，可供共用原胞核验 | default=
- {C13_STRUCTURE} | required=False | type=doc | var_name=C13 初始结构 | hint=已有结构及来源，可供共用原胞核验 | default=
- {HISTORICAL_DATA} | required=False | type=doc | var_name=历史数据资料 | hint=标明可用性和用途 | default=

## 产出
- 共用优化原胞及收敛证据
- 几何检查与固定 Cu 清单
- 输入审计报告

## 质量门禁 quality_gate
- 体系和原胞来源可追溯
- 几何与固定 Cu 索引通过
- 电子、离子收敛及可动原子残余力通过核验

## 可调资源（edge:resource，仅真实存在）
- datasets/matpl
- models/data-efficient-machine-learning-potentials-modeling-catalytic
- tools/molecular-structure-preparation

## 实例任务（本骨架在各场景的实例化）
- matchem-verifying-structure-available-co2-cu111-water-k-interface-inst

## 复用场景
- CO2_Cu111_12C13C_MACE_LAMMPS动力学验证
