---
name: bio-samplesheet-metadata-design
description: 样本表与元数据设计 skill。用于 RNA-seq、variant calling、ATAC-seq、single-cell、Nextflow/Snakemake 等任务的 samplesheet、metadata、contrast、batch、covariate、data dictionary 和命名规范设计。
---

# 样本表与元数据设计

## 可复用资源

- `onescience-coder/assets/bio_table_templates/generic_samplesheet.csv`：通用 FASTQ 样本表模板，包含 sample、library、lane、condition、batch、fastq_1、fastq_2。

具体 pipeline 若有自己的 samplesheet schema，优先使用 pipeline-specific 模板；否则以该模板为起点。

## 推荐流程

1. 明确 pipeline 需要的必填列。
2. 统一样本命名：sample、library、lane、replicate、patient、condition、batch。
3. 记录文件路径：fastq_1、fastq_2、bam、vcf、matrix、metadata。
4. 统计设计字段：condition、batch、sex、age、timepoint、paired/blocking factor、contrast。
5. 校验：路径存在、paired-end 匹配、重复 sample ID、缺失 metadata、非法字符。
6. 输出 CSV/TSV 样本表、data dictionary、contrast table。

## 交接物

```yaml
bio_task_family: samplesheet-metadata
target_workflow:
required_columns:
sample_id_rules:
file_columns:
design_columns:
contrast_plan:
validation_checks:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要把 biological replicate 和 technical replicate 混同。
- 不要在设计矩阵中放入完全混杂的 batch/condition 而不标记风险。
- 不要用相对路径提交远程 workflow，除非运行目录已明确。
