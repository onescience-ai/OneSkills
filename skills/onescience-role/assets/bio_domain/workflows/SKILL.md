---
name: bio-workflows
description: 生物信息端到端分析流程范畴路由。用于 RNA-seq、单细胞、空间组学、变异检测、表观组、微生物组、蛋白质组、代谢组、多组学、免疫组库、基因组组装注释、蛋白设计到结构验证等分析链路，选择具体 workflow skill 并生成角色交接物。
---

# 生信 Workflow 范畴路由

当用户目标是从生物数据到结果表、图、报告或可运行流程时，使用本范畴。先选择具体 workflow skill，不要停留在本层。

## 具体 skill 路由

- bulk RNA-seq、count matrix、差异表达、富集前置：读取 `./rnaseq-differential-expression/SKILL.md`
- 10x/scRNA-seq、QC、聚类、marker、注释、scVI：读取 `./single-cell-rna-analysis/SKILL.md`
- 空间转录组、CITE-seq、multiome、跨模态整合：读取 `./spatial-multiomics-analysis/SKILL.md`
- germline/somatic variant、CNV/SV、VCF 注释：读取 `./variant-calling-interpretation/SKILL.md`
- ATAC-seq、ChIP-seq、methylation、Hi-C、GRN：读取 `./epigenomics-regulation/SKILL.md`
- microbiome、metagenomics、eDNA、pathogen genomics：读取 `./microbiome-metagenomics/SKILL.md`
- proteomics、metabolomics、lipidomics、mzML：读取 `./proteomics-metabolomics/SKILL.md`
- pathway、multi-omics、metabolic model、systems biology：读取 `./multiomics-systems-biology/SKILL.md`
- TCR/BCR、neoantigen、MHC/epitope：读取 `./immune-repertoire-neoantigen/SKILL.md`
- 蛋白设计流水线、RFdiffusion -> ProteinMPNN -> SimpleFold/Protenix/AlphaFold3 结构验证、候选排序：读取 `./protein-design-structure-validation/SKILL.md`
- genome assembly、annotation、comparative genomics：读取 `./genome-assembly-annotation/SKILL.md`
- Nanopore/PacBio、long-read QC、SV、Iso-Seq、direct RNA、nanopore methylation、phasing：读取 `./long-read-sequencing-analysis/SKILL.md`
- alternative splicing、Ribo-seq、small RNA、CLIP-seq、m6A/epitranscriptomics、RNA modification：读取 `./post-transcriptional-regulation/SKILL.md`
- CRISPR screen、Perturb-seq、DepMap/gene essentiality、pooled screen QC、MAGeCK/PinAPL-Py：读取 `./functional-genomics-screens/SKILL.md`

## 交接规则

输出时至少整理：

- `assay_or_pipeline`
- `input_object`
- `organism_or_taxon`
- `reference_build_or_database`
- `sample_metadata`
- `workflow_stages`
- `qc_checkpoints`
- `expected_outputs`
- `execution_entry`

如果需要写脚本或配置，交给 `onescience-skill -> onescience-coder`。如果需要提交运行，追加 `platform-engineer` 并交给 `onescience-runtime`。
