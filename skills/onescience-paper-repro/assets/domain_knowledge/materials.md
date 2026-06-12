# Materials Domain Knowledge

| 字段 | 摘要 |
| --- | --- |
| 适用领域 | 材料、化学、分子、晶体和原子尺度建模论文。 |
| 召回信号 | materials、chemistry、molecule、crystal、atom、lattice、energy、force、stress、neighbor graph、cutoff、equivariance。 |
| 核心用途 | 提示原子/晶胞/周期边界/能量力应力/图构建/等变性/单位与归一化的提取与审计。 |
| 注意事项 | 只作为检查清单；只有论文或用户材料出现的内容才能写成确定要求。 |

用于材料、化学、分子、晶体和原子尺度建模论文的提取提示。这里只提供检查清单，不提供论文事实。

## 常见数据对象

- atom types、positions、lattice/cell、periodic boundary condition。
- energy、force、stress、charge、dipole、band gap、formation energy。
- neighbor graph、cutoff radius、edge features、angle/dihedral/three-body features。
- E(3)/SE(3) equivariance、invariance、reference energy。

## 提取时重点检查

- 能量、力、应力等目标要分清训练 target、预测 output 和评估 metric。
- 单位转换、reference energy、normalization 和 per-atom/per-structure reduction 必须有证据。
- graph 构建要记录 cutoff、neighbor limit、periodic image、edge direction 和 feature 维度。
- 等变/不变约束不能只写模型名，要说明作用对象和输出变换规则。
- 数据 split 要检查 composition、structure、time、material family 或 benchmark split。

## 常见评估提示

- MAE/RMSE for energy/force/stress。
- per-atom energy error、force component error、relaxation success。
- property prediction metrics：AUC、F1、R2、Spearman/Pearson。

只有论文实际出现或用户材料提供的指标才能写成确定评估要求。
