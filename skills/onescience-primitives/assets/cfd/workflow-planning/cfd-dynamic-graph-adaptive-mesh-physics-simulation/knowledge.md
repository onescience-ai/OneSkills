# 动态图网络与自适应网格物理时序模拟

## 适用范围

**触发条件**：
- 输入数据为动态图（节点特征随时间演化）或拉格朗日粒子轨迹时序
- 需要在非结构化网格或自适应网格上求解偏微分方程或预测物理场
- 目标是构建物理一致的代理模型替代或加速传统CFD求解器

**适用场景**：
- 流体动力学中的粒子法（SPH）模拟加速
- 自适应网格上的Navier-Stokes方程代理求解
- 基于消息传递的物理场时空预测（如洪水淹没、布料模拟）
- 动态拓扑结构（网格随物理量自适应演化）的物理模拟

**不适用场景**：
- 规则网格上的固定拓扑卷积PDE求解（适用标准CNN/PINO类方法）
- 无时序依赖的静态物理场预测
- 纯数据驱动无物理约束的黑箱模拟（需物理一致性评估时本场景适用）

## 输入

- **动态图数据**：节点特征（位置、速度、压力等物理量）+ 边连接（邻接关系随时间变化），格式为时序图序列
- **拉格朗日粒子数据**：粒子位置、速度、密度等物理量的时间序列，粒子数可变
- **网格数据**：自适应网格的节点坐标、单元连接、网格层级信息，网格拓扑随物理量演化
- **物理参数**：流体粘度、密度、边界条件等物理常量
- **数据契约**：变量名、单位、坐标系、网格拓扑定义的结构化描述

## 输出

- **可复现模型**：训练好的消息传递PDE求解器或自适应网格GNN权重（best_checkpoint.pt）
- **任务结果**：测试集上的逐样本预测结果、反归一化后的物理量恢复
- **物理一致性评估**：统计误差（relative_L2、RMSE）、物理约束满足度（守恒残差、边界误差）
- **适用域报告**：模型在训练域内和域外工况的性能边界，标注哪些工况需要CFD复核

## 流程节点

### Step 1：数据接入与契约核验
- **操作**：读取动态图与拉格朗日粒子时序数据，建立数据清单，核验样本、变量、单位、网格坐标及许可
- **参数**：数据集路径、数据集名称、数据契约（变量单位网格定义）
- **工具**：文件系统读取、JSON解析、数据审计脚本
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏
- **输出**：dataset_manifest.json、data_contract.json、data_audit.md

### Step 2：预处理与数据切分
- **操作**：统一物理量与表示，按几何、工况或时间构造无泄漏切分，完成归一化或无量纲化
- **参数**：切分配置（train/val/test比例、种子、分组策略）、目标变量列表、是否无量纲化
- **工具**：归一化计算器、切分工具、图构建器
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏
- **输出**：train_manifest.json、validation_manifest.json、test_manifest.json、normalization.json

### Step 3：模型配置与训练
- **操作**：训练消息传递神经PDE求解器与自适应网格GNN，完成输入到目标物理量的映射
- **参数**：模型名称、训练配置（框架、 epochs、batch_size、学习率、种子、早停）、可选预训练权重
- **工具**：PyTorch、GNN库（如PyG、DGL）、训练监控脚本
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现
- **输出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt

### Step 4：批量推理与物理恢复
- **操作**：在独立测试集上推理，反归一化并恢复原始单位、网格和物理派生量
- **参数**：模型权重路径、计算设备、推理批大小
- **工具**：模型加载器、反归一化脚本、结果格式化工具
- **质量门禁**：预测无NaN或Inf且形状单位正确；每个测试样本有唯一结果；推理未使用测试目标校正
- **输出**：predictions/、inference_manifest.json、timing.csv

