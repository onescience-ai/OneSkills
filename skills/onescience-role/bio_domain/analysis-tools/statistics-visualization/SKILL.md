---
name: bio-statistics-visualization
description: 生信统计与可视化 skill。用于实验统计设计、PCA/UMAP、volcano、MA、heatmap、survival、regression、multiple testing、batch correction、SHAP、publication-ready figures 和 QC 图表规划。
---

# 生信统计与可视化

## 使用边界

用于统计方法选择、图表设计和解释框架。具体 assay 的流程仍由对应 workflow skill 主导。

## 推荐内容

- 多重检验：BH-FDR、family-wise、independent filtering。
- 组间比较：t/Wilcoxon、negative binomial、linear model、mixed model。
- 降维：PCA、UMAP、t-SNE，说明输入是否 normalized/scaled。
- 聚类：hierarchical、k-means、Leiden，说明距离和 resolution。
- 生存分析：Kaplan-Meier、Cox、censoring、covariates。
- 可视化：volcano、MA、heatmap、dotplot、ridge、violin、QC dashboard。

## 交接物

```yaml
tool_family: statistics-visualization
data_matrix:
grouping_or_covariates:
statistical_test:
multiple_testing:
visualization_type:
interpretation_limits:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要把相关性解释成因果。
- 不要在样本量不足或设计混杂时输出过强结论。
- 不要隐藏过滤阈值和多重检验方法。
