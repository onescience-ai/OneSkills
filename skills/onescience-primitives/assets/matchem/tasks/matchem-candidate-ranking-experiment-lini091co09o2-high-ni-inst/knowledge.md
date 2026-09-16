# 实例任务：候选排序与实验/文献交叉验证 @ LiNiCo_高镍层状正极掺杂结构优化与应变风险分析

- domain: matchem
- 骨架: matchem-candidate-ranking-experiment-literature-cross-validation-task
- 场景: matchem-lini091co09o2-high-ni-layered-cathode-doping-strain-risk-scenario (LiNiCo_高镍层状正极掺杂结构优化与应变风险分析)
- step_id: s05
- depend: ['s04']

## 场景研究主体
- LiNiCo_高镍层状正极掺杂结构优化与应变风险分析
- 关联论文: Transition metal-doped Ni-rich layered cathode materials for durable Li-ion batteries | doi:; Additive engineering for robust interphases to stabilize high-Ni layered structures at ultra-high voltage of 4.8 V | doi:; High-nickel layered oxide cathodes for lithium-based automotive batteries | doi:; Origin of structural degradation in Li-rich layered oxide cathode | doi:

## 本实例步骤描述
按层状结构稳定性、低应变和力学风险代理指标排序，优先输出前 3 个候选；若提供验证数据，则对晶格、相变、循环或裂纹趋势进行独立对照。

## 本实例执行 prompt
依据 {ANALYSIS_TABLES} 对候选排序；有 {VALIDATION_DATA} 时逐项对照，无验证数据时明确写出计算范围和未验证项，输出 PASS、REJECT 或 BLOCKED。

## 本实例输入槽
- {ANALYSIS_TABLES} | required=True | type=doc | var_name=分析结果表 | hint=s03-s04 输出。 | default={ANALYSIS_TABLES}
- {VALIDATION_DATA} | required=False | type=doc | var_name=验证数据 | hint=实验或文献数据；缺失时不做实验结论。 | default={VALIDATION_DATA}

## 本实例产出
- 候选排序与推荐理由
- 结构—掺杂—应变关系
- 可复现实验配置与最终判定

## 本实例质量门禁
- 推荐候选的原始结构、参数和日志齐全
- 未提供实验数据时不得声称已验证开裂强度或循环寿命
- 每个结论都能回溯到 PDF 证据、计算结果或明确假设

## 可调资源（edge:resource，仅真实存在）
- datapipes/xps-nife-oer-surface-analysis
- models/data-efficient-machine-learning-potentials-modeling-catalytic
- models/operando-ct-image-analysis-for-lithium-metal-batteries
- tools/phonopy-phonon-analysis
- tools/pymatgen

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
