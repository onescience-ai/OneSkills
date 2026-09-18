# Mamba选择性状态空间模型（SSM）神经算子架构

## 适用范围

**触发条件**：
- 需要为PDE求解任务设计神经算子模型
- 需要捕捉PDE轨迹的长程时序依赖关系
- 需要线性复杂度的序列建模替代Transformer方案
- 需要实现Mamba Neural Operator或State-space operator

**适用场景**：
- 流体力学（Navier-Stokes方程、Burgers方程）的时序预测
- 热传导方程、波动方程等PDE的解算子近似
- 需要处理长序列PDE轨迹数据的算子学习任务
- 需要同时训练Mamba Neural Operator和独立State-space operator的双模型评估

**不适用场景**：
- 纯空间特征提取（无时序维度）的任务——此时CNN或FNO更合适
- 序列长度极短（<10步）的任务——SSM优势不明显
- 需要精确注意力机制可解释性的场景

## 输入

- PDE轨迹数据：时空网格上的解场 u(x,t)，形状为 (batch, channels, nx, nt) 或展平为序列
- 初始条件与边界条件信息
- 网格坐标信息（用于关联物理空间位置）
- 模型超参数配置：d_model, d_state, d_inner, n_layers, ssm_ratio等

## 输出

- MambaNeuralOperator模型类，支持forward方法接收PDE输入并输出预测解场
- State-space operator独立模型类（如场景要求双模型对比）
- 模型参数量与计算复杂度信息
- 训练后的checkpoint文件

## 流程节点

### Step 1：SSM核心参数初始化
- **操作**：定义连续SSM参数矩阵 A, B, C 和离散化步长 Δ
- **参数**：d_state（SSM状态维度，典型值4-64）、d_inner（展开维度，典型值为d_model的2-4倍）
- **工具**：PyTorch nn.Parameter
- **质量门禁**：A矩阵初始化为负实部（保证稳定性），B/C初始化为小随机值或正交矩阵

### Step 2：离散化（ZOH/FOH）
- **操作**：将连续参数(A, B, C, Δ)通过零阶保持（ZOH）或一阶保持（FOH）转换为离散参数
- **ZOH公式**：Ā = exp(Δ·A), B̄ = (Δ·A)⁻¹(Ā - I)·Δ·B
- **参数**：Δ可通过softplus确保正性，A_log参数化确保A负定
- **工具**：torch.linalg.solve, torch.expm
- **质量门禁**：Ā的谱半径 < 1（离散稳定性），Δ值在合理范围（1e-4 ~ 1e2）

### Step 3：选择性扫描（Selective Scan）
- **操作**：实现输入依赖的SSM状态空间传播
- **核心机制**：B, C, Δ由输入x通过线性投影动态生成（而非固定参数）
- **并行扫描算法**：利用scan的结合律实现O(n)并行前向传播
- **参数**：序列长度n, 状态维度d_state
- **工具**：自定义CUDA kernel或PyTorch associative_scan实现
- **质量门禁**：forward时间复杂度为O(n·d_model·d_state)，内存复杂度为O(n·d_model)

### Step 4：Mamba块组装
- **操作**：将SSM层组装为标准Mamba块结构
- **标准路径**：input_proj → Conv1d → SSM → SiLU门控 → output_proj
- **参数**：conv_kernel_size（典型值4）、d_model（隐藏维度）
- **工具**：nn.Linear, nn.Conv1d, SiLU
- **质量门禁**：Mamba块输出形状与输入一致（残差连接可行）

### Step 5：Mamba Neural Operator构建
- **操作**：堆叠多个Mamba块构建完整算子模型
- **参数**：n_layers（层数，典型值4-8）、输入输出维度映射
- **工具**：nn.ModuleList
- **质量门禁**：模型可接受PDE数据输入并输出预测解场，梯度可回传

### Step 6：State-space operator独立实现
- **操作**：根据场景要求实现独立的State-space operator模型
- **要求**：与MambaNeuralOperator共享SSM核心组件，但作为独立模型类
- **参数**：与MambaNeuralOperator类似的超参数配置
- **质量门禁**：独立模型可单独训练和推理，不依赖MambaNeuralOperator

