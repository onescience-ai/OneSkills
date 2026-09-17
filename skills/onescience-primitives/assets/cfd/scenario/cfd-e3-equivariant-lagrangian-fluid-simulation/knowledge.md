# E3等变粒子网络拉格朗日流体模拟

## 适用范围

面向拉格朗日粒子轨迹数据的E3等变图神经网络流体动力学模拟。本场景适用于：
- 基于粒子表示的流体动力学建模（如SPH、物质点法输出的粒子轨迹）
- 需要保持旋转、平移、反射等变性的物理场量预测
- 从粒子状态（位置、速度、密度等）到目标物理量（压力、涡量等）的映射学习
- 需要物理约束（守恒律、边界条件）的深度学习流体模型

不适用场景：
- 欧拉网格表示的流体模拟（网格拓扑固定）
- 纯数据驱动无物理约束的黑箱模型
- 域外工况（需CFD复核确认适用性）

## 输入

**数据格式**：
- 拉格朗日粒子轨迹数据（粒子位置、速度、物理属性时间序列）
- 支持格式：HDF5、NumPy、自定义二进制
- 坐标系：笛卡尔坐标系
- 时间分辨率：固定或可变时间步

**预处理要求**：
- 粒子邻域构建（kNN或半径搜索）
- 物理量无量纲化（保留可逆变换）
- 边界掩膜定义

## 输出

**模型产物**：
- 训练好的E3等变GNN模型权重（best_checkpoint.pt）
- 训练配置与环境记录（train_config.json, environment.txt）
- 训练指标曲线（training_metrics.csv）

**评估产物**：
- 测试集预测结果（predictions/）
- 评估报告（evaluation.json, worst_cases.csv）
- 适用域报告（applicability_report.md）
- 验收判定（PASS/REJECT/BLOCKED）

## 流程节点

```
数据接入与契约核验(s01) → 预处理与数据切分(s02) → 模型配置与训练(s03) → 批量推理与物理恢复(s04) → 任务验收与适用域判定(s05)
```

**s01 数据接入与契约核验**：
- 操作：读取数据集，核验样本、变量、单位、坐标系
- 输出：dataset_manifest.json, data_contract.json, data_audit.md
- 质量门禁：数据文件可读、变量定义完整、无训练测试泄漏

**s02 预处理与数据切分**：
- 操作：无量纲化、图构建、按几何/工况切分
- 输出：train/validation/test manifests, normalization.json
- 质量门禁：轨迹互斥、仅训练集统计、边界语义完整

**s03 模型配置与训练**：
- 操作：配置E3-equivariant GNN，执行训练
- 输出：best_checkpoint.pt, training_metrics.csv
- 质量门禁：损失有限、权重可加载、随机种子可复现

**s04 批量推理与物理恢复**：
- 操作：测试集推理，反归一化恢复物理单位
- 输出：predictions/, inference_manifest.json
- 质量门禁：预测无NaN、样本唯一、未使用测试标签

**s05 任务验收与适用域判定**：
- 操作：统计误差、物理约束、泛化能力评估
- 输出：evaluation.json, applicability_report.md
- 质量门禁：双指标报告、最差样本追溯、适用域限制明确

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 等变群 | E(3) = SO(3) × Z₂ | [场景需求书] | 旋转+反射等变性 |
| 图构建方法 | kNN或半径搜索 | [场景需求书] | 粒子邻域定义 |
| 切分比例 | train:0.7, val:0.15, test:0.15 | [场景需求书] | 默认配置 |
| 切分单位 | 几何/轨迹/工况 | [场景需求书] | 禁止帧随机打散 |
| 训练框架 | PyTorch | [场景需求书] | 默认实现 |
| 默认epoch | 100 | [场景需求书] | 可配置 |
| 默认batch_size | 8 | [场景需求书] | 按显存调整 |
| 学习率 | 0.001 | [场景需求书] | 默认配置 |
| 早停耐心 | 15 | [场景需求书] | 防止过拟合 |
| 相对误差门限 | 0.1 | [场景需求书] | 测试集放行阈值 |

## 边界与分流

**数据层面**：
- 缺少必填输入（数据集路径、数据集名称）→ 返回BLOCKED，列出缺项
- 数据文件不可读或格式不支持 → 拒绝处理，要求修复数据源

**模型层面**：
- 初始权重结构不兼容 → 检查模型架构差异，建议重新初始化
- 训练损失出现NaN/Inf → 检查学习率、数据归一化、数值稳定性

**验收层面**：
- 相对L2误差超过门限 → REJECT，需调整模型或数据
- 物理约束违反严重 → REJECT，需增加物理正则化
- 域外工况测试失败 → 明确适用域限制，建议CFD复核

## 质量检查

**数据质量**：
- 样本可追溯性（每个粒子有唯一ID）
- 变量单位一致性检查
- 训练测试泄漏检测（轨迹级别互斥）

**模型质量**：
- 训练验证损失收敛性
- 最佳权重可重新加载性
- 配置环境可复现性

**物理质量**：
- 守恒残差（质量、动量、能量）
- 边界误差（壁面、自由面）
- 最差样本分析（可追溯、可诊断）

## 回退策略

**数据问题回退**：
- 数据格式不兼容 → 转换为标准格式（HDF5/NumPy）
- 数据量不足 → 扩充数据或使用迁移学习
- 物理量缺失 → 明确标注缺失量，调整预测目标

**训练问题回退**：
- 训练不收敛 → 降低学习率、增加正则化、检查数据质量
- 过拟合 → 增加数据增强、调整模型复杂度、早停
- 显存不足 → 减小batch_size、使用梯度累积

**验收问题回退**：
- 误差超标 → 分析误差来源（数据/模型/评估），针对性优化
- 物理违反 → 增加物理约束损失、调整网络结构
- 域外失败 → 缩小适用域范围，增加域外数据训练

## 资源召回建议

**何时召回本卡片**：
- 用户描述涉及"E3等变"、"等变神经网络"、"粒子网络"等关键词
- 需要拉格朗日表示的流体动力学模拟
- 需要保持物理对称性（旋转、平移、反射）的深度学习模型
- 需要粒子轨迹数据到物理场量的映射学习

**配套资源**：
- 相关论文证据库（arXiv:2305.15603等）
- E3等变GNN实现参考（PyTorch Geometric, e3nn）
- 拉格朗日流体基准测试（LagrangeBench）
- 物理约束深度学习方法（守恒律、边界条件）

## 证据来源

[1] Learning Lagrangian Fluid Mechanics with E(3)-Equivariant Graph Neural Networks, arXiv:2305.15603, 2023
[2] DEL: Discrete Element Learner for Learning 3D Particle Dynamics with Neural Rendering, 2023
[3] Learning Physical Models that Can Respect Conservation Laws, 2022
[4] Modeling Dynamics over Meshes with Gauge Equivariant Nonlinear Message Passing, 2022
[5] Incorporating Symmetry into Deep Dynamics Models for Improved Generalization, arXiv:2002.03061, 2020
[6] LagrangeBench: A Lagrangian Fluid Mechanics Benchmarking Suite, arXiv:1806.01261, 2018
[7] Symmetric Basis Convolutions for Learning Lagrangian Fluid Mechanics, 2023