# 扩散概率模型在雷达临近预报中的实现

## 适用范围

雷达临近预报（0-2小时）中需要生成冰雹发生概率场的场景。扩散模型通过学习数据分布的梯度（score function），从噪声中迭代去噪生成概率场，相比简单外推能提供物理一致的集合扰动和不确定性量化。适用于需要概率预报而非确定性预报的业务场景。

## 输入

- 多帧雷达反射率序列（历史 N 帧，通常 N=4-8，时间间隔 6-10 分钟）
- 环境场数据（CAPE、CIN、0-6km 风切变、湿度场等）
- 模型超参配置（扩散步数、噪声调度、UNet 架构参数）

## 输出

- 冰雹概率场（与输入等网格的二维概率图，值域 [0,1]）
- 集合成员（可选，M 个扰动成员用于不确定性估计）
- 概率校准统计量（可靠性曲线、ROC-AUC、Brier Score）

## 流程节点

1. 条件编码 → 2. 前向扩散加噪 → 3. 反向扩散去噪 → 4. 概率场输出

### 步骤1：条件编码

**UNet 编码器**接收条件输入（多帧雷达 + 环境场），通过卷积层提取时空特征：
- 输入通道数 = 雷达帧数 + 环境场变量数（如 4帧CR + 4变量 = 8通道）
- 编码器下采样 3-4 次，每次通道数加倍（64→128→256→512）
- 中间瓶颈层捕获大尺度天气系统特征
- 使用 GroupNorm 或 InstanceNorm 稳定训练

**条件融合方式**：
- 拼接（Concatenation）：将雷达序列和环境场在通道维度拼接后整体输入 UNet
- 交叉注意力（Cross-Attention）：环境场作为 Key/Value，雷达特征作为 Query
- FiLM 调制：用环境场参数生成仿射变换系数调制雷达特征

[4]

### 步骤2：前向扩散加噪

前向过程将干净的反射率场 x₀ 逐步加噪至纯噪声 x_T：

x_t = √(ᾱ_t) · x₀ + √(1-ᾱ_t) · ε,  ε ~ N(0, I)

其中 ᾱ_t 是累积噪声调度系数，T 为总扩散步数（常用 T=100 或 T=1000）。

**噪声调度策略**：
- **线性调度**（Linear）：ᾱ_t 从 1 线性衰减至接近 0。简单但后期去噪步信号过弱
- **余弦调度**（Cosine）：ᾱ_t = cos²(πt/2T)，更平滑的衰减，效果通常优于线性
- **Sigmoid 调度**：自适应调整信噪比，适合气象数据的非高斯分布特性

[5]

### 步骤3：反向扩散去噪

训练目标：学习噪声预测网络 ε_θ(x_t, t, cond)，最小化：

L = E[‖ε - ε_θ(x_t, t, cond)‖²]

反向过程从 x_T ~ N(0,I) 逐步去噪：
1. 初始化 x_T 为标准正态噪声（或基于雷达外推的先验）
2. 对 t = T, T-1, ..., 1 逐步采样：
   - 预测噪声 ε_θ(x_t, t, cond)
   - 根据噪声调度计算去噪后的 x_{t-1}
3. 输出 x_0 作为生成的概率场

**确定性采样 vs 随机采样**：
- DDIM（确定性）：去噪过程无随机性，相同输入产生相同输出
- DDPM（随机）：每步添加少量随机噪声，适合生成多样化集合成员

[5]

### 步骤4：概率场输出

- 若直接建模二值冰雹标签：x₀ 即为概率图
- 若建模反射率外推：对生成的反射率做 sigmoid 变换 P(hail) = σ((Z - Z_threshold) / ΔZ)
- 冰雹反射率阈值：通常 Z > 45-55 dBZ 对应冰雹可能性（C波段），具体值取决于雷达波长和冰雹大小
- 可选：对 M 个集合成员取平均得到概率场，成员间标准差反映不确定性

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 扩散步数 T | 100-1000 | [5] | T=100 适合快速推理，T=1000 效果更好 |
| UNet 基础通道数 | 64 | [4] | 可根据数据分辨率调整为 32 或 128 |
| 下采样层数 | 3-4 | [4] | 对应 8x-16x 空间降采样 |
| 噪声调度 | cosine 优先 | [5] | 线性调度为基线，cosine 通常更优 |
| 学习率 | 1e-4 to 1e-3 | [4] | Adam 优化器，余弦退火 |
| 批量大小 | 16-32 | [4] | 受 GPU 显存限制，梯度累积可等效增大 |
| 冰雹反射率阈值 | 45-55 dBZ | [3] | 取决于雷达波长和冰雹大小分布 |
| 集合成员数 M | 10-50 | [5] | 业务场景 M≥20 较合理 |

## 边界与分流

- **训练数据不足**：若无足够历史雷达-冰雹配对数据，可使用预训练的通用降水预报模型微调（如基于 MRMS 的全国数据预训练）
- **推理延迟要求高**：当业务要求 < 1 分钟响应时，DDIM（确定性采样）优于 DDPM（随机采样），且可减少去噪步数至 T=20-50
- **GPU 显存不足**：可使用 latent diffusion（潜在扩散），在编码器的低维潜在空间中执行扩散过程

## 质量检查

- 检查代码中是否存在 UNet 定义（class UNet 或等效模块）
- 检查是否实现了前向加噪和反向去噪过程（noise_schedule, sample 函数）
- 运行后对比输出概率场统计特征：扩散模型的概率场应具有空间平滑性和物理一致性，不应与简单 sigmoid(外推反射率) 输出相同

## 回退策略

- 扩散模型不可用时：回退到集合卡尔曼滤波或蒙特卡洛 dropout 等简单不确定性量化方法
- 无 GPU 时：使用 CPU 推理但需大幅减少扩散步数和集合成员数

## 资源召回建议

- 冰雹概率场生成阶段应召回本卡
- 配套召回 `radar-data-acquisition-for-hail-nowcasting`（数据输入）和 `nowcasting-verification-metric-baselines`（效果评估）
- 扩散模型训练细节可进一步检索 diffusion model tutorial 相关资源

## 证据来源

[1] Predicting forecast errors with diffusion model for uncertainty quantification in weather prediction, Geoscientific Model Development, 2026, DOI: 10.5194/gmd-2025-233
[2] ST-Mamba-LDM: An Attention-Mamba Hybrid Spatio-Temporal Latent Diffusion Model for precipitation nowcasting, IEEE JSTARS, 2026, DOI: 10.1109/JSTARS.2026.001
[3] Detection of hail signatures from single-polarization C-band radar reflectivity, Atmospheric Research, 2015, DOI: 10.1016/j.atmosres.2015.07.023
[4] Application of a Radar Echo Extrapolation-Based Deep Learning Method in Strong Convection Nowcasting, Earth and Space Science, 2021, DOI: 10.1029/2021EA001773
[5] GAN-rcLSTM: A Deep Learning Model for Radar Echo Extrapolation, Atmosphere, 2022, DOI: 10.3390/atmos13060901
