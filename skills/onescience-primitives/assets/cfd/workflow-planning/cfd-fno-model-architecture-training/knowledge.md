# Fourier Neural Operator 模型架构与训练

## 适用范围

适用于在规则网格（2D/3D）上进行PDE算子学习的场景，特别是需要学习从PDE参数（如扩散系数、初始条件、边界条件）到解算子的映射。典型应用包括Darcy流（稳态椭圆PDE）和Navier-Stokes方程（非定常不可压流体）的前向求解与参数反演。不适用于非规则网格或需要网格自适应的场景。

## 输入

- **Darcy流**：渗透率场 $a(x) \in \mathbb{R}^{H \times W}$（标量场），表示空间分布的扩散系数
- **Navier-Stokes**：初始涡度场 $w_0(x) \in \mathbb{R}^{H \times W}$ 或速度场 $u(x) \in \mathbb{R}^{H \times W \times 2}$
- 输入数据需为规则网格上的点值，网格分辨率在训练和推理时可不同（分辨率不变性）

## 输出

- **Darcy流**：压力场 $u(x) \in \mathbb{R}^{H \times W}$（标量场）
- **Navier-Stokes**：后续时刻的涡度场或速度场序列 $w(x,t) \in \mathbb{R}^{H \times W \times T}$
- 输出分辨率可与输入不同（零样本超分辨率能力）

## 流程节点

### 1. 模型架构定义

FNO的核心架构包含以下组件：

**Lifting层**：将输入从低维映射到高维特征空间
- 操作：局部线性变换（通常为浅层全连接网络）
- 输入通道数：$d_a$（输入物理量维度）
- 输出通道数：$d_v$（隐藏特征维度，通常32或64）
- 代码示例：`P = nn.Linear(in_channels, hidden_channels)`

**Fourier层（核心）**：在频域执行全局卷积
- 操作流程：FFT → 频域线性变换 $R$ → 逆FFT → 残差连接 + 激活函数
- 更新公式：$v_{t+1}(x) = \sigma(W v_t(x) + \mathcal{F}^{-1}(R_\phi \cdot \mathcal{F}(v_t))(x))$
- 频域截断：保留前 $k_{\max}$ 个频率模式，滤除高频模式
- 典型配置：$k_{\max,j} = 12$（2D问题）或 $k_{\max,j} = 16$（1D问题）
- 权重张量 $R \in \mathbb{C}^{k_{\max} \times d_v \times d_v}$，施加共轭对称性

**Projection层**：将高维特征映射回输出空间
- 操作：局部线性变换
- 代码示例：`Q = nn.Linear(hidden_channels, out_channels)`

### 2. 训练超参数配置

**优化器**：Adam
- 初始学习率：0.001
- 学习率调度：每100个epoch减半
- 总训练epoch：500

**批次大小**：8（受GPU显存限制）

**激活函数**：ReLU

**归一化**：支持多种归一化策略（NeuralOperator 2.0.0）
- `'ada_in'`：Adaptive Instance Normalization
- `'group_norm'`：Group Normalization
- `'instance_norm'`：Instance Normalization
- `None`：不使用归一化
- 默认建议：`'group_norm'` 或 `'instance_norm'`

**训练数据量**：1000个样本（标准配置），10000个样本（高精度配置）

### 3. 场景配置差异

| 参数 | Darcy流 | Navier-Stokes |
|------|---------|---------------|
| 输入通道数 $d_a$ | 1（渗透率场） | 2-3（涡度/速度场） |
| 输出通道数 $d_u$ | 1（压力场） | 2-3（涡度/速度场） |
| 隐藏通道数 $d_v$ | 32 | 32或64 |
| 频率模式数 $k_{\max}$ | 12 | 12（2D）/16（1D） |
| Fourier层数 | 4 | 4 |
| 时间建模 | 不适用（稳态） | FNO-2D（RNN时间步进）或FNO-3D（时空卷积） |

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 学习率 | 0.001 | [1] | Adam优化器初始学习率 |
| 学习率衰减 | 每100 epoch减半 | [1] | 500 epoch训练时的调度策略 |
| 隐藏通道数 $d_v$ | 32（2D）/64（1D） | [1] | Fourier层的特征维度 |
| 频率模式数 $k_{\max}$ | 12（2D）/16（1D） | [1] | 频域截断的最高频率 |
| Fourier层数 | 4 | [1] | 堆叠的频域卷积层数 |
| 批大小 | 8 | [1] | 受V100 16GB显存限制 |
| 训练epoch | 500 | [1] | 标准训练周期数 |
| 激活函数 | ReLU | [1] | 非线性激活 |
| 归一化 | Batch Norm | [1] | 每层后添加 |

## 边界与分流

