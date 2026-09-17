# 模型配置与训练

## 适用范围

**触发条件**：
- 已有预处理好的训练数据（s02输出）
- 需要使用Transolver、Mesh Transformer等模型训练流场预测模型
- 需要可复现的训练流程

**适用场景**：
- 大规模网格Transformer流场预测的模型训练阶段
- 任何需要训练神经PDE求解器的场景

**不适用场景**：
- 使用预训练模型直接推理
- 小规模问题使用传统数值方法

## 输入

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| {MODEL_NAME} | str | 是 | 模型名称（Transolver、Mesh Transformer） |
| {TRAIN_CONFIG} | object | 是 | 训练配置（超参数、随机种子等） |
| {INIT_CHECKPOINT} | doc | 否 | 可选预训练权重 |

**{TRAIN_CONFIG}默认结构**：
```json
{
  "framework": "PyTorch",
  "epochs": 100,
  "batch_size": 8,
  "learning_rate": 0.001,
  "seed": 42,
  "early_stopping_patience": 15
}
```

## 输出

| 输出 | 格式 | 说明 |
|------|------|------|
| best_checkpoint.pt | PyTorch | 最佳模型权重 |
| train_config.json | JSON | 训练配置 |
| training_metrics.csv | CSV | 逐轮训练验证指标 |
| environment.txt | Text | 环境信息（代码版本、依赖） |

## 操作流程

### 1. 数据加载
- 加载s02切分后的训练集和验证集
- 加载normalization.json统计量
- 构建数据加载器

### 2. 模型初始化
- 根据{MODEL_NAME}初始化模型
- 若提供{INIT_CHECKPOINT}，检查结构兼容性
- 初始化优化器和损失函数

### 3. 记录环境
- 记录代码版本
- 记录依赖包版本
- 记录随机种子
- 记录硬件信息

### 4. 训练循环
- 逐轮训练和验证
- 记录训练损失和验证损失
- 应用早停策略（patience=15）
- 保存最佳权重

### 5. 结果保存
- 保存best_checkpoint.pt
- 保存train_config.json
- 保存training_metrics.csv
- 保存environment.txt

## 质量门禁

| 门禁 | 标准 | 失败处理 |
|------|------|----------|
| 损失有限 | 训练验证损失均为有限值 | 检查模型和数据 |
| 权重可加载 | 最佳权重可重新加载 | 检查保存逻辑 |
| 可复现 | 配置环境随机种子可复现 | 记录完整环境 |
| 无编造 | 不得编造数据、权重、工况或结果 | 如实记录 |

## 边界与分流

| 情况 | 处理方式 |
|------|----------|
| 缺少必填输入 | 返回BLOCKED并列出缺项 |
| 模型不收敛 | 调整学习率/批大小/模型复杂度 |
| 权重结构不匹配 | 检查{INIT_CHECKPOINT}兼容性 |
| 训练过拟合 | 增加正则化、调整早停耐心 |
| 训练欠拟合 | 增加训练轮数、调整学习率 |

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 框架 | PyTorch | [场景需求书] | 默认训练框架 |
| 早停耐心 | 15 | [场景需求书] | 验证损失不改善容忍轮数 |
| 可复现 | 随机种子+环境记录 | [场景需求书] | 必须保证 |

### 校准数值

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 训练轮数 | 100 | [场景需求书] | 以下数值来自CFD_S006场景，供量级校准；其他体系需以自身证据重新锚定 |
| 批大小 | 8 | [场景需求书] | 默认训练批大小 |
| 学习率 | 0.001 | [场景需求书] | 默认学习率 |
| 随机种子 | 42 | [场景需求书] | 可复现性保证 |

## 回退策略

1. **不收敛**：调整学习率（减小/增大）、批大小、模型复杂度
2. **过拟合**：增加正则化、数据增强、调整早停耐心
3. **欠拟合**：增加训练轮数、调整学习率、增加模型容量
4. **权重不匹配**：检查模型结构，调整{INIT_CHECKPOINT}
5. **资源不足**：减小批大小、使用混合精度训练

## 资源召回建议

当用户需求涉及以下场景时应召回本卡片：
- 训练Transolver、Mesh Transformer等神经PDE求解器
- 需要可复现的训练流程
- 需要训练监控和早停策略

配套资源建议：
- `cfd-mesh-transformer-preprocessing-split`：上一步预处理卡
- `cfd-mesh-transformer-inference-recovery`：下一步推理卡

## 证据来源

[1] "Transolver: A Fast Transformer Solver for PDEs on General Geometries", 2024
[2] "Transolver++: An Accurate Neural Solver for PDEs on Million-Scale Geometries", 2024

注：本卡片知识来源为场景需求书CFD_S006的s03步骤定义。
