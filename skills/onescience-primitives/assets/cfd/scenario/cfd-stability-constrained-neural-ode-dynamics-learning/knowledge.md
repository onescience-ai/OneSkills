# 稳定性约束神经微分方程动力学学习

## 适用范围

面向显式约束动力系统时序数据的稳定性约束神经微分方程（Stable Neural ODE）与约束神经过程（Constrained Neural Process）建模场景。适用于：
- 具有显式物理约束（守恒律、边界条件、能量有界性）的动力系统时序数据建模
- 需要保证数值稳定性的连续时间动力学学习
- 从离散时间序列到连续时间微分方程的参数化学习
- 需要物理一致性评估与适用域判定的工程应用场景

不适用场景：
- 无物理约束的纯数据驱动黑箱模型（无稳定性保障需求）
- 离散时间步模型无需连续时间表示的场景
- 域外工况需经CFD复核确认适用性

## 输入

**数据格式**：
- 显式约束动力系统时序数据（状态变量、控制输入、时间戳）
- 支持格式：HDF5、NumPy、CSV等
- 包含物理约束定义（守恒量、边界条件、能量约束）

**预处理要求**：
- 物理量无量纲化（保留可逆变换）
- 时间序列对齐与插值
- 边界掩膜与约束条件编码

## 输出

**模型产物**：
- 训练好的Stable Neural ODE模型权重（best_checkpoint.pt）
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
- 操作：读取动力系统时序数据，核验样本、变量、单位、网格坐标及许可
- 输出：dataset_manifest.json, data_contract.json, data_audit.md
- 质量门禁：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏

**s02 预处理与数据切分**：
- 操作：统一物理量与表示，按几何、工况或时间构造无泄漏切分
- 输出：train/validation/test manifests, normalization.json
- 质量门禁：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏

**s03 模型配置与训练**：
- 操作：配置Stable Neural ODE、Constrained Neural Process，执行训练
- 输出：best_checkpoint.pt, training_metrics.csv
- 质量门禁：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现

**s04 批量推理与物理恢复**：
- 操作：测试集推理，恢复原始单位、网格和物理派生量
- 输出：predictions/, inference_manifest.json, timing.csv
- 质量门禁：预测无NaN或Inf且形状单位正确；每个测试样本有唯一结果；推理未使用测试目标校正

**s05 任务验收与适用域判定**：
- 操作：评估统计误差、关键物理约束、泛化能力和计算收益
- 输出：evaluation.json, applicability_report.md, PASS_REJECT_BLOCKED.txt
- 质量门禁：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型类型 | Stable Neural ODE, Constrained Neural Process | [场景需求书] | 稳定性约束+显式约束双路径 |
| 切分单位 | 几何、完整轨迹或物理工况 | [场景需求书s02] | 不得把同一轨迹的帧随机打散 |
| 验收指标 | relative_L2, RMSE, conservation_residual, boundary_error | [场景需求书s05] | 统计与物理指标必须同时报告 |
| 外推测试 | 需要（默认true） | [场景需求书s05] | 几何或工况外推测试决定适用域边界 |
| 稳定性约束 | 需要（模型核心特性） | [场景需求书] | 保证数值稳定性与物理一致性 |

### 校准数值
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| train/val/test比例 | 0.7/0.15/0.15 | [场景需求书s02] | 以下数值来自场景默认配置，其他体系需以自身证据重新锚定 |
| 随机种子 | 42 | [场景需求书] | |
| 相对误差门限 | 0.1 | [场景需求书s05] | 测试集放行阈值 |
| 训练轮次 | 100 | [场景需求书s03] | |
| 批大小 | 8 | [场景需求书s03/s04] | |
| 学习率 | 0.001 | [场景需求书s03] | |
| 早停耐心 | 15 | [场景需求书s03] | 防止过拟合 |

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
- 样本可追溯性
- 变量单位一致性检查
- 训练测试泄漏检测（轨迹级别互斥）

**模型质量**：
- 训练验证损失收敛性
- 最佳权重可重新加载性
- 配置环境可复现性

**物理质量**：
- 守恒残差（质量、动量、能量）
- 边界误差（壁面、自由面）
- 稳定性约束满足度
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
- 域外失败 → 缩小适用域范围、增加域外数据训练

## 资源召回建议

**何时召回本卡片**：
- 用户描述涉及"Neural ODE"、"神经微分方程"、"稳定性约束"等关键词
- 需要连续时间动力学学习的时序数据建模
- 需要保证数值稳定性与物理一致性的深度学习模型
- 需要显式约束（守恒律、边界条件）的动力系统建模

**配套资源**：
- 论文证据库（Stabilized Neural ODE等5篇）
- 神经微分方程实现参考（torchdiffeq, DeepXDE）
- 物理约束深度学习方法（守恒律、边界条件）

## 证据来源

[1] Stabilized Neural Differential Equations for Learning Dynamics with Explicit Constraints, [场景需求书related_papers]
[2] Neural Processes with Stability, [场景需求书related_papers]
[3] Axial Neural Networks for Dimension-Free Foundation Models, arXiv:2510.13665, [场景需求书related_papers]
[4] HHD-GP_ Incorporating Helmholtz-Hodge Decomposition into Gaussian Processes for Learning Dynamical Systems, [场景需求书related_papers]
[5] Spatio-Temporal Prediction of Unsteady Airfoil Aerodynamics Using Augmented Graph Neural Ordinary Differential Equations with Exogenous Controls, arXiv:2607.18309, [场景需求书related_papers]
