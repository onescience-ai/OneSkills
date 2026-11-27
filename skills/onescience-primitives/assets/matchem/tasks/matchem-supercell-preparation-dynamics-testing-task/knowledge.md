# 骨架任务：准备超胞与动力学测试

- domain: matchem
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 由共用优化原胞构建两套 3×3×1 超胞，核对目标碳质量、逐原子固定映射和 LAMMPS 部署等价性。

## 执行 prompt（跨场景聚合去重）
- 按 {SUPERCELL} 和 {FIXED_CU_PER_CELL} 逐原子核验每套 288 个固定 Cu。两套输入仅改变目标碳质量，读回检查三斜晶胞和元素/模型映射，验证部署势能与逐原子力。

## 输入槽（var/hint/default）
- {SUPERCELL} | required=True | type=enum | var_name=面内扩胞倍数 | hint=固定为 3×3×1 | default=3x3x1
- {FIXED_CU_PER_CELL} | required=True | type=int | var_name=原胞固定铜数 | hint=底部两层共 32 个 | default=32

## 产出
- C12/C13 超胞
- 固定 Cu 映射
- 晶胞和类型读回检查及 LAMMPS 能量/力比对记录

## 质量门禁 quality_gate
- 固定 Cu 数为 288
- 扩胞原子数正确
- 晶胞与类型映射正确
- 部署能量和力在约定容差内一致

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- matchem-supercell-preparation-co2-cu111-water-k-interface-inst

## 复用场景
- CO2_Cu111_12C13C_MACE_LAMMPS动力学验证
