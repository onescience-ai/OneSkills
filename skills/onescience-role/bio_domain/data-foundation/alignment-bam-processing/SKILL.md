---
name: bio-alignment-bam-processing
description: 比对文件处理 skill。用于 STAR/BWA/Bowtie2/HISAT2/minimap2 输出后的 SAM/BAM/CRAM sort、index、filter、dedup、coverage、mapping QC、read group、region extraction 和 pysam/samtools 操作设计。
---

# 比对与 BAM/CRAM 处理

## 使用边界

用于 read alignment 结果处理。若还没有比对策略，结合具体 workflow skill 决定比对器；若是变异解释，进入 `workflows/variant-calling-interpretation`。

## 推荐流程

1. 明确 reference build、aligner、read group、paired-end、coordinate sort 状态。
2. 标准处理：sort -> index -> flagstat/stats -> optional mark duplicates。
3. 过滤：MAPQ、proper pair、primary alignment、chromosome/region、duplicate、secondary/supplementary。
4. 下游特异：
   - RNA-seq：junction、gene body、assignment。
   - variant：BQSR/read group/duplicate。
   - ChIP/ATAC：mitochondrial、blacklist、fragment size。
5. 输出 BAM/CRAM、BAI/CSI、QC summary 和过滤表达式。

## 交接物

```yaml
bio_task_family: alignment-bam-processing
input_alignment:
reference_build:
aligner:
sort_index_status:
filter_rules:
qc_metrics:
downstream_workflow:
execution_entry:
```

## 禁止事项

- 不要混用不同 reference 的 BAM 和 BED/VCF。
- 不要删除 secondary/supplementary reads 前忽略下游任务需求。
- 不要缺失 read group 就进入 GATK cohort 流程。
