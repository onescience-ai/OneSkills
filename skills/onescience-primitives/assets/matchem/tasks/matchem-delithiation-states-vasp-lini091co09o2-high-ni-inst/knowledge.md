# 实例任务：不同脱锂状态下的 VASP 结构弛豫 @ LiNiCo_高镍层状正极掺杂结构优化与应变风险分析

- domain: matchem
- 骨架: matchem-delithiation-states-vasp-structural-relaxation-task
- 场景: matchem-lini091co09o2-high-ni-layered-cathode-doping-strain-risk-scenario (LiNiCo_高镍层状正极掺杂结构优化与应变风险分析)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- LiNiCo_高镍层状正极掺杂结构优化与应变风险分析
- 关联论文: Transition metal-doped Ni-rich layered cathode materials for durable Li-ion batteries | doi:; Additive engineering for robust interphases to stabilize high-Ni layered structures at ultra-high voltage of 4.8 V | doi:; High-nickel layered oxide cathodes for lithium-based automotive batteries | doi:; Origin of structural degradation in Li-rich layered oxide cathode | doi:

## 本实例步骤描述
对母体和每个掺杂候选，在满锂与目标深度脱锂状态下使用统一 VASP 设置弛豫晶胞和原子位置，保存总能、晶格参数、体积和应力。

## 本实例执行 prompt
使用 VASP 按 {DFT_CONFIG} 对 {CANDIDATE_STRUCTURES} 在 x=1 和 x={LI_CONTENT} 下分别弛豫；记录 OUTCAR、CONTCAR、总能、晶格和应力，不得比较不同收敛标准的结果。

## 本实例输入槽
- {CANDIDATE_STRUCTURES} | required=True | type=doc | var_name=候选结构集合 | hint=s01 输出。 | default={CANDIDATE_STRUCTURES}
- {LI_CONTENT} | required=True | type=float | var_name=脱锂状态 | hint=Li_x 化学计量数。 | default={LI_CONTENT}
- {DFT_CONFIG} | required=True | type=object | var_name=DFT 设置 | hint=统一的 VASP 参数。 | default={DFT_CONFIG}

## 本实例产出
- 弛豫后 CONTCAR/POSCAR
- 总能与晶格参数表
- 应力和收敛日志

## 本实例质量门禁
- 电子步和离子步均达到设定收敛标准
- 所有候选使用一致的泛函、U、赝势、ENCUT 和 K 点标准
- 弛豫后无明显非物理短键或未处理的自旋/电荷状态

## 可调资源（edge:resource，仅真实存在）
- tools/molecular-structure-preparation
- tools/pymatgen

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
