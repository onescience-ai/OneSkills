# 模型配置与训练

## 适用范围

适用于物理信息扩散模型在流场分布生成任务中的训练阶段。涵盖模型架构选择、超参数配置、训练执行、指标记录与权重保存。支持从头训练与预训练权重微调两种模式。

## 输入

- {MODEL_NAME}（必填）：模型实现或注册名，默认 Physics-informed diffusion model
- {TRAIN_CONFIG}（必填）：训练超参数配置
- {INIT_CHECKPOINT}（可选）：预训练权重路径
- s02 产出的切分数据与 normalization.json

## 输出

- best_checkpoint.pt：最佳模型权重
- train_config.json：完整训练配置记录
- training_metrics.csv：逐轮训练验证指标
- environment.txt：代码版本、依赖、随机种子

## 流程节点

1. 加载 s02 切分数据与归一化统计量
2. 解析 {TRAIN_CONFIG}，初始化模型架构
3. 若提供 {INIT_CHECKPOINT}，加载并检查结构兼容性
4. 执行训练循环：前向传播、物理损失计算、反向传播、参数更新
5. 逐轮记录训练与验证指标
6. 应用早停机制（early_stopping_patience）
7. 保存最佳权重（基于验证损失）
8. 输出训练配置、指标与环境信息

## 关键参数

### 通用判据

| 参数 | 说明 | 来源 |
|------|------|------|
| 损失有限性 | 训练与验证损失均为有限值（非 NaN/Inf） | [场景需求书 s03] |
| 权重可重载 | best_checkpoint.pt 可被正确加载 | [场景需求书 s03] |
| 可复现性 | 随机种子、环境、配置完整记录 | [场景需求书 s03] |
| 结构兼容性 | {INIT_CHECKPOINT} 与当前模型架构匹配 | [场景需求书 s03] |

### 校准数值

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认框架 | PyTorch | [场景需求书] | 默认实现 |
| 默认 epochs | 100 | [场景需求书] | 可调整 |
| 默认 batch_size | 8 | [场景需求书] | 按显存调整 |
| 默认 learning_rate | 0.001 | [场景需求书] | 可调整 |
| 默认 seed | 42 | [场景需求书] | 可调整 |
| early_stopping_patience | 15 | [场景需求书] | 防止过拟合 |

## 边界与分流

- 损失为 NaN/Inf → 检查数据质量与超参数，降低学习率或减小 batch_size
- {INIT_CHECKPOINT} 结构不兼容 → 回退到从头训练
- 训练不收敛（损失平台） → 增加 epochs 或调整学习率调度
- 显存不足 → 减小 batch_size 或使用梯度累积

## 质量检查

- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

## 回退策略

- 从头训练失败 → 使用预训练权重微调
- 物理损失权重过高导致训练不稳定 → 降低物理损失权重
- 验证损失持续上升 → 加强早停或调整正则化

## 资源召回建议

- 需要了解扩散模型训练配置时召回本卡
- 需要了解物理信息损失设计时召回场景卡
- 需要了解模型架构选择时召回论文证据

## 证据来源

[1] Physics-Informed Diffusion Models, 2024
[2] Learning Distributions of Complex Fluid Simulations with Diffusion Graph Networks, Lino et al., ICLR 2025, arXiv:2504.02843
[3] Self-Augmented Diffusion Guidance for Physics-Informed Generation, Osaka et al., 2026, arXiv:2608.26748
[4] 场景需求书 CFD_S091 s03
