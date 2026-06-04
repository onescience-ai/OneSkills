# 功能基因组筛选 QC

## Pooled Screen

- Library representation：每个 sgRNA 的覆盖度和分布。
- Mapping rate：reads 到 sgRNA library 的比率。
- Control guide：non-targeting 和 essential/non-essential positive controls。
- Bottleneck：低复杂度会造成假阳性 dropout。

## Hit Calling

sgRNA-level 变化需聚合到 gene level。记录 normalization、contrast、统计模型、多重检验和 replicate 一致性。

## Perturb-seq

需要 guide assignment、MOI、doublet、cell QC、perturbation efficiency 和 per-perturbation DE。单细胞表达分析与 screen 统计需要清楚分层。
