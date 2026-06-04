---
name: bio-read-qc-trimming
description: FASTQ 质控与剪切 skill。用于 raw FASTQ 的 FastQC/fastp/MultiQC、adapter 去除、质量过滤、长度过滤、UMI 预处理、paired-end 一致性检查和下游比对/定量前数据准备。
---

# FASTQ 质控与剪切

## 推荐流程

1. 明确 single-end/paired-end、read length、文库类型、UMI、barcode、平台。
2. 做原始 QC：per-base quality、adapter、duplication、GC、overrepresented sequences。
3. 执行 trimming/filtering：adapter detection、Q threshold、minimum length、polyG/polyX、UMI handling。
4. 做剪切后 QC，并汇总为 MultiQC。
5. 输出 trimmed FASTQ、QC HTML/JSON、过滤统计和下游建议。

## QC 检查点

- Q30 比例和低质量尾部。
- adapter 是否充分去除。
- paired-end 文件是否同步。
- 过滤后 read 数是否异常下降。

## 交接物

```yaml
bio_task_family: read-qc
input_fastq:
library_type:
paired_end:
umi_or_barcode:
trim_strategy:
qc_reports:
downstream_workflow:
execution_entry:
```

## 禁止事项

- 不要在不了解 UMI/barcode 结构时随意剪切 read 头部。
- 不要只看剪切后指标，必须保留剪切前后对比。
