---
name: bio-population-phylo-evolution
description: 群体遗传、系统发育与进化基因组学范畴路由。用于 GWAS、PLINK、VCF 群体结构、LD、选择扫描、系统树推断、比较基因组、同源基因、正选择、单倍型分型、基因型填补和病原基因组监测。
---

# 群体遗传、系统发育与进化基因组学范畴路由

当用户目标是从变异、序列比对或基因组比较中解释群体结构、亲缘关系、演化过程或传播关系时，使用本范畴。若任务只是 VCF 格式修复，优先进入 `../data-foundation/variant-interval-files/SKILL.md`。

## 具体 skill 路由

- Newick/Nexus、IQ-TREE/RAxML/BEAST、模型选择、bootstrap、rooting、tree figure：读取 `./phylogenetics-tree-analysis/SKILL.md`
- PLINK/scikit-allel、GWAS、PCA/admixture、LD、Fst/Tajima's D/iHS/XP-EHH、Manhattan/QQ：读取 `./population-genetics-gwas/SKILL.md`
- ortholog、synteny、positive selection、dN/dS、HGT、ancestral reconstruction、annotation transfer：读取 `./comparative-genomics-evolution/SKILL.md`
- haplotype phasing、genotype imputation、reference panel、imputation QC、polygenic risk handoff：读取 `./phasing-imputation-prs/SKILL.md`
- pathogen outbreak、SNP distance、lineage/cluster、time-resolved tree、metadata reconciliation、surveillance report：读取 `./pathogen-genomic-surveillance/SKILL.md`

## 交接规则

输出时至少整理：

- `evolution_task`
- `input_data_type`
- `taxon_or_population`
- `reference_or_alignment`
- `sample_metadata`
- `statistical_model`
- `qc_checkpoints`
- `interpretation_limits`
- `execution_entry`

## 禁止事项

- 不要混淆样本亲缘、群体结构、系统发育树和传播链；它们的证据模型不同。
- 不要在未说明参考面板、基因组 build、群体来源或采样时间时解释 GWAS/填补/传播结果。
- 不要把 bootstrap、posterior probability、SH-aLRT、concordance factor 当成同一种支持度。
