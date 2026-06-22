---
name: bio-pathway-ppi-databases
description: 通路、功能、互作和调控数据库 skill。用于 GO、KEGG、Reactome、WikiPathways、STRING、BRENDA、QuickGO、JASPAR、motif、enzyme、PPI、pathway enrichment 和网络证据查询。
---

# 通路、功能与互作数据库

## 推荐流程

1. 明确输入 ID 类型：gene symbol、Entrez、Ensembl、UniProt、protein accession。
2. 选择数据库：GO/QuickGO、KEGG、Reactome、WikiPathways、STRING、BRENDA、JASPAR。
3. 明确任务：annotation lookup、enrichment、PPI network、enzyme reaction、TF motif。
4. 记录 background set、species、database release。
5. 输出通路表、network edge list、motif hit、enzyme evidence。

## 交接物

```yaml
database_family: pathway-ppi
input_ids:
id_type:
species_or_taxon:
database_or_ontology:
analysis_mode:
background_set:
return_fields:
execution_entry:
```

## 禁止事项

- 富集分析不能缺背景集。
- 不要把 PPI 数据库边当作直接物理互作，除非证据类型支持。
- 不要混用人类和模式生物基因 ID。
