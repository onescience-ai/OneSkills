---
name: bio-variant-clinical-databases
description: 变异、疾病和临床证据数据库 skill。用于 ClinVar、gnomAD、dbSNP、COSMIC、cBioPortal、DepMap、GWAS Catalog、Monarch 等查询，整理 variant ID、population frequency、clinical significance、cancer evidence 和 dependency evidence。
---

# 变异与临床证据数据库

## 推荐流程

1. 明确 variant 表示：HGVS、rsID、VCF coordinate、protein change、gene+mutation。
2. 确认 reference build、transcript、allele normalization。
3. 查询证据类型：
   - 人群频率：gnomAD/dbSNP。
   - 临床意义：ClinVar。
   - 癌症：COSMIC/cBioPortal。
   - 依赖性/功能：DepMap。
   - GWAS/表型：GWAS Catalog/Monarch。
4. 输出 evidence table，记录数据库 release/date 和冲突证据。

## 交接物

```yaml
database_family: variant-clinical
variant_representation:
reference_build:
transcript:
databases:
evidence_fields:
conflict_handling:
output_format:
execution_entry:
```

## 禁止事项

- 不要把数据库注释当作临床诊断。
- 不要忽略 transcript 差异导致的 HGVS 不一致。
- 不要混用不同 genome build 坐标。
