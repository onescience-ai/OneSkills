# 无铅杂化钙钛矿稳定性机器学习模型

## 适用范围
适用于无铅杂化钙钛矿材料稳定性预测任务，需要选择或配置机器学习模型的场景。

## 输入
- 特征数据：材料组成、晶体结构、电子结构特征
- 标签数据：稳定性指标（如形成能、分解能、带隙）
- 模型配置：超参数、训练策略

## 输出
- 预测结果：稳定性评分、分类标签
- 模型性能：准确率、R²值、MAE等
- 不确定性估计：预测置信区间（如适用）

## 流程节点
1. 数据预处理 → 2. 特征工程 → 3. 模型选择 → 4. 超参数调优 → 5. 模型训练 → 6. 模型验证

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Random Forest | n_estimators=100 | [1] | 随机森林模型，适用于小数据集 |
| XGBoost | learning_rate=0.1 | [2] | 梯度提升树模型，性能优异 |
| Neural Network | hidden_layers=[64,32] | [2] | 神经网络模型，适用于复杂模式 |
| 训练集比例 | 80% | [1] | 标准训练/测试划分 |
| 交叉验证 | 5-fold CV | [1] | 交叉验证评估模型稳定性 |

## 边界与分流
- 如果数据量小（<100样本），优先使用Random Forest或简单模型
- 如果特征维度高，考虑使用XGBoost或神经网络
- 如果需要不确定性估计，考虑使用贝叶斯方法或集成学习

## 质量检查
- 检查模型在验证集上的性能
- 评估过拟合风险（训练集与验证集性能差异）
- 验证模型泛化能力

## 回退策略
- 如果模型过拟合，尝试正则化或简化模型
- 如果数据不足，使用数据增强或迁移学习
- 如果性能不达标，尝试其他模型类型

## 资源召回建议
- 当任务需要选择或配置机器学习模型时召回本卡片
- 当任务涉及材料性能预测时召回本卡片
- 配套工具：scikit-learn、XGBoost、PyTorch

## 证据来源
[1] Machine learning stability and band gap of lead-free halide double perovskite materials for perovskite solar cells, Zongmei Guo, Bin Lin, Solar Energy, 2021, DOI: 10.1016/j.solener.2021.09.030
[2] Efficiency and Stability Analysis of 2D/3D Perovskite Solar Cells Using Machine Learning, Beyza Yılmaz, Çağla Odabaşı, Ramazan Yıldırım, Energy Technology, 2022, DOI: 10.1002/ente.202100948
[3] Machine learning incorporating stability features and Bayesian Optimization for perovskite structure prediction, Pan Xu, Yang Liu, Li Song, Solid State Communications, 2025, DOI: 10.1016/j.ssc.2025.116174