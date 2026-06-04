---
name: bio-phylogenetics-tree-analysis
description: 系统发育树分析 skill。用于 Newick/Nexus/PhyloXML 读取转换、ML 或 Bayesian tree inference、模型选择、bootstrap/posterior 支持度、rooting、pruning、species tree、divergence dating 和树图交接。
---

# 系统发育树分析

## 使用边界

用于从 alignment 或 tree file 推断、整理、可视化和解释系统发育关系。若重点是病原传播监测，读取 `../pathogen-genomic-surveillance/SKILL.md`；若重点是群体结构/GWAS，读取 `../population-genetics-gwas/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_population_templates/phylo_analysis_plan.yaml`：alignment、taxa、模型、支持度、rooting 和输出模板。
- `references/phylo_method_selection.md`：tree inference、support、rooting、species tree 和 dating 的方法选择。
- `onescience-coder/assets/bio_population_tools/newick_qc.py`：轻量 Newick 括号、叶名和分支长度 QC。

## 推荐流程

1. 明确输入：multiple sequence alignment、gene tree、species tree、partition、metadata。
2. 选择方法：distance/NJ 探索、ML tree、Bayesian tree、coalescent species tree、dating。
3. 记录模型：substitution model、partition scheme、rate heterogeneity、clock model。
4. 评估支持度：bootstrap、SH-aLRT、posterior probability、concordance factors。
5. 处理树：rooting、pruning、renaming、ladderize、metadata annotation、figure。
6. 输出：tree file、方法参数、支持度解释、图、限制说明。

## 交接物

```yaml
bio_task_family: population-phylo-evolution
evolution_task: phylogenetics-tree-analysis
alignment_or_tree:
taxa_metadata:
inference_method:
model_or_partition:
support_metrics:
rooting_strategy:
visualization:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要把不同支持度指标混为一个阈值。
- 不要在没有 outgroup 或 rooting 依据时解释祖先方向。
- 不要忽略 alignment quality、recombination、horizontal transfer 或 paralog 混入。
