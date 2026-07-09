# RNA-seq 差异表达工作流

- workflow_id: `rnaseq-differential-expression`

## 适用范围

用于 bulk RNA-seq 从 FASTQ 或 raw count matrix 到定量、差异表达、可视化和通路富集前置结果的规划。典型触发包括 RNA-seq、DESeq2、edgeR、PyDESeq2、Salmon、STAR、featureCounts、tximport、contrast、差异基因、火山图、MA 图和热图。

## 输入

- 必需：FASTQ 或 raw integer count matrix；样本元数据；实验分组；contrast；物种和参考版本。
- FASTQ 分支必需：reference genome/transcriptome、GTF/GFF 注释、链特异性信息或检查计划。
- 可选：batch/covariates、paired design、重复信息、gene set/pathway 数据库、已有 MultiQC 或定量结果。

## 输出

- count table 或 transcript/gene 汇总矩阵。
- 差异表达结果表：log2 fold change、p value、adjusted p value、过滤阈值。
- PCA、sample distance、dispersion、volcano、MA、heatmap 等图。
- 方法记录、QC 报告、富集分析输入表。

## 流程节点

1. 校验样本表、contrast、batch、paired design 和 count 列名是否一致。
2. 若输入为 FASTQ，规划 read QC、adapter trimming、污染/重复/链特异性检查。
3. 选择定量路线：alignment + featureCounts，或 Salmon/Kallisto + transcript-to-gene 汇总。
4. 构建 count-based 统计模型，执行过滤、归一化、离散度估计、差异检验和多重检验校正。
5. 生成探索性图和差异结果图，标记异常样本和批次影响。
6. 输出结果、参数、参考版本、软件版本和可复现报告。

## 边界与分流

- 单细胞或单核 RNA-seq 转到 `single-cell-rna-analysis`。
- 空间转录组或 multiome 转到 `spatial-multiomics-analysis`。
- 只有 normalized TPM/FPKM 时，不做 DESeq2/edgeR 结论；只能规划探索性分析并请求 raw counts。
- 转录后调控、剪接、Ribo-seq 或 m6A 转到 `post-transcriptional-regulation`。

## 模型与工具选择边界

- raw counts + 常规设计：DESeq2、edgeR 或 PyDESeq2。
- 大型线性模型或连续协变量较多：limma-voom 可作为备选。
- transcript-level quantification：Salmon/Kallisto 后再做 transcript-to-gene 汇总。
- 不使用单细胞 marker test 替代 bulk RNA-seq 差异模型。

## 质量检查

- 样本元数据与矩阵列完全对齐。
- read 质量、adapter content、duplication、mapping/assignment rate、library size、strandedness 可解释。
- PCA/样本距离图中异常样本有记录。
- dispersion trend 和 size factor 合理。
- contrast、batch 和协变量已确认。

## 回退策略

- 缺 contrast：只规划 QC 和探索性分析，要求补充 contrast。
- 缺 raw counts：不输出正式 DE 结论，请求 raw count matrix。
- 样本量不足或无重复：标记统计功效不足，只输出描述性差异和风险。

## 资源召回建议

- 模板：`bio_workflow_template_app`。
- R/Python/Bioconductor 交接：`bio_analysis_toolkit_app`。
- 报告：`bio_qc_report_app`。
