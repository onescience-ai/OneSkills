# Transformer通用PDE算子预训练与微调

## 适用范围

本场景适用于使用Transformer架构对偏微分方程(PDE)求解器进行算子学习，通过在多方程、多网格数据上预训练通用表征，再针对特定PDE任务微调的完整工作流。覆盖Navier-Stokes方程、扩散方程、波动方程等常见PDE类型，支持规则网格与非结构化网格数据。不适用于纯数据驱动的统计降阶模型（如POD-DNN）或传统数值方法的替代。

## 输入

- **数据格式**：多方程多网格预训练数据集，包含空间坐标、时间步、物理场变量
- **数据来源**：CFD数值模拟结果（如OpenFOAM、FEniCS输出）、实验数据、合成数据
- **预处理要求**：变量单位统一、坐标系对齐、网格拓扑验证、缺失值处理

## 输出

- **可复现模型**：训练完成的Transformer权重（best_checkpoint.pt）
- **任务结果**：测试集预测场、逐样本误差统计
- **物理一致性评估**：守恒残差、边界误差、物理约束满足度
- **适用域报告**：几何/工况外推能力、泛化边界、复核建议

## 流程节点

1. **数据接入与契约核验** → 验证文件可读性、样本数、变量定义、单位坐标系
2. **预处理与数据切分** → 无量纲化、按几何/轨迹/工况切分、确保无泄漏
3. **模型配置与训练** → 选择PDE Transformer或UPT、超参数配置、训练监控
4. **批量推理与物理恢复** → 反归一化、恢复物理单位、保存逐样本结果
5. **任务验收与适用域判定** → 统计+物理指标双评估、OOD测试、适用域边界

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认模型 | PDE Transformer, Universal Physics Transformer | 场景配置 | 可选其他Transformer算子模型 |
| 训练框架 | PyTorch | 场景配置 | 标准深度学习框架 |
| 默认epochs | 100 | 场景配置 | 可根据收敛情况调整 |
| 默认batch_size | 8 | 场景配置 | 受显存限制 |
| 默认learning_rate | 0.001 | 场景配置 | Adam优化器常用值 |
| early_stopping_patience | 15 | 场景配置 | 防止过拟合 |
| 切分比例 | train:0.7, val:0.15, test:0.15 | 场景配置 | 标准三划分 |
| 切分单位 | geometry_or_trajectory | 场景配置 | 按几何体或完整轨迹切分 |
| 验收指标 | relative_L2, RMSE, conservation_residual, boundary_error | 场景配置 | 统计+物理双维度 |
| 相对误差门限 | 0.1 (10%) | 场景配置 | 测试集放行阈值 |

## 边界与分流

- **数据格式不兼容**：若预训练数据来自多个求解器且格式差异大，需先完成数据标准化（调用onescience-data-standardizer）
- **显存不足**：batch_size需减小或启用梯度累积，必要时切换至单GPU调试模式
- **收敛失败**：learning_rate过高导致震荡，过低导致不收敛，需网格搜索或学习率调度
- **物理约束严重违反**：守恒残差超阈值时，需检查数据质量或引入物理信息约束（PINN损失）
- **域外工况测试**：几何/工况外推失败时，需明确适用域边界并标记需CFD复核

## 质量检查

- 训练验证损失均为有限值（非NaN/Inf）
- 最佳权重可重新加载并产生一致预测
- 配置环境随机种子可复现训练结果
- 预测无NaN/Inf且形状单位正确
- 每个测试样本有唯一结果
- 推理未使用测试目标校正（无数据泄漏）

## 回退策略

- 训练不收敛：回退至更简单模型（如FNO）或增加数据增强
- 物理约束不满足：回退至纯数值解或引入更强物理先验
- 适用域过窄：扩大预训练数据覆盖范围或增加OOD数据

## 资源召回建议

当用户需要：(1) 基于Transformer的PDE求解器训练；(2) 神经算子预训练与微调；(3) 多方程多网格数据上的通用模型构建时，召回本卡片。

## 证据来源

[1] PDE-Transformer_ Efficient and Versatile Transformers for Physics Simulations
[2] Universal Physics Transformers_ A Framework For Efficiently Scaling Neural Operators
[3] Unisolver_ PDE-Conditional Transformers Towards Universal Neural PDE Solvers
[4] DPOT_ Auto-Regressive Denoising Operator Transformer for Large-Scale PDE Pre-Training
[5] Positional Knowledge is All You Need_ Position-induced Transformer (PiT) for Operator Learning
[6] Curvature-aware Graph Attention for PDEs on Manifolds
[7] Neural Interpretable PDEs_ Harmonizing Fourier Insights with Attention for Scalable and Interpretable Physics Di
[8] S-Crescendo_ A Nested Transformer Weaving Framework for Scalable Nonlinear System in S-Domain Representation
[9] FUSE_ Fast Unified Simulation and Estimation for PDEs
[10] Choose a Transformer_ Fourier or Galerkin
