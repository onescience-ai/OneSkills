---
name: bio-python-bio-toolkit
description: Python 生信编程工具 skill。用于 Biopython、pysam、cyvcf2、scikit-bio、Bio.PDB、Entrez、BLAST 解析、FASTA/GenBank/PDB/BAM/VCF 编程处理和自定义 Python 生信脚本设计。
---

# Python 生信工具

## 使用边界

用于包级或脚本级 Python 生信任务。端到端流程仍应由 `workflows` 选择主线。

## 工具选择

- 序列和 GenBank：Biopython SeqIO/SeqRecord/SeqFeature。
- NCBI 查询：Entrez；需要 email/API key 和速率限制。
- BLAST：远程 qblast 或本地 BLAST+，解析 XML/tabular。
- 结构：Bio.PDB 或 MDAnalysis，处理 PDB/mmCIF、chain、residue、RMSD。
- BAM/CRAM：pysam，用于 region fetch、flag/MAPQ、pileup。
- VCF：cyvcf2/pysam.VariantFile，用于 sample genotype、INFO/FORMAT、filter。
- diversity/phylogeny：scikit-bio、Bio.Phylo。

## 交接物

```yaml
tool_family: python-bio
packages:
input_format:
operation:
data_size:
rate_limit_or_external_tool:
expected_output:
execution_entry:
```

## 禁止事项

- 不要用手写正则解析复杂生物格式。
- 不要忽略 NCBI 查询速率和 email/API key。
- 大文件必须用流式或索引访问，不要全量读入。
