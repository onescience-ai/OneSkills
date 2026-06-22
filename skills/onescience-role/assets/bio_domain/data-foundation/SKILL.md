---
name: bio-data-foundation
description: 生物信息数据基础设施范畴路由。用于序列文件、FASTQ 质控、BAM/CRAM/SAM、VCF/BCF/BED/GFF、公共数据下载接入、样本表和元数据设计等底层数据任务，选择具体 data-foundation skill 并生成交接物。
---

# 生信数据基础设施范畴路由

当用户任务主要是整理输入数据、解析文件格式、生成样本表、做基础 QC 或准备下游 workflow 输入时，使用本范畴。

## 具体 skill 路由

- FASTA/FASTQ/GenBank/GFF、序列统计、反向互补、翻译、格式转换：读取 `./sequence-io-manipulation/SKILL.md`
- FASTQ 质量控制、adapter trimming、MultiQC：读取 `./read-qc-trimming/SKILL.md`
- SAM/BAM/CRAM、sort/index/filter、比对后 QC：读取 `./alignment-bam-processing/SKILL.md`
- VCF/BCF/BED/GTF/GFF、interval overlap、坐标系：读取 `./variant-interval-files/SKILL.md`
- GEO/SRA/ENA/公共 FASTQ 和矩阵接入：读取 `./public-data-ingestion/SKILL.md`
- samplesheet、metadata、contrast、batch、数据字典：读取 `./samplesheet-metadata-design/SKILL.md`
- count matrix、feature table、gene ID mapping、metadata join、sparse matrix、AnnData/loom/zarr 交接：读取 `./expression-matrix-feature-tables/SKILL.md`

## 交接规则

输出时至少整理：

- `data_object`
- `format`
- `organism_or_taxon`
- `reference_build`
- `path_or_accession`
- `validation_checks`
- `downstream_workflow`
- `execution_entry`
