# Neural SDE 架构设计与训练方法

## 适用范围

面向PDE场量预测（如扩散-反应方程、Navier-Stokes方程）中需要学习随机动力学的条件生成任务。适用于需要同时建模确定性动力学和随机性的场景，例如多物理PDE模拟中的不确定性量化、条件场量生成、轨迹预测等。不适用于纯确定性ODE系统或不需要随机性的任务。

## 输入

- PDE场量数据（浓度场、温度场、速度场的时间序列）
- 条件信息（初始条件、边界条件、物理参数）
- 训练配置（epochs、learning_rate、batch_size）

## 输出

- 训练好的Neural SDE模型（drift网络 + diffusion网络 checkpoint）
- 训练指标（loss曲线、KL散度、Wasserstein距离）
- 生成样本（从噪声分布到目标分布的采样结果）

## 流程节点

### 1. Neural SDE 架构定义
- **操作**：定义drift函数 f(x,t) 和 diffusion函数 g(x,t) 的神经网络参数化
- **参数**：drift_net（MLP/CNN，输入x+t，输出f(x,t)），diffusion_net（MLP/CNN，输入x+t，输出g(x,t)）
- **工具**：PyTorch/TensorFlow
- **质量门禁**：drift和diffusion网络输出维度与状态空间匹配；diffusion输出非负（通过softplus或abs激活）

### 2. SDE 求解器选择
- **操作**：选择前向和反向SDE的数值求解器
- **参数**：solver=Euler-Maruyama（一阶）或SRK（高阶），dt=0.01, n_steps=100
- **工具**：torchsde/torchdiffeq库
- **质量门禁**：求解器步长满足稳定性条件；轨迹数值稳定（无NaN/Inf）

### 3. Score Matching 训练
- **操作**：使用denoising score matching目标训练score网络
- **参数**：loss=denoising_score_matching, weighting=likelihood (λ(t)=g(t)²)
- **工具**：自定义训练循环
- **质量门禁**：训练loss收敛；验证集score matching误差稳定下降

### 4. ODE-SDE 一致性保障
- **操作**：添加Fokker-Planck残差正则化项以缩小ODE-SDE差距
- **参数**：w_R=0.1-1.0（正则化权重），FP_residual_weight=0.1
- **工具**：自定义损失函数
- **质量门禁**：Wasserstein-2距离(P_θ^ODE, P_θ^SDE) < C·δ（定理3.1）

### 5. 条件生成集成
- **操作**：将条件信息嵌入drift/diffusion网络（通过拼接、加法或注意力机制）
- **参数**：condition_embedding_dim=64, guidance_scale=λ（classifier-free guidance）
- **工具**：条件嵌入模块
- **质量门禁**：条件生成分布与目标条件分布的KL散度在合理范围

### 6. 评估与验证
- **操作**：计算生成分布与真实分布的KL散度和Wasserstein距离
- **参数**：n_eval_samples=10000, metrics=[KL, W2, FID]
- **工具**：SciPy/POT库
- **质量门禁**：KL散度<5.0；生成样本物理合理性检查（non-negative、守恒律）

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 前向SDE形式 | VP-SDE: f(x,t)=-0.5β(t)x, g(t)=√β(t) | [1] | Variance Preserving SDE，β(t)从0.001线性增至0.5 |
| Score网络 | s_θ(x,t) ≈ ∇_x log p(x,t) | [1] | 通过反向传播自动可微计算 |
| Euler-Maruyama步长 | dt ≤ 0.01 | [2] | 确保SDE数值解稳定性 |
| Denoising score matching | L_DSM = E[λ(t)||s_θ(x_t,t) - ∇_x log p(x_t|x_0)||²] | [2] | 标准训练目标 |
| Likelihood weighting | λ(t) = g(t)² | [2] | 与似然训练相关的加权函数 |
| Fokker-Planck残差 | R̃(θ,u_θ,t) | [2] | 衡量神经近似与Fokker-Planck方程的一致性 |
| ODE-SDE差距 | W_2(p_θ^ODE, p_θ^SDE) ≤ C·R̃ | [2] | 定理3.1：Wasserstein-2距离的上界 |
| Classifier-free guidance | s̃_θ(x,c,t) = (1+λ)s_θ(x,c,t) - λs_θ(x,t) | [1] | 条件生成的分数调整 |

### 校准数值（扩散-反应PDE体系）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| VP-SDE β(t)范围 | 0.001 → 0.5 | [1] | 线性增加的噪声调度 |
| 状态空间维度 | 2D latent (d=2) | [1] | VAE编码后的潜空间维度 |
| 时间嵌入维度 | d/2 | [1] | sin/cos编码的频率参数维度 |
| 生成质量指标（KL） | <0.1（无条件）; <0.5（有条件） | [1] | KL散度越小表示生成分布越接近真实分布 |

## 边界与分流

- **SDE求解器不稳定**：减小步长dt或改用高阶求解器（如SRK方法）
- **ODE-SDE差距过大**：增加Fokker-Planck残差正则化权重w_R，但注意可能降低SDE采样质量
- **条件生成模式坍塌**：增加classifier-free guidance的随机性（训练时随机drop条件）
- **训练不收敛**：检查score网络初始化、学习率调度、噪声调度β(t)范围

## 质量检查

- [ ] model/目录下存在drift网络和diffusion网络的checkpoint
- [ ] training_metrics.json记录了完整的训练曲线
- [ ] 生成样本的KL散度在合理范围
- [ ] 生成场量无NaN/Inf值
- [ ] 条件生成结果与条件信息一致

## 回退策略

- 若Neural SDE训练不成功，可退化为Neural ODE（仅使用drift网络，无diffusion）
- 若SDE求解器不稳定，可使用概率流ODE替代反向SDE采样
- 若score matching训练困难，可改用flow matching作为替代训练范式

## 资源召回建议

- 本卡片适用于需要同时建模确定性和随机性动力学的PDE条件生成任务
- 配套资源：cfd-conditional-generative-pde-data-pipeline（数据准备流程）
- 配套资源：cfd-pde-training-evaluation-standards（训练配置与评估标准）

## 证据来源

[1] Chen Y, et al. "Resistive memory-based neural differential equation solver for score-based diffusion models", Nature Communications, 2026, DOI: 10.1038/s41467-026-72900-z

[2] Dickinson T, et al. "Closing the ODE-SDE gap in score-based diffusion models through the Fokker-Planck equation", Phil. Trans. R. Soc. A, 2025, DOI: 10.1098/rsta.2024.0503

[3] Zeng S, et al. "Generative models of cell dynamics: from Neural ODEs to flow matching", Communications Biology, 2026, DOI: 10.1038/s42003-026-09758-w
