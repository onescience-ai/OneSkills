# 生物标志物 ML 验证

## 数据泄漏

- 同一患者、同一 slide、多时间点或技术重复必须在同一 split。
- Normalization、feature selection、imputation 和 batch correction 需要在训练折内拟合，再应用到验证折。
- 外部验证优先于只做交叉验证。

## 高维小样本

特征数远高于样本数时，优先使用正则化模型、稳定特征选择和嵌套交叉验证。避免在小样本上训练复杂深度模型。

## 生存分析

需要 event indicator、follow-up time、censoring 定义和 proportional hazards 检查。报告 c-index、time-dependent AUC 或 calibration，而不是普通 accuracy。
