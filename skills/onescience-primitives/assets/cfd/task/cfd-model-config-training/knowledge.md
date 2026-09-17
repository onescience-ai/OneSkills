# 模型配置与训练

## 适用范围

本任务卡适用于数据驱动RANS湍流闭合模型的训练阶段，支持Tensor-basis neural network（张量基神经网络）和Symbolic closure model（符号闭合模型）两类模型架构，提供从超参数配置到训练监控、权重保存的完整流程。

## 输入

| 变量 | 类型 | 必填 | 说明 |
|------|------|------|------|
| MODEL_NAME | str | 是 | 模型名称（Tensor-basis neural network或Symbolic closure model） |
| TRAIN_CONFIG | object | 是 | 训练配置（框架、超参数、随机种子） |
| INIT_CHECKPOINT | doc | 否 | 可选预训练权重路径 |

## 输出

| 文件 | 说明 |
|------|------|
| best_checkpoint.pt | 最佳模型权重 |
| train_config.json | 训练配置记录 |
| training_metrics.csv | 逐轮训练验证指标 |
| environment.txt | 代码版本、依赖、随机种子 |

## 流程节点

1. **环境记录**
   - 记录Python版本、PyTorch版本、CUDA版本
   - 记录所有依赖包版本（requirements.txt或pip freeze）
   - 记录随机种子设置（Python random, NumPy, PyTorch）
   - 输出到environment.txt

2. **模型初始化**
   - 根据MODEL_NAME加载模型架构
   - 若提供INIT_CHECKPOINT，检查结构兼容性
   - 初始化优化器（默认Adam）和学习率调度器

3. **训练循环**
   - 加载s02切分的训练集和验证集
   - 逐epoch执行：
     - 前向传播计算预测值
     - 计算损失函数（默认MSE）
     - 反向传播与参数更新
     - 记录训练损失和验证损失
   - 早停机制：若验证损失连续early_stopping_patience轮无改善则停止

4. **最佳权重保存**
   - 保存验证损失最低的模型权重
   - 保存格式：PyTorch state_dict + 模型架构信息
   - 验证权重可重新加载

5. **训练指标记录**
   - 逐轮记录：epoch, train_loss, val_loss, learning_rate
   - 记录最佳epoch和对应损失
   - 输出到training_metrics.csv

## 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| framework | PyTorch | 训练框架 |
| epochs | 100 | 最大训练轮数 |
| batch_size | 8 | 批大小 |
| learning_rate | 0.001 | 初始学习率 |
| seed | 42 | 全局随机种子 |
| early_stopping_patience | 15 | 早停耐心值 |
| optimizer | Adam | 优化器 |
| loss_function | MSE | 损失函数 |

## 边界与分流

- **Tensor-basis neural network**：输入为局部流动特征（应变率张量、旋转张量、湍流量等），输出为雷诺应力张量各分量；需保证输出满足张量对称性和可实现性约束
- **Symbolic closure model**：输入同上，输出为符号表达式形式的闭合模型；训练过程为符号搜索而非梯度下降，需调整超参数
- **INIT_CHECKPOINT不兼容**：返回BLOCKED，列出架构差异
- **训练发散**：降低学习率或增加正则化重试

## 质量检查

| 检查项 | 判据 | 失败处理 |
|--------|------|----------|
| 损失有限 | 训练验证损失均为有限值 | BLOCKED |
| 权重可加载 | best_checkpoint.pt可重新加载 | BLOCKED |
| 环境可复现 | 随机种子固定，结果可复现 | WARNING |
| 早停触发 | 验证损失收敛 | WARNING |

## 回退策略

- 训练发散：降低学习率、增加batch_size、添加权重衰减
- 过拟合：增加正则化、使用数据增强、简化模型架构
- 欠拟合：增加模型容量、延长训练轮数、调整损失函数

## 资源召回建议

当完成数据预处理（cfd-preprocessing-data-splitting）后召回本卡。本卡是工作流第三步，完成后进入cfd-closure-prediction-coupling。