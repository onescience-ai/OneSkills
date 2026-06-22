---
name: bio-rnaseq-differential-expression
description: bulk RNA-seq workflow skill。用于 FASTQ 或 count matrix 到基因/转录本定量、差异表达、火山图、MA 图、热图和通路富集前置的任务；触发词包括 RNA-seq、DESeq2、edgeR、PyDESeq2、Salmon、STAR、featureCounts、tximport、差异基因。
---

# RNA-seq 差异表达流程

## 使用边界

用于 bulk RNA-seq，不用于单细胞分析；单细胞进入 `single-cell-rna-analysis`。如果用户只给 count matrix，从统计建模阶段开始；如果给 FASTQ，从 QC 和定量开始。

## 可复用资源

- `onescience-coder/assets/bio_workflow_templates/rnaseq_metadata.csv`：FASTQ 到差异表达的最小样本表模板。
- `onescience-coder/assets/bio_workflow_templates/rnaseq_contrast.yaml`：DESeq2/PyDESeq2 设计公式、contrast、过滤阈值和输出清单模板。

当用户要求生成项目骨架、样本表或分析说明时，优先复用这些模板。

## 推荐流程

1. 明确物种、参考基因组、注释版本、样本分组、批次、paired-end、链特异性。
2. FASTQ 阶段：fastp/FastQC 做读长 QC 和 adapter trimming，MultiQC 汇总。
3. 定量路线二选一：
   - transcript-level：Salmon/Kallisto -> tximport -> gene-level counts。
   - alignment-based：STAR/HISAT2 -> featureCounts/HTSeq。
4. 差异分析：DESeq2/edgeR 或 PyDESeq2；明确 design formula、contrast、reference level。
5. 结果解释：padj、log2FC、baseMean、独立过滤、Cook outlier、LFC shrinkage。
6. 可视化和交付：PCA、sample distance、dispersion、MA、volcano、top gene heatmap、显著基因 CSV。

## QC 检查点

- 读段质量：Q30、adapter content、duplication、overrepresented sequence。
- 定量质量：mapping/assignment rate、library size、gene body bias、strandedness。
- 统计质量：样本 PCA 是否按条件/批次分布、dispersion trend 是否合理、异常样本是否解释。

## 交接物

```yaml
bio_task_family: bio-workflow
assay_or_pipeline: bulk-rnaseq-de
input_object:
organism_or_taxon:
reference_build_or_database:
sample_metadata:
design_formula:
contrast:
primary_tools:
qc_checkpoints:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要把 normalized TPM/FPKM 直接作为 DESeq2 原始 count 输入。
- 不要在未确认批次和 contrast 时输出最终差异结论。
- 不要把 scRNA-seq 的细胞级矩阵当 bulk RNA-seq 处理。
