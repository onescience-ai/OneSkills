# 骨架任务：轨迹与效应质量评估

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 计算分类准确率并导出区间、碱基或变异层结果。
- 计算宏平均F1并导出区间、碱基或变异层结果。
- 计算干预效应并导出区间、碱基或变异层结果。
- 计算平均精度并导出区间、碱基或变异层结果。
- 计算序列似然并导出区间、碱基或变异层结果。
- 计算目标活性达成率并导出区间、碱基或变异层结果。
- 计算综合排名并导出区间、碱基或变异层结果。
- 计算调控活性提升并导出区间、碱基或变异层结果。
- 计算轨迹相关性并导出区间、碱基或变异层结果。

## 执行 prompt（跨场景聚合去重）
- 计算分类准确率，用{SCORE_THRESHOLD}标记显著结果，并按{OUTPUT_LEVEL}导出可追溯记录。
- 计算宏平均F1，用{SCORE_THRESHOLD}标记显著结果，并按{OUTPUT_LEVEL}导出可追溯记录。
- 计算干预效应，用{SCORE_THRESHOLD}标记显著结果，并按{OUTPUT_LEVEL}导出可追溯记录。
- 计算平均精度，用{SCORE_THRESHOLD}标记显著结果，并按{OUTPUT_LEVEL}导出可追溯记录。
- 计算序列似然，用{SCORE_THRESHOLD}标记显著结果，并按{OUTPUT_LEVEL}导出可追溯记录。
- 计算目标活性达成率，用{SCORE_THRESHOLD}标记显著结果，并按{OUTPUT_LEVEL}导出可追溯记录。
- 计算综合排名，用{SCORE_THRESHOLD}标记显著结果，并按{OUTPUT_LEVEL}导出可追溯记录。
- 计算调控活性提升，用{SCORE_THRESHOLD}标记显著结果，并按{OUTPUT_LEVEL}导出可追溯记录。
- 计算轨迹相关性，用{SCORE_THRESHOLD}标记显著结果，并按{OUTPUT_LEVEL}导出可追溯记录。

## 输入槽（var/hint/default）
- {SCORE_THRESHOLD} | required=False | type=float | var_name=结果阈值 | hint=设置显著结果阈值 | default=0.5
- {OUTPUT_LEVEL} | required=False | type=enum | var_name=输出粒度 | hint=选择结果输出粒度 | default=variant

## 产出
- 分类准确率汇总
- 基因组质控报告
- 宏平均F1汇总
- 干预效应汇总
- 平均精度汇总
- 序列似然汇总
- 目标活性达成率汇总
- 结果表
- 综合排名汇总
- 调控活性提升汇总
- 轨迹相关性汇总

## 质量门禁 quality_gate
- 参考与替代等位可区分
- 指标与数据切分匹配
- 输出坐标未越界

## 可调资源（edge:resource，仅真实存在）
- datasets/tm-score-evaluation

## 实例任务（本骨架在各场景的实例化）
- bio-trajectory-and-effect-quality-bidirectional-equivariant-inst
- bio-trajectory-and-effect-quality-cell-type-specific-regulator-inst
- bio-trajectory-and-effect-quality-dna-language-model-biologica-inst
- bio-trajectory-and-effect-quality-genomic-language-model-inst
- bio-trajectory-and-effect-quality-histone-modification-driven-inst
- bio-trajectory-and-effect-quality-long-dna-interval-multi-inst
- bio-trajectory-and-effect-quality-million-base-context-genome-inst
- bio-trajectory-and-effect-quality-multi-species-dna-sequence-inst
- bio-trajectory-and-effect-quality-rice-breeding-variant-inst
- bio-trajectory-and-effect-quality-simplex-flow-matching-inst

## 复用场景
- B65
- B70
- B64
- B66
- B63
- B69
- B62
- B68
- B67
- B61
