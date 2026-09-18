# Bayesian PINN 变分推断的正确实现流程

## 适用范围
面向 Bayesian Physics-informed Neural Network（Bayesian PINN）训练任务，通过变分推断量化预测不确定性。适用于需要不确定性量化的科学计算任务，如流场反演、参数识别等。

## 输入
- 训练数据：坐标 (x, y, t) 和对应物理量 (u, v, p)
- PDE 定义：控制方程和边界条件
- 模型结构：包含贝叶斯层的神经网络

## 输出
- 变分后验分布：权重参数的均值 mu 和标准差 sigma
- ELBO 损失：数据似然 - KL 散度
- 不确定性估计：预测分布的均值和方差

## 流程节点
1. **变分后验参数化**：每个贝叶斯层的权重表示为 w = mu + sigma * epsilon，epsilon ~ N(0,1)
2. **前向传播**：通过多次 MC 采样获得预测分布
3. **数据似然计算**：负对数似然作为数据损失
4. **KL 散度计算**：解析计算后验与先验的 KL 散度
5. **ELBO 损失**：数据似然 - kl_weight * KL 散度
6. **反向传播**：ELBO 损失对模型参数求梯度

每步质量门禁：
- 贝叶斯层参数 mu 和 sigma 正确初始化
- KL 散度值非零且合理
- ELBO 损失收敛

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| KL 权重初始值 | 0.1-1.0 | [D2] | 需要网格搜索确定最佳值 |
| KL 权重退火 | 线性退火 | [D2] | 从 0 逐渐增加到目标值 |
| MC 采样次数 | 10-100 | [D2] | 影响不确定性估计质量 |
| 先验分布 | N(0,1) | [D2] | 标准正态先验 |
| 变分后验 | N(mu, sigma^2) | [D2] | 对角高斯后验 |

## 边界与分流
- 如果 KL 散度为零：检查 KL 权重是否设置过小，检查 KL 计算是否正确
- 如果不确定性估计不合理：增加 MC 采样次数，调整 KL 权重
- 如果训练不稳定：降低学习率，使用 KL 退火策略

## 质量检查
- 验证点：KL 散度 > 0 且随训练合理变化
- 阈值：KL 值应在合理范围内（如 0.01-10）
- 失败处理：重新检查 KL 计算公式

## 回退策略
- 如果变分推断不稳定：使用 Monte Carlo Dropout 作为近似
- 如果 KL 散度计算困难：使用重参数化技巧的数值近似

## 资源召回建议
- 何时召回：当 Bayesian PINN 训练中 KL 散度未有效参与损失时
- 配套资源：变分推断实现模板、KL 散度计算公式

## 补充证据（开源文档/用户自有，可选）
[D1] PyTorch Probabilistic Programming with Pyro, Pyro AI, v1.0.0, URL: https://pyro.ai/examples/（accessed_at 2026-09-17，交叉验证）
[D2] Variational Inference: A Review for Statisticians, arXiv, v1, URL: https://arxiv.org/abs/1601.00670（accessed_at 2026-09-17，单源参考）

## 证据来源
[1] Blei, D. M., Kucukelbir, A., & McAuliffe, J. D. (2017). Variational inference: A review for statisticians. Journal of the American Statistical Association, 112(518), 859-877. DOI: 10.1080/01621459.2017.1285773