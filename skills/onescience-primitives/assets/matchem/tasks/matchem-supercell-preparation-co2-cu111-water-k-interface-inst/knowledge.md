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
构建 C12/C13 的 3×3 面内超胞，核对三斜晶胞、元素映射、模型映射及底部两层 Cu 固定约束。

## 本实例执行 prompt
准备 {SUPERCELL} 超胞，依据 {FIXED_CU_PER_CELL} 核对固定 Cu 映射、元素类型、晶胞表示和模型加载条件。

## 本实例输入槽
- {SUPERCELL} | required=True | type=enum | var_name=面内扩胞倍数 | hint=固定为 3×3×1 | default=3x3x1
- {FIXED_CU_PER_CELL} | required=True | type=int | var_name=原胞固定铜数 | hint=底部两层共 32 个 | default=32

## 本实例产出
- C12/C13 超胞
- 固定 Cu 映射
- 提交前预检报告

## 本实例质量门禁
- 扩胞原子数正确
- 固定 Cu 数为 288
- 晶胞与类型映射正确

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
