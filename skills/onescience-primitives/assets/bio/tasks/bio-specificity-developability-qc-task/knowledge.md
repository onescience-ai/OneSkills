# 骨架任务：特异性与可开发性质控

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 按AUROC及序列、结构和特异性指标筛选结果。
- 按CDR-RMSD及序列、结构和特异性指标筛选结果。
- 按Spearman相关及序列、结构和特异性指标筛选结果。
- 按亲和力提升及序列、结构和特异性指标筛选结果。
- 按功能成功率及序列、结构和特异性指标筛选结果。
- 按序列恢复率及序列、结构和特异性指标筛选结果。
- 按界面AUPRC及序列、结构和特异性指标筛选结果。
- 按界面RMSD及序列、结构和特异性指标筛选结果。
- 按结合分数及序列、结构和特异性指标筛选结果。
- 按表位AUPRC及序列、结构和特异性指标筛选结果。

## 执行 prompt（跨场景聚合去重）
- 计算AUROC和可开发性指标，用{SCORE_THRESHOLD}筛选并保留前{TOP_K}个候选。
- 计算CDR-RMSD和可开发性指标，用{SCORE_THRESHOLD}筛选并保留前{TOP_K}个候选。
- 计算Spearman相关和可开发性指标，用{SCORE_THRESHOLD}筛选并保留前{TOP_K}个候选。
- 计算亲和力提升和可开发性指标，用{SCORE_THRESHOLD}筛选并保留前{TOP_K}个候选。
- 计算功能成功率和可开发性指标，用{SCORE_THRESHOLD}筛选并保留前{TOP_K}个候选。
- 计算序列恢复率和可开发性指标，用{SCORE_THRESHOLD}筛选并保留前{TOP_K}个候选。
- 计算界面AUPRC和可开发性指标，用{SCORE_THRESHOLD}筛选并保留前{TOP_K}个候选。
- 计算界面RMSD和可开发性指标，用{SCORE_THRESHOLD}筛选并保留前{TOP_K}个候选。
- 计算结合分数和可开发性指标，用{SCORE_THRESHOLD}筛选并保留前{TOP_K}个候选。
- 计算表位AUPRC和可开发性指标，用{SCORE_THRESHOLD}筛选并保留前{TOP_K}个候选。

## 输入槽（var/hint/default）
- {SCORE_THRESHOLD} | required=False | type=float | var_name=得分阈值 | hint=设置候选得分下限 | default=0.7
- {TOP_K} | required=False | type=int | var_name=保留数量 | hint=设置最终保留数量 | default=20

## 产出
- AUROC结果
- CDR-RMSD结果
- Spearman相关结果
- 亲和力提升结果
- 功能成功率结果
- 可开发性报告
- 序列恢复率结果
- 排序候选
- 界面AUPRC结果
- 界面RMSD结果
- 结合分数结果
- 表位AUPRC结果

## 质量门禁 quality_gate
- 低特异候选已标记
- 保留规则可复现
- 关键CDR未异常截断

## 可调资源（edge:resource，仅真实存在）
- datasets/tm-score-evaluation

## 实例任务（本骨架在各场景的实例化）
- bio-specificity-developability-qc-affinity-optimized-structure-inst
- bio-specificity-developability-qc-antibody-antigen-binding-inst
- bio-specificity-developability-qc-antigen-conditioned-full-inst
- bio-specificity-developability-qc-antigen-specific-multimodal-inst
- bio-specificity-developability-qc-cd4-t-cell-epitope-processin-inst
- bio-specificity-developability-qc-cdr-loop-antibody-scaffold-inst
- bio-specificity-developability-qc-interpretable-tcr-epitope-inst
- bio-specificity-developability-qc-reinforcement-learning-inst
- bio-specificity-developability-qc-sars-cov-2-antibody-binding-inst
- bio-specificity-developability-qc-structure-retrieval-augmente-inst

## 复用场景
- B26
- B22
- B28
- B27
- B23
- B25
- B21
- B30
- B29
- B24
