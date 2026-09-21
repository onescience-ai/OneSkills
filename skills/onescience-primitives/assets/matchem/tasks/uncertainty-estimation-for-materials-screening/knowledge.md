# 材料筛选中的不确定性估计

## 适用范围
适用于机器学习模型在材料筛选任务中需要评估预测可靠性的场景，特别是高风险候选材料的筛选。

## 输入
- 训练好的机器学习模型
- 测试数据或新候选材料
- 不确定性估计方法选择

## 输出
- 预测值及其置信区间
- 不确定性评分
- 可靠性排序

## 流程节点
1. 选择不确定性估计方法 → 2. 实现不确定性计算 → 3. 集成到预测流程 → 4. 验证不确定性估计效果

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 集成方法 | Bagging/Boosting | [1] | 通过模型集成估计不确定性 |
| 贝叶斯神经网络 | 变分推断 | [2] | 使用贝叶斯方法估计参数不确定性 |
| Dropout | Monte Carlo Dropout | [1] | 训练时使用Dropout，预测时多次采样 |
| 置信区间 | 95% CI | [1] | 标准置信区间水平 |
| 采样次数 | 100次 | [1] | Monte Carlo Dropout采样次数 |

## 边界与分流
- 如果模型是集成模型（如Random Forest），可以直接使用树预测的方差
- 如果模型是神经网络，考虑使用Bayesian方法或Dropout
- 如果计算资源有限，使用简化的不确定性估计方法

## 质量检查
- 验证不确定性估计与实际误差的相关性
- 检查不确定性评分是否合理（高不确定性对应高误差）
- 评估不确定性估计的计算开销

## 回退策略
- 如果复杂方法计算开销大，使用简单的集成方法
- 如果贝叶斯方法实现困难，使用Dropout近似
- 如果不确定性估计效果差，记录局限性

## 资源召回建议
- 当任务需要评估预测可靠性时召回本卡片
- 当任务涉及高风险材料筛选时召回本卡片
- 配套工具：scikit-learn、TensorFlow Probability、Pyro

## 证据来源
[1] From prediction to reliable screening: Explainable and uncertainty-aware machine learning for the limiting oxygen index of flame-retardant epoxy composites, Diana Rbehat, Materials Letters, 2026, DOI: 10.1016/j.matlet.2026.141596
[2] Machine learning incorporating stability features and Bayesian Optimization for perovskite structure prediction, Pan Xu, Yang Liu, Li Song, Solid State Communications, 2025, DOI: 10.1016/j.ssc.2025.116174