# 长读长测序分析工作流

- workflow_id: `long-read-sequencing-analysis`

## 适用范围

用于 Oxford Nanopore 或 PacBio 数据的 basecalling、read QC、barcode demultiplex、long-read alignment、SV calling、Iso-Seq、direct RNA、nanopore methylation、phasing、assembly polishing 和长读长交付。

## 输入

- 必需：平台和化学版本；POD5/FAST5/BAM/FASTQ/HiFi reads；样本和 barcode metadata；目标分析分支。
- 分支输入：reference build、raw signal、transcript annotation、methylation 模型、assembly draft、phasing 需求。
- 可选：run summary、basecaller 版本、flowcell/kit 信息、覆盖预期。

## 输出

- demultiplexed FASTQ/BAM。
- read QC 报告：yield、read length N50、Q-score、coverage、barcode balance。
- aligned BAM/CRAM。
- 分支产物：SV/variant VCF/BED、Iso-Seq transcript GTF/FASTA、methylation bedMethyl、phasing blocks、polishing inputs。

## 流程节点

1. 判定数据类型：ONT raw signal、ONT FASTQ、PacBio CLR、PacBio HiFi、Iso-Seq 或 direct RNA。
2. 规划 basecalling/demultiplex，若已完成则校验版本和参数。
3. 执行 read-level QC，检查长度、质量、产量、污染、barcode balance 和 coverage。
4. 选择 minimap2 或平台特异 alignment preset，记录 reference build。
5. 按目标分支规划 SV/phasing、methylation、Iso-Seq/direct RNA 或 polishing。
6. 输出平台感知的 QC 和分支产物。

## 边界与分流

- 最终 germline/somatic 解释转到 `variant-calling-interpretation`。
- de novo assembly 和 annotation 转到 `genome-assembly-annotation`。
- direct RNA 或 isoform regulation 可联动 `post-transcriptional-regulation`。
- 不使用 short-read QC 阈值直接判断 long-read 可靠性。

## 模型与工具选择边界

- ONT raw signal 可使用 signal-aware methylation/basecalling 分支；没有 raw signal 时不能做 signal-level 任务。
- PacBio HiFi 使用 HiFi/CCS 假设，不套用 ONT Q-score 分支。
- SV caller、methylation caller、Iso-Seq 工具按平台和输入类型选择。

## 质量检查

- 平台、化学版本、basecaller 版本明确。
- read length、Q-score、yield、coverage 达到分支要求。
- barcode/sample mapping 正确。
- supplementary alignment 和 chimeric reads 处理策略明确。

## 回退策略

- 没有 raw signal：跳过 signal-level methylation/basecalling。
- 覆盖不足：限制 SV/isoform/phasing 解释，输出 QC 风险。
- 平台未知：只做文件格式和基本 QC，要求补充平台信息。

## 资源召回建议

- run plan 模板：`bio_workflow_template_app`。
- 基因组数据标准：`biology_genome_dataset`。
- 病原监测或 phylogeny 分支：`bio_population_phylo_app`。
