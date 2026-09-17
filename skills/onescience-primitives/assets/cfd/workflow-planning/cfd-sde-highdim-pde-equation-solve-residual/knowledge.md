# Equation Solve & Physical Residual Recovery for Stochastic PDE

## 适用范围
本任务面向随机微分方程（SDE）与高维偏微分方程（PDE）求解的求解验证阶段，在查询配点或网格上恢复解场、导数、边界值与方程残差。使用自动微分或离散算子恢复导数、通量和方程残差。适用于所有需要物理信息PDE求解的求解验证场景，**禁止仅凭训练损失判定方程已求解**。

## 输入
- {CHECKPOINT}：模型权重（通过训练门限权重），必填
- {DEVICE}：计算设备（CPU或CUDA设备），必填
- {BATCH_SIZE}：推理批大小（按显存调整），可选

## 输出
- solution_fields/：解场文件
- pde_residuals/：PDE残差场
- boundary_residuals.csv：边界残差

## 流程节点
```
1. 加载checkpoint → 2. 在测试参数/边界/查询坐标上求解目标PDE
→ 3. 使用自动微分或离散算子恢复导数 → 4. 计算通量与方程残差
→ 5. 保存解场与残差场 → 6. 有限值检查
```

## 关键参数

### 通用判据（方法层，同类体系可参考）

| 参数 | 判据 | 说明 |
|------|------|------|
| 解场有限值 | 所有解场值为有限值 | NaN/Inf表示求解失败 |
| 导数有限值 | 自动微分导数为有限值 | 梯度爆炸/消失检查 |
| 残差有限值 | PDE残差为有限值 | 方程未被正确求解 |
| 边界条件满足 | 边初值逐项满足门限 | 边界误差在可接受范围内 |
| 独立验证 | 独立数值解或解析解可对照 | 不能仅凭训练损失判定 |

### 校准数值（场景专属值，供量级校准）
以下数值来自 CFD_S046 场景，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认DEVICE | cuda | 场景需求书 | GPU推理 |
| 默认BATCH_SIZE | 8 | 场景需求书 | 推理批大小 |

## 边界与分流
- **解场出现NaN/Inf**：降低推理批大小、检查checkpoint完整性、调整计算设备
- **导数爆炸**：检查自动微分设置、调整网络架构
- **边界误差过大**：检查边界条件定义、调整边界损失权重
- **无独立解对照**：标记为"验证受限"，仅报告统计误差

## 质量检查
- 解场有限值检查
- 导数有限值检查
- PDE残差有限值检查
- 边界条件逐项验证
- 残差场可视化检查

## 回退策略
- 求解失败：降低批大小、调整计算设备、检查模型权重
- 边界误差过大：调整边界损失权重、增加边界配点
- 无独立解：标记为验证受限，仅报告统计指标

## 资源召回建议
当遇到以下需求时召回本卡片：
- 物理信息PDE求解器的解场恢复
- PDE残差计算与验证
- 边界条件验证

配套卡片：cfd-sde-highdim-pde-model-training（模型训练），cfd-sde-highdim-pde-task-acceptance（任务验收）

## 证据来源
[1] Physics-Informed Inference Time Scaling for Solving High-Dimensional Partial Differential Equations, 2024
[2] Learning a Neural Solver for Parametric PDEs to Enhance Physics-Informed Methods, 10.1145/3620665.3640366, 2024
[3] Physics-informed machine learning with smoothed particle hydrodynamics, PhysRevFluids.8.054602, 2023
