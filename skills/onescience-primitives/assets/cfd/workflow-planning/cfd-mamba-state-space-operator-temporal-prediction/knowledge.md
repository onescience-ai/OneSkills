# Mamba状态空间神经算子时序预测

## 适用范围

**触发条件**：
- 需要对时间依赖PDE（如Navier-Stokes、Burgers、浅水方程、反应扩散、可压缩欧拉）的轨迹数据进行神经算子时序预测
- 目标是从有限历史窗口（T_in）预测未来完整演化轨迹（T_out）
- 需要线性复杂度的全局感受野，替代Transformer的二次复杂度注意力机制

**适用场景**：
- 流体力学：湍流预测、涡旋演化、不可压缩/可压缩NS方程
- 地球物理：浅水方程模拟、海洋/大气动力学
- 材料科学：反应扩散系统的时空演化
- 计算物理：正问题求解器的加速替代模型

**不适用场景**：
- 纯稳态PDE（无时间维度的椭圆/抛物型方程需适配）
- 高度不规则网格上的PDE（未经网格感知token化时性能下降）
- 极小数据量（<100样本）下的冷启动（需额外正则化或迁移学习）
- 需要精确边界条件恢复的工程场景（需与CFD复核耦合）

## 输入

- **数据格式**：时间依赖PDE轨迹数据集，包含空间网格上的多变量场随时间演化的快照序列
- **典型变量**：速度场(u,v)、压力p、密度ρ、温度T、涡量ω等
- **网格要求**：支持规则网格（首选）、结构化网格、点云（需额外编码）
- **切分要求**：按几何/工况/完整轨迹切分，禁止同轨迹帧随机打散
- **预处理**：无量纲化或归一化至[0,1]，保存统计量用于反归一化

## 输出

- **预测场**：逐时间步的空间场预测，恢复原始物理单位
- **评估指标**：相对L2误差、RMSE、守恒残差、边界误差
- **适用域报告**：几何/工况外推能力、最差样本分析、推理成本
- **判定结论**：PASS/REJECT/BLOCKED，含域外工况CFD复核建议

## 流程节点

### Step 1：数据接入与契约核验
- **操作**：读取PDE轨迹数据集，核验样本数、变量、单位、网格坐标、时间范围、缺失值和使用许可
- **输出**：dataset_manifest.json, data_contract.json, data_audit.md
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏

### Step 2：预处理与数据切分
- **操作**：统一物理量表示，按几何/工况/时间构造无泄漏切分，执行归一化或无量纲化
- **输出**：train/validation/test_manifest.json, normalization.json
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏

### Step 3：模型配置与训练
- **操作**：配置Mamba/SSM架构超参数，加载切分数据，执行训练，记录逐轮指标与最佳权重
- **输出**：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现

### Step 4：批量推理与物理恢复
- **操作**：加载最佳权重，在独立测试集上推理，反归一化恢复物理单位和网格
- **输出**：predictions/, inference_manifest.json, timing.csv
- **质量门禁**：预测无NaN/Inf且形状单位正确；每个测试样本有唯一结果；推理未使用测试目标校正

### Step 5：任务验收与适用域判定
- **操作**：计算统计误差、物理约束残差、推理成本，执行外推测试，给出PASS/REJECT/BLOCKED
- **输出**：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议

## 关键参数

### 通用判据（方法层，同类体系可参考）

| 参数 | 推荐范围 | 来源 | 说明 |
|------|----------|------|------|
| SSM隐藏状态维度 d_state | 16–64 | [1][2] | 16已可用，64为常用上限；过高增加参数且收益递减 |
| SSM通道比例 ssm_ratio | 2 | [1] | 分配给SSM分支的通道比例，=2为最佳平衡点 |
| 扫描方向 | 双向（bidirectional） | [1][2] | 双向扫描必须；单向扫描违反全视场准则，误差高10x+ |
| 阻尼参数 ρ_k | >0（自适应学习） | [2] | 使核在FNO全局核与CNN局部核之间自适应插值 |
| 频率参数 ω_k | 可学习 | [2] | 数据驱动的频谱选择，优于固定DFT基 |
| 记忆窗口 K | 4–8 | [2] | 时序记忆深度；K>8收益递减 |
| 时空层位置 | 中间（stack中部） | [2] | 时序S4层放在空间层堆栈中部效果最优 |
| 训练噪声 σ | 0.001–0.005 | [2] | 高噪声有助于稳定性，σ=0.005(Burgers), 0.001(其他) |
| 优化器 | AdamW | [2] | weight_decay=1e-4, lr=1e-3, cosine annealing |
| 训练轮数 | 500 | [2] | 配合early stopping使用 |

