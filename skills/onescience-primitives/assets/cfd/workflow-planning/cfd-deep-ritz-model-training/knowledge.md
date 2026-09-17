# 模型配置与训练

## 适用范围

**触发条件**：
- 已完成数据预处理与切分（s02）
- 需要训练Deep Ritz网络或弱形式神经求解器

**适用场景**：
- Deep Ritz网络训练（直接最小化能量泛函）
- 弱形式神经求解器训练（分布意义下满足方程）
- 需要可复现训练过程的场景

**不适用场景**：
- 数据尚未预处理
- 需要迁移学习或微调的场景（需检查兼容性）

## 输入

- **MODEL_NAME**（必需）：模型名称，如"Deep Ritz network"或"Weak-form neural solver"
- **TRAIN_CONFIG**（必需）：训练配置，含框架、epochs、batch_size、learning_rate等
- **INIT_CHECKPOINT**（可选）：预训练权重，需检查结构兼容性
- s02产出的切分数据和归一化参数

## 输出

- **best_checkpoint.pt**：最佳模型权重
- **train_config.json**：训练配置快照
- **training_metrics.csv**：逐轮训练验证指标
- **environment.txt**：代码版本、依赖、随机种子

## 流程节点

### 1. 模型初始化
- 根据MODEL_NAME选择网络架构
- 初始化权重（或加载INIT_CHECKPOINT）
- 验证输入输出维度匹配

### 2. 损失函数配置
- Deep Ritz：能量泛函积分损失
- 弱形式：弱形式残差积分损失
- 可选：边界条件损失、正则化项

### 3. 训练循环
- 逐epoch计算训练损失和验证损失
- 记录逐轮指标
- 早停策略（patience=15）

### 4. 最佳权重保存
- 基于验证损失选择最佳epoch
- 保存checkpoint（含模型状态、优化器状态、epoch）
- 验证权重可重新加载

### 5. 环境记录
- 记录Python版本、PyTorch版本
- 记录所有依赖包版本
- 记录随机种子设置

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 框架 | PyTorch | [1] | 默认实现框架 |
| epochs | 100 | [1] | 默认训练轮数 |
| batch_size | 8 | [1] | 按显存调整 |
| learning_rate | 0.001 | [1] | 需根据问题调整 |
| early_stopping_patience | 15 | [1] | 防止过拟合 |
| 随机种子 | 42 | [1] | 可复现性 |

## 边界与分流

- **INIT_CHECKPOINT不兼容**：若结构不匹配，忽略预训练权重并从头训练
- **训练损失为NaN/Inf**：检查变分形式、学习率、网络初始化
- **验证损失不下降**：调整学习率、增加正则化、检查数据
- **内存不足**：减小batch_size或使用梯度累积

## 质量检查

- [ ] 训练验证损失均为有限值
- [ ] 最佳权重可重新加载
- [ ] 配置环境随机种子可复现
- [ ] 训练指标完整记录

## 回退策略

- 训练不收敛 → 调整超参数重试
- 内存不足 → 减小batch_size
- 模型不适用 → 尝试另一种变分求解器

## 资源召回建议

本卡是Deep Ritz工作流的第三步。完成后进入方程求解与物理残差恢复步骤（cfd-deep-ritz-equation-solving-residual-recovery）。

## 证据来源

[1] "The Deep Ritz Method: A Deep Learning-Based Numerical Algorithm for Solving Variational Problems", E and Yu, 2017
[2] "Refined generalization analysis of the Deep Ritz Method and Physics-Informed Neural Networks", 2023
[3] "Adaptive activation functions accelerate convergence in deep and physics-informed neural networks", 2019
