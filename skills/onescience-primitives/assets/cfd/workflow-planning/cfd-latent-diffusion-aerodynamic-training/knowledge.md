# 潜空间扩散模型气动逆向设计训练

## 适用范围

**触发条件**：
- 已完成数据预处理与切分（s02），需要训练Latent diffusion model或Generative design model
- 需要配置训练超参数、记录训练过程、保存最佳权重
- 需要验证模型可复现性（随机种子、环境、配置完整记录）

**适用场景**：
- 基于潜空间扩散模型的气动外形-流场联合逆向设计
- 生成模型在气动设计领域的训练与验证
- 需要可复现的气动设计模型训练

**不适用场景**：
- 使用传统代理模型（如Kriging、RBF）的场景
- 仅需推理不需训练的场景（使用 cfd-aerodynamic-physics-consistent-sampling）
- 无GPU环境的纯CPU训练（训练效率过低）

## 输入

- 预处理切分数据（s02输出的 train/val/test manifest）
- 归一化参数（s02输出的 normalization.json）
- 模型名称（{MODEL_NAME}：默认Latent diffusion model、Generative design model）
- 训练配置（{TRAIN_CONFIG}：框架、epochs、batch_size、learning_rate、seed、early_stopping_patience）
- 可选预训练权重（{INIT_CHECKPOINT}）

## 输出

- best_checkpoint.pt：最佳模型权重
- train_config.json：训练配置快照
- training_metrics.csv：逐轮训练验证指标
- environment.txt：依赖环境版本

## 流程节点

### Step 1：环境与配置记录
- **操作**：记录代码版本、Python/PyTorch版本、依赖列表、随机种子
- **工具**：pip freeze、git rev-parse
- **质量门禁**：环境信息完整，可复现

### Step 2：模型初始化
- **操作**：实例化Latent diffusion model、Generative design model，检查参数量和结构
- **参数**：模型架构、隐空间维度、编码器/解码器结构
- **质量门禁**：模型参数量合理；若提供初始权重需检查结构兼容性

### Step 3：训练循环
- **操作**：加载训练集，执行前向传播、损失计算、反向传播、参数更新
- **参数**：epochs=100, batch_size=8, lr=0.001, seed=42
- **质量门禁**：训练损失为有限值；不出现NaN/Inf

### Step 4：验证与早停
- **操作**：每轮在验证集上评估，记录指标，若连续patience轮无改善则早停
- **参数**：early_stopping_patience=15
- **质量门禁**：验证损失为有限值；最佳权重可重新加载

### Step 5：保存最佳权重与指标
- **操作**：保存最佳权重、训练配置、逐轮指标CSV
- **工具**：torch.save、json.dump、csv.writer
- **质量门禁**：文件完整可读；权重可重新加载

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 框架 | PyTorch | [1] | 默认 |
| epochs | 100 | [1] | 最大轮数 |
| batch_size | 8 | [1] | 按显存调整 |
| learning_rate | 0.001 | [1] | 默认 |
| seed | 42 | [1] | 可复现 |
| early_stopping_patience | 15 | [1] | 耐心值 |
| 模型 | Latent diffusion model + Generative design model | [1] | 场景指定 |

## 边界与分流

- **训练loss出现NaN/Inf**：降低学习率，检查数据质量，必要时使用梯度裁剪
- **验证loss持续不降**：检查数据-标签配对是否正确，调整模型复杂度
- **显存不足**：减小batch_size或使用混合精度训练
- **初始权重结构不兼容**：放弃初始权重，从头训练
- **训练时间过长**：减少epochs或使用更小模型

## 质量检查

- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现
- training_metrics.csv 包含逐轮train/val loss

## 回退策略

- 训练完全失败：回退到传统优化方法（如遗传算法+CFD评估）
- 模型性能不足：尝试不同模型架构或调整超参数
- 显存不足：使用梯度累积或模型并行

## 资源召回建议

- 当需要训练潜空间扩散模型用于气动设计时召回
- 配套资源：cfd-aerodynamic-data-preprocessing-split（上游）、cfd-aerodynamic-physics-consistent-sampling（下游）
- 若仅需推理：使用 cfd-aerodynamic-physics-consistent-sampling
- 若需完整工作流：使用 cfd-aerodynamic-inverse-design-workflow

## 证据来源

[1] 场景需求书 CFD_S094：生成模型气动外形与流场联合逆向设计，scenario_catalogs/fluid/CFD_S094_生成模型气动外形与流场联合逆向设计.json
[2] "Aerodynamic Shape Design Space Exploration with Deep Latent Diffusion Model", arXiv:2609.00812
[3] "From Zero to Turbulence_ Generative Modeling for 3D Flow Simulation", DOI: 10.1017/jfm.2019.923
