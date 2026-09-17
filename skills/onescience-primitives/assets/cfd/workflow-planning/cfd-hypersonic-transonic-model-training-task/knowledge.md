# 模型配置与训练任务

## 适用范围

本任务描述数据驱动湍流代理模型构建的第三步：训练Transformer aerodynamic surrogate、Neural turbulence model完成指定输入到目标物理量的映射。这是将数据转化为可预测模型的核心步骤。

**适用场景**：
- 高超声速冷壁边界层湍流代理模型训练
- 跨声速机翼CFD数据驱动模型训练
- 需要物理一致性约束的神经网络训练
- 需要可复现训练过程的模型开发

**不适用场景**：
- 非神经网络模型（如随机森林、支持向量机）
- 已有预训练模型且无需微调
- 数据量过小无法训练深度学习模型

## 输入

- **{MODEL_NAME}**（必填）：模型名称，默认"Transformer aerodynamic surrogate、Neural turbulence model"
- **{TRAIN_CONFIG}**（必填）：训练配置，默认framework: PyTorch, epochs: 100, batch_size: 8, learning_rate: 0.001, seed: 42, early_stopping_patience: 15
- **{INIT_CHECKPOINT}**（可选）：初始权重路径

## 输出

- **best_checkpoint.pt**：最佳模型权重
- **train_config.json**：训练配置文件
- **training_metrics.csv**：训练指标记录
- **environment.txt**：环境依赖信息

## 流程节点

```
加载数据切分 → 初始化模型 → 配置训练参数 → 执行训练循环 → 记录训练指标 → 保存最佳权重 → 验证可复现性
```

### 操作步骤

1. **加载数据切分**：读取s02输出的train/validation/test清单
2. **初始化模型**：根据{MODEL_NAME}创建模型实例
3. **配置训练参数**：设置{TRAIN_CONFIG}中的超参数
4. **执行训练循环**：训练模型，监控训练和验证损失
5. **记录训练指标**：保存逐轮训练验证指标
6. **保存最佳权重**：保存验证损失最低的模型权重
7. **验证可复现性**：使用相同种子重新训练，验证结果一致

## 关键参数

### 通用判据（方法层，同类体系可参考）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 训练框架 | PyTorch | [场景需求书s03] | 默认框架 |
| 训练轮数 | 100 | [场景需求书s03] | 默认epochs |
| 批大小 | 8 | [场景需求书s03] | 默认batch_size |
| 学习率 | 0.001 | [场景需求书s03] | 默认learning_rate |
| 随机种子 | 42 | [场景需求书s03] | 可复现性 |
| 早停耐心 | 15 | [场景需求书s03] | early_stopping_patience |

### 校准数值（体系专属值）

以下数值来自高超声速冷壁与跨声速机翼CFD体系，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型类型 | Transformer aerodynamic surrogate, Neural turbulence model | [场景需求书s03] | 数据驱动湍流代理模型 |
| 损失函数 | 待确认 | [场景需求书s03] | 需根据任务选择 |
| 优化器 | 待确认 | [场景需求书s03] | 需根据任务选择 |

## 边界与分流

**关键前提与分流策略**：

1. **前提：数据切分可用**
   - 不成立时：需返回s02重新进行数据切分
   - 分流目标：完成预处理与数据切分

2. **前提：模型结构可定义**
   - 不成立时：若模型结构不明确，需参考文献定义
   - 分流目标：使用标准Transformer或MLP结构

3. **前提：训练过程稳定**
   - 不成立时：若训练发散，需调整超参数
   - 分流目标：降低学习率、增加批次大小、添加正则化

4. **前提：验证损失收敛**
   - 不成立时：若验证损失不收敛，需检查数据质量
   - 分流目标：增加数据量、简化模型、调整早停耐心

## 质量检查

**验证点**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现
- 训练指标记录完整

**阈值**：
- 训练损失：有限值（非NaN/Inf）
- 验证损失：有限值（非NaN/Inf）
- 可复现性：相同种子结果一致

**失败处理**：
- 训练发散：调整超参数
- 验证损失不收敛：检查数据质量
- 权重保存失败：检查磁盘空间、文件权限

## 回退策略

1. **训练发散**：降低学习率、增加批次大小、添加正则化
2. **验证损失不收敛**：增加数据量、简化模型、调整早停耐心
3. **权重保存失败**：检查磁盘空间、文件权限
4. **可复现性失败**：固定随机种子、检查依赖版本

## 资源召回建议

**何时应召回本卡片**：
- 用户需要训练数据驱动的湍流代理模型
- 场景涉及高超声速或跨声速边界层CFD
- 需要可复现的训练过程

**配套资源**：
- cfd-hypersonic-transonic-turbulence-surrogate-scenario: 场景级概述
- cfd-hypersonic-transonic-turbulence-surrogate-workflow: 完整工作流
- cfd-hypersonic-transonic-preprocessing-task: 预处理与切分
- cfd-hypersonic-transonic-posteriori-validation-task: 后验耦合验证

## 证据来源

[1] Data-Driven Turbulence Modeling Approach for Cold-Wall Hypersonic Boundary Layers, arXiv:2406.17446, 2024
[2] Scalable Transformer for PDE Surrogate Modeling, arXiv:2209.04934, 2022
