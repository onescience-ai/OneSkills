# 骨架任务：基因组预测或序列生成

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 批量执行轨迹、分类、变异评分或条件生成。

## 执行 prompt（跨场景聚合去重）
- 以批次{BATCH_SIZE}和种子{SEED}运行DNA语言模型生物任务基准评测，分别输出{CELL_CONTEXTS}上下文的结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行单纯形流匹配的调控DNA序列设计，分别输出{CELL_CONTEXTS}上下文的结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行双向等变长程DNA序列建模，分别输出{CELL_CONTEXTS}上下文的结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行基因组语言模型中转录因子特征的因果解析，分别输出{CELL_CONTEXTS}上下文的结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行多物种DNA序列表征与下游分类，分别输出{CELL_CONTEXTS}上下文的结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行水稻育种变异功能效应优先级预测，分别输出{CELL_CONTEXTS}上下文的结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行百万碱基上下文基因组建模与序列设计，分别输出{CELL_CONTEXTS}上下文的结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行组蛋白修饰驱动的基因表达预测，分别输出{CELL_CONTEXTS}上下文的结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行细胞类型特异调控DNA条件生成，分别输出{CELL_CONTEXTS}上下文的结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行长DNA区间多组学轨迹与变异效应预测，分别输出{CELL_CONTEXTS}上下文的结果。

## 输入槽（var/hint/default）
- {BATCH_SIZE} | required=True | type=int | var_name=批次大小 | hint=设置序列批次大小 | default=8
- {CELL_CONTEXTS} | required=False | type=list[str] | var_name=细胞上下文 | hint=选择组织或细胞类型 | default=['K562', 'HepG2']
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定生成或评测结果 | default=2025

## 产出
- 变异或生成分数
- 基因组预测
- 运行日志

## 质量门禁 quality_gate
- 数值无NaN或Inf
- 正反链结果已对齐
- 每个区间均有结果

## 可调资源（edge:resource，仅真实存在）
- models/proteinmpnn

## 实例任务（本骨架在各场景的实例化）
- bio-genome-prediction-sequence-bidirectional-equivariant-inst
- bio-genome-prediction-sequence-cell-type-specific-regulator-inst
- bio-genome-prediction-sequence-dna-language-model-biologica-inst
- bio-genome-prediction-sequence-genomic-language-model-inst
- bio-genome-prediction-sequence-histone-modification-driven-inst
- bio-genome-prediction-sequence-long-dna-interval-multi-inst
- bio-genome-prediction-sequence-million-base-context-genome-inst
- bio-genome-prediction-sequence-multi-species-dna-sequence-inst
- bio-genome-prediction-sequence-rice-breeding-variant-inst
- bio-genome-prediction-sequence-simplex-flow-matching-inst

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
