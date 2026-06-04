# 系统发育方法选择

## 输入检查

- Alignment 需要检查长度、缺失、低复杂度、饱和突变、重组和 paralog 混入。
- Partition 适合多基因或 codon position 分区。
- Tree file 需要确认叶名和 metadata 是否一一对应。

## 方法

- NJ/UPGMA：探索性、快速，不适合最终复杂演化解释。
- ML：常用作发表级系统树，需模型选择和支持度评估。
- Bayesian：适合 posterior 支持、clock model、模型平均，但需 MCMC 收敛检查。
- Species tree：多基因树冲突或 incomplete lineage sorting 时使用。
- Divergence dating：需要校准点、clock model 和先验说明。

## 支持度解释

Bootstrap、SH-aLRT、posterior probability、concordance factor 不是同一种统计量，不能机械比较。
