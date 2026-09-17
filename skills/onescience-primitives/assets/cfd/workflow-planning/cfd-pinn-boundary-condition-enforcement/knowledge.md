# PINN 边界条件施加策略

## 适用范围

**触发条件**：
- PINN 求解 NS 方程时需要施加 Dirichlet、Neumann 或周期性边界条件
- 需要在"软约束"（损失惩罚）和"硬约束"（架构保证）之间选择
- 非齐次边界条件导致边界误差过大

**适用场景**：
- 软边界条件：通用场景，实现简单，适用于大多数层流问题
- 硬边界条件：边界精度要求极高、或需要零训练误差的场景
- Tr-PINNs：非齐次 Dirichlet 边界条件下的误差校正

**不适用场景**：
- 移动边界（需要动态网格或 immersed boundary 方法）
- 自由表面边界（需要额外的界面追踪）

## 输入

- **边界类型**：Dirichlet（给定速度）、Neumann（给定压力/速度梯度）、周期性
- **边界数据**：边界上的速度值/梯度值/周期映射关系
- **精度要求**：边界误差门限

## 输出

- **边界施加方案**：软/硬约束选择和实现细节
- **边界残差报告**：边界点上的逐点误差
- **边界误差统计**：最大误差、平均误差、L2 范数

## 流程节点

### 方法 1：软边界条件（损失惩罚）
- **操作**：将边界条件作为损失函数的一项：L_BC = λ_BC · Σ∥u_boundary - u_predicted∥²
- **实现**：在边界配点上计算预测值与目标值的偏差，加权后加入总损失
- **参数**：边界配点数（通常为域内配点数的 10%~50%）、λ_BC（通常 10~100）
- **优势**：实现简单，不改变网络架构，适用于任意复杂边界
- **劣势**：边界满足程度依赖 λ_BC 和训练充分度，可能存在残余误差
- **质量门禁**：边界相对误差 < 1e-3（对工程应用）[1][3]

### 方法 2：硬边界条件（架构约束）
- **操作**：通过网络架构设计保证边界条件精确满足，如 u_boundary = u_network(x) + g(x)（g(x) 为满足 BC 的已知函数）
- **实现**：
  - Dirichlet BC：输出 = network_output · distance_function + boundary_value
  - Neumann BC：使用满足梯度约束的特征函数
- **优势**：训练过程中边界误差恒为零，无需调参 λ_BC
- **劣势**：需要已知满足 BC 的辅助函数，实现复杂度较高
- **质量门禁**：边界误差精确为零（架构保证）[2]

### 方法 3：Tr-PINNs（边界误差校正）
- **操作**：对非齐次 Dirichlet 边界，在标准 PINN 基础上添加边界值误差校正项
- **原理**：基于非齐次 Stokes 问题的解结构，将边界误差分解并逐一校正
- **优势**：显著提升非齐次 BC 下的精度
- **质量门禁**：相比标准 PINN，精度提升一个数量级 [2]

### 方法 4：压力 Poisson 边界条件
- **操作**：对 VP 表述中的压力，通过 Poisson 方程 ∇²p = -ρ·∇·(u·∇u) + μ∇²(∇·u) 施加约束
- **适用**：需要高精度压力场的场景
- **质量门禁**：压力边界误差 < 1e-2 [3]

## 关键参数

### 通用判据

| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| 软边界权重 λ_BC | 10~100 | [1][3] | 大于域内 PDE 权重 |
| 边界配点占比 | 10%~50% | [1] | 取决于边界复杂度 |
| 边界误差门限（工程） | < 1e-3 | [2] | 相对误差 |
| 边界误差门限（研究） | < 1e-4 | [2] | 更严格要求 |
| 硬 BC 辅助函数 | 线性插值/距离函数 | [2] | 取决于边界类型 |

### 校准数值

以下数值来自特定基准体系，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 腔体流硬 BC 相对 L2 误差 | O(10^-4)~O(10^-1) | [2] | 取决于 Re |
| 圆柱绕流软 BC 误差 | ~O(10^-2) | [1] | 标准 PINN |
| Tr-PINNs 精度提升 | 10x vs 标准 PINN | [2] | 非齐次 Dirichlet |
| 压力 Poisson 增强 | 10x 压力精度 | [3] | Beltrami 流验证 |

## 边界与分流

| 前提 | 不成立时改道 |
|------|-------------|
| 边界条件已知且固定 | 转向自由边界方法或 immersed boundary |
| 边界几何简单 | 使用硬 BC；复杂几何用软 BC |
| 非齐次 Dirichlet BC | 使用 Tr-PINNs 校正 |
| 需要零边界误差 | 使用硬 BC 或 Tr-PINNs |

## 质量检查

- 软 BC：逐点检查边界误差分布，确认无异常突变点
- 硬 BC：验证辅助函数确实满足边界条件
- 对比软/硬 BC 在相同配点数下的精度差异

## 回退策略

- 软 BC 误差大：增加 λ_BC → 增加边界配点 → 改用硬 BC
- 硬 BC 实现困难：简化辅助函数 → 回退软 BC + 大 λ_BC
- 非齐次 BC 精度不足：使用 Tr-PINNs 校正

## 资源召回建议

- 本卡聚焦边界条件，与以下卡片配合：
  - NS 方程表述：`cfd-pinn-ns-formulation-selection`（影响压力边界处理）
  - 损失权重策略：`cfd-pinn-loss-weighting-strategies`（影响软 BC 权重选择）
  - 完整工作流：`cfd-pinn-incompressible-ns-forward-workflow`

## 证据来源

[1] Pal R, Mukherjee S, Dutta U, Choudhury A. "Solving Navier-Stokes Equations Using Data-free PINNs With Hard Boundary Conditions", arXiv:2511.14497, 2025
[2] Liu D, Li X, Yang R. "Error Analysis of Tr-PINNs Algorithm for 2D Incompressible Navier-Stokes Equations with Non-Homogeneous Boundary Conditions", arXiv:2606.06268, 2026
[3] Goraya S, Sobh N, Masud A. "Error Estimates and Physics Informed Augmentation for Thermally Coupled Incompressible Navier Stokes Equations", arXiv:2209.02977, 2022
