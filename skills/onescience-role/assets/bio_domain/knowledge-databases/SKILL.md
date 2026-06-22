---
name: bio-knowledge-databases
description: 生物信息知识库与数据库范畴路由。用于文献、序列、公共测序、变异临床、通路互作、结构、化合物、药物靶点、单细胞图谱等数据库查询与证据整理任务，选择具体 database skill。
---

# 生信知识库与数据库范畴路由

当用户主要目标是查找、下载、汇总或交叉链接公共知识库信息时，使用本范畴。需要实际联网时，由执行层按权限处理；本层负责查询设计和交接。

## 具体 skill 路由

- PubMed、NCBI Gene/Protein/Nucleotide、SRA/GEO、UniProt、Ensembl：读取 `./literature-sequence-search/SKILL.md`
- ClinVar、gnomAD、dbSNP、COSMIC、cBioPortal、DepMap：读取 `./variant-clinical-databases/SKILL.md`
- GO、KEGG、Reactome、STRING、BRENDA、JASPAR、WikiPathways：读取 `./pathway-ppi-databases/SKILL.md`
- PDB、EMDB、AlphaFold DB、PubChem、ChEMBL、DrugBank、ZINC、OpenTargets：读取 `./structure-compound-databases/SKILL.md`
- cell atlas、cellxgene、reference mapping、ARCHS4：读取 `./single-cell-atlas-databases/SKILL.md`
- PRIDE、PeptideAtlas、MassIVE、HMDB、Metabolomics Workbench、RefMet、GNPS：读取 `./proteomics-metabolomics-databases/SKILL.md`
- ENCODE、ReMap、Cistrome、JASPAR motif、RegulomeDB、Roadmap epigenomics、UCSC tracks：读取 `./regulatory-annotation-databases/SKILL.md`

## 交接规则

输出时至少整理：

- `database_family`
- `query_terms`
- `identifier_type`
- `species_or_taxon`
- `release_or_date`
- `return_fields`
- `output_format`
- `execution_entry`
