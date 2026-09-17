# 神经算子模型训练

## 适用范围

**触发条件**：
- 数据预处理与切分完成后，需要训练神经算子模型
- 需要配置Continuous-time或Stochastic神经算子
- 需要可复现的训练流程与完整记录

**适用场景**：
- Continuous-time neural operator（基于流匹配/ODE积分的算子学习）训练
- Stochastic neural operator（引入随机潜变量的算子学习）训练
- 预训练模型微调（给定INIT_CHECKPOINT）

**不适用场景**：
- 数据未完成切分（先执行s02）
- 仅需推理不需训练（跳到s04）
- 模型架构自定义需求超出默认配置

## 输入

- 模型名称（MODEL_NAME）：Continuous-time neural operator或Stochastic neural operator，必填
- 训练配置（TRAIN_CONFIG）：框架、轮数、批大小、学习率、种子、早停耐心，必填
- 初始权重（INIT_CHECKPOINT）：可选预训练权重，可选

## 输出

- best_checkpoint.pt：最佳验证性能的模型权重
- train_config.json：完整训练配置
- training_metrics.csv：逐轮训练验证指标
- environment.txt：代码版本、依赖环境、随机种子

## 流程节点

### Step 3.1：模型初始化
- **操作**：根据MODEL_NAME加载或创建神经算子模型
- **质量门禁**：模型结构正确实例化；参数数量与预期一致

### Step 3.2：预训练权重加载（可选）
- **操作**：若提供INIT_CHECKPOINT，检查结构兼容性并加载
- **质量门禁**：权重shape匹配；加载无报错
- **分支**：无INIT_CHECKPOINT时随机初始化

### Step 3.3：训练循环
- **操作**：加载s02切分数据与统计量，执行训练循环
- **质量门禁**：训练损失逐轮为有限值；验证损失逐轮为有限值
- **记录**：逐轮指标写入training_metrics.csv

### Step 3.4：最佳权重保存
- **操作**：保存验证性能最佳的checkpoint
- **质量门禁**：best_checkpoint.pt可重新加载；权重文件非空

### Step 3.5：环境记录
- **操作**：记录代码版本、Python/PyTorch版本、随机种子、GPU信息
- **质量门禁**：environment.txt可追溯复现环境

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认框架 | PyTorch | 场景需求书 | 训练框架 |
| 默认轮数 | 100 epochs | 场景需求书 | 可据早停调整 |
| 默认批大小 | 8 | 场景需求书 | 按显存调整 |
| 默认学习率 | 0.001 | 场景需求书 | 优化器学习率 |
| 默认种子 | 42 | 场景需求书 | 可复现性 |
| 早停耐心 | 15 epochs | 场景需求书 | 验证损失不改善等待 |

## 边界与分流

- **INIT_CHECKPOINT结构不兼容**：拒绝加载，回退随机初始化，记录日志
- **训练损失出现NaN/Inf**：终止训练，检查数据与学习率
- **验证损失持续不下降**：触发早停，保存当前最佳
- **GPU显存不足**：减小批大小或使用梯度累积
- **缺少必填输入**：返回BLOCKED，列出缺项，不得编造权重

## 质量检查

- 逐轮训练验证损失均为有限值
- 最佳权重可重新加载且shape正确
- 配置环境（种子+版本）可复现
- 训练日志完整（无缺失轮次）

## 回退策略

- 训练不收敛：调整学习率/批大小/模型架构
- 显存溢出：减小批大小、启用混合精度
- 过拟合：增加数据增强、调整正则化、减少模型容量
- 早停触发过早：增加耐心或检查数据质量

## 资源召回建议

- 本卡片为PDE神经算子预测工作流的第三步
- 依赖cfd-pde-data-preprocessing-split的切分产出
- 完成后进入cfd-neural-operator-inference-physics-recovery进行推理

## 证据来源

[1] CFO: Learning Continuous-Time PDE Dynamics via Flow-Matched Neural Operators, arXiv:2303.08797, 2023
[2] Wavelet Diffusion Neural Operator, 2024
[3] Neural Stochastic PDEs: Resolution-Invariant Learning of Continuous Spatiotemporal Dynamics, 2023
