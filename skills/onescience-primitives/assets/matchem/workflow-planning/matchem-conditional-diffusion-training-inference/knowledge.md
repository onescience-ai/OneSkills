# Conditional Diffusion Training and Inference for Molecular Generation

## 适用范围
- **触发条件**：当任务需要训练或使用条件扩散模型生成具有特定性质的分子时。
- **适用场景**：靶点条件生成、多目标优化、属性引导生成。
- **不适用场景**：无条件分子生成、非扩散模型（如 VAE、GAN）。

## 输入
- **训练数据**：分子 SMILES、三维构象、靶点口袋特征。
- **条件信息**：目标性质（QED、SA）、靶点口袋条件向量。
- **模型配置**：噪声调度、学习率、批量大小。

## 输出
- **训练模型**：收敛的扩散模型检查点。
- **生成样本**：多样化、符合条件的三维分子。
- **训练日志**：损失曲线、收敛指标、生成质量。

## 流程节点
1. **数据编码**：将 SMILES 编码为 token 序列，三维坐标归一化。
2. **噪声调度**：定义前向扩散的噪声强度 β_t（线性或余弦调度）。
3. **条件编码**：将靶点口袋特征编码为条件向量（condition vector）。
4. **模型训练**：使用去噪分数匹配（denoising score matching）或变分下界（VLB）训练。
5. **损失监控**：监控训练损失、梯度范数、学习率。
6. **推理采样**：
   - **随机噪声初始化**：每个样本使用不同的随机种子。
   - **反向扩散**：从高斯噪声逐步去噪生成分子。
   - **条件注入**：通过交叉注意力或 FiLM 注入条件向量。
7. **后处理**：力场优化、化学价验证、多样性过滤。

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 噪声调度 β_t | 0.0001→0.02（线性） | [论文1] | 前向扩散噪声强度 |
| 学习率 | 1e-4 ~ 1e-3 | [论文2] | 优化器学习率 |
| 批量大小 | 32-128 | [论文1] | 训练批量 |
| 反向扩散步数 | 50-1000 | [论文1] | 采样质量与速度权衡 |
| 温度 τ | 0.8-1.2 | [论文2] | 控制采样多样性 |
| Classifier guidance 权重 | 0.5-2.0 | [论文3] | 条件引导强度 |

## 边界与分流
- **训练不收敛**：若损失不下降，检查学习率、损失函数、数据预处理。
- **生成多样性低**：增加温度 τ、使用不同的随机种子、增加噪声。
- **条件引导过强**：降低 classifier guidance 权重，避免模式崩溃。

## 质量检查
- **收敛标准**：训练损失下降至稳定值（SMILES 交叉熵 <5 bits/token）。
- **生成有效性**：生成分子有效性 >90%。
- **多样性**：去重后分子数 >生成数量的 50%。
- **条件符合度**：生成分子性质满足目标阈值。

## 回退策略
- **扩散模型不收敛**：回退到 VAE 或 GAN 模型。
- **条件引导失败**：使用无条件生成后过滤。
- **计算资源不足**：使用潜在扩散（latent diffusion）或减少反向扩散步数。

## 资源召回建议
- **何时召回**：当任务需要训练条件扩散模型、优化生成多样性、诊断训练问题时。
- **配套资源**：
  - `matchem-next-mol-1d-3d-fusion-architecture`：1D-3D 融合架构。
  - `matchem-molecular-generation-data-evaluation`：数据标准和评估指标。
  - `matchem-3d-diffusion-models`：三维扩散模型实现。

## 证据来源
[1] Alakhdar et al., "Diffusion Models in De Novo Drug Design", Journal of Chemical Information and Modeling, 2024, DOI: 10.1021/acs.jcim.4c01107
[2] Anstine & Isayev, "Generative Models as an Emerging Paradigm in the Chemical Sciences", Journal of the American Chemical Society, 2023, DOI: 10.1021/jacs.2c13467
[3] Zeng et al., "Deep generative molecular design reshapes drug discovery", Cell Reports Medicine, 2022, DOI: 10.1016/j.xcrm.2022.100794