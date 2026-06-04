---
name: bio-phasing-imputation-prs
description: 单倍型分型、基因型填补和多基因风险评分 skill。用于 phasing、reference panel、imputation server/local imputation、INFO/R2 QC、dosage、PRSice/LDpred/PRS-CS 风险评分和校准交接。
---

# 单倍型分型、基因型填补与 PRS

## 使用边界

用于 genotype array 或 WGS 变异的 haplotype phasing、missing genotype imputation、dosage QC 和 polygenic risk score 交接。若重点是临床药物基因组解释，读取 `../../translational-biomarker/pharmacogenomics-risk/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_population_templates/imputation_prs_manifest.yaml`：genotype、reference panel、population、QC、PRS summary stats 和输出模板。
- `references/phasing_imputation_prs_qc.md`：phasing、imputation、dosage 和 PRS 评估边界。

## 推荐流程

1. 输入 QC：build、strand、allele coding、sample relatedness、MAF、missingness、HWE。
2. Phasing：选择工具和 reference panel，记录 chromosome split 和 pedigree 情况。
3. Imputation：选择 panel、population 匹配、chunk、server/local、INFO/R2 阈值。
4. Post-QC：dosage 格式、ambiguous SNP、liftover、variant ID 标准化。
5. PRS：summary stats harmonization、LD reference、score method、ancestry calibration、validation metrics。
6. 输出：imputed dosage、QC table、PRS table、calibration plot 和限制说明。

## 交接物

```yaml
bio_task_family: population-phylo-evolution
evolution_task: phasing-imputation-prs
genotype_input:
reference_panel:
population_context:
pre_imputation_qc:
imputation_qc:
prs_method:
validation_or_calibration:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要在 build/strand 未 harmonize 时进行填补或 PRS。
- 不要把欧洲人群 PRS 直接泛化到其他 ancestry 而不校准。
- 不要隐藏低 INFO/R2 variant 的过滤阈值。
