# CFD场量物理约束阈值校准方法

## 适用范围

面向CFD场量（浓度场、温度场、速度场、压力场）生成任务中物理约束检查的阈值设定与校准。适用于扩散-反应方程、Navier-Stokes方程、Euler方程等PDE场量预测后的物理一致性验证。不适用于纯数据驱动任务或不涉及物理约束的生成模型评估。

## 输入

- 生成的CFD场量数据（numpy/torch tensor，shape=[batch, channels, H, W]）
- 归一化统计量（normalization.json，含mean、std、min、max）
- 物理约束定义文件（physics_constraints.json）

## 输出

- 物理筛选结果（physics_filter.json，含每个样本的各约束检查结果）
- 不合格样本索引列表
- 物理一致性评估报告

## 流程节点

### 1. Non-negative 约束检查
- **操作**：检查场量最小值是否≥0（或≥物理允许的最小值）
- **参数**：threshold=0（绝对阈值），或threshold=min物理值
- **工具**：NumPy min()函数
- **质量门禁**：non_negative检查结果与实际场量负值情况一致；不使用归一化统计量设定阈值

### 2. Laplacian 平滑性检查
- **操作**：计算场量的Laplacian算子，检查平滑性
- **参数**：smoothness_threshold=基于网格分辨率Δx和物理扩散系数D（如：threshold=κ/Δx²，κ为平滑系数）
- **工具**：PyTorch/FiRM卷积算子
- **质量门禁**：Laplacian最大值在物理合理范围内（不出现数值振荡）

### 3. 边界条件一致性检查
- **操作**：检查场量在边界处是否满足指定的边界条件类型
- **参数**：boundary_type=Dirichlet/Neumann/Robin, tolerance=1e-6
- **工具**：边界提取 + 比较
- **质量门禁**：Dirichlet边界处场量值与边界条件的偏差<tolerance

### 4. 守恒律验证
- **操作**：对场量在全域积分，检查质量/能量守恒
- **参数**：conservation_check=[mass, energy], tolerance=1e-4
- **工具**：数值积分（梯形法则）
- **质量门禁**：总质量变化<tolerance（不考虑源项时守恒）

### 5. 梯度权重物理筛选
- **操作**：对PDE残差进行梯度加权，降低间断区域的影响
- **参数**：gradient_weight=λ=1/(1+ε₁||∇u||²)，ε₁=0.01(Burgers)/0.2(Euler)
- **工具**：自动微分 + 加权损失
- **质量门禁**：梯度权重正确反映局部流动特征（光滑区域权重≈1，间断区域权重<1）

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Non-negative阈值 | min_val ≥ 0（绝对阈值） | [论文1] | 浓度/温度场的物理非负约束，不使用归一化mean设定阈值 |
| 梯度权重ε₁(Burgers) | 0.01 | [论文1] | Burgers方程的梯度权重灵敏度参数 |
| 梯度权重ε₁(Euler) | 0.2 | [论文1] | Euler方程的梯度权重灵敏度参数 |
| Hard constraint边界 | 精确满足Dirichlet条件 | [论文1] | 通过网络架构设计强制满足，而非loss惩罚 |
| 守恒律约束 | 全域积分质量守恒 | [论文1] | soft conservation constraint，权重w_CONS=1 |
| 平滑性阈值 | 基于Δx和物理扩散系数 | [论文2] | 避免数值振荡的物理依据 |

### 校准数值（扩散-反应PDE体系）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 浓度场non-negative | min_val ≥ 0 | 常识 | 浓度不能为负 |
| 温度场non-negative | min_val ≥ 0K | 常识 | 绝对温度不能为负 |
| 速度场可正可负 | 无non-negative约束 | 常识 | 速度方向由符号决定 |
| Laplacian平滑性 | |∇²u| < κ_max/Δx² | [论文2] | κ_max为最大物理扩散系数 |

## 边界与分流

- **non_negative检查全部失败**（如所有样本min_val<0）：检查数据预处理是否包含非负截断，或生成模型是否学习到正确的物理约束
- **Laplacian值异常大**：可能是数值振荡（Gibbs现象），增加平滑性约束权重或使用谱滤波
- **边界条件不一致**：检查hard constraint实现是否正确；若使用soft constraint，增加边界loss权重
- **守恒律违反**：检查PDE残差是否包含源项；若无源项，守恒律违反表明模型物理不一致

## 质量检查

- [ ] physics_filter.json中non_negative字段与实际场量负值情况一致
- [ ] passed=true的样本确实满足所有物理约束（无false positive）
- [ ] Laplacian平滑性检查结果与网格分辨率一致
- [ ] 边界条件检查覆盖所有边界类型（Dirichlet/Neumann/Robin）
- [ ] 守恒律验证误差在tolerance范围内

## 回退策略

- 若non-negative约束过于严格导致大量样本被拒，可适当放宽阈值（如min_val ≥ -0.01·max_val）并记录偏离原因
- 若Laplacian检查误判过多，改用基于频谱的平滑性检查
- 若守恒律验证失败，检查PDE求解器的时间步长设置

## 资源召回建议

- 本卡片适用于CFD场量生成后的物理一致性验证阶段
- 配套资源：cfd-conditional-generative-pde-data-pipeline（数据准备流程）
- 配套资源：cfd-pde-training-evaluation-standards（训练配置与评估标准）

## 证据来源

[1] Ahmad A, et al. "WHC-PINN: Physics-Informed Neural Network with weighted loss and hard constraint for compressible flow", Scientific Reports, 2026, DOI: 10.1038/s41598-025-34263-1

[2] Zhai X, et al. "Subject-specific modeling framework for particle deposition using computational fluid dynamics and particle tracking", J. Aerosol Science, 2025, DOI: 10.1016/j.jaerosci.2025.106660
