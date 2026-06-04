---
name: bio-structure-compound-databases
description: 结构、化合物和药物靶点数据库 skill。用于 PDB、EMDB、AlphaFold DB、PubChem、ChEMBL、DrugBank、ZINC、OpenTargets、UniChem、PDB ligand、compound bioactivity 和 target evidence 查询。
---

# 结构、化合物与药物靶点数据库

## 推荐流程

1. 明确查询对象：protein structure、complex、ligand、compound、target、bioactivity、drug。
2. 明确 ID：PDB ID、UniProt、SMILES/InChIKey、CID、ChEMBL ID、DrugBank ID。
3. 查询结构证据：resolution、method、chain、ligand、mutation、assembly。
4. 查询化合物证据：bioactivity assay、IC50/Kd/Ki、target、ADMET、approved status。
5. 输出结构/化合物清单、证据字段、可下载对象和风险说明。

## 交接物

```yaml
database_family: structure-compound
query_object:
identifier_type:
databases:
evidence_fields:
structure_or_compound_filters:
output_format:
execution_entry:
```

## 禁止事项

- 不要把 AlphaFold DB 预测结构等同实验结构。
- 不要比较不同 assay 条件下的活性值而不说明条件。
- 不要把 docking pose 当作已验证结合。