- **非周期边界**：标准FNO假设周期性边界条件。对于非周期问题，需采用padding策略或使用扩展的FNO变体（如geoFNO）。简单padding适用于数据驱动应用，但可能在边界引入不连续性；高级应用可使用Fourier continuation技术
- **非规则网格**：FNO仅适用于规则网格。非规则网格需使用Graph Neural Operator (GNO)、Geometry-Aware FNO (Geo-FNO) 或 Geometry-Informed Neural Operator (GINO)
- **极高频问题**：若PDE解包含大量高频模式，需增大 $k_{\max}$ 或采用多尺度FNO变体。注意：$k_{\max}$ 过大可能引入混叠伪影
- **显存不足**：可通过张量分解（如Tucker分解）减少参数量，使用 `TFNO` 替代 `FNO`，仅保留10%参数量
- **多分辨率训练**：可使用增量FNO（iFNO）框架，逐步增加模型表达力和数据分辨率
- **物理信息训练**：可结合PINO（Physics-Informed Neural Operator）使用物理损失和数据损失的组合

## 质量检查

- 模型参数量检查：标准FNO-2D约40万参数，FNO-3D约650万参数
- 收敛性检查：训练损失应在前100 epoch内显著下降
- 分辨率不变性验证：在64×64训练后，在256×256上测试应保持相似误差
- 零样本超分辨率：训练分辨率与测试分辨率不同时，误差应保持稳定

## 回退策略

- 若FNO训练不收敛，尝试降低学习率至0.0001或增加训练数据量
- 若显存不足，使用张量分解版本（TFNO）或减小隐藏通道数
- 若频域截断导致精度不足，增大 $k_{\max}$ 但注意计算复杂度增加
- 若过拟合严重，增加正则化（weight decay、dropout）或使用早停
- 若欠拟合，增加模型容量（更多层、更多隐藏通道）或减少正则化

## 补充：损失函数选择

**数据损失**：
- L2损失（MSE）：最常用，$\mathcal{L}_{data} = \|u_{pred} - u_{true}\|_2^2$
- 相对L2损失：更适合多尺度问题，$\mathcal{L}_{rel} = \frac{\|u_{pred} - u_{true}\|_2}{\|u_{true}\|_2}$
- L1损失：对异常值更鲁棒

**物理损失（PINO）**：
- PDE残差损失：$\mathcal{L}_{pde} = \|N[u_{pred}] - 0\|_2^2$，其中 $N$ 是PDE算子
- 边界条件损失：$\mathcal{L}_{bc} = \|u_{pred}|_{\partial\Omega} - u_{bc}\|_2^2$
- 初始条件损失：$\mathcal{L}_{ic} = \|u_{pred}(t=0) - u_0\|_2^2$

**组合损失**：
- $\mathcal{L} = \lambda_{data} \mathcal{L}_{data} + \lambda_{pde} \mathcal{L}_{pde} + \lambda_{bc} \mathcal{L}_{bc}$
- 权重可使用自适应策略自动调整

## 补充：超参数调优建议

**小规模过拟合实验**：
- 在正式训练前，用小数据子集快速验证模型容量和训练损失
- 可快速识别欠拟合/过拟合问题
- 测试不同损失函数和归一化策略的效果

**频率模式数 $n_{modes}$ 选择**：
- 进行功率谱分析，确定数据中有效频率范围
- 确保 $n_{modes}$ 不超过Nyquist限制（$N/2$，$N$为网格分辨率）
- 各向异性问题可为不同维度设置不同的 $n_{modes}$

**层数和隐藏通道选择**：
- 建议从3-6层开始，根据需要增加
- 隐藏通道数：32（2D）或64（1D）为良好起点

## 资源召回建议

- 本卡片适用于FNO模型的架构设计、超参数配置和训练策略制定
- 配套资源：`cfd-pde-operator-data-evaluation`（数据处理与评估指标）
- 配套组件：`neuralop` Python库（官方PyTorch实现）

## 证据来源

[1] Li, Z., Kovachki, N., Azizzadenesheli, K., Liu, B., Bhattacharya, K., Stuart, A., & Anandkumar, A. (2020). Fourier Neural Operator for Parametric Partial Differential Equations. arXiv:2010.08895.

[2] Kovachki, N., Li, Z., Liu, B., Azizzadenesheli, K., Bhattacharya, K., Stuart, A., & Anandkumar, A. (2023). Neural Operator: Learning Maps Between Function Spaces with Applications to PDEs. JMLR, 24(1):89.

[3] Kossaifi, J., Kovachki, N., Li, Z., et al. (2025). A Library for Learning Neural Operators. arXiv:2412.10354.

[4] Duruisseaux, V., Kossaifi, J., & Anandkumar, A. (2025). Fourier Neural Operators Explained: A Practical Perspective. arXiv:2512.01421.

[D1] NeuralOperator GitHub Repository. https://github.com/neuraloperator/neuraloperator (accessed 2026-09-18).
