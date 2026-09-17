# 自编码器潜空间流动降阶时序预测

## 适用范围

本卡片服务的问题类是：面向高维流场快照时序数据，使用自编码器进行潜空间流动降阶并完成时序预测。适用于平流主导型偏微分方程系统（如 Burgers 方程、浅水方程）的低维表示与时间演化建模，适用于需要快速推理的工程仿真场景。不适用于扩散主导型系统或需要严格守恒律保证的场景。

## 输入

- **数据格式**：高维流场快照时序数据（如 2D/3D 网格上的速度、压力场）
- **数据来源**：CFD 模拟输出、实验测量数据
- **预处理要求**：统一物理量与表示，按几何、工况或时间构造无泄漏切分；归一化或无量纲化处理

## 输出

- **产物**：训练好的自编码器模型、潜空间动力学模型、预测结果、物理一致性评估报告
- **格式**：模型权重文件、预测数据文件、评估指标报告
- **验证标准**：相对 L2 误差、RMSE、守恒残差、边界误差等统计与物理指标

## 流程节点

1. **数据接入与契约核验** → 检查文件可读性、样本数、变量单位、坐标系、网格拓扑、时间范围、缺失值和使用许可
2. **预处理与数据切分** → 统一物理量与表示，按几何、工况或时间构造无泄漏切分
3. **模型配置与训练** → 训练卷积自编码器（CAE）和潜空间动力学模型
4. **批量推理与物理恢复** → 在独立测试集推理，恢复原始单位、网格和物理派生量
5. **任务验收与适用域判定** → 评估统计误差、关键物理约束、泛化能力和计算收益

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 潜空间维度 | 2-6 | [1] | 低维表示维度，需平衡重建质量与预测能力 |
| 自编码器类型 | 卷积自编码器（CAE） | [1][5] | 适用于流场数据的局部特征提取 |
| 动力学模型 | RNN/LSTM/NODE | [1][3] | 用于潜空间时序演化建模 |
| 训练框架 | PyTorch | 场景需求书 | 默认深度学习框架 |
| 早停耐心 | 15 | 场景需求书 | 防止过拟合的早停轮数 |
| 相对误差门限 | 0.1 | 场景需求书 | 测试集放行阈值 |

## 边界与分流

- **平流主导系统**：CAE+RNN 组合优于传统 POD-Galerkin 方法 [1]
- **混沌系统**：β-VAE+Transformer 组合可捕捉复杂动力学 [2]
- **需要解释性**：可采用可解释 CAE 方法 [5]
- **域外工况**：需经 CFD 复核，不得仅凭平均误差宣称工程可用

## 质量检查

- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现
- 预测无 NaN 或 Inf 且形状单位正确
- 统计与物理指标同时报告

## 回退策略

- 若自编码器重建质量不足，可调整潜空间维度或网络结构
- 若动力学模型预测发散，可尝试不同的时间序列模型（LSTM、NODE、Transformer）
- 若物理一致性不满足，可添加物理约束正则化项

## 资源召回建议

- 当用户需要流场降阶建模时召回本卡片
- 配套资源：数据处理技能（onescience-data-standardizer）、模型训练技能（onescience-trainer）
- 相关场景：CFD 流场预测、流动稳定性分析、参数化研究

## 证据来源

[1] Reduced-order modeling of advection-dominated systems with recurrent neural networks and convolutional autoencoders, Maulik et al., 2020, DOI: 10.48550/arXiv.2002.00470
[2] β-Variational autoencoders and transformers for reduced-order modelling of fluid flows, Solera-Rico et al., 2023, DOI: 10.48550/arXiv.2304.03571
[3] Evolve Smoothly, Fit Consistently: Learning Smooth Latent Dynamics For Advection-Dominated Systems, Wan et al., 2023, DOI: 10.48550/arXiv.2301.10391
[4] Time-series learning of latent-space dynamics for reduced-order model closure, Maulik et al., 2019, DOI: 10.48550/arXiv.1906.07815
[5] Slim multi-scale convolutional autoencoder-based reduced-order models for interpretable features of a complex dynamical system, Teutsch et al., 2025, DOI: 10.48550/arXiv.2501.03070