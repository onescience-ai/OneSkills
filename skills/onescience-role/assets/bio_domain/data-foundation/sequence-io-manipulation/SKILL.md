---
name: bio-sequence-io-manipulation
description: 序列读写与操作 skill。用于 FASTA、FASTQ、GenBank、EMBL、GFF/GTF、PDB/mmCIF 中的序列解析、格式转换、反向互补、转录翻译、GC/长度统计、motif 搜索、批量序列处理和序列抽取。
---

# 序列读写与操作

## 使用边界

用于 sequence-level 操作。若涉及 read-level QC 进入 `read-qc-trimming`；若涉及比对后的 BAM/CRAM 进入 `alignment-bam-processing`。

## 推荐流程

1. 确认输入格式、压缩方式、序列 ID 规则和文件大小。
2. 读取方式：
   - 小文件可一次性读取。
   - 大 FASTA/FASTQ 使用索引或流式迭代。
3. 操作类型：
   - 统计：长度、GC、N 比例、quality。
   - 转换：FASTA/FASTQ/GenBank/GFF 互转。
   - 生物学变换：reverse complement、transcribe、translate、ORF/motif。
   - feature 提取：CDS、gene、exon、protein。
4. 输出新文件时保留 ID 映射和过滤日志。

## 交接物

```yaml
bio_task_family: sequence-io
input_format:
output_format:
sequence_type: dna | rna | protein | mixed
operation:
id_handling:
validation_checks:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要用临时字符串切分解析复杂 GenBank/GFF；使用结构化解析思路。
- 不要在未确认遗传密码表时翻译非标准生物。
- 不要丢失原始 record ID 和坐标映射。
