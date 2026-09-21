# 材料机器学习中的过拟合诊断

## 适用范围
适用于材料科学机器学习任务中需要诊断和处理过拟合问题的场景，特别是模型在训练集表现良好但验证集表现差的情况。

## 输入
- 训练好的机器学习模型
- 训练集和验证集性能指标
- 模型复杂度参数

## 输出
- 过拟合诊断：是否过拟合、过拟合程度
- 诊断方法：学习曲线、验证曲线
- 解决方案：正则化、交叉验证、简化模型

## 流程节点
1. 收集性能指标 → 2. 绘制学习曲线 → 3. 分析验证曲线 → 4. 选择正则化方法 → 5. 实施解决方案 → 6. 验证效果

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 过拟合阈值 | 训练R² - 验证R² > 0.2 | [1] | 过拟合诊断标准 |
| 学习曲线 | 训练/验证误差随样本量变化 | [1] | 诊断过拟合的常用方法 |
| 验证曲线 | 性能随超参数变化 | [1] | 选择最优超参数 |
| 正则化 | L1/L2正则化 | [2] | 减少模型复杂度 |
| 交叉验证 | k-fold CV | [1] | 评估模型泛化能力 |

## 边界与分流
- 如果过拟合严重，尝试增加数据或简化模型
- 如果欠拟合，尝试增加模型复杂度或特征
- 如果数据量小，使用交叉验证而非简单划分

## 质量检查
- 检查学习曲线是否收敛
- 评估正则化效果
- 验证交叉验证结果的稳定性

## 回退策略
- 如果正则化效果差，尝试其他正则化方法
- 如果交叉验证结果不稳定，增加交叉验证折数
- 如果无法解决过拟合，记录模型局限性

## 资源召回建议
- 当任务涉及模型过拟合问题时召回本卡片
- 当任务需要模型选择和验证时召回本卡片
- 配套工具：scikit-learn、matplotlib、seaborn

## 证据来源
[1] Machine learning analysis on stability of perovskite solar cells, Çağla Odabaşı, Ramazan Yıldırım, Solar Energy Materials and Solar Cells, 2020, DOI: 10.1016/j.solmat.2019.110284
[2] Associations of Normalization and Regularization with Machine Learning Overfitting in Cross-dataset Classification of Deaths Using Transcriptomic and Clinical Data: A Secondary Analysis of Publicly Available Databases, Fei Deng, Lanjing Zhang, Journal of Clinical and Translational Pathology, 2026, DOI: 10.14218/jctp.2025.00051