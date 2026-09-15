# 实例任务：母体结构检查与掺杂候选建模 @ LiNiCo_高镍层状正极掺杂结构优化与应变风险分析

- domain: matchem
- 骨架: tk-matchem-883c63a1
- 场景: sc-f94cf8ec (LiNiCo_高镍层状正极掺杂结构优化与应变风险分析)
- step_id: s01
- depend: []

## 场景研究主体
- LiNiCo_高镍层状正极掺杂结构优化与应变风险分析
- 关联论文: Transition metal-doped Ni-rich layered cathode materials for durable Li-ion batteries | doi:; Additive engineering for robust interphases to stabilize high-Ni layered structures at ultra-high voltage of 4.8 V | doi:; High-nickel layered oxide cathodes for lithium-based automotive batteries | doi:; Origin of structural degradation in Li-rich layered oxide cathode | doi:

## 本实例步骤描述
读取 Li[Ni0.91Co0.09]O2 结构，检查层状堆垛、元素占位和 Li/Ni 位点；按统一比例生成 Mg、Al、Ti、Ta、Mo 掺杂候选，并记录每个替位构型。

## 本实例执行 prompt
读取 {PARENT_STRUCTURE}，核对 Li、Ni、Co、O 的元素顺序和层状结构；按照 {DOPANT_SET} 与 {DOPANT_RATIO} 生成候选。无法由输入确定的氧化态、电荷补偿或替位位点写 BLOCKED，不得猜测。

## 本实例输入槽
- {PARENT_STRUCTURE} | required=True | type=doc | var_name=母体结构文件 | hint=CIF/POSCAR 及来源。 | default={PARENT_STRUCTURE}
- {DOPANT_SET} | required=True | type=list[str] | var_name=掺杂集合 | hint=元素、氧化态和替位位点。 | default={DOPANT_SET}
- {DOPANT_RATIO} | required=True | type=list[float] | var_name=掺杂比例 | hint=统一化学计量定义。 | default={DOPANT_RATIO}

## 本实例产出
- 候选结构 POSCAR/CIF
- 构型与化学计量清单
- 建模日志

## 本实例质量门禁
- 所有候选结构元素守恒且无明显原子重叠
- 层状母体和掺杂位点可追溯
- 电荷补偿未定义时输出 BLOCKED 而非静默假设

## 可调资源（edge:resource，仅真实存在）
- tools/pymatgen

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
