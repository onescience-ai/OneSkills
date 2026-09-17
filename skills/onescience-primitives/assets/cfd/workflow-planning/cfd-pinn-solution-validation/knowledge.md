# PINN 解场验证与适用域判定

## 适用范围

**触发条件**：
- PINN 训练完成后需要系统评估解场质量
- 需要判断 PINN 解是否满足工程精度和物理一致性
- 需要划定 PINN 解的适用域范围

**适用场景**：
- 基准验证：与解析解（Kovasznay、Beltrami）对比
- 数值验证：与 DNS/CFD 参考解对比
- 参数化验证：不同 Reynolds 数下的泛化能力评估
- 域外测试（OOD）：几何或工况超出训练范围时的外推能力

**不适用场景**：
- 仅有 PINN 解而无任何参考解或解析解时（需先建立基准）

## 输入

- **PINN 解场**：速度 (u, v)、压力 p 或涡量 ω 在查询坐标上的值
- **参考解**：解析解、DNS 数据、CFD 参考解或实验数据
- **验收指标列表**：relative_L2, PDE_residual, boundary_error, conservation_error
- **误差门限**：PASS/REJECT 阈值

## 输出

- **验收报告**：逐变量误差、PDE 残差、边界误差、守恒误差
- **最差样本列表**：worst_cases.csv
- **适用域报告**：applicability_report.md
- **三态结论**：PASS / REJECT / BLOCKED

## 流程节点

### Step 1：统计误差评估
- **操作**：计算 PINN 解与参考解之间的逐点和统计误差
- **指标**：
  - 相对 L2 误差：∥u_PINN - u_ref∥₂ / ∥u_ref∥₂
  - 最大点误差：max|u_PINN - u_ref|
  - 均方根误差（RMSE）
- **质量门禁**：相对 L2 误差 < 0.1（PASS 阈值）[场景需求书 s05]

### Step 2：PDE 残差检查
- **操作**：在独立配点（非训练配点）上计算 NS 方程残差
- **公式**：
  - 动量残差：∥ρ(∂u/∂t + u·∇u) + ∇p - μ∇²u∥
  - 连续性残差：∥∇·u∥
- **质量门禁**：PDE 残差范数 < 1e-4（PASS 阈值）[1][4]

### Step 3：边界条件满足度
- **操作**：在边界点上评估预测值与目标边界条件的偏差
- **指标**：边界相对误差、逐点最大偏差
- **质量门禁**：边界误差 < 1e-3（PASS 阈值）[2]

### Step 4：守恒性检查
- **操作**：验证质量守恒（∇·u ≈ 0）和动量守恒
- **指标**：质量通量积分误差、动量通量误差
- **质量门禁**：守恒误差 < 5% [场景需求书 s05]

### Step 5：最差样本分析
- **操作**：识别误差最大的区域或工况，分析失败原因
- **输出**：worst_cases.csv（位置、误差值、可能原因）
- **质量门禁**：最差样本可追溯，有明确归因 [场景需求书 s05]

### Step 6：域外泛化测试（OOD）
- **操作**：在训练工况之外的 Reynolds 数或几何上测试泛化能力
- **方法**：
  - 几何外推：不同障碍物形状或位置
  - 工况外推：Re 超出训练范围
  - 参数外推：粘度或密度变化
- **质量门禁**：外推精度低于内插，需在适用域报告中明确标注 [场景需求书 s05]

### Step 7：适用域判定与三态结论
- **操作**：综合所有指标给出 PASS/REJECT/BLOCKED 结论
- **判据**：
  - PASS：所有指标通过门限
  - REJECT：至少一项指标未通过
  - BLOCKED：缺少必要输入或参考解
- **输出**：适用域报告需包含：适用的 Re 范围、几何限制、精度声明和复核建议

## 关键参数

### 通用判据

| 指标 | PASS 阈值 | REJECT 阈值 | 来源 | 说明 |
|------|-----------|-------------|------|------|
| 相对 L2 误差 | < 0.1 | > 0.3 | [场景需求书] | 速度场 |
| PDE 残差范数 | < 1e-4 | > 1e-2 | [1][4] | 在独立配点上 |
| 边界误差 | < 1e-3 | > 1e-1 | [2] | 相对误差 |
| 守恒误差 | < 5% | > 10% | [场景需求书] | 质量/动量 |
| 推理成本 | 报告值 | — | — | 秒/样本 |

### 校准数值

以下数值来自特定基准体系，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Kovasznay 流典型 L2 | O(10^-4)~O(10^-3) | [2] | 2D 稳态解析解 |
| 圆柱绕流 Re=100 典型 L2 | O(10^-3) | [1] | 2D 非稳态 |
| Beltrami 流压力 Poisson 增强 | 10x 精度提升 | [4] | 3D 稳态 |
| 腔体流 Re=1000 典型 L2 | O(10^-3)~O(10^-2) | [1] | 2D 稳态 |
| 泛化误差界 | 与 Re 和 ν 相关 | [5] | 理论分析 |

## 边界与分流

| 条件 | 行动 |
|------|------|
| 无参考解可用 | 使用 PDE 残差和守恒性作为内部验证，标注"无外部验证" |
| 外推测试失败 | 缩小适用域，标注需 CFD 复核 |
| 最差样本位于边界 | 检查边界条件施加策略 |
| 最差样本位于高曲率区域 | 检查配点密度，考虑局部加密 |

## 质量检查

- 统计指标和物理指标必须同时报告，不可只报告其一
- 最差样本必须可追溯到具体位置和工况
- 适用域报告必须包含限制条件和复核建议

## 回退策略

- 指标不通过：增加训练数据/配点 → 调整损失权重 → 使用更强网络
- 外推失败：标注为适用域边界 → 建议使用传统 CFD 复核
- 缺少参考解：使用 PDE 残差和守恒性作为最低验证标准

## 资源召回建议

- 本卡聚焦验证方法，与以下卡片配合：
  - 完整工作流：`cfd-pinn-incompressible-ns-forward-workflow`（Step 5 验收）
  - 损失权重策略：`cfd-pinn-loss-weighting-strategies`（影响训练质量）
  - 边界条件处理：`cfd-pinn-boundary-condition-enforcement`（影响边界误差）

## 证据来源

[1] Jin X, Cai S, Li H, Karniadakis GE. "NSFnets: Physics-informed neural networks for the incompressible Navier-Stokes equations", JCP, 2020, DOI: 10.1016/j.jcp.2020.109951
[2] Xiang Z et al. "Self-adaptive loss balanced PINNs", Neurocomputing, 2022, DOI: 10.1016/j.neucom.2022.05.015
[3] Liu D, Li X, Yang R. "Error Analysis of Tr-PINNs for 2D Incompressible Navier-Stokes", arXiv:2606.06268, 2026
[4] Goraya S, Sobh N, Masud A. "Error Estimates and Physics Informed Augmentation for Thermally Coupled Incompressible Navier Stokes", arXiv:2209.02977, 2022
[5] Andre-Sloan S et al. "Generalization Bounds for Physics-Informed Neural Networks for the Incompressible Navier-Stokes Equations", arXiv:2603.23072, 2026