### Step 5：任务验收与适用域判定
- **操作**：评估统计误差、关键物理约束、泛化能力和计算收益，给出PASS/REJECT/BLOCKED结论
- **参数**：验收指标列表、相对误差门限、是否执行外推测试
- **工具**：误差计算脚本、物理约束检查器、可视化工具
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
- **输出**：evaluation.json、worst_cases.csv、applicability_report.md、PASS_REJECT_BLOCKED.txt

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型类型 | Message-passing neural PDE solver, Adaptive mesh GNN | [场景CFD_S020] | 两种互补的图神经网络架构 |
| 默认框架 | PyTorch | [场景CFD_S020] | 训练与推理框架 |
| 默认epochs | 100 | [场景CFD_S020] | 训练轮数，可通过早停提前终止 |
| 默认batch_size | 8 | [场景CFD_S020] | 训练批大小，需适配显存 |
| 默认学习率 | 0.001 | [场景CFD_S020] | Adam优化器默认学习率 |
| 早停耐心 | 15 | [场景CFD_S020] | 验证集loss不下降的最大容忍轮数 |
| 相对误差门限 | 0.1 | [场景CFD_S020] | 测试集PASS/REJECT判定阈值 |
| 默认切分比 | 0.7/0.15/0.15 | [场景CFD_S020] | 训练/验证/测试比例 |
| 默认随机种子 | 42 | [场景CFD_S020] | 确保可复现性 |
| 验收指标 | relative_L2, RMSE, conservation_residual, boundary_error | [场景CFD_S020] | 统计与物理约束双重评估 |

## 边界与分流

- **数据格式不兼容**：动态图格式与消息传递框架不匹配时，先执行图格式转换（如DGL↔PyG适配），再进入Step 2
- **网格自适应失败**：自适应网格演化导致拓扑不稳定时，降级为固定网格GNN或回退到拉格朗日粒子表示
- **物理约束违反**：守恒残差超出阈值时，在损失函数中添加物理约束正则项重新训练
- **域外工况检测**：外推测试显示性能骤降时，在适用域报告中标注需要CFD复核的工况范围
- **训练不收敛**：损失曲线振荡或发散时，降低学习率、增大早停耐心或检查数据质量

## 质量检查

- 数据审计：每个变量的统计分布合理性、缺失值比例、坐标系一致性
- 训练过程：损失曲线平滑性、验证集泛化间隙、梯度爆炸检测
- 推理结果：逐样本预测的物理合理性（速度场连续性、压力非负性等）
- 物理一致性：守恒方程残差量级、边界条件满足度、时间演化稳定性
- 适用域：训练分布覆盖度、OOD样本比例、最差样本的物理特征分析

## 回退策略

- 图神经网络不适用时：退化为传统CFD求解器（如OpenFOAM）或网格无关方法（如PINN）
- 消息传递不稳定时：改用注意力机制（如Graph Attention Network）或增加消息传递轮数
- 自适应网格开销过大时：使用多尺度图表示或分层图网络降低计算复杂度
- 训练数据不足时：采用迁移学习从预训练PDE求解器微调

## 资源召回建议

- 当用户提及"动态图网络""自适应网格""消息传递PDE求解器""拉格朗日粒子模拟"时召回本卡
- 配套资源：cfd-neural-pde-solver-workflow（完整工作流）、cfd-message-passing-pde-training（训练细节）、cfd-adaptive-mesh-inference（推理细节）
- 相关领域卡：cfd-turbulence-simulation-mesh-generation（网格生成）、cfd-sph-particle-method（粒子法）

## 证据来源

[1] "EvoMesh: Adaptive Physical Simulation with Hierarchical Graph Evolutions", 2024
[2] "Geometric and Physical Constraints Synergistically Enhance Neural PDE Surrogates", 2024
[3] "Breaking the Discretization Barrier of Continuous Physics Simulation Learning", arXiv:2509.17955, 2025
[4] "Neural SPH: Improved Neural Modeling of Lagrangian Fluid Dynamics", 2024
[5] "Pluvial Flood Emulation with Hydraulics-informed Message Passing", 2024
[6] "A Stable and Scalable Method for Solving Initial Value PDEs with Neural Networks", arXiv:2304.14994, 2023
[7] "ACMP: Allen-Cahn Message Passing with Attractive and Repulsive Forces for Graph Neural Networks", arXiv:2206.05437, 2022
[8] "Learning Neural PDE Solvers with Parameter-Guided Channel Attention", 2024
[9] "Newton-Cotes Graph Neural Networks: On the Time Evolution of Dynamic Systems", 2024
[10] "Message Passing Neural PDE Solvers", arXiv:2202.03376, 2022
[11] "Learning 3D Garment Animation from Trajectories of A Piece of Cloth", 2024
