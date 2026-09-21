# 材料机器学习中的数据集规模要求

## 适用范围
适用于材料科学机器学习任务中需要评估数据集规模是否足够的场景，特别是小数据集问题。

## 输入
- 当前数据集：样本数量、特征维度
- 模型类型：机器学习算法
- 性能要求：泛化能力、过拟合风险

## 输出
- 数据集规模评估：是否满足最低要求
- 过拟合风险评估：训练集与验证集性能差异
- 数据增强建议：增加数据集规模的方法

## 流程节点
1. 评估当前数据集规模 → 2. 分析过拟合风险 → 3. 选择数据增强方法 → 4. 实施数据增强 → 5. 验证效果

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 最低样本量 | 10×特征数 | [1] | 经验法则：样本量至少是特征数的10倍 |
| 过拟合阈值 | 训练R² - 验证R² > 0.2 | [2] | 过拟合诊断标准 |
| 数据增强方法 | SMOTE | [1] | 合成少数类过采样技术 |
| 交叉验证 | 5-fold CV | [1] | 评估模型泛化能力 |
| 特征选择 | PCA/特征重要性 | [1] | 降低特征维度 |

## 边界与分流
- 如果数据量严重不足（<50样本），考虑使用简单模型或迁移学习
- 如果特征维度高，使用特征选择或降维
- 如果过拟合严重，使用正则化或集成方法

## 质量检查
- 检查数据集规模是否满足模型要求
- 评估过拟合风险
- 验证数据增强效果

## 回退策略
- 如果数据增强效果差，记录数据局限性
- 如果模型过拟合，尝试简化模型或增加数据
- 如果无法获得足够数据，使用迁移学习或预训练模型

## 资源召回建议
- 当任务涉及小数据集机器学习时召回本卡片
- 当任务需要评估数据集规模时召回本卡片
- 配套工具：scikit-learn、imbalanced-learn、SMOTE

## 证据来源
[1] Predicting the thermodynamic stability of perovskite oxides using multiple machine learning techniques, Vidyasagar Shetty, Shabari Shedthi B, J. Kumaraswamy, Materials Today: Proceedings, 2022, DOI: 10.1016/j.matpr.2021.09.208
[2] On a Scalable Entropic Breaching of the Overfitting Barrier for Small Data Problems in Machine Learning, Illia Horenko, Neural Computation, 2020, DOI: 10.1162/neco_a_01296