---
name: bio-single-cell-atlas-databases
description: 单细胞图谱与参考数据库 skill。用于 cell atlas、cellxgene、reference mapping、cell type marker、ARCHS4、public h5ad、tissue atlas、query-to-reference、label transfer 数据来源选择和证据整理。
---

# 单细胞图谱数据库

## 推荐流程

1. 明确物种、组织、疾病状态、测序平台和细胞类型粒度。
2. 选择 reference：同物种/同组织/同技术优先。
3. 明确用途：marker lookup、reference mapping、label transfer、atlas comparison、download h5ad。
4. 记录 reference 版本、cell ontology、batch/platform、license。
5. 输出 reference candidates、marker evidence、mapping 字段和数据清单。

## 交接物

```yaml
database_family: single-cell-atlas
species_or_taxon:
tissue_or_disease:
technology:
reference_candidates:
cell_type_schema:
return_fields:
output_format:
execution_entry:
```

## 禁止事项

- 不要用跨物种/跨组织 reference 做强注释而不说明风险。
- 不要忽略 cell ontology 粒度差异。
- 不要把 marker list 当作唯一注释证据。
