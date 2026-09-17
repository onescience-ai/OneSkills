# 等变PDE模型配置与训练

## 适用范围

本卡片服务于对称PDE预测模型的训练阶段。在数据预处理与切分完成后，需要选择并配置等变神经网络架构（Lie-equivariant neural network或PDO convolution），完成从输入物理场到目标物理场的映射训练。适用于需要保持旋转/平移等变性的PDE预测任务。不适用于：PDE无明显群对称性（应使用标准U-Net/ResNet）；数据量极小无法支撑等变网络参数量（应使用迁移学习或小模型策略）。

## 输入

- s02输出的train/validation/test manifest与normalization.json
- 模型名称（{MODEL_NAME}）：默认Lie-equivariant neural network、PDO convolution
- 训练配置（{TRAIN_CONFIG}）：框架、超参数、随机种子
- 可选初始权重（{INIT_CHECKPOINT}）

## 输出

- best_checkpoint.pt：最佳模型权重
- train_config.json：训练配置快照
- training_metrics.csv：逐轮训练验证指标
- environment.txt：代码版本、依赖环境

## 流程节点

1. **模型实例化** → 按{MODEL_NAME}选择架构，检查参数量与显存适配
2. **权重加载** → 若提供{INIT_CHECKPOINT}检查结构兼容性
3. **数据加载器构建** → 基于s02 manifest构建DataLoader，应用normalization.json变换
4. **训练循环** → 记录逐轮train/val loss、学习率、epoch时间
5. **早停与模型保存** → 按early_stopping_patience保存best checkpoint
6. **环境记录** → 保存代码版本、pip freeze、随机种子

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 架构选择 | Lie-equivariant / PDO convolution | 场景JSON s03 | 根据对称群选择 |
| 训练验证损失 | 均为有限值 | 场景JSON s03 quality_gate | NaN/Inf即BLOCKED |
| 权重可重加载 | best_checkpoint.pt可重新加载 | 场景JSON s03 quality_gate | 强制门禁 |
| 环境可复现 | 随机种子+依赖版本完整 | 场景JSON s03 quality_gate | 强制门禁 |
| 预训练权重检查 | 结构兼容性验证 | 场景JSON s03 prompt | 加载前必须 |

### 校准数值（来自CFD_S063场景）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 框架 | PyTorch | 场景JSON s03 default | |
| epochs | 100 | 场景JSON s03 default | |
| batch_size | 8 | 场景JSON s03 default | |
| learning_rate | 0.001 | 场景JSON s03 default | |
| seed | 42 | 场景JSON s03 default | |
| early_stopping_patience | 15 | 场景JSON s03 default | |

## 边界与分流

- **显存不足**：减小batch_size或使用梯度累积
- **训练损失不收敛**：检查学习率、数据契约一致性、对称群选择是否匹配
- **预训练权重结构不兼容**：跳过预训练，从头训练
- **验证损失振荡**：增加early_stopping_patience或降低学习率

## 质量检查

- 训练验证损失均为有限值（质量门禁）
- 最佳权重可重新加载（质量门禁）
- 配置环境随机种子可复现（质量门禁）
- training_metrics.csv包含逐轮指标

## 回退策略

- 等变网络训练失败：退化为标准U-Net基线对比
- 全部超参组合失败：报告失败原因，建议架构调整或数据增强

## 资源召回建议

当用户任务涉及以下场景时召回：
- "等变网络训练"、"PDO卷积训练"、"PDE模型训练"、"Lie equivariant training"
- 配套卡片：cfd-pdo-convolution-layer-design（PDO层设计细节）、cfd-lie-algebra-canonicalization（李代数正规化）

## 证据来源

场景CFD_S063 workflow step s03定义。
[8] PDO-eConvs: Partial Differential Operator Based Equivariant Convolutions
[9] PDO-s3DCNNs: Partial Differential Operator Based Steerable 3D CNNs
