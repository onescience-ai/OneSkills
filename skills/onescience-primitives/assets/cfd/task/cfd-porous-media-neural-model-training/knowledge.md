# 模型配置与训练

## 适用范围

**触发条件**：
- 需要训练 CNN surrogate 或 Neural differential equation 模型
- 需要记录训练过程并产出可复现的 checkpoint

**适用场景**：
- 多孔介质 CFD 数据驱动代理模型的训练
- 需要训练-验证双轨监控和早停策略
- 需要产出可复现的模型权重和训练配置

**不适用场景**：
- 已有预训练模型且无需微调
- 不涉及神经网络的传统机器学习模型

## 输入

- {MODEL_NAME}：模型名称（必填，默认"CNN surrogate, Neural differential equation"）
- {TRAIN_CONFIG}：训练配置（必填，含 framework, epochs, batch_size, learning_rate, seed, early_stopping_patience）
- {INIT_CHECKPOINT}：初始权重（可选，需检查结构兼容性）

## 输出

- best_checkpoint.pt：最佳模型权重
- train_config.json：训练配置
- training_metrics.csv：逐轮训练验证指标
- environment.txt：代码版本、依赖环境

## 流程节点

### Step 3.1：模型初始化
- **操作**：根据 MODEL_NAME 初始化模型架构
- **参数**：模型名称、输入输出维度
- **工具**：PyTorch
- **质量门禁**：模型参数量合理，前向传播可执行

### Step 3.2：训练循环
- **操作**：执行训练循环，监控训练与验证损失
- **参数**：训练配置（epochs, batch_size, learning_rate, seed）
- **工具**：PyTorch DataLoader, 优化器
- **质量门禁**：训练损失单调下降（或有合理波动），验证损失不持续上升

### Step 3.3：早停与最佳权重保存
- **操作**：根据验证损失触发早停，保存最佳权重
- **参数**：early_stopping_patience
- **工具**：早停逻辑
- **质量门禁**：最佳权重可重新加载，早停轮次合理

### Step 3.4：环境记录
- **操作**：记录代码版本、依赖库版本、随机种子
- **参数**：代码仓库、requirements
- **工具**：版本记录脚本
- **质量门禁**：环境信息完整，可复现

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 框架 | PyTorch | [场景需求书 s03] | 默认深度学习框架 |
| 早停策略 | 基于验证损失 | [场景需求书 s03] | 防止过拟合 |
| 随机种子 | 固定种子 | [场景需求书 s03] | 可复现性保证 |
| 权重保存 | 仅保存最佳验证损失对应权重 | [场景需求书 s03] | 避免保存过拟合权重 |

### 校准数值

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认 epochs | 100 | [场景需求书] | 配合早停使用 |
| 默认 batch_size | 8 | [场景需求书] | 可根据显存调整 |
| 默认 learning_rate | 0.001 | [场景需求书] | 可根据收敛情况调整 |
| 默认 seed | 42 | [场景需求书] | 可复现性保证 |
| 默认 early_stopping_patience | 15 | [场景需求书] | 可根据训练曲线调整 |

> 以上数值来自 CFD_S077 场景需求书，供量级校准；其他体系需以自身证据重新锚定。

## 边界与分流

- **训练损失出现 NaN**：降低学习率或检查数据质量
- **验证损失持续上升**：增加早停耐心或减小模型复杂度
- **模型不收敛**：检查数据预处理、调整超参数
- **初始权重不兼容**：忽略初始权重，从头训练
- **显存不足**：减小 batch_size 或使用混合精度训练

## 质量检查

- 损失有限值：训练和验证损失均为有限值
- 权重可加载：best_checkpoint.pt 可重新加载
- 配置可复现：相同种子和配置可复现训练结果
- 环境记录完整：代码版本、依赖版本、随机种子均有记录

## 回退策略

- 若 PyTorch 训练失败，可尝试 TensorFlow 框架
- 若模型架构不合适，可简化模型或调整超参数
- 若训练时间过长，可使用迁移学习或预训练权重

## 资源召回建议

当用户需要训练多孔介质 CFD 数据驱动模型时召回本卡。配套召回 `cfd-porous-media-preprocessing-split` 了解数据预处理要求。

## 证据来源

[1] "Advances in Scientific Machine Learning for Coupled Fluid Flow and Transport", arXiv:2606.19562, 2026
[2] "Online Gate-Driven Flow Control in Resin Transfer Moulding Using a Neural-Network Surrogate", arXiv:2608.29521, 2026
