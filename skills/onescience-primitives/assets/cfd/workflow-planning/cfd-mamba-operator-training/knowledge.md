# Mamba状态空间神经算子训练

## 适用范围

**触发条件**：
- PDE轨迹数据已完成预处理和切分，需要配置并训练Mamba/SSM神经算子
- 需要将结构化状态空间模型（S4/Mamba）与神经算子框架结合

**适用场景**：
- MNO（Mamba Neural Operator）：将Mamba嵌入GNOT/Galerkin Transformer/OFormer等架构
- SS-NO（State Space Neural Operator）：空间S4D+时序S4的统一时空算子
- LaMO（Latent Mamba Operator）：潜在空间中的Mamba算子
- GeoMaNO：几何感知的Mamba算子

**不适用场景**：
- 非Mamba架构（FNO、DeepONet等）的训练——应使用对应baseline训练卡
- 推理阶段——应使用推理卡

## 输入

- 切分数据 `train_manifest.json`, `validation_manifest.json`
- 归一化参数 `normalization.json`
- 训练配置 `{TRAIN_CONFIG}`
- 可选初始权重 `{INIT_CHECKPOINT}`

## 输出

- `best_checkpoint.pt`：最佳模型权重
- `train_config.json`：完整训练配置
- `training_metrics.csv`：逐轮训练验证指标
- `environment.txt`：依赖和版本信息

## 流程节点

### Step 1：架构配置
- **操作**：根据任务选择Mamba变体，配置SSM超参数
- **关键参数**：
  - SSM类型：S4D（对角化，效率优先）或S6/Mamba（选择机制，精度优先）
  - d_state：16（性价比最优）或64（精度最优）
  - ssm_ratio：2（SSM通道分配比例）
  - 扫描方向：双向（必须）
  - 阻尼/频率：自适应学习
  - 记忆窗口K：4（默认，时序S4层）
  - 时序层位置：stack中部
- **质量门禁**：架构配置与数据维度兼容

### Step 2：训练循环
- **操作**：加载数据、初始化模型、执行训练循环
- **默认超参数**：
  - 优化器：AdamW, lr=1e-3, weight_decay=1e-4
  - 学习率调度：cosine annealing
  - 损失函数：相对L2误差（step-wise normalized）
  - 训练噪声：σ=0.005(Burgers), 0.001(其他)
  - 训练轮数：500（配合early stopping, patience=15）
  - 批大小：8（受GPU显存限制）
- **质量门禁**：训练损失下降、验证损失有限

### Step 3：最佳权重保存
- **操作**：保存验证损失最低的权重、记录训练配置和指标
- **质量门禁**：权重可重新加载；配置可完整复现

## 关键参数

### 通用训练判据

| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| 优化器 | AdamW | [2] | weight_decay=1e-4 |
| 学习率 | 1e-3 | [2] | cosine annealing调度 |
| 损失函数 | 相对L2误差 | [2] | step-wise normalized |
| 训练噪声σ | 0.001–0.005 | [2] | 稳定性增强 |
| epochs | 500 | [2] | 配合early stopping |
| early stopping patience | 15 | 场景需求书 | 防止过拟合 |
| batch_size | 8 | 场景需求书 | 受GPU显存限制 |
| 随机种子 | 42 | 场景需求书 | 可复现性 |

### Mamba架构超参数

| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| d_state | 16–64 | [1][2] | 16性价比最优，64精度最优 |
| ssm_ratio | 2 | [1] | SSM分支通道比例 |
| 扫描方向 | bidirectional | [1][2] | 必须双向 |
| 阻尼 | 自适应学习(ρ>0) | [2] | 核定位自适应 |
| 频率 | 自适应学习 | [2] | 数据驱动频谱选择 |
| 记忆窗口K | 4 | [2] | 时序S4层窗口 |
| 时序层位置 | 中间 | [2] | stack中部 |
| 块数 | 4 | [2] | 默认深度 |
| 隐藏维度 | 64 | [2] | 默认宽度 |
| 中间层维度 | 128 | [2] | 线性层中间维度 |

### MNO特定参数（嵌入Transformer架构时）

| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| Mamba增强方式 | 替换注意力机制 | [1] | 将Galern/Softmax注意力替换为S6/Cross S6 |
| Cross S6比率q | 可学习标量 | [1] | 控制第二输入的贡献比例 |

### 校准数值（具体体系参考值）

| 体系 | 训练/测试 | 网格 | 时间步 | 来源 |
|------|-----------|------|--------|------|
| Darcy Flow | 9000/1000 | 128² | 稳态 | [1] |
| Shallow Water 2D | 900/100 | 128² | 101步 | [1] |
| Diffusion Reaction 2D | 900/100 | 128² | 101步 | [1] |
| 1D Burgers' | 2048/1000 | N=128 | 20步 | [2] |
| 1D KS (ν=0.075) | 2048/256 | N=128 | 26步 | [2] |
| 2D NS TorusLi | — | 64² | 20步 | [2] |

## 边界与分流

- 训练不收敛 → 降低lr(1e-4)、增加轮数、检查数据质量和归一化
- 过拟合 → 增大训练噪声、减小d_state、增加数据增强
- GPU显存不足 → 降低batch_size、使用梯度累积、减小hidden_dim
- 提供INIT_CHECKPOINT → 检查结构兼容性，不兼容则从头训练

## 质量检查

- 训练曲线：验证损失在合理轮数内单调下降
- 最佳权重：best_checkpoint.pt可加载并复现验证指标
- 配置复现：固定种子后结果标准差<5%
- 环境记录：environment.txt包含完整依赖版本

## 资源召回建议

- 训练完成后召回 `cfd-mamba-inference-physical-recovery` 进入推理
- 需要分布式训练时召回并行训练卡
- 需要架构选择建议时参考场景卡中的baseline对比数据

## 证据来源

[1] Cheng et al., "Mamba Neural Operator", JCP 2025, arXiv:2410.02113
[2] Koren & Lanthaler, "State Space Neural Operator", arXiv:2507.23428, 2025
[3] Tiwari et al., "Latent Mamba Operator", ICML 2025, arXiv:2505.19105
