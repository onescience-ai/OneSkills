# 群体遗传和 GWAS QC

## 样本 QC

- missingness、sex discordance、heterozygosity outlier、relatedness、duplicate。
- PCA/admixture 用于 ancestry outlier 和 population stratification。
- Case/control 不平衡时需记录模型和校正方法。

## 变异 QC

- MAF、call rate、HWE、imputation INFO/R2、allele coding、strand ambiguity。
- LD pruning 用于 PCA，不应直接替代关联分析变异集。

## GWAS 输出

结果表至少包含 variant id、chrom、pos、effect allele、other allele、beta/OR、SE、P、N、INFO。Manhattan 和 QQ 需要记录 lambda GC 和有效样本数。
