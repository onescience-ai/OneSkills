# 实例任务：准备超胞与动力学测试 @ CO2_Cu111_12C13C_MACE_LAMMPS动力学验证

- domain: matchem
- 骨架: matchem-supercell-preparation-dynamics-testing-task
- 场景: matchem-co2-cu111-water-k-interface-12c-13c-kinetics-verification-scenario (CO2_Cu111_12C13C_MACE_LAMMPS动力学验证)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- CO2_Cu111_12C13C_MACE_LAMMPS动力学验证
- 关联论文: （源场景未提供）

## 本实例步骤描述
由共用优化原胞构建 C12/C13 的 3×3×1 超胞，核对读回映射并验证 LAMMPS 部署的能量和力。

## 本实例执行 prompt
准备 {SUPERCELL} 超胞，依据 {FIXED_CU_PER_CELL} 核对固定 Cu 映射、元素类型、晶胞表示和模型加载条件。

先取得 s01 的共用优化原胞和 s02 的势准入结论。沿九个 `(i,j,0)` 平移建立超胞（`i,j=0,1,2`），面内基矢各放大三倍，第三基矢保持。生成两套输入，保持坐标、晶胞、原子顺序、元素类型、势模型和约束一致，仅改变目标碳位点及其对应周期副本的质量。若 LAMMPS 以类型设质量，目标碳与其他碳须可独立赋值，两套使用相同类型表，所有碳类型均映射到势模型的 C。按实际三斜表示转换原点、基矢、倾斜因子、坐标及 image flags，核对周期几何，并确认体积和各元素计数均为原胞的九倍。若使用档案的 188 原子原胞，单套超胞应有 1692 个原子。

## 本实例输入槽
- {SUPERCELL} | required=True | type=enum | var_name=面内扩胞倍数 | hint=固定为 3×3×1 | default=3x3x1
- {FIXED_CU_PER_CELL} | required=True | type=int | var_name=原胞固定铜数 | hint=底部两层共 32 个 | default=32

## 本实例产出
- C12/C13 超胞
- 固定 Cu 映射
- 晶胞和类型读回检查及 LAMMPS 能量/力比对记录

交付两套实际写盘并读回的 LAMMPS data、固定组和映射清单。每行记录原胞索引及基准、平移元组、唯一输出 ID、元素/类型/质量、模型元素表对应和固定标志。

## 本实例质量门禁
- 扩胞原子数正确
- 固定 Cu 数为 288
- 晶胞与类型映射正确
- LAMMPS 与原模型的能量和力在约定容差内一致

按原胞索引和复制平移逐个核对每套 288 个固定 Cu 的周期位置与读回 ID，验证固定组无缺漏或重复。比较两套读回结果并确认差异仅出现在目标碳质量。以相同目标周期构型和准入模型为基准，对齐单位、原子顺序、笛卡尔坐标系和元素映射，比对两套部署的势能及逐原子力。应在施加清零力等固定操作前取力，归档模型版本与摘要、部署格式、容差依据和实测差值。

## 可调资源（edge:resource，仅真实存在）
- 本卡给出映射和读回要求。通用方法见 [LAMMPS 超胞](../../workflow-planning/matchem-lammps-supercell/knowledge.md)和 [MD 输入审计](../../workflow-planning/matchem-md-input-audit/knowledge.md)。

## 验收/缺失策略（继承场景）
- acceptance: 两套读回的晶胞、类型、质量、逐原子固定组映射及部署能量/力均通过后交接 s04。
- missing_policy: 上游未准入或读回未通过时，交付实际已核验内容、阻断位置和恢复条件。