### 校准数值（具体体系参考值，其他体系需重新锚定）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Darcy Flow训练/测试比 | 9000/1000 | [1] | 9:1划分 |
| Shallow Water 2D | 900/100 | [1] | 128²网格, 101时间步 |
| NS 2D TorusLi | 64²网格 | [2] | ν=10⁻⁵, Re=2000 |
| KS方程粘度范围 | ν∈{0.075, 0.1, 0.125} | [2] | 混沌程度递增 |
| 压缩欧拉 Richtmeyer-Meshkov | 128²→64² | [2] | 5场: ρ,v_x,v_y,p,tracer |

## 边界与分流

| 前提 | 不成立时的改道方案 |
|------|---------------------|
| 输入数据为规则网格 | 转用GeoMaNO（几何Mamba）或图神经算子方案；或采用网格感知token化（Laplacian特征、图消息传递） |
| 数据量充足（>1000轨迹） | 数据稀缺时引入数据增强、迁移学习或使用更小的SSM状态维度（d_state=16） |
| 时序预测为主（需记忆） | 纯空间映射（稳态PDE）可省略时序模块，仅用空间SSM |
| 域内工况预测 | 域外工况必须经CFD复核，不可仅凭平均误差宣称工程可用 |
| 计算资源充足 | 资源受限时降低hidden_dim或使用factorized变体 |

## 质量检查

- 训练收敛：验证损失在合理轮数内下降，无NaN/Inf
- 重量可恢复：best_checkpoint.pt可重新加载并复现推理结果
- 复现性：固定随机种子后结果差异<5%（标准差低于均值的5%）
- 物理一致性：守恒残差在可接受范围，边界误差不显著
- 外推测试：几何/工况外推时误差上升不超过域内误差的3倍

## 回退策略

- 模型不收敛：降低学习率（1e-4）、增加训练轮数、检查数据质量
- 过拟合：增大训练噪声、减小模型容量、增加数据增强
- 推理不稳定：减小推理批大小、检查反归一化统计量、验证网格一致性
- 域外性能差：明确标注适用域，建议与CFD求解器耦合验证

## 资源召回建议

- 需要PDE数据处理与切分方案时召回 `cfd-pde-preprocessing-split`
- 需要Mamba/SSM架构配置与训练细节时召回 `cfd-mamba-operator-training`
- 需要推理与物理量恢复流程时召回 `cfd-mamba-inference-physical-recovery`
- 需要验收评估与适用域判定时召回 `cfd-pde-evaluation-applicability`
- 需要数据接入与契约核验时召回 `cfd-pde-data-intake-contract-validation`
- 与FNO/DeepONet等传统神经算子对比时参考相关 baseline 卡片

## 证据来源

[1] Cheng et al., "Mamba Neural Operator: Who Wins? Transformers vs. State-Space Models for PDEs", Journal of Computational Physics (accepted 2025), arXiv:2410.02113
[2] Koren & Lanthaler, "Merging Memory and Space: A State Space Neural Operator", arXiv:2507.23428, 2025
[3] Tiwari et al., "Latent Mamba Operator for Partial Differential Equations", ICML 2025, arXiv:2505.19105
[4] Song & Jiang, "Adaptive Mamba Neural Operators", ICLR 2026, arXiv:2607.18043
[5] Han et al., "GeoMaNO: Geometric Mamba Neural Operator for Partial Differential Equations", arXiv:2505.12020, 2025
[6] Buitrago et al., "On the Benefits of Memory for Modeling Time-Dependent PDEs", arXiv:2409.02313, 2024
[7] Soares et al., "Towards a Foundation Model for Partial Differential Equations Across Physics Domains", AAAI 2026, arXiv:2511.21861
