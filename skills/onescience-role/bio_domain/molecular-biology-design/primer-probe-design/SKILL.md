---
name: bio-primer-probe-design
description: PCR、qPCR、测序引物和探针设计 skill。用于设计或验证 primer pair、TaqMan probe、molecular beacon、amplicon、Tm GC 二聚体发夹、SNP/repeat 避让和特异性检查交接。
---

# 引物与探针设计

## 使用边界

用于 PCR/qPCR/ddPCR/测序引物、探针和已有引物验证。若用户目标是 CRISPR 编辑验证引物，可先用本 skill 设计 flanking PCR，再回到 `../crispr-guide-editing/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_molecular_templates/primer_request.yaml`：记录模板序列、目标区域、amplicon、Tm/GC、排除区域和输出格式。
- `references/design_constraints.md`：Primer3 约束、qPCR 探针约束、特异性和失败排查。
- `onescience-coder/assets/bio_molecular_tools/sequence_design_checks.py`：无第三方依赖的序列清洗、GC、Wallace Tm、poly-X、简易二聚体和 FASTA 摘要工具。

## 推荐流程

1. 明确 assay：PCR、qPCR、ddPCR、Sanger、amplicon-seq 或 cloning validation。
2. 收集模板序列、物种、参考版本、isoform、目标坐标、SNP/repeat/同源区避让清单。
3. 设置约束：product size、primer length、Tm、GC、probe Tm、primer-probe spacing、最大 poly-X 和 3' 互补。
4. 生成候选：优先使用 Primer3 或兼容实现；没有运行环境时先把 `primer_request.yaml` 对应字段交给 `onescience-coder`。
5. 验证候选：检查目标唯一性、二聚体/发夹、amplicon 是否跨目标区域或 exon junction。
6. 输出表：primer name、sequence、strand、start/end、Tm、GC、product size、penalty、warning。

## 交接物

```yaml
bio_task_family: molecular-biology-design
molecular_task: primer-probe-design
assay:
template_sequence_or_fasta:
organism_or_reference:
target_region:
excluded_regions:
product_size_range:
primer_constraints:
probe_constraints:
specificity_check:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要只给 primer 序列而不给坐标、Tm、GC、amplicon 和验证状态。
- qPCR 探针设计必须显式区分 primer Tm 与 probe Tm。
- 不要忽略模板方向、cDNA/genomic DNA 差异和剪接异构体。
