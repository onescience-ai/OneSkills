# 实例任务：弹性与开裂风险代理指标分析 @ LiNiCo_高镍层状正极掺杂结构优化与应变风险分析

- domain: matchem
- 骨架: matchem-elasticity-cracking-risk-proxy-indicator-analysis-task
- 场景: matchem-lini091co09o2-high-ni-layered-cathode-doping-strain-risk-scenario (LiNiCo_高镍层状正极掺杂结构优化与应变风险分析)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- LiNiCo_高镍层状正极掺杂结构优化与应变风险分析
- 关联论文: Transition metal-doped Ni-rich layered cathode materials for durable Li-ion batteries | doi:; Additive engineering for robust interphases to stabilize high-Ni layered structures at ultra-high voltage of 4.8 V | doi:; High-nickel layered oxide cathodes for lithium-based automotive batteries | doi:; Origin of structural degradation in Li-rich layered oxide cathode | doi:

## 本实例步骤描述
对通过结构稳定性门限的候选计算弹性响应或应力—应变指标，结合脱锂晶格各向异性和体积变化形成开裂风险代理评分；计算不稳定时只保留可解释的应变指标。

## 本实例执行 prompt
对 {STABLE_CANDIDATES} 计算 {MECHANICAL_METHOD}，提取弹性常数/应力响应、各向异性、脱锂体积变化和层间距变化；将结构不稳定、未收敛或超出适用域的结果标记 REJECT 或 BLOCKED。

## 本实例输入槽
- {STABLE_CANDIDATES} | required=True | type=doc | var_name=稳定候选集合 | hint=s03 输出，包含结构稳定性门限结果。 | default={STABLE_CANDIDATES}
- {MECHANICAL_METHOD} | required=False | type=enum | var_name=力学分析方法 | hint=可选弹性张量或有限应变应力响应；需与结构 | default=elastic_tensor

## 本实例产出
- 弹性或应力—应变指标
- 脱锂应变各向异性表
- 开裂风险代理评分及其组成

## 本实例质量门禁
- 弹性常数满足所采用晶体稳定性判据或明确标记失败
- 风险评分可追溯到混排能、ΔV 和各向异性等原始量
- 开裂风险代理不得表述为已完成实验断裂强度测量

## 可调资源（edge:resource，仅真实存在）
- datasets/stable-active-co2-reduction-formate-redox-modulated
- models/computational-screening-for-thermodynamically-stable-mxenes
- models/strain-tuning-method-for-hbn-quantum-emitters
- tools/pymatgen
- tools/rapid-inverse-design-metamaterials-prescribed-mechanical-behavior

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
