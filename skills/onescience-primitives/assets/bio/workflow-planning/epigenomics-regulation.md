# 表观组学与调控分析工作流

- workflow_id: `epigenomics-regulation`

## 适用范围

用于 ATAC-seq、ChIP-seq、CUT&Tag、CUT&RUN、methylation、Hi-C、CLIP-seq、motif、peak calling、differential binding、TAD、loop、GRN、SCENIC 类调控分析规划。

## 输入

- 必需：FASTQ/BAM/peak 或 contact matrix；assay type；reference genome；sample metadata；contrast 或 condition。
- 可选：input/control、replicates、blacklist regions、motif database、gene annotation、matched RNA-seq、known TF/RBP 列表。

## 输出

- peak/DMR/loop/TAD/regulon 表。
- bigWig、BED、browser tracks。
- differential binding 或 differential accessibility 表。
- motif enrichment、peak-gene link、regulatory network 结果。
- QC 图和报告。

## 流程节点

1. 判定 assay 分支：ATAC、ChIP、CUT&Tag/CUT&RUN、methylation、Hi-C、CLIP 或 GRN。
2. 规划 QC、trimming、alignment、dedup、low MAPQ/mitochondrial/blacklist filtering。
3. 调用 feature：peak、DMR、loop/TAD、RBP binding site 或 regulon。
4. 按 replicate 和 contrast 做 differential binding/accessibility/regulation。
5. 做 motif、gene annotation、pathway 或 regulatory network 解释。
6. 输出 tracks、tables、plots 和解释边界。

## 边界与分流

- scATAC、single-cell multiome 或空间调控转到 `spatial-multiomics-analysis`。
- gene expression 差异转到 `rnaseq-differential-expression`。
- Ribo-seq、splicing、m6A 或 RNA modification 转到 `post-transcriptional-regulation`。

## 模型与工具选择边界

- ATAC/ChIP/CUT&Tag 多数走 peak calling 和 differential binding 分支。
- methylation 使用 DMR/methylation 专用方法。
- Hi-C 使用 contact matrix、TAD、loop 专用方法。
- AlphaGenome 类模型只在任务是 sequence-to-function/regulatory effect 且原语召回命中时使用。

## 质量检查

- control/input 和 replicate 信息明确。
- FRiP、TSS enrichment、fragment length、library complexity、duplication 等指标可解释。
- peak 坐标、genome build 和 annotation build 一致。
- blacklist 和 mitochondrial filtering 策略记录。

## 回退策略

- 无 replicate：只做描述性 peak/track 和风险提示，不做强 differential 结论。
- 缺 control/input：标记 binding 结论置信度限制。
- genome build 不明：暂停 annotation 和 motif/peak-gene link。

## 资源召回建议

- 模板：`bio_workflow_template_app`。
- 数据库和调控注释：`bio_knowledge_query_app`。
- 通用工具交接：`bio_analysis_toolkit_app`。
- sequence-to-function 模型：按需召回 `alphagenome`。
