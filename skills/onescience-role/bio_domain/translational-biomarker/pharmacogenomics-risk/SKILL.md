---
name: bio-pharmacogenomics-risk
description: 药物基因组与遗传风险评分 skill。用于 PharmGKB/CPIC 风格 drug-gene 注释、HLA 风险、CYP star allele、药物反应研究、多基因风险评分和临床可解释交接。
---

# 药物基因组与遗传风险评分

## 使用边界

用于药物反应相关变异、基因型到 phenotype/star allele、PRS 和临床研究报告交接。真实用药或剂量调整必须保留人工临床审核边界。

## 可复用资源

- `onescience-coder/assets/bio_table_templates/pharmacogenomics_handoff.yaml`：药物、基因、变异、证据来源、phenotype 和审核字段模板。
- `references/pgx_prs_interpretation.md`：PGx、HLA、CYP、PRS 和临床解释注意事项。

## 推荐流程

1. 明确场景：药物反应、毒性风险、HLA hypersensitivity、CYP metabolism、PRS disease risk。
2. 标准化输入：VCF/table、star allele call、HLA type、effect allele、build。
3. 注释证据：drug-gene pair、phenotype、guideline level、population frequency、known limitations。
4. 风险评分：summary stats harmonization、LD reference、ancestry calibration、absolute/relative risk。
5. 输出：evidence table、phenotype call、risk score、临床审核和不可自动决策事项。

## 交接物

```yaml
bio_task_family: translational-biomarker
translational_task: pharmacogenomics-risk
drug_or_risk_context:
genotype_input:
gene_or_variant_set:
evidence_sources:
phenotype_translation:
prs_method:
calibration:
manual_review_required:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要直接给用药或剂量建议。
- 不要忽略 ancestry、star allele caller 版本和 copy number 对 PGx phenotype 的影响。
- 不要把相对风险 PRS 解释为个体绝对疾病概率。