## 关键参数

### 通用判据（方法层）

| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| SSM离散化方法 | ZOH（零阶保持） | [1][3] | 最常用离散化方法，适合均匀时间步 |
| 选择性扫描类型 | Hardware-efficient parallel scan | [1] | O(n)并行复杂度，可替代因果卷积近似 |
| 状态维度 d_state | 16-64 | [1][3] | 越大表达力越强但计算量增加 |
| 离散化步长 Δ | softplus参数化 | [1] | 确保正性，可通过学习优化 |
| A矩阵参数化 | A_log（对数参数化） | [1] | 确保A负定（离散稳定性） |
| 门控机制 | SiLU (Swish) | [1][3] | 非线性门控，与SSM输出逐元素相乘 |
| Conv1d核大小 | 4 | [1] | 局部特征提取，弥补SSM的因果性限制 |

### 校准数值（来自Mamba Neural Operator体系，供量级校准；其他体系需以自身证据重新锚定）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| d_model | 128-512 | [1] | 隐藏维度，取决于问题规模 |
| d_inner | 256-1024 | [1] | SSM展开维度，通常为d_model的2-4倍 |
| n_layers | 4-8 | [1][3] | Mamba块堆叠层数 |
| batch_size | 8-32 | [1] | 训练批大小 |
| learning_rate | 1e-3 ~ 1e-4 | [1] | Adam优化器学习率 |
| 训练epoch | 100-500 | [1] | 取决于数据集大小和收敛速度 |

## 边界与分流

- **SSM离散化不稳定**：若Ā谱半径≥1，降低Δ或改用FOH离散化；若仍不稳定，检查A矩阵初始化
- **选择性扫描内存不足**：对超长序列（>10k步），改用chunk-wise扫描或降低d_state
- **训练不收敛**：检查Δ值范围（过大导致梯度爆炸，过小导致梯度消失），检查学习率调度
- **缺少SSM核心组件**：若最终实现仅含Conv1d+LayerNorm（无SSM层），则模型退化为近似前馈网络，无法捕捉长程依赖——必须恢复SSM层实现
- **State-space operator缺失**：若场景要求双模型对比但仅实现单一模型，需新增独立State-space operator类

## 质量检查

- [ ] SSM层包含A_log/B/C/Δ参数（非仅Conv1d+LayerNorm）
- [ ] ZOH离散化后Ā谱半径 < 1
- [ ] 选择性扫描实现O(n)时间复杂度
- [ ] Mamba块标准路径完整（proj→Conv→SSM→Gate→proj）
- [ ] 模型forward/backward可执行，梯度可回传
- [ ] State-space operator作为独立模型类可单独训练
- [ ] 训练损失在100 epoch内有显著下降（>50%）

## 回退策略

- 若SSM实现过于复杂无法短期完成，可先用简化SSM（固定B/C，仅学习Δ）验证架构可行性
- 若选择性扫描的CUDA kernel不可用，使用PyTorch associative_scan参考实现
- 若State-space operator与MambaNeuralOperator差异不大，可在同一SSM核心上添加不同头部分支

## 资源召回建议

- 需实现Mamba Neural Operator时召回本卡
- 需理解SSM离散化方法时召回本卡
- 需对比Transformer与SSM在PDE任务上的表现时召回本卡
- 配套卡片：cfd-pde-numerical-stability-data-generation（数据生成规范）

## 证据来源

[1] "Mamba Neural Operator: Who Wins? Transformers vs. State-Space Models for PDEs", Cheng et al., Journal of Computational Physics, 2024, DOI: 10.48550/arXiv.2410.02113
[2] "Adaptive Mamba Neural Operators", Song & Jiang, ICLR 2026, DOI: 10.48550/arXiv.2607.18043
[3] "Latent Mamba Operator for Partial Differential Equations", Tiwari et al., ICML 2025, DOI: 10.48550/arXiv.2505.19105
[4] "Regularity and Stability Properties of Selective SSMs with Discontinuous Gating", Zubić & Scaramuzza, 2025, DOI: 10.48550/arXiv.2505.11602
