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
建立或复用 C12/C13 共用的优化原胞，核验结构质量、DFT 收敛及历史资料的适用性。

## 本实例执行 prompt
审计 {OPTIMIZED_PRIMITIVE_CELL}、{C12_STRUCTURE}、{C13_STRUCTURE} 和 {HISTORICAL_DATA} 中实际提供的资料。复用同体系、同约束且证据完整的优化原胞，或在已确认的计算范围内构建并优化。输出共用优化原胞、收敛证据、正式输入清单及异常排除项。

## 本实例输入槽
- {OPTIMIZED_PRIMITIVE_CELL} | required=False | type=doc | var_name=共用优化原胞 | hint=提供同体系同约束原胞和同次收敛证据 | default=
- {C12_STRUCTURE} | required=False | type=doc | var_name=C12 初始结构 | hint=已有结构及来源，可供共用原胞核验 | default=
- {C13_STRUCTURE} | required=False | type=doc | var_name=C13 初始结构 | hint=已有结构及来源，可供共用原胞核验 | default=
- {HISTORICAL_DATA} | required=False | type=doc | var_name=历史数据资料 | hint=标明可用性和用途 | default=

从头建模时，构建周期性 Cu(111) 基底，布置显式水、CO₂ 和 K，记录组成、覆盖度（含定义）、晶胞、各方向周期边界、体系净电荷和电极边界条件。提交前按周期最小镜像检查原子间距和重叠，核对溶剂分子几何及底部两层共 32 个 Cu 的固定索引。保存索引基准和原子顺序，检查 VASP 的 Selective dynamics 标记与固定清单一致。

几何通过后用 VASP 优化。保存优化输入、最终结构和同次日志，按实际设置核验电子收敛、离子优化终止原因及可动原子最大残余力与验收阈值，同时核查固定 Cu 位置。复用原胞时按相同口径审计体系、约束、最终几何和收敛记录。异常终止 AIMD 的末帧禁止用作初始结构。

核对提供结构的元素、坐标、晶胞、PBC、原子顺序及目标碳位点，给出唯一的共用优化原胞与目标碳映射。两个同位素条件的质量在 s03 配置。188 个原子和一基碳 ID 81 仅作为相应历史档案的核对值。

## 本实例产出
- 输入审计报告
- 共用优化原胞及收敛证据
- 几何检查与固定 Cu 清单

交接共用原胞的路径、版本或文件摘要、建模条件、原子顺序、目标碳位点、固定 Cu 清单和同次收敛依据。登记参考和排除的资料及原因，保留最后健康材料。

## 本实例质量门禁
- 体系和原胞来源可追溯
- 几何与固定 Cu 索引通过
- 电子、离子收敛及可动原子残余力通过核验

复用记录须对应实际交付的同一原胞。文件可读性和摘要用于验证文件身份，几何和收敛须结合原始输出核验。

## 可调资源（edge:resource，仅真实存在）
- datasets/matpl
- models/data-efficient-machine-learning-potentials-modeling-catalytic
- tools/molecular-structure-preparation

## 验收/缺失策略（继承场景）
- acceptance: 正式结构须可追溯且质量通过，保持 3×3×1、32→288 固定 Cu 和 C12/C13 仅碳质量变化的比较约束；依据证据分别判为 PASS、PARTIAL、REJECT 或 BLOCKED。
- missing_policy: 无合格可复用原胞时，按已确认范围构建并优化。必要建模条件、计算资源或收敛证据缺失时，记录阻断位置、最后健康材料和恢复条件，继续可行的资料审计。
