# 转录后调控分析工作流

- workflow_id: `post-transcriptional-regulation`

## 适用范围

用于 alternative splicing、differential splicing、Ribo-seq、small RNA/miRNA、CLIP-seq/RBP binding、m6A/epitranscriptomics、RNA modification calling 和 RNA 调控可视化交接。

## 输入

- 必需：FASTQ/BAM 或 event/peak/modification table；assay type；reference genome/transcriptome；annotation；sample metadata。
- 可选：RBP/motif/modification database、matched RNA-seq、input/control、replicates、read structure、ribosome profiling metadata。

## 输出

- splicing event table、differential splicing table。
- Ribo-seq ORF/translation 或 ribosome occupancy 表。
- small RNA/miRNA 表。
- CLIP/RBP peaks、RNA modification calls。
- track files、QC figures、解释边界。

## 流程节点

1. 判定分支：splicing、Ribo-seq、small RNA、CLIP/RBP、m6A 或 direct RNA modification。
2. 按 assay 做 trimming、alignment、dedup、feature extraction。
3. 调用事件、ORF、peak、binding site 或 modification。
4. 做 differential usage、differential occupancy、binding 或 modification 分析。
5. 关联 gene/transcript、motif、pathway 和 regulatory interpretation。
6. 输出表格、tracks、figures 和限制说明。

## 边界与分流

- 普通 gene-level differential expression 转到 `rnaseq-differential-expression`。
- 单细胞 RNA velocity 或 multiome dynamics 转到 `single-cell-rna-analysis` 或 `spatial-multiomics-analysis`。
- 不把表达差异直接解释为剪接或翻译效率差异。

## 模型与工具选择边界

- splicing 使用 exon/junction/event usage 方法。
- Ribo-seq 必须先检查周期性和 P-site offset，再解释 ORF 或 translation。
- CLIP/RBP 使用 binding peak 专用方法。
- m6A/direct RNA 使用 modification calling 专用分支。

## 质量检查

- read length、junction support、annotation version 明确。
- Ribo-seq 检查三核苷酸周期性、P-site offset 和 CDS enrichment。
- CLIP/m6A 检查 input/control、replicate 和 peak reproducibility。
- small RNA 检查 adapter trimming 和 length distribution。

## 回退策略

- assay type 不明确：要求补充 protocol/read structure。
- 缺 replicate：只输出描述性事件或 peaks。
- annotation build 不明：暂停 transcript-level 解释。

## 资源召回建议

- 模板：`bio_workflow_template_app`。
- 数据标准：`biology_genome_dataset`。
- 通用分析工具：`bio_analysis_toolkit_app`。
