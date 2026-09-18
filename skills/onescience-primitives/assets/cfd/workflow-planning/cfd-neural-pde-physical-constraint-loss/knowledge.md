# 神经PDE求解器的物理约束损失函数设计

## 适用范围

面向物理信息神经网络（PINN）及神经算子在求解偏微分方程时的损失函数设计，当需要确保模型输出满足质量守恒、能量守恒等基本物理定律时召回本卡片。适用于扩散方程、Navier-Stokes方程、Allen-Cahn方程、KdV方程等需要物理一致性的CFD仿真场景。核心方法是将PDE残差、守恒律约束作为损失项嵌入训练目标，同时采用适当的激活函数和多目标优化策略。不适用于纯数据驱动且无需物理约束的场景。

## 输入

- **PDE定义**：控制方程（如Navier-Stokes、扩散方程）、边界条件、初始条件
- **训练数据**：配点坐标（x, t）及对应的解值或残差标签
- **物理约束类型**：质量守恒、能量守恒、动量守恒、PDE残差
- **激活函数选择**：tanh、sin、ReLU等，影响频谱表达能力
- **损失权重配置**：数据损失、PDE损失、边界损失、守恒损失的权重

## 输出

- **物理一致的预测解**：满足PDE和守恒律的解 u(x, t)
- **损失收敛曲线**：各损失项的收敛情况
- **守恒误差指标**：质量/能量守恒误差的定量评估
- **模型检查点**：训练过程中保存的最佳模型权重

## 流程节点

```
Step 1: 配点采样 → 在时空域内采样训练配点（随机/自适应）
Step 2: 损失函数构建 → 组合数据损失、PDE损失、边界损失、守恒损失
Step 3: 前向传播 → 神经网络预测解 u_nn(x, t)
Step 4: 自动微分计算 → 计算PDE残差所需的偏导数
Step 5: 损失计算 → 分别计算各损失项并加权求和
Step 6: 反向传播 → 梯度下降更新网络参数
Step 7: 收敛判断 → 检查损失是否满足阈值，若未满足返回Step 3
Step 8: 守恒验证 → 在测试集上验证质量/能量守恒误差
```

每步含：
- **操作**：配点采样、自动微分、损失计算
- **参数**：配点数、损失权重、学习率、激活函数
- **工具**：PyTorch自动微分、自定义损失函数
- **质量门禁**：PDE残差 < 1e-3，守恒误差 < 5%

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| PDE残差损失权重 | 1.0 - 10.0 | [1][2][4] | 根据问题难度调整 |
| 守恒约束损失权重 | 0.1 - 1.0 | [1][2] | 过大可能影响精度 |
| 边界条件损失权重 | 1.0 - 100.0 | [3][4] | 边界约束通常较强 |
| 数据损失权重 | 1.0 | [3][4] | 有监督数据时使用 |
| 激活函数 | sin/tanh（频谱问题） | [1] | sin更适合振荡解 |

### 校准数值（KdV/Allen-Cahn体系）

以下数值来自具体论文实验，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| KdV方程质量守恒误差 | < 1e-4 | [1] | 正弦激活+守恒约束 |
| KdV方程能量守恒误差 | < 1e-4 | [1] | 正弦激活+守恒约束 |
| Allen-Cahn质量守恒误差 | < 1e-3 | [2] | 时空自适应采样 |
| 质量约束损失权重 | 1.0 - 10.0 | [2] | 补偿质量退化问题 |
| 激活函数收敛加速 | 比tanh快2-5倍 | [1] | 正弦激活函数 |

## 边界与分流

- **守恒约束过强**：若守恒损失权重过大，可能导致解偏离真实PDE解→ 降低权重或改用软约束
- **PDE残差计算不稳定**：若自动微分导致梯度爆炸→ 降低学习率或使用梯度裁剪
- **激活函数选择不当**：若tanh无法捕捉高频振荡→ 改用正弦激活函数
- **多目标损失冲突**：若各损失项梯度方向冲突→ 使用多目标优化算法（如Pareto优化）

## 质量检查

- **PDE残差验证**：在独立测试集上计算PDE残差是否满足阈值
- **守恒律验证**：计算质量/能量守恒误差是否满足阈值（如 < 5%）
- **边界条件验证**：检查边界上的预测值是否满足边界条件
- **收敛曲线分析**：检查各损失项是否单调下降

## 回退策略

- **守恒误差过大**：增加守恒约束权重或改用结构保持方法
- **PDE残差不收敛**：增加配点数或使用自适应采样
- **训练不稳定**：降低学习率或使用学习率调度器
- **激活函数失效**：尝试不同激活函数（sin/tanh/ReLU）

## 资源召回建议

- 当任务涉及**PINN或神经算子训练**时召回本卡片
- 当需要**确保物理守恒律**时召回本卡片
- 配套资源：cfd-parareal-neural-operator-time-parallel（时间并行求解）、cfd-pinn-complex-geometry-collocation-data（复杂几何配点）

## 证据来源

[1] Obieke V, Oguadimma E. "Structure-Preserving Physics-Informed Neural Network for the Korteweg--de Vries (KdV) Equation", arXiv:2511.00418, 2025

[2] Huang Q, Ma J, Xu Z. "Mass-preserving spatio-temporal adaptive PINN for Cahn-Hilliard equations with strong nonlinearity and singularity", arXiv:2404.18054, 2024

[3] Karra S, Ahmmed B, Mudunuru MK. "AdjointNet: Constraining machine learning models with physics-based codes", arXiv:2109.03956, 2021

[4] Laubscher R, Rousseau P. "Application of mixed-variable physics-informed neural networks to solve normalised momentum and energy transport equations for 2D internal convective flow", arXiv:2105.10889, 2021
