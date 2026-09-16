# 实例任务：轨迹与效应质量评估 @ B67

- domain: bio
- 骨架: bio-trajectory-and-effect-quality-evaluation-task
- 场景: bio-cell-type-specific-regulatory-dna-conditional-generation-scenario (B67)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- B67
- 关联论文: Conditional Monte Carlo Tree Diffusion for Designing Cell-Type-Specific and Biologically Faithful Regulatory DNA | doi:

## 本实例步骤描述
计算调控活性提升并导出区间、碱基或变异层结果。

## 本实例执行 prompt
计算调控活性提升，用{SCORE_THRESHOLD}标记显著结果，并按{OUTPUT_LEVEL}导出可追溯记录。

## 本实例输入槽
- {SCORE_THRESHOLD} | required=False | type=float | var_name=结果阈值 | hint=设置显著结果阈值 | default=0.5
- {OUTPUT_LEVEL} | required=False | type=enum | var_name=输出粒度 | hint=选择结果输出粒度 | default=variant

## 本实例产出
- 结果表
- 调控活性提升汇总
- 基因组质控报告

## 本实例质量门禁
- 参考与替代等位可区分
- 输出坐标未越界
- 指标与数据切分匹配

## 可调资源（edge:resource，仅真实存在）
- datasets/tm-score-evaluation

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
