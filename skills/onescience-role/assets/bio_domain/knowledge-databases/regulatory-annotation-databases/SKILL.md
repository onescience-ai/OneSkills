---
name: bio-regulatory-annotation-databases
description: 调控注释数据库 skill。用于 ENCODE、ReMap、Cistrome、JASPAR、RegulomeDB、Roadmap Epigenomics、UCSC/Genome Browser tracks、TF motif、peak set 和 enhancer/promoter 注释查询交接。
---

# 调控注释数据库

## 使用边界

用于查询转录因子结合、motif、开放染色质、增强子、表观组 track 和调控证据。若任务是 ATAC/ChIP/Hi-C 原始数据分析，读取 `../../workflows/epigenomics-regulation/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_knowledge_templates/regulatory_query.yaml`：基因组区域、细胞类型、assay、TF/motif 和 track 字段模板。
- `references/regulatory_database_fields.md`：调控注释来源、字段和 genome build 注意事项。

## 推荐流程

1. 明确查询对象：region、gene promoter、TF motif、peak set、cell type、enhancer。
2. 确认 genome build 和坐标系统。
3. 选择数据库：ENCODE/Roadmap for assay tracks，JASPAR for motif，ReMap/Cistrome for TF binding，RegulomeDB for variant regulatory evidence。
4. 输出：track accession、cell type、assay、biosample、peak/motif fields、证据强度和下载/可视化入口。

## 交接物

```yaml
database_family: regulatory-annotation
query_region_or_gene:
genome_build:
cell_type_or_tissue:
assay_or_tf:
databases:
return_fields:
coordinate_handling:
output_format:
execution_entry:
```

## 禁止事项

- 不要混用不同 genome build 的 peak/variant 坐标。
- 不要把 motif hit 当成实际 TF binding 证据。
- 不要忽略细胞类型、处理条件和 assay 差异。
