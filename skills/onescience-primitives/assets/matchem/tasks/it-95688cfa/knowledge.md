# 实例任务：Li/Ni 混排与结构稳定性计算 @ LiNiCo_高镍层状正极掺杂结构优化与应变风险分析

- domain: matchem
- 骨架: tk-matchem-89afddd7
- 场景: sc-f94cf8ec (LiNiCo_高镍层状正极掺杂结构优化与应变风险分析)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- LiNiCo_高镍层状正极掺杂结构优化与应变风险分析
- 关联论文: Transition metal-doped Ni-rich layered cathode materials for durable Li-ion batteries | doi:; Additive engineering for robust interphases to stabilize high-Ni layered structures at ultra-high voltage of 4.8 V | doi:; High-nickel layered oxide cathodes for lithium-based automotive batteries | doi:; Origin of structural degradation in Li-rich layered oxide cathode | doi:

## 本实例步骤描述
在母体和掺杂结构中枚举对称不等价的 Li/Ni 交换构型，计算混排能；同时提取脱锂引起的晶格参数、体积和层间距变化。

## 本实例执行 prompt
基于 {RELAXED_STRUCTURES} 构造对称不等价 Li/Ni 混排构型，计算 Emixing=E(mixed)-E(layered)，并统计 Δa、Δc、ΔV、层间距变化；明确 Emixing 的符号约定。

## 本实例输入槽
- {RELAXED_STRUCTURES} | required=True | type=doc | var_name=弛豫结构集合 | hint=s02 输出。 | default={RELAXED_STRUCTURES}
- {LI_CONTENT} | required=True | type=float | var_name=脱锂状态 | hint=用于比较相同 x。 | default={LI_CONTENT}

## 本实例产出
- Li/Ni 混排能表
- 晶格应变与体积变化表
- 结构稳定性对比图

## 本实例质量门禁
- 混排构型与母体参考结构具有相同化学计量
- 能量差采用统一参考零点并保留结构文件
- 不得把较低混排能误报为更稳定的层状结构

## 可调资源（edge:resource，仅真实存在）
- tools/pymatgen

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
