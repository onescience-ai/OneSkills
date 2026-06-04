---
name: bio-causal-genomics
description: 因果基因组学 skill。用于 Mendelian randomization、colocalization、fine mapping、pleiotropy、Steiger filtering、mediation、eQTL/mQTL/pQTL 与 GWAS 信号整合和敏感性分析交接。
---

# 因果基因组学

## 使用边界

用于从 GWAS/QTL/omics summary stats 中评估可能的因果关系和候选 causal variant/gene。若只是运行 GWAS，读取 `../../population-phylo-evolution/population-genetics-gwas/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_table_templates/causal_genomics_plan.yaml`：暴露、结局、工具变量、LD、colocalization 和敏感性分析模板。
- `references/causal_inference_checks.md`：MR 假设、pleiotropy、fine mapping、colocalization 和 mediation 边界。

## 推荐流程

1. 明确问题：exposure、outcome、population、trait definition 和方向。
2. 工具变量：显著阈值、LD clumping、F statistic、Steiger direction、palindromic SNP。
3. MR：IVW、weighted median、MR-Egger、MR-PRESSO、leave-one-out。
4. Colocalization/fine mapping：GWAS 与 QTL 是否共享 causal variant，credible set 和 LD reference。
5. Mediation：genotype -> molecular phenotype -> disease 的直接/间接效应。
6. 输出：effect estimate、sensitivity table、assumption checks、not-causal caveats。

## 交接物

```yaml
bio_task_family: translational-biomarker
translational_task: causal-genomics
exposure:
outcome:
summary_stats:
ld_reference:
instrument_selection:
mr_methods:
colocalization_or_finemapping:
sensitivity_checks:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要把相关性或共定位概率直接写成因果证明。
- 不要忽略水平多效性、样本重叠和 ancestry mismatch。
- 不要在没有 LD reference 的情况下构建 credible set。
