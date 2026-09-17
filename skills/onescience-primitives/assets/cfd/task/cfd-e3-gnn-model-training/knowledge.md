# E3等变图神经网络模型配置与训练

## 适用范围

面向E3等变图神经网络（E3-equivariant GNN）的模型配置与训练任务。适用于：
- 拉格朗日流体动力学模拟的深度学习模型训练
- 需要保持E(3)等变性（旋转、平移、反射）的物理场量预测
- 基于粒子邻域图的特征学习与动力学建模

任务目标：配置E3-equivariant GNN和Lagrangian simulator，执行训练并记录配置、指标与最佳权重，确保模型可复现、权重可加载。

## 输入

**必填输入**：
- {MODEL_NAME}: 模型名称（实现或模型注册名）
- {TRAIN_CONFIG}: 训练配置（框架、超参数、随机种子）

**可选输入**：
- {INIT_CHECKPOINT}: 初始权重（可选预训练权重）

**前置依赖**：
- s02输出的切分清单（train/val/test manifests）
- s02输出的归一化统计（normalization.json）

**训练配置默认值**：
- framework: PyTorch
- epochs: 100
- batch_size: 8
- learning_rate: 0.001
- seed: 42
- early_stopping_patience: 15

## 输出

**核心产物**：
- best_checkpoint.pt: 最佳模型权重（验证集最优）
- train_config.json: 训练配置（完整记录）
- training_metrics.csv: 训练指标（逐轮train/val loss等）
- environment.txt: 环境记录（Python版本、依赖版本、GPU信息）

**中间产物**：
- 模型结构定义
- 优化器配置
- 学习率调度器
- 早停回调

## 流程节点

```
模型初始化 → 配置加载 → 数据加载 → 训练循环 → 验证评估 → 早停 → 权重保存
```

**模型初始化**：
- 操作：加载{MODEL_NAME}（E3-equivariant GNN + Lagrangian simulator）
- 参数：模型架构参数（隐层维度、消息传递轮数等）
- 质量门禁：模型结构正确、参数初始化合理

**配置加载**：
- 操作：应用{TRAIN_CONFIG}（框架、超参数、随机种子）
- 参数：完整训练配置
- 质量门禁：配置完整、随机种子固定

**数据加载**：
- 操作：加载s02切分与统计量
- 参数：batch_size、数据加载器配置
- 质量门禁：数据加载正确、归一化应用正确

**训练循环**：
- 操作：执行前向传播、计算损失、反向传播、更新权重
- 参数：epochs、learning_rate、优化器
- 质量门禁：损失为有限值、梯度正常

**验证评估**：
- 操作：在验证集上评估模型性能
- 参数：评估指标
- 质量门禁：验证损失为有限值、指标可解释

**早停**：
- 操作：监控验证集性能，提前停止训练
- 参数：early_stopping_patience
- 质量门禁：早停逻辑正确、最佳权重保存

**权重保存**：
- 操作：保存最佳模型权重与配置
- 参数：保存路径、格式
- 质量门禁：权重可重新加载、配置完整

## 关键参数

| 参数 | 默认值 | 来源 | 说明 |
|------|--------|------|------|
| 模型架构 | E3-equivariant GNN | [场景需求书] | 保持E(3)等变性 |
| 训练框架 | PyTorch | [场景需求书] | 默认实现 |
| Epochs | 100 | [场景需求书] | 可配置 |
| Batch size | 8 | [场景需求书] | 按显存调整 |
| 学习率 | 0.001 | [场景需求书] | 默认配置 |
| 随机种子 | 42 | [场景需求书] | 可复现性 |
| 早停耐心 | 15 | [场景需求书] | 防止过拟合 |
| 隐层维度 | 64 | [场景需求书] | 默认配置 |
| 消息传递轮数 | 4 | [场景需求书] | 默认配置 |
| 等变群 | E(3) = SO(3) × Z₂ | [场景需求书] | 旋转+反射等变 |

## 边界与分流

**初始权重问题**：
- {INIT_CHECKPOINT}结构不兼容 → 检查架构差异，建议重新初始化
- {INIT_CHECKPOINT}文件不存在 → 忽略，从随机初始化开始

**训练不收敛**：
- 损失震荡 → 降低学习率、增加正则化
- 损失不下降 → 检查数据质量、调整模型复杂度
- 损失出现NaN/Inf → 检查数值稳定性、降低学习率

**过拟合**：
- 训练损失低但验证损失高 → 增加数据增强、调整模型复杂度
- 早停触发过早 → 增加耐心值、调整正则化

**显存不足**：
- CUDA OOM → 减小batch_size、使用梯度累积
- 内存不足 → 减少数据加载器工作进程

## 质量检查

**训练稳定性**：
- 损失曲线收敛性（无震荡、无发散）
- 梯度范数合理性（无爆炸、无消失）
- 学习率调度正确性

**权重可加载性**：
- 最佳权重可重新加载
- 模型结构与权重形状匹配
- 优化器状态可恢复（可选）

**配置可复现性**：
- 随机种子固定（Python、NumPy、PyTorch、CUDA）
- 依赖版本记录完整
- 环境信息完整（GPU型号、驱动版本）

**指标完整性**：
- 逐轮训练损失记录
- 逐轮验证损失记录
- 最佳轮次标记
- 训练时间统计

## 回退策略

**训练失败回退**：
- 从检查点恢复训练（如果支持）
- 调整超参数重新训练
- 使用更简单的模型架构

**权重保存失败**：
- 使用最近保存的权重
- 检查磁盘空间和权限
- 调整保存频率

**环境问题**：
- GPU不可用 → 降级到CPU训练（耗时增加）
- 依赖冲突 → 使用虚拟环境隔离
- 版本不兼容 → 降级或升级依赖

**数据加载问题**：
- 数据损坏 → 重新生成切分
- 格式不兼容 → 转换格式
- 加载缓慢 → 优化数据加载器

## 资源召回建议

**何时召回本卡片**：
- 需要配置和训练E3等变图神经网络
- 需要拉格朗日流体模拟的模型训练
- 需要保持物理对称性的深度学习模型
- 需要可复现的训练流程

**配套资源**：
- 任务卡：cfd-lagrangian-data-preprocessing-split
- 任务卡：cfd-lagrangian-inference-physics-recovery
- 工作流卡：cfd-e3-equivariant-lagrangian-fluid-workflow
- 场景卡：cfd-e3-equivariant-lagrangian-fluid-simulation

**参考实现**：
- e3nn: E(3)-equivariant neural networks
- PyTorch Geometric: 图神经网络框架
- PyTorch Lightning: 训练框架（可选）

## 证据来源

[1] Learning Lagrangian Fluid Mechanics with E(3)-Equivariant Graph Neural Networks, arXiv:2305.15603, 2023
[2] Incorporating Symmetry into Deep Dynamics Models for Improved Generalization, arXiv:2002.03061, 2020
[3] CFD_S062场景需求书, s03步骤定义, 2026