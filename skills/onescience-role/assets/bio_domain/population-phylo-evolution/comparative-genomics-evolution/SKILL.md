---
name: bio-comparative-genomics-evolution
description: 比较基因组与进化分析 skill。用于 ortholog inference、synteny、whole-genome duplication、positive selection、dN/dS、HGT、ancestral reconstruction、annotation transfer 和跨物种功能比较。
---

# 比较基因组与进化分析

## 使用边界

用于多个物种或多个基因组之间的基因家族、共线性、选择压力和功能演化分析。若只是组装注释流程，读取 `../../workflows/genome-assembly-annotation/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_population_templates/comparative_genomics_plan.yaml`：物种、基因组、蛋白/注释、ortholog、synteny 和选择分析模板。
- `references/comparative_evolution_methods.md`：ortholog、synteny、positive selection、HGT 和 annotation transfer 注意事项。

## 推荐流程

1. 收集输入：genome assembly、GFF/GTF、protein FASTA、CDS FASTA、species metadata。
2. 质量检查：BUSCO、annotation completeness、isoform collapse、contamination。
3. Ortholog inference：orthogroups、single-copy genes、paralog/co-ortholog。
4. Genome structure：syntenic blocks、rearrangement、WGD、copy number expansion。
5. Evolution tests：dN/dS、branch-site、site model、HGT、ancestral reconstruction。
6. 输出：orthogroup table、synteny blocks、selected genes、figures、method caveats。

## 交接物

```yaml
bio_task_family: population-phylo-evolution
evolution_task: comparative-genomics-evolution
species_set:
genome_annotation_inputs:
quality_filters:
ortholog_strategy:
synteny_strategy:
selection_or_hgt_tests:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要把 paralog 当作 one-to-one ortholog 做选择分析。
- 不要在低质量注释上直接解释 gene family expansion。
- dN/dS 分析必须使用 codon alignment 和合适的物种/基因树。
