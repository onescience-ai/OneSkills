# 模型配置与训练

## 适用范围

本卡片描述物理信息神经网络稀疏观测参数反演工作流的第三步：模型配置与训练。适用于：
- Inverse PINN的训练与调优
- Physics-informed data assimilation的实现
- 物理约束与数据损失的融合训练

**不适用场景**：
- 纯数据驱动的模型训练
- 无物理约束的正问题求解

## 输入

1. **模型名称** `{MODEL_NAME}`：Inverse PINN, Physics-informed data assimilation
2. **训练配置** `{TRAIN_CONFIG}`：超参数和随机种子
3. **初始权重** `{INIT_CHECKPOINT}`：可选预训练权重

## 输出

1. **最佳权重** `best_checkpoint.pt`
2. **训练配置** `train_config.json`
3. **训练指标** `training_metrics.csv`
4. **环境信息** `environment.txt`

## 流程节点

```
加载切分数据 → 初始化模型 → 定义损失函数 → 训练循环 → 验证评估 → 保存最佳权重 → 记录环境
```

### 详细操作

#### 1. 数据加载与模型初始化

**操作**：
- 加载s02切分与统计量
- 初始化Inverse PINN或Physics-informed data assimilation模型
- 检查模型结构与数据维度匹配

**判定标准**：
- 数据加载成功
- 模型初始化完成
- 维度匹配

#### 2. 损失函数定义

**操作**：
- 数据损失：观测点处的预测与真实值误差
- 物理损失：PDE方程残差
- 边界损失：边界条件满足程度
- 总损失：加权组合

**判定标准**：
- 损失函数可计算
- 权重设置合理
- 梯度可传播

#### 3. 训练循环

**操作**：
- 执行训练 epochs 轮
- 每轮计算训练损失与验证损失
- 应用早停策略
- 记录逐轮指标

**判定标准**：
- 损失为有限值
- 验证损失不发散
- 早停正确触发

#### 4. 最佳权重保存

**操作**：
- 基于验证损失选择最佳权重
- 保存模型状态字典
- 验证权重可重新加载

**判定标准**：
- 最佳权重保存成功
- 权重可重新加载
- 模型结构一致

#### 5. 环境记录

**操作**：
- 记录代码版本
- 记录依赖库版本
- 记录随机种子
- 记录训练时间

**判定标准**：
- 环境信息完整
- 可复现性保证

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 训练框架 | PyTorch | [场景需求书] | 深度学习框架 |
| 早停耐心 | 15 epochs | [场景需求书] | 防止过拟合 |
| 随机种子 | 42 | [场景需求书] | 可复现性 |

### 校准数值（以下数值来自CFD_S038场景，供量级校准；其他体系需以自身证据重新锚定）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| epochs | 100 | [场景需求书] | 训练轮数 |
| batch_size | 8 | [场景需求书] | 批量大小 |
| learning_rate | 0.001 | [场景需求书] | 学习率 |

## 边界与分流

1. **训练不收敛**：损失为NaN或Inf → 调整学习率或损失权重
2. **过拟合**：验证损失上升 → 增加早停耐心或正则化
3. **欠拟合**：训练验证损失均高 → 增加模型容量或训练轮数
4. **梯度消失/爆炸**：梯度范数异常 → 调整网络架构或使用梯度裁剪
5. **显存不足**：batch_size过大 → 减小批量或使用梯度累积

## 质量检查

1. **损失有限**：训练验证损失均为有限值
2. **权重可加载**：最佳权重可重新加载
3. **可复现**：配置环境随机种子可复现
4. **收敛性**：训练损失下降趋势
5. **泛化性**：验证损失与训练损失差距合理

## 回退策略

1. **训练失败** → 传统优化方法（遗传算法、粒子群）
2. **显存不足** → 减小批量或使用混合精度
3. **收敛困难** → 调整学习率调度器
4. **过拟合** → 增加数据增强或正则化

## 资源召回建议

**何时召回本卡片**：
- 需要执行PINN模型的训练
- 需要定义物理约束损失函数
- 需要训练过程的监控与保存

**配套资源**：
- 场景卡：cfd-inverse-pinn-sparse-observation-parameter-inversion
- 工作流卡：cfd-inverse-pinn-sparse-observation-workflow
- 任务卡：cfd-inverse-pinn-preprocessing-data-split
- 任务卡：cfd-inverse-pinn-equation-solving-residual-recovery

## 证据来源

[1] Physics informed deep learning (Part I): Data-driven solutions of nonlinear partial differential equations, 2017, URL: https://arxiv.org/abs/1711.10561
[2] Inferring flow parameters and turbulent configuration with physics-informed data assimilation and spectral nudging, 2018, URL: https://arxiv.org/abs/1804.07680
[3] 场景需求书CFD_S038：物理信息网络稀疏观测参数反演，s03步骤定义
