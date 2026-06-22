---
name: bio-clinical-variant-oncology
description: 临床变异与肿瘤基因组解释 skill。用于 ClinVar、gnomAD、dbSNP、COSMIC、cBioPortal、TMB、mutational signatures、HLA typing、罕见病候选变异和肿瘤变异优先级交接。
---

# 临床变异与肿瘤基因组解释

## 使用边界

用于研究或临床研究场景中的变异注释、优先级和肿瘤基因组指标。若任务需要真实诊断结论，必须交接给人工临床/遗传审核。

## 可复用资源

- `onescience-coder/assets/bio_table_templates/variant_prioritization_schema.tsv`：变异优先级字段模板。
- `references/clinical_variant_evidence.md`：证据层级、频率、致病性、TMB、签名和 HLA 边界。

## 推荐流程

1. 明确变异来源：germline、somatic、tumor-only、tumor-normal、panel、WES/WGS。
2. 标准化：genome build、HGVS、transcript、left normalization、VCF fields。
3. 注释：population frequency、ClinVar significance、cancer hotspots、gene function、consequence、known therapy/resistance。
4. 肿瘤指标：TMB、MSI、mutational signatures、CNV/SV、HLA/neoantigen handoff。
5. 优先级：ACMG/AMP 或肿瘤证据框架，区分 actionability、pathogenicity、prognosis。
6. 输出：prioritized variant table、evidence summary、过滤理由、人工审核项。

## 交接物

```yaml
bio_task_family: translational-biomarker
translational_task: clinical-variant-oncology
variant_context:
input_vcf_or_table:
reference_build:
annotation_sources:
filtering_rules:
evidence_tiers:
tumor_metrics:
manual_review_required:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要把数据库注释等同于临床诊断。
- 不要混淆 pathogenicity、drug actionability 和 prognostic association。
- 不要在 tumor-only 场景中忽略 germline 可能性。
