# 矩阵和特征表规则

## 方向

Bulk RNA-seq count matrix 常见是 feature x sample；机器学习 feature table 常见是 sample x feature；AnnData 常见是 obs x var。交接物必须明确方向。

## 数值类型

Raw counts 适合 DESeq2/edgeR 等计数模型；TPM/CPM/log normalized 适合可视化或部分 ML，但不应当作 raw counts 输入计数模型。

## ID 映射

Ensembl 版本号、gene symbol 别名、Entrez ID 和 protein accession 不能无损一一映射。合并前要记录丢失、重复和多对一规则。

## Metadata join

样本列顺序必须与 metadata 一致。任何缺失、重复或多余样本都要作为 QC flag。
