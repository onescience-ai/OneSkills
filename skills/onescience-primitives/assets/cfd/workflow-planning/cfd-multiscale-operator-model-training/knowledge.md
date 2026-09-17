# 多尺度算子模型训练

## 适用范围

**触发条件**：
- 已完成数据预处理与切分，需要训练神经算子模型
- 需要训练Wavelet Neural Operator或Localized-kernel Operator
- 需要记录训练过程与最佳权重

**适用场景**：
- 算子学习工作流的模型训练阶段
- 需要确保模型收敛性与可复现性
- 需要保存训练配置与环境记录

**不适用场景**：
- 数据未预处理或切分完成
- 非神经算子模型的训练任务

## 输入

**必填输入**：
- {MODEL_NAME}：模型名称（默认Wavelet Neural Operator、Localized-kernel operator）
- {TRAIN_CONFIG}：训练配置（框架、epochs、batch_size、学习率等）

**可选输入**：
- {INIT_CHECKPOINT}：初始权重（可选预训练权重）

## 输出

**产物清单**：
- best_checkpoint.pt：最佳模型权重
- train_config.json：训练配置
- training_metrics.csv：逐轮训练验证指标
- environment.txt：依赖环境记录

## 流程节点

### 操作步骤
1. 使用{MODEL_NAME}和{TRAIN_CONFIG}训练模型
2. 加载s02切分与统计量
3. 记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重
4. 若提供{INIT_CHECKPOINT}须检查结构兼容性
5. 缺少必填输入时返回BLOCKED并列出缺项

### 关键参数
- 模型：Wavelet Neural Operator, Localized-kernel Operator
- 框架：PyTorch
- 默认epochs：100
- 默认batch_size：8
- 默认learning_rate：0.001
- 默认early_stopping_patience：15

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认epochs | 100 | [场景S055] | 训练轮数 |
| 默认batch_size | 8 | [场景S055] | 批大小 |
| 默认learning_rate | 0.001 | [场景S055] | 学习率 |
| 默认early_stopping_patience | 15 | [场景S055] | 早停耐心 |
| 训练框架 | PyTorch | [场景S055] | 默认深度学习框架 |
| 随机种子 | 42 | [场景S055] | 可复现性 |

## 边界与分流

**异常处理**：
1. 训练损失不收敛 → 检查数据质量、调整学习率或模型架构
2. 验证损失过拟合 → 增加正则化、使用早停或数据增强
3. 初始权重不兼容 → 移除预训练权重，从头训练
4. 计算资源不足 → 降级为小规模实验或使用混合精度训练

## 质量检查

**验证点**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

**失败处理**：
- 任一验证点不通过 → 检查训练日志，定位问题并修复

## 回退策略

**替代方案**：
- 模型不收敛 → 更换架构或调整超参数
- 过拟合严重 → 增加数据量或使用更强正则化
- 计算资源不足 → 降级为小规模实验

## 资源召回建议

**何时召回**：
- 算子学习工作流的模型训练阶段
- 需要训练Wavelet或Localized-kernel模型时
- 需要确保模型可复现性时

**配套资源**：
- cfd-pde-data-preprocessing-splitting（数据预处理任务）
- cfd-operator-inference-physical-recovery（推理恢复任务）

## 证据来源

[1] Multiwavelet-based Operator Learning for Differential Equations, arXiv:2109.13459, 2021
[2] Neural Operators with Localized Integral and Differential Kernels, 2023
