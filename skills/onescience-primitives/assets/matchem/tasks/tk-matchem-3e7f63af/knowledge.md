# 骨架任务：准备超胞与动力学测试

- domain: matchem
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 构建 C12/C13 的 3×3 面内超胞，核对三斜晶胞、元素映射、模型映射及底部两层 Cu 固定约束。

## 执行 prompt（跨场景聚合去重）
- 准备 {SUPERCELL} 超胞，依据 {FIXED_CU_PER_CELL} 核对固定 Cu 映射、元素类型、晶胞表示和模型加载条件。

## 输入槽（var/hint/default）
- {SUPERCELL} | required=True | type=enum | var_name=面内扩胞倍数 | hint=固定为 3×3×1 | default=3x3x1
- {FIXED_CU_PER_CELL} | required=True | type=int | var_name=原胞固定铜数 | hint=底部两层共 32 个 | default=32

## 产出
- C12/C13 超胞
- 固定 Cu 映射
- 提交前预检报告

## 质量门禁 quality_gate
- 固定 Cu 数为 288
- 扩胞原子数正确
- 晶胞与类型映射正确

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-4f013a4e

## 复用场景
- CO2_Cu111_12C13C_MACE_LAMMPS动力学验证
