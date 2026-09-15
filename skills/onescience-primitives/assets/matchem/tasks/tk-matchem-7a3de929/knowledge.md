# 骨架任务：不同脱锂状态下的 VASP 结构弛豫

- domain: matchem
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 对母体和每个掺杂候选，在满锂与目标深度脱锂状态下使用统一 VASP 设置弛豫晶胞和原子位置，保存总能、晶格参数、体积和应力。

## 执行 prompt（跨场景聚合去重）
- 使用 VASP 按 {DFT_CONFIG} 对 {CANDIDATE_STRUCTURES} 在 x=1 和 x={LI_CONTENT} 下分别弛豫；记录 OUTCAR、CONTCAR、总能、晶格和应力，不得比较不同收敛标准的结果。

## 输入槽（var/hint/default）
- {CANDIDATE_STRUCTURES} | required=True | type=doc | var_name=候选结构集合 | hint=s01 输出。 | default={CANDIDATE_STRUCTURES}
- {LI_CONTENT} | required=True | type=float | var_name=脱锂状态 | hint=Li_x 化学计量数。 | default={LI_CONTENT}
- {DFT_CONFIG} | required=True | type=object | var_name=DFT 设置 | hint=统一的 VASP 参数。 | default={DFT_CONFIG}

## 产出
- 应力和收敛日志
- 弛豫后 CONTCAR/POSCAR
- 总能与晶格参数表

## 质量门禁 quality_gate
- 弛豫后无明显非物理短键或未处理的自旋/电荷状态
- 所有候选使用一致的泛函、U、赝势、ENCUT 和 K 点标准
- 电子步和离子步均达到设定收敛标准

## 可调资源（edge:resource，仅真实存在）
- tools/pymatgen

## 实例任务（本骨架在各场景的实例化）
- it-c7a51d14

## 复用场景
- LiNiCo_高镍层状正极掺杂结构优化与应变风险分析
