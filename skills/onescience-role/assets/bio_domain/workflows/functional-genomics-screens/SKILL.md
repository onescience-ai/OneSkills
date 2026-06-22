---
name: bio-functional-genomics-screens
description: 功能基因组筛选 workflow skill。用于 pooled CRISPR screen、RNAi screen、Perturb-seq、DepMap/gene essentiality、sgRNA count matrix、MAGeCK 风格 hit calling、library QC 和候选基因优先级交接。
---

# 功能基因组筛选流程

## 使用边界

用于 pooled perturbation screens 和 gene essentiality 分析。若用户正在设计单个 CRISPR guide，读取 `../../molecular-biology-design/crispr-guide-editing/SKILL.md`；若是单细胞 Perturb-seq 表达分析，可能还要串联 `../single-cell-rna-analysis/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_workflow_templates/screen_analysis_plan.yaml`：library、样本、count matrix、contrast、QC 和 hit calling 模板。
- `references/screen_analysis_qc.md`：screen 设计、library representation、MAGeCK/RRA、Perturb-seq 和 DepMap 解释边界。

## 推荐流程

1. 明确 screen 类型：knockout、CRISPRi/a、base editor screen、RNAi、Perturb-seq、drug modifier。
2. 输入检查：library annotation、sgRNA counts、sample metadata、timepoint/treatment、replicate。
3. QC：read depth、mapping rate、library representation、Gini index、control guide behavior、bottleneck。
4. Hit calling：sgRNA-level normalization、gene-level aggregation、RRA/negative binomial/model-based contrast。
5. Perturb-seq：guide assignment、MOI、cell QC、DE per perturbation、pathway/regulon。
6. 输出：gene hit table、sgRNA table、QC report、candidate prioritization 和验证建议。

## 交接物

```yaml
bio_task_family: workflows
assay_or_pipeline: functional-genomics-screens
screen_type:
library_annotation:
count_matrix:
sample_metadata:
contrast:
qc_checkpoints:
hit_calling_method:
validation_plan:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要在 library representation 失败时解释 dropout hit。
- 不要把单条 sgRNA 的变化直接等同于 gene-level hit。
- 不要忽略非靶向 guide、阳性对照和批次/时间点结构。
