# 方程求解与物理残差恢复

## 适用范围

本卡片描述硬约束PINN复杂几何边界求解工作流的第四步：方程求解与物理残差恢复。适用于：
- 在查询配点或网格上恢复解场、导数、边界值与方程残差
- 使用自动微分或离散算子恢复导数、通量和方程残差
- 保存解场与残差场

**不适用场景**：
- 完整流场数据的正问题求解
- 无物理约束的数据处理

## 输入

1. **模型权重** `{CHECKPOINT}`：通过训练门限权重
2. **计算设备** `{DEVICE}`：CPU或CUDA设备
3. **推理批大小** `{BATCH_SIZE}`：按显存调整批量

## 输出

1. **解场** `solution_fields/`：PDE的近似解
2. **PDE残差** `pde_residuals/`：方程残差
3. **边界残差** `boundary_residuals.csv`：边界条件残差

## 流程节点

```
加载模型权重 → 准备查询坐标 → 前向传播 → 自动微分计算导数 → 计算PDE残差 → 计算边界残差 → 保存解场与残差场
```

### 详细操作

#### 1. 模型加载

**操作**：
- 加载训练好的模型权重
- 验证模型结构正确
- 设置计算设备

**判定标准**：
- 模型加载成功
- 模型结构正确
- 计算设备设置正确

#### 2. 查询坐标准备

**操作**：
- 准备测试参数、边界和查询坐标
- 验证坐标格式正确
- 确保坐标覆盖感兴趣区域

**判定标准**：
- 查询坐标格式正确
- 坐标覆盖完整
- 无异常坐标

#### 3. 前向传播

**操作**：
- 在查询坐标上执行前向传播
- 获取模型预测值
- 验证预测值有限

**判定标准**：
- 前向传播成功
- 预测值有限
- 无异常值

#### 4. 导数计算

**操作**：
- 使用自动微分计算导数
- 计算速度梯度、压力梯度等
- 验证导数有限

**判定标准**：
- 自动微分计算成功
- 导数均为有限值
- 无异常导数

#### 5. 残差计算

**操作**：
- 计算PDE方程残差
- 计算边界条件残差
- 验证残差有限

**判定标准**：
- PDE残差计算成功
- 边界残差计算成功
- 残差均为有限值

#### 6. 结果保存

**操作**：
- 保存解场文件
- 保存PDE残差文件
- 保存边界残差文件
- 验证保存成功

**判定标准**：
- 解场文件保存成功
- PDE残差文件保存成功
- 边界残差文件保存成功
- 文件可读取

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 解场导数有限 | 必须通过 | [场景需求书s04] | 解场导数与残差均为有限值 |
| 边初值满足门限 | 必须通过 | [场景需求书s04] | 边初值逐项满足门限 |
| 可对照解存在 | 必须通过 | [场景需求书s04] | 独立数值解或解析解可对照 |

### 校准数值

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 计算设备 | cuda | [场景需求书s04] | 默认计算设备 |
| 推理批大小 | 8 | [场景需求书s04] | 默认推理批大小，可根据显存调整 |

以下数值来自CFD_S040场景，供量级校准；其他体系需以自身证据重新锚定。

## 边界与分流

1. **模型加载失败** → 检查权重文件、模型架构
2. **前向传播失败** → 检查输入数据、模型结构
3. **导数计算失败** → 检查自动微分设置、计算图
4. **残差过大** → 调整模型、增加配点、调整损失权重
5. **保存失败** → 检查存储空间、文件权限

## 质量检查

1. **解场完整性**：所有查询点均有解值
2. **导数有限性**：自动微分计算的导数均为有限值
3. **残差收敛性**：PDE残差和边界残差均收敛到可接受水平
4. **物理一致性**：解满足质量守恒、动量守恒等物理约束
5. **可读性**：输出文件格式正确、可被后续步骤读取

## 回退策略

1. **解场计算失败** → 检查查询坐标、模型权重
2. **残差计算失败** → 检查PDE方程定义、边界条件
3. **保存失败** → 手动保存或检查存储空间
4. **物理约束违反** → 调整模型、增加配点

## 资源召回建议

**何时召回本卡片**：
- 需要执行硬约束PINN复杂几何边界求解的方程求解阶段
- 需要计算PINN模型的PDE残差
- 需要恢复解场和物理残差

**配套资源**：
- 场景卡：cfd-hard-constraint-pinn-complex-geometry-solution
- 工作流卡：cfd-hard-constraint-pinn-complex-geometry-workflow
- 任务卡：cfd-hard-constraint-pinn-data-intake-contract-validation
- 任务卡：cfd-hard-constraint-pinn-preprocessing-data-splitting
- 任务卡：cfd-hard-constraint-pinn-model-training
- 任务卡：cfd-hard-constraint-pinn-acceptance-applicability

## 证据来源

[1] Nonparametric Boundary Geometry in Physics Informed Deep Learning, 2020
[2] Solving Differential Equations with Constrained Learning, 2020
[3] Hybrid Boundary Physics-Informed Neural Networks for Solving Navier–Stokes Equations with Complex Boundary Conditions, 2025, URL: https://arxiv.org/abs/2507.17535
[4] SPINN: Separable Physics-Informed Neural Networks, 2021
[5] A Unified Hard-Constraint Framework for Solving Geometrically Complex PDEs, 2023
[6] Error analysis for physics informed neural networks (PINNs) approximating Kolmogorov PDEs, 2021, URL: https://arxiv.org/abs/2106.14473
[7] 场景需求书CFD_S040：硬约束PINN复杂几何边界求解，s04步骤定义