# 实例任务：特异性与可开发性质控 @ B25

- domain: bio
- 骨架: bio-specificity-developability-qc-task
- 场景: bio-antibody-antigen-binding-site-joint-prediction-scenario (B25)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- B25
- 关联论文: CAME-AB: Cross-Modality Attention with Mixture-of-Experts for Antibody Binding Site Prediction | doi:; APLSuite: An Integrated Suite for CD4+ T Cell Epitope Prediction via Antigen Processing Likelihood | doi:

## 本实例步骤描述
按界面AUPRC及序列、结构和特异性指标筛选结果。

## 本实例执行 prompt
计算界面AUPRC和可开发性指标，用{SCORE_THRESHOLD}筛选并保留前{TOP_K}个候选。

## 本实例输入槽
- {SCORE_THRESHOLD} | required=False | type=float | var_name=得分阈值 | hint=设置候选得分下限 | default=0.7
- {TOP_K} | required=False | type=int | var_name=保留数量 | hint=设置最终保留数量 | default=20

## 本实例产出
- 排序候选
- 界面AUPRC结果
- 可开发性报告

## 本实例质量门禁
- 关键CDR未异常截断
- 低特异候选已标记
- 保留规则可复现

## 可调资源（edge:resource，仅真实存在）
- datasets/tm-score-evaluation

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
