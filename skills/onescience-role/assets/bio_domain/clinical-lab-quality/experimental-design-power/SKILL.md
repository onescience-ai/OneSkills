---
name: bio-experimental-design-power
description: 生物实验设计、样本量和统计功效 skill。用于 omics study design、批次设计、paired/blocking、replicate、power analysis、multiple testing、randomization、covariate、time course 和统计风险评估。
---

# 实验设计与功效

## 推荐流程

1. 明确研究问题、主要终点、数据类型和预期 effect size。
2. 设计样本结构：condition、batch、sex、age、timepoint、paired/block、technical/biological replicate。
3. 样本量与功效：根据测试类型、dispersion/variance、multiple testing 和可用预算估计。
4. 批次与随机化：平衡关键协变量，避免 condition 与 batch 完全混杂。
5. 输出设计矩阵、contrast、风险点和最小可行实验设计。

## 交接物

```yaml
task_context: experimental-design
assay:
primary_endpoint:
groups_and_covariates:
replicate_plan:
power_assumptions:
batch_randomization:
contrast_plan:
deliverable:
execution_entry:
```

## 禁止事项

- 不要把 technical replicate 当 biological replicate。
- 不要忽略多重检验对功效的影响。
- 不要接受完全混杂的 batch/condition 而不标记风险。
