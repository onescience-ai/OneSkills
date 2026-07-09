# 单细胞 RNA 分析工作流

- workflow_id: `single-cell-rna-analysis`

## 适用范围

用于 scRNA-seq 或 snRNA-seq 的 10x matrix/h5、h5ad、Seurat、loom 数据，从 QC、过滤、归一化、HVG、整合、聚类、marker、细胞类型注释到轨迹、标签迁移和 scVI/scANVI 分支。

## 输入

- 必需：10x matrix/h5、h5ad、Seurat object 或 loom；样本/细胞元数据；物种；batch key；condition label。
- 可选：raw counts layer、参考 atlas、marker gene set、spliced/unspliced layer、CITE-seq protein matrix、doublet/ambient RNA 结果。

## 输出

- 过滤后对象。
- QC 表和图。
- normalized representation、PCA/UMAP、clusters。
- marker gene 表、cell type annotation 表。
- integration diagnostics、trajectory/velocity 或 DE 分支结果。

## 流程节点

1. 校验对象结构、raw counts、obs/var、gene ID、mitochondrial/ribosomal gene 命名。
2. 计算 n_genes、total_counts、pct_mito、pct_ribo、doublet、ambient RNA 等 QC 指标。
3. 选择过滤阈值，保留过滤前后统计。
4. 进行 normalization、log transform、HVG、PCA、neighbors、UMAP、clustering。
5. 按 batch 和设计选择是否整合。
6. 生成 marker、参考注释或手动注释。
7. 按需规划 trajectory、RNA velocity、label transfer、cluster DE 或 composition 分析。

## 边界与分流

- bulk RNA-seq 转到 `rnaseq-differential-expression`。
- 空间坐标、ATAC、CITE-seq 或 multiome 转到 `spatial-multiomics-analysis`。
- 只是调用工具脚本或模板时，召回单细胞应用卡即可，不必使用完整工作流。

## 模型与工具选择边界

- 标准 QC/聚类：Scanpy/Seurat 风格方法。
- batch correction：仅在 batch 与生物因素可区分且确有需要时使用。
- scVI：需要 raw integer counts 和 batch covariates。
- scANVI：用于半监督标签迁移。
- CellTypist/PopV 类方法用于参考注释，不能替代 marker 复核。

## 质量检查

- raw counts layer 保留。
- cell/sample metadata 与矩阵对齐。
- doublet、ambient RNA 和 mitochondrial threshold 有说明。
- batch correction 前后生物信号未被过度消除。
- 细胞类型命名有 marker 或 reference 支持。

## 回退策略

- 缺 raw counts：避免 scVI/scANVI，使用 classical branch，并请求 raw counts。
- 缺 metadata：只做 QC、聚类和 marker，不做 condition-level 结论。
- 细胞数过少或 QC 失败：输出失败原因和最小可解释结果。

## 资源召回建议

- 单细胞脚本和模板：`bio_single_cell_analysis_app`。
- 矩阵/元数据检查：`bio_table_qc_biomarker_app`。
- 报告：`bio_qc_report_app`。
