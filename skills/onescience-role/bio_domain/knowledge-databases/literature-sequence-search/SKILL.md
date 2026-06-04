---
name: bio-literature-sequence-search
description: 文献、序列和公共测序数据库查询 skill。用于 PubMed、NCBI Gene/Nucleotide/Protein/SRA/GEO、ENA、UniProt、Ensembl、BioProject、BioSample、accession 映射、FASTA/GenBank 下载和文献证据整理。
---

# 文献、序列与公共测序查询

## 推荐流程

1. 明确查询对象：gene、protein、sequence accession、article、study、sample、run。
2. 明确 ID 类型：gene symbol、Entrez ID、Ensembl ID、UniProt accession、RefSeq、SRA accession。
3. 明确物种、日期范围、数据库和返回字段。
4. 设计查询式：关键词、字段限定、布尔逻辑、分页或 history。
5. 输出记录列表、metadata、下载清单或证据摘要。

## 交接物

```yaml
database_family: literature-sequence
databases:
query_terms:
identifier_type:
species_or_taxon:
date_or_release:
return_fields:
output_format:
execution_entry:
```

## 禁止事项

- 不要在同名基因未限定物种时直接返回结论。
- 不要忽略 accession 版本号。
- 文献证据要区分 review、preprint、primary research 和 database record。
