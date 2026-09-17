# 模型配置与训练

## 适用范围

本卡描述可迁移ROM工作流第三步：加载s02切分数据与统计量，使用Transferable ROM或Shallow Recurrent Decoder训练可迁移降阶模型。适用于需要跨几何参数泛化的CFD ROM训练任务。

## 输入

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| s02切分数据 | object | 是 | train_manifest.json, validation_manifest.json |
| s02统计量 | object | 是 | normalization.json |
| {MODEL_NAME} | str | 是 | 模型名称（Transferable ROM或Shallow Recurrent Decoder） |
| {TRAIN_CONFIG} | object | 是 | 训练超参数配置 |
| {INIT_CHECKPOINT} | doc | 否 | 预训练权重（可选） |

## 输出

| 输出 | 说明 |
|------|------|
| best_checkpoint.pt | 最佳验证性能的模型权重 |
| train_config.json | 最终训练配置（含所有超参数） |
| training_metrics.csv | 逐轮训练验证指标（loss、metrics等） |
| environment.txt | 代码版本、依赖库版本、随机种子信息 |

## 流程节点

1. **数据加载**：读取s02切分数据与归一化统计量
2. **模型构建**：按{MODEL_NAME}实例化Transferable ROM或Shallow Recurrent Decoder
3. **权重初始化**：若提供{INIT_CHECKPOINT}检查结构兼容性并加载
4. **训练循环**：按{TRAIN_CONFIG}执行训练，逐轮记录训练与验证指标
5. **早停判断**：基于验证集性能与patience参数决定是否早停
6. **最佳权重保存**：保存验证性能最佳的模型权重
7. **环境记录**：记录代码版本、依赖库、随机种子等复现信息

## 关键参数

### 通用判据

| 参数 | 判据 | 来源 | 说明 |
|------|------|------|------|
| 损失有限性 | 训练与验证loss均为有限值 | s03质量门禁 | 训练过程健康指标 |
| 权重可加载 | best_checkpoint.pt可重新加载 | s03质量门禁 | 产物有效性验证 |
| 可复现性 | 配置环境随机种子可复现 | s03质量门禁 | 科学可复现性要求 |
| 结构兼容性 | {INIT_CHECKPOINT}与当前模型结构匹配 | s03流程要求 | 预训练权重加载前提 |

### 校准数值

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认框架 | PyTorch | 场景需求书s03 | 其他体系需重新锚定 |
| 默认Epochs | 100 | 场景需求书s03 | 其他体系需重新锚定 |
| 默认Batch Size | 8 | 场景需求书s03 | 其他体系需重新锚定 |
| 默认学习率 | 0.001 | 场景需求书s03 | 其他体系需重新锚定 |
| 默认随机种子 | 42 | 场景需求书s03 | 复现性保障 |
| Early Stopping Patience | 15 | 场景需求书s03 | 其他体系需重新锚定 |

## 边界与分流

- 训练/验证loss出现NaN或Inf → 终止训练，检查数据质量与超参数
- 权重无法重新加载 → 判定训练产物无效，需重新训练
- {INIT_CHECKPOINT}结构不兼容 → 跳过预训练权重加载，从头训练
- 缺少必填输入 → 返回BLOCKED并列出缺项
- 训练过程不收敛 → 调整学习率、batch size或模型架构

## 质量检查

- 训练验证损失均为有限值（无NaN/Inf）
- 最佳权重可重新加载（结构与参数完整）
- 配置环境随机种子可复现（记录所有随机源）
- training_metrics.csv包含逐轮训练与验证指标
- environment.txt包含完整的依赖版本信息

## 回退策略

- 不收敛：调整学习率（降低或增加）、增大batch size、更换优化器
- 过拟合：增加正则化、调整模型复杂度、增加训练数据
- 欠拟合：增加模型容量、延长训练轮数、调整特征工程
- 权重加载失败：检查模型架构差异，必要时从头训练

## 资源召回建议

当任务需要训练可迁移ROM或Shallow Recurrent Decoder时召回本卡片。本卡片依赖s02切分数据，完成后进入s04推理。

## 证据来源

[1] 场景需求书CFD_S090 s03步骤定义
[2] Real-Time Monitoring of MHD Liquid Metal Flows with Shallow Recurrent Decoders, arxiv:2608.28366, 2026
[3] Non-intrusive, transferable model for coupled turbulent channel-porous media flow based upon neural networks, arxiv:2311.15600, 2023
[4] Intrusive versus non-intrusive reduced-order modeling of generalized Newtonian fluid flows, arxiv:2608.18259, 2026
