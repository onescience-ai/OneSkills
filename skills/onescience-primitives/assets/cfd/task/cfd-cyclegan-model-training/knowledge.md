# CycleGAN无配对超分辨率重建模型训练

## 适用范围

**触发条件**：
- 已完成非配对LES与DNS数据预处理与切分
- 需要训练CycleGAN完成LES到DNS的无配对映射
- 拥有计算资源（GPU推荐）和训练配置

**适用场景**：
- 湍流超分辨率的无配对域映射训练
- CycleGAN对抗训练与循环一致性约束
- LES到DNS的跨分辨率流场映射

**不适用场景**：
- 监督学习超分辨率（有配对数据）
- 实时在线推理部署
- 无计算资源的轻量级应用

## 输入

- 模型名称（{MODEL_NAME}）：默认CycleGAN
- 训练配置（{TRAIN_CONFIG}）：框架、 epochs、batch_size、学习率、种子、早停耐心
- 初始权重（{INIT_CHECKPOINT}）：可选预训练权重
- s02产出的切分与统计量

## 输出

- best_checkpoint.pt：最佳模型权重
- train_config.json：训练配置记录
- training_metrics.csv：逐轮训练验证指标
- environment.txt：代码版本与依赖环境

## 流程节点

### Step 1：环境与配置记录
- **操作**：记录代码版本、依赖库版本、随机种子
- **参数**：{TRAIN_CONFIG}中的framework、seed
- **质量门禁**：配置环境随机种子可复现

### Step 2：模型初始化
- **操作**：加载s02切分与统计量，初始化CycleGAN生成器与判别器
- **参数**：{MODEL_NAME}、{INIT_CHECKPOINT}
- **质量门禁**：若提供{INIT_CHECKPOINT}须检查结构兼容性

### Step 3：对抗训练与循环一致性
- **操作**：执行CycleGAN训练，包含对抗损失、循环一致性损失和身份损失
- **参数**：{TRAIN_CONFIG}中的epochs、batch_size、learning_rate
- **质量门禁**：训练验证损失均为有限值

### Step 4：模型保存与验证
- **操作**：保存最佳权重与训练指标，验证权重可重新加载
- **参数**：early_stopping_patience控制早停
- **质量门禁**：最佳权重可重新加载

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 训练框架 | PyTorch | 场景需求书 s03 | 深度学习框架 |
| epochs | 100 | 场景需求书 s03 | 训练轮次上限 |
| batch_size | 8 | 场景需求书 s03 | 训练批大小 |
| learning_rate | 0.001 | 场景需求书 s03 | Adam默认量级 |
| 随机种子 | 42 | 场景需求书 s03 | 可复现性 |
| 早停耐心 | 15 | 场景需求书 s03 | 防止过拟合 |

## 边界与分流

- 缺少必填输入时返回BLOCKED并列出缺项，不得编造数据
- 训练不收敛：调整超参数或回退到监督超分辨模型
- 初始权重结构不兼容：忽略预训练权重从头训练

## 质量检查

- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现
- 训练指标完整记录

## 回退策略

- 训练不收敛：调整学习率或批大小重新训练
- 过拟合：增加早停耐心或增加数据增强
- 权重保存失败：检查磁盘空间与保存逻辑

## 资源召回建议

- 何时召回本卡片：CycleGAN训练阶段、模型配置、训练策略选择
- 配套资源：cfd-cyclegan-preprocessing-data-splitting（数据预处理）、cfd-cyclegan-super-resolution-reconstruction（流场重构）

## 证据来源

[1] "Unsupervised deep learning for super-resolution reconstruction of turbulence", arXiv:2007.15324, 2020
场景需求书 CFD_S099 workflow step s03 定义。
