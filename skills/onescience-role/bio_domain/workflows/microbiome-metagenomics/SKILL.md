---
name: bio-microbiome-metagenomics
description: 微生物组、宏基因组、eDNA 和病原基因组 workflow skill。用于 16S/ITS、shotgun metagenomics、Kraken、MetaPhlAn、QIIME2、HUMAnN、AMR、strain tracking、taxonomy、diversity、outbreak surveillance 等任务。
---

# 微生物组与宏基因组流程

## 使用边界

用于样本群落、环境 DNA、宏基因组或病原监测分析。先区分 amplicon 与 shotgun。

## 推荐流程

1. 明确数据类型：16S/ITS amplicon、shotgun metagenome、metatranscriptome、pathogen WGS。
2. 明确 host removal、barcode/primer、数据库、taxonomy level、metadata。
3. amplicon：denoise/ASV、taxonomy assignment、alpha/beta diversity、differential abundance。
4. shotgun：QC、host depletion、taxonomic profiling、functional profiling、AMR、strain tracking。
5. pathogen：assembly/typing、variant surveillance、phylogenetics、transmission hints。
6. 输出：feature table、taxonomy table、diversity plots、functional profiles、QC report。

## 交接物

```yaml
bio_task_family: microbiome-metagenomics
data_type:
organism_or_environment:
host_depletion_needed:
reference_database:
metadata_variables:
diversity_or_function_goal:
qc_checkpoints:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要把 16S ASV 结果解释为物种级绝对定量。
- 不要忽略 batch、采样深度和污染控制。
- 不要在数据库版本不明时做强结论。
