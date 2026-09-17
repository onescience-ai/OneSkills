# 可微PDE模型训练

## 适用范围

**触发条件**：
- 已完成数据预处理与切分
- 需要训练嵌入PDE物理约束的深度学习模型
- 模型需支持自动微分计算PDE残差

**适用场景**：
- PINN/PDE-GNN/DeepONet等物理信息模型的训练
- 流体力学中的正问题（给定参数求解流场）和反问题（从观测反推参数）
- 需要物理一致性的流场预测

**不适用场景**：
- 纯数据驱动模型（无PDE约束）
- 离线训练已完成、仅需推理的场景

## 输入

- 模型名称（{MODEL_NAME}）：Differentiable PDE-GNN、Physics-aware data assimilation
- 训练配置（{TRAIN_CONFIG}）：框架、 epochs、batch_size、learning_rate、seed等
- 初始权重（{INIT_CHECKPOINT}）：可选预训练权重

## 输出

- best_checkpoint.pt：最佳模型权重
- train_config.json：训练配置
- training_metrics.csv：逐轮训练验证指标
- environment.txt：代码版本、依赖、随机种子

## 流程节点

### Step 1：模型架构配置
- **操作**：选择并配置模型架构（PINN/DeepONet/GNN）
- **参数**：网络深度4-6层，宽度50-100神经元/层 [2]
- **质量门禁**：架构配置与数据维度匹配

### Step 2：损失函数设计
- **操作**：设计组合损失函数
- **参数**：L = λ_data * L_data + λ_physics * L_physics + λ_bc * L_bc [1]
- **质量门禁**：各损失项均为有限值，权重可调

### Step 3：激活函数选择
- **操作**：根据源项光滑性选择激活函数
- **参数**：光滑源项→tanh（LAAF-5）；非光滑源项→sigmoid（LAAF-10）[2]
- **质量门禁**：激活函数选择与问题特征匹配

### Step 4：优化器训练
- **操作**：Adam→L-BFGS-B两阶段优化 [2]
- **参数**：Adam学习率0.001，10-2000 epochs；L-BFGS-B 1000+ epochs
- **质量门禁**：训练验证损失均为有限值

### Step 5：迁移学习与早停
- **操作**：利用预训练权重初始化，监控验证损失早停
- **参数**：early_stopping_patience=15
- **质量门禁**：最佳权重可重新加载

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 网络深度 | 4-6层 | [2] | 深度比宽度更重要 |
| 激活函数 | tanh/sigmoid | [2] | 光滑用tanh，非光滑用sigmoid |
| LAAF因子 | 5（光滑）/10（非光滑） | [2] | 局部自适应激活函数 |
| 优化器 | Adam→L-BFGS-B | [2] | 两阶段策略 |
| Adam epochs | 10-2000 | [2] | 避免L-BFGS-B陷入局部极小 |
| L-BFGS-B | ftol≤1E-4 | [2] | 停止准则 |
| 损失权重 | λ_data, λ_physics, λ_bc | [1] | 可学习或手动调节 |
| 配点数 | 128×128域内+4000边界 | [2] | 示例配置 |
| 迁移学习 | 预训练权重初始化 | [2] | 显著减少训练epoch |

## 边界与分流

- 激活函数选择错误：可能导致训练不收敛或精度不足
- L-BFGS-B直接使用（无Adam预训练）：可能快速收敛到错误解
- 配点数过少：训练误差不反映实际精度
- 源项含高频分量时：迁移学习预训练源应含高频分量

## 质量检查

- 训练/验证损失曲线平滑下降
- 最佳权重可重新加载并产生一致预测
- 随机种子和环境信息完整记录

## 回退策略

- 训练不收敛：检查激活函数、降低学习率、增加配点
- 过拟合：增加正则化、减少网络深度、使用早停
- 物理不一致：增加PDE残差权重

## 资源召回建议

- 何时召回本卡片：训练物理信息模型、PINN/DeepONet/GNN训练配置
- 配套资源：cfd-differentiable-pde-gnn-hybrid-data-assimilation（场景总卡）、cfd-batch-inference-physical-recovery（推理）

## 证据来源

[1] Wang S, Wang H, Perdikaris P. "Learning the solution operator of parametric PDEs with physics-informed DeepONets", Science Advances, 2021, DOI: 10.1126/sciadv.abi8605
[2] Markidis S. "The Old and the New: Can Physics-Informed Deep-Learning Replace Traditional Linear Solvers?", Frontiers in Big Data, 2021, DOI: 10.3389/fdata.2021.669097
