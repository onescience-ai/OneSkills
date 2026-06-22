---
name: bio-translational-biomarker
description: 转化医学与生物标志物范畴路由。用于 cfDNA/ctDNA、液体活检、临床变异优先级、肿瘤突变负荷和突变签名、因果基因组学、组学生物标志物机器学习、生存模型、药物基因组和多基因风险评分。
---

# 转化医学与生物标志物范畴路由

当用户目标是把组学信号转化为诊断、预后、治疗反应、药物反应或临床研究假设时，使用本范畴。若任务涉及患者级决策、真实诊疗或法规结论，必须输出不确定性和人工审核边界。

## 具体 skill 路由

- cfDNA preprocessing、ctDNA low-VAF mutation、UMI consensus、tumor fraction、fragmentomics、纵向 MRD：读取 `./liquid-biopsy-ctdna/SKILL.md`
- ClinVar/gnomAD/dbSNP/COSMIC、rare disease variant prioritization、TMB、somatic signatures、HLA：读取 `./clinical-variant-oncology/SKILL.md`
- Mendelian randomization、colocalization、fine mapping、pleiotropy、mediation：读取 `./causal-genomics/SKILL.md`
- omics classifier、feature selection、nested CV、SHAP/LIME、生存模型和 biomarker report：读取 `./biomarker-machine-learning/SKILL.md`
- PharmGKB/CPIC、drug-gene interaction、polygenic risk、risk calibration、临床可解释交接：读取 `./pharmacogenomics-risk/SKILL.md`

## 交接规则

输出时至少整理：

- `translational_question`
- `cohort_or_patient_context`
- `assay_or_feature_source`
- `clinical_endpoint`
- `analysis_design`
- `evidence_sources`
- `bias_and_leakage_controls`
- `clinical_review_boundary`
- `execution_entry`

## 禁止事项

- 不要把研究型预测分数写成诊断或治疗建议。
- 不要忽略队列划分、事件定义、随访时间、批次、缺失值和外部验证。
- 不要把 germline、somatic、cfDNA、bulk tumor、single-cell 证据混作同一层级。
