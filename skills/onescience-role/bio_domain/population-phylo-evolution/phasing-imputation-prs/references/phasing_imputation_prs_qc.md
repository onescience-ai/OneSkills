# Phasing、Imputation 和 PRS QC

## Harmonization

在 phasing 或 imputation 前确认 genome build、chromosome naming、REF/ALT、effect allele、strand 和 ambiguous A/T C/G SNP 处理。

## Imputation QC

记录 reference panel、population match、chunk、INFO/R2 threshold 和 post-imputation MAF。低质量 dosage 不应用于 PRS 或关联分析。

## PRS

PRS 需要 summary stats 与目标 genotype 的 allele harmonization。模型表现应报告 AUC、R2、校准、分层表现和 ancestry 限制。
