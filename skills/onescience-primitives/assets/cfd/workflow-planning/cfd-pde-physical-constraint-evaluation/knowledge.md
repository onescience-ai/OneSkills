# PDE物理守恒约束量化评估方法

## 适用范围

**触发条件**：
- 需要验证PDE求解模型的预测是否满足基本物理守恒定律
- 评估指标要求包含conservation_residual和boundary_error
- 需要对流体力学模型进行物理一致性评估

**适用场景**：
- Navier-Stokes方程、Burgers方程等守恒律方程的数值解评估
- 物理信息神经网络（PINNs）的预测质量验证
- 神经算子（FNO、DeepONet、Mamba-NO）的物理约束满足度检查
- 模型对比评估中需要物理一致性指标的场景

**不适用场景**：
- 纯统计误差评估（L2、RMSE、MAE已足够）
- 无明确守恒律的非物理PDE问题
- 稳态问题（无需时间导数项的守恒评估）

## 输入

- 模型预测场 u_pred(x,t) 和真实场 u_true(x,t)
- 网格信息：空间步长 Δx（或 Δx, Δy, Δz），时间步长 Δt
- 边界条件类型：Dirichlet / Neumann / 周期性 / 无通量
- PDE类型：守恒律形式 ∂u/∂t + ∇·F(u) = 0 中的通量函数F

## 输出

- conservation_residual：基于PDE守恒律的离散残差标量值
- boundary_error：边界条件偏差的量化指标
- 联合评估报告：包含统计误差和物理约束指标的完整报告
- 判定结论：模型是否满足基本物理约束

## 流程节点

### Step 1：守恒残差计算
- **操作**：对预测场计算离散化的PDE守恒律残差
- **质量守恒**：∂u/∂t + ∇·(uv) = 0 → residual = (u_pred[t+1]-u_pred[t])/Δt + div(u_pred*v_pred)
- **动量守恒**：∂(ρu)/∂t + ∇·(ρu⊗u) + ∇p = f → 计算各项离散差分
- **参数**：Δx, Δt, 离散格式（一阶/二阶中心差分）
- **工具**：NumPy/PyTorch张量运算
- **质量门禁**：residual量级应远小于u_pred量级（相对残差<1e-2为良好）

### Step 2：边界误差计算
- **操作**：在边界处计算预测值与边界条件的偏差
- **Dirichlet**：boundary_error = ||u_pred(boundary) - u_bc||₂
- **Neumann**：boundary_error = ||∂u_pred/∂n(boundary) - g_bc||₂
- **周期性**：boundary_error = ||u_pred(left) - u_pred(right)||₂
- **参数**：边界条件类型、边界法向量（Neumann情况）
- **工具**：NumPy/PyTorch
- **质量门禁**：boundary_error应接近0（周期性边界尤其重要）

### Step 3：总质量变化率评估（简化版）
- **操作**：计算预测场总质量随时间的变化率
- **公式**：mass_change_rate = |Σ(u_pred(t)) - Σ(u_pred(0))| / Σ(u_pred(0))
- **参数**：无
- **工具**：NumPy求和
- **质量门禁**：对周期性/无通量边界，mass_change_rate应 < 1e-3

### Step 4：联合报告生成
- **操作**：汇总所有评估指标，生成结构化报告
- **输出格式**：JSON或YAML，包含所有指标数值和判定结论
- **工具**：json/yaml库
- **质量门禁**：报告包含relative_L2, RMSE, conservation_residual, boundary_error四项指标

## 关键参数

### 通用判据（方法层）

| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| 离散格式 | 二阶中心差分 | [D1] | 空间导数的离散化，精度与稳定性平衡 |
| 守恒残差阈值 | < 1e-2（相对） | [1] | 低于此值认为物理约束满足良好 |
| 边界误差阈值 | < 1e-4（归一化后） | [D1] | 取决于具体边界条件类型 |
| 总质量变化率 | < 1e-3 | [1] | 对守恒系统的时间积分一致性检验 |

### 校准数值（来自Burgers方程体系，供量级校准；其他体系需以自身证据重新锚定）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 空间步长 Δx | 0.01-0.1 | [D1] | 取决于问题域大小和分辨率要求 |
| 时间步长 Δt | 0.001-0.01 | [D1] | 需满足CFL条件 |
| 测试样本数 | ≥ 50 | [1] | 统计显著性要求 |

## 边界与分流

- **边界条件类型未知**：默认使用Dirichlet边界进行边界误差计算，在报告中标注假设
- **非守恒PDE**：若PDE不具有守恒形式，跳过conservation_residual计算，仅报告统计误差
- **高维PDE（3D+）**：守恒残差计算量随维度增加，可降采样后评估
- **稳态问题**：无需计算时间导数项，改为空间残差评估

## 质量检查

- [ ] conservation_residual基于PDE守恒律的离散残差（非简单的输入输出质量比值）
- [ ] boundary_error覆盖实际边界条件类型
- [ ] 评估结果包含relative_L2, RMSE, conservation_residual, boundary_error四项
- [ ] 报告包含判定结论和阈值对比
- [ ] 对线性对流方程精确解，conservation_residual应接近0

## 回退策略

- 若无法获取精确的PDE守恒律形式，使用总质量变化率作为conservation_residual的近似
- 若边界条件类型不确定，使用周期性边界假设（适用于大多数合成数据场景）
- 若无法计算空间导数，使用残差的频域估计（适用于周期性域）

## 资源召回建议

- 需要评估PDE模型的物理约束满足度时召回本卡
- 需要计算conservation_residual和boundary_error时召回本卡
- 配套卡片：cfd-pde-numerical-stability-data-generation（数据生成规范）

## 证据来源

[1] "Improving Weak PINNs for Hyperbolic Conservation Laws: Dual Norm Computation, Boundary Conditions and Systems", Chaumet & Giesselmann, 2022, DOI: 10.48550/arXiv.2211.12393
[2] "Solving BDNK diffusion using physics-informed neural networks", Chomalí-Castro et al., 2026, DOI: 10.48550/arXiv.2602.16117

## 补充证据（开源文档）

[D1] LeVeque, R.J. "Finite Difference Methods for Ordinary and Partial Differential Equations", SIAM, 2007（交叉验证：有限差分法的标准教材，CFL条件和守恒律离散化方法的权威参考）
[D2] Trefethen, L.N. "Spectral Methods in MATLAB", SIAM, 2000（交叉验证：谱方法求解PDE的标准参考）
