# 基因组组装与注释工作流

- workflow_id: `genome-assembly-annotation`

## 适用范围

用于 short-read、long-read、HiFi、hybrid assembly、polishing、scaffolding、BUSCO、QUAST、contamination、Prokka、真核 gene prediction、repeat/ncRNA/functional annotation、ortholog、synteny 和 selection 前置交付。

## 输入

- 必需：reads 或 draft assembly；物种/样本信息；预估 genome size；目标分支；污染检查需求。
- 可选：Hi-C/optical map、related reference、RNA-seq/protein evidence、repeat database、BUSCO lineage、annotation database。

## 输出

- assembly FASTA。
- polished/scaffolded FASTA。
- GFF/GTF、CDS FASTA、protein FASTA。
- repeat/ncRNA/functional annotation。
- BUSCO/QUAST/k-mer/contamination/QC 报告。
- comparative genomics handoff 表。

## 流程节点

1. 判定组装策略：short-read、long-read、HiFi、hybrid、metagenome 或 reference-guided。
2. 做 reads QC、k-mer/genome size 估计、coverage、heterozygosity 和 contamination 检查。
3. 规划 assembler、polishing rounds 和可选 scaffolding。
4. 用 N50/L50、BUSCO、QUAST、k-mer consistency、coverage 和 contamination 综合评价。
5. 按原核/真核分支规划 gene prediction、repeat masking、ncRNA 和 functional annotation。
6. 准备 ortholog、synteny、pan-genome 或 selection 分析交接。

## 边界与分流

- 原始长读长 QC 先走 `long-read-sequencing-analysis`。
- 下游群体遗传、GWAS、pathogen surveillance 或 phylogeny 使用 `bio_population_phylo_app`。
- 不把原核注释流程直接套到真核基因组。

## 模型与工具选择边界

- 细菌/小基因组：Prokka 类原核注释分支。
- 真核基因组：repeat masking + evidence-aware gene prediction。
- BUSCO lineage 必须与物种接近。
- N50 只能作为结构指标之一，不能单独代表 assembly 质量。

## 质量检查

- coverage 和 read quality 支持组装目标。
- contamination、duplication、haplotig、重复序列和倍性有检查。
- BUSCO completeness 和 duplication 分开解释。
- 注释数据库、软件版本和证据来源有记录。

## 回退策略

- 物种或 genome size 不明：先做通用 QC 和 k-mer 估计，再确定 assembler。
- contamination 高：先规划去污染或样本复核，不进入正式注释结论。
- evidence 不足：输出结构注释草案并标记功能注释置信度限制。

## 资源召回建议

- 基因组数据标准：`biology_genome_dataset`。
- 比较基因组/phylogeny 交接：`bio_population_phylo_app`。
- 报告：`bio_qc_report_app`。
