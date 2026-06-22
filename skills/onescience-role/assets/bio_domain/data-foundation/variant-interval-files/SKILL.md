---
name: bio-variant-interval-files
description: 变异与区间文件处理 skill。用于 VCF/BCF、BED、GFF/GTF、interval_list、peak、DMR、loop、genomic ranges 的过滤、合并、交集、注释、坐标系转换和 genome build 一致性检查。
---

# 变异与基因组区间文件处理

## 推荐流程

1. 明确文件类型、坐标系统、reference build、是否压缩和索引。
2. VCF/BCF：normalize、left-align、split multiallelic、filter、subset samples、annotate。
3. BED/GFF/GTF：sort、merge、intersect、closest、coverage、feature extraction。
4. 一致性检查：chrom naming、0-based/1-based、strand、genome build。
5. 输出处理后文件、索引、统计表和操作记录。

## 交接物

```yaml
bio_task_family: variant-interval-files
input_files:
file_formats:
reference_build:
coordinate_convention:
operations:
validation_checks:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要把 BED 的 0-based half-open 坐标当成 GFF 的 1-based inclusive。
- 不要忽略 chr 前缀差异。
- 不要在未 normalize VCF 时直接按位点合并复杂变异。
