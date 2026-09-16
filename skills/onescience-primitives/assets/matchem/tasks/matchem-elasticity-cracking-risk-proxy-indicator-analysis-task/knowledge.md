# 骨架任务：弹性与开裂风险代理指标分析

- domain: matchem
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 对通过结构稳定性门限的候选计算弹性响应或应力—应变指标，结合脱锂晶格各向异性和体积变化形成开裂风险代理评分；计算不稳定时只保留可解释的应变指标。

## 执行 prompt（跨场景聚合去重）
- 对 {STABLE_CANDIDATES} 计算 {MECHANICAL_METHOD}，提取弹性常数/应力响应、各向异性、脱锂体积变化和层间距变化；将结构不稳定、未收敛或超出适用域的结果标记 REJECT 或 BLOCKED。

## 输入槽（var/hint/default）
- {STABLE_CANDIDATES} | required=True | type=doc | var_name=稳定候选集合 | hint=s03 输出，包含结构稳定性门限结果。 | default={STABLE_CANDIDATES}
- {MECHANICAL_METHOD} | required=False | type=enum | var_name=力学分析方法 | hint=可选弹性张量或有限应变应力响应；需与结构 | default=elastic_tensor

## 产出
- 开裂风险代理评分及其组成
- 弹性或应力—应变指标
- 脱锂应变各向异性表

## 质量门禁 quality_gate
- 开裂风险代理不得表述为已完成实验断裂强度测量
- 弹性常数满足所采用晶体稳定性判据或明确标记失败
- 风险评分可追溯到混排能、ΔV 和各向异性等原始量

## 可调资源（edge:resource，仅真实存在）
- datasets/stable-active-co2-reduction-formate-redox-modulated
- models/computational-screening-for-thermodynamically-stable-mxenes
- models/strain-tuning-method-for-hbn-quantum-emitters
- tools/pymatgen
- tools/rapid-inverse-design-metamaterials-prescribed-mechanical-behavior

## 实例任务（本骨架在各场景的实例化）
- matchem-elasticity-cracking-risk-lini091co09o2-high-ni-inst

## 复用场景
- LiNiCo_高镍层状正极掺杂结构优化与应变风险分析
