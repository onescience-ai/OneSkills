# Lie群等变网络对称PDE预测 — 端到端工作流

## 适用范围

本卡片服务的问题类：面向具有旋转、平移或其他连续李群对称性的偏微分方程（PDE）数据，使用保持群等变性的神经网络架构完成从初始条件/边界条件到物理场演化的映射预测。适用场景包括但不限于：具有SO(2)/SE(2)对称的二维不可压Navier-Stokes方程、具有平移不变性的波动方程、具有旋转不变性的涡度方程等。不适用场景：PDE本身不具有连续群对称性（如各向异性介质中的强非均匀方程）；对称性仅在离散网格上成立（需额外验证连续极限）；需要严格保辛或保能量等更强物理约束的场景需额外设计。

## 输入

- 具有群对称性的PDE数据集（时间序列快照、空间场、边界条件等）
- 数据契约（变量定义、单位、网格坐标系、拓扑）
- 切分配置（按几何/轨迹/工况无泄漏切分）
- 模型配置（框架、超参数、随机种子）

## 输出

- 可复现模型检查点（best_checkpoint.pt）
- 逐变量预测结果（含反归一化后的物理单位）
- 评估指标（relative L2、RMSE、守恒残差、边界误差）
- 物理一致性评估报告
- 适用域报告（含OOD工况外推测试结果）
- 最终验收判定（PASS / REJECT / BLOCKED）

## 流程节点

数据接入与契约核验 → 预处理与数据切分 → 模型配置与训练 → 批量推理与物理恢复 → 任务验收与适用域判定

每步含：操作、参数、工具、质量门禁（详见各workflow卡）

## 关键参数

### 通用判据（方法层，同类体系可参考）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型架构族 | Lie-equivariant neural network / PDO convolution | [P1][P8][P9] | 保持群等变性的架构选择 |
| 等变性类型 | 旋转+平移（SE(2)）或更广Lie群 | [P1][P7] | 根据PDE对称群选择 |
| 验收指标 | relative_L2, RMSE, conservation_residual, boundary_error | 场景JSON s05 | 统计与物理指标并行 |
| 相对误差门限 | 0.1 (10%) | 场景JSON s05 | 默认PASS/REJECT阈值 |
| 切分比例 | train:0.7, val:0.15, test:0.15 | 场景JSON s02 | 标准无泄漏切分 |
| 切分单位 | 按几何/轨迹/工况 | 场景JSON s02 | 禁止打散同一轨迹帧 |
| 早停耐心 | 15 epochs | 场景JSON s03 | 防过拟合 |
| 无量纲化 | 默认开启 | 场景JSON s02 | 统一跨工况量纲 |

### 校准数值（以下数值来自场景CFD_S063，供量级校准；其他体系需以自身证据重新锚定）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| batch_size | 8 | 场景JSON s03/s04 | 训练和推理批大小 |
| learning_rate | 0.001 | 场景JSON s03 | 默认学习率 |
| epochs | 100 | 场景JSON s03 | 最大训练轮数 |
| seed | 42 | 场景JSON s02/s03 | 可复现随机种子 |
| framework | PyTorch | 场景JSON s03 | 训练框架 |

## 边界与分流

- **对称群不存在或未知**：无法直接使用Lie等变网络；需先通过李群分析确定PDE的对称群，或改用非等变基线模型。
- **对称性仅为近似**：参考Approximately Equivariant Networks思路（[P7]），在网络中引入可学习的对称破缺项。
- **域外工况（OOD）**：超出训练分布的几何/工况必须经CFD复核，不得仅凭平均误差宣称工程可用。
- **高维三维复杂几何**：PDO-s3DCNNs（[P9]）提供可转向三维卷积方案，但计算开销显著增加。

## 质量检查

- 训练/验证损失均为有限值（无NaN/Inf）
- 最佳权重可重新加载并产生一致预测
- 预测结果无NaN/Inf且形状单位正确
- 每个测试样本有唯一结果
- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

## 回退策略

- 等变网络训练失败：退化为标准U-Net/ResNet基线对比
- PDO卷积实现不兼容：使用标准等变卷积替代
- 物理约束违反严重：引入物理信息惩罚项（PINN风格）重新训练
- OOD测试全部失败：限定适用域为训练分布内，输出适用域报告

## 资源召回建议

当用户任务涉及以下关键词时应召回本卡片：
- "Lie等变"、"对称PDE"、"PDO卷积"、"等变神经算子"、"群不变预测"
- 配套卡片：cfd-pdo-convolution-layer-design（PDO卷积层设计细节）、cfd-lie-algebra-canonicalization（李代数正规化）、cfd-equivariant-pde-physical-consistency（物理一致性评估）

## 证据来源

[1] Lie Algebra Canonicalization: Equivariant Neural Operators under arbitrary Lie Groups
[2] Space-Time Continuous PDE Forecasting using Equivariant Neural Fields
[3] Physics and Lie symmetry informed Gaussian processes
[4] Equivariant Neural Simulators for Stochastic Spatiotemporal Dynamics
[5] Equivariant Spatio-Temporal Attentive Graph Networks to Simulate Physical Dynamics
[6] Self-Supervised Learning with Lie Symmetries for Partial Differential Equations
[7] Approximately Equivariant Networks for Imperfectly Symmetric Dynamics
[8] PDO-eConvs: Partial Differential Operator Based Equivariant Convolutions
[9] PDO-s3DCNNs: Partial Differential Operator Based Steerable 3D CNNs
