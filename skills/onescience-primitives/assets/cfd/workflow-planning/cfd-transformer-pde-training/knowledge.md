# PDE Transformer模型训练

## 适用范围

本任务用于PDE算子学习工作流的第三阶段，使用PDE Transformer或Universal Physics Transformer等架构训练PDE求解器，完成输入场到目标场的映射学习。适用于多方程多网格数据上的预训练或微调任务。

## 输入

- **模型名称**（{MODEL_NAME}）：PDE Transformer、Universal Physics Transformer等
- **训练配置**（{TRAIN_CONFIG}）：框架、epochs、batch_size、learning_rate、seed、early_stopping_patience
- **初始权重**（{INIT_CHECKPOINT}）：可选预训练权重，用于微调
- **切分数据**（来自s02）：train/val/test manifests与归一化统计量

## 输出

- **best_checkpoint.pt**：验证集最优模型权重
- **train_config.json**：训练配置快照
- **training_metrics.csv**：逐轮训练验证指标
- **environment.txt**：代码版本、依赖、随机种子等环境信息

## 流程节点

1. **环境准备** → 记录代码版本、依赖库版本、随机种子
2. **数据加载** → 基于s02 manifests加载训练验证数据
3. **模型构建** → 根据{MODEL_NAME}实例化Transformer模型
4. **权重初始化** → 若提供{INIT_CHECKPOINT}检查结构兼容性并加载
5. **训练循环** → 逐epoch训练，记录损失、指标，应用早停
6. **最佳权重保存** → 基于验证集指标保存best_checkpoint.pt
7. **环境记录** → 保存完整训练环境信息

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| framework | PyTorch | 场景默认 | 标准框架 |
| epochs | 100 | 场景默认 | 可根据收敛调整 |
| batch_size | 8 | 场景默认 | 受显存限制 |
| learning_rate | 0.001 | 场景默认 | Adam优化器 |
| seed | 42 | 场景默认 | 可复现训练 |
| early_stopping_patience | 15 | 场景默认 | 防止过拟合 |
| 初始权重检查 | 结构兼容性 | 场景配置 | 微调时必需 |

## 边界与分流

- **显存不足**：减小batch_size或启用梯度累积
- **收敛失败**：调整学习率、更换优化器、增加正则化
- **过拟合**：增加数据增强、增大dropout、减小模型复杂度
- **初始权重不兼容**：跳过预训练权重，从随机初始化开始
- **NaN/Inf损失**：降低学习率、检查数据质量、添加梯度裁剪

## 质量检查

- 训练验证损失均为有限值（非NaN/Inf）
- 最佳权重可重新加载并产生一致预测
- 配置环境随机种子可复现训练结果
- 早停触发时模型未严重过拟合

## 回退策略

训练不收敛→回退至更简单模型（如FNO）或增加数据增强；过拟合严重→回退至更简单模型或增加数据量。

## 资源召回建议

当用户需要PDE Transformer模型训练、预训练权重微调、或训练过程监控时，召回本卡片。

## 证据来源

[1] PDE-Transformer_ Efficient and Versatile Transformers for Physics Simulations（训练流程）
[2] Universal Physics Transformers_ A Framework For Efficiently Scaling Neural Operators（可扩展训练框架）
