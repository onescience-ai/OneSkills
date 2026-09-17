# 连续时间与随机生成神经算子预测

## 适用范围

**触发条件**：
- 需要对随机PDE或连续时间PDE分布数据进行场量预测
- 需要在连续时间域上学习PDE动力学演化
- 需要对随机PDE进行概率采样预测

**适用场景**：
- 随机偏微分方程（SPDE）的统计矩预测与采样
- 连续时间ODE/PDE系统的长期动力学预测
- 多尺度、多物理场耦合PDE的算子学习
- 分辨率不变的时空场预测
- 需要物理一致性评估的工程预测任务

**不适用场景**：
- 确定性稳态PDE求解（应使用Deep Equilibrium Neural Operator等）
- 无需时间演化的纯空间场插值
- 缺乏PDE先验知识的纯数据驱动回归
- 域外工况且无法进行CFD复核验证的场景

## 输入

- 随机或连续时间PDE分布数据集（含空间坐标、时间坐标、物理场量）
- 数据契约定义（输入字段、目标字段、单位、坐标系）
- 可选：预训练权重（用于微调场景）

## 输出

- 训练完成的神经算子模型（best_checkpoint.pt）
- 独立测试集上的预测结果（逐样本、恢复物理单位）
- 逐变量误差统计、边界误差、守恒/方程残差
- 物理一致性评估报告与适用域判定（PASS/REJECT/BLOCKED）
- 最差样本分析与推理成本报告

## 流程节点

### Phase 1：数据接入与契约核验
- **操作**：接入PDE分布数据，建立数据清单，核验样本可追溯性、变量定义、单位、坐标系、网格拓扑
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏

### Phase 2：预处理与数据切分
- **操作**：统一物理量表示，按几何/工况/轨迹进行无泄漏切分，归一化或无量纲化
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏

### Phase 3：模型配置与训练
- **操作**：配置Continuous-time neural operator和Stochastic neural operator，执行训练并记录指标
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现

### Phase 4：批量推理与物理恢复
- **操作**：在独立测试集上推理，反归一化恢复物理单位、网格和派生量
- **质量门禁**：预测无NaN或Inf且形状单位正确；每个测试样本有唯一结果；推理未使用测试目标校正

### Phase 5：任务验收与适用域判定
- **操作**：评估统计误差、物理约束、泛化能力和计算收益，给出PASS/REJECT/BLOCKED结论
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 框架 | PyTorch | 场景需求书 | 默认训练框架 |
| 训练轮数 | 100 epochs | 场景需求书 | 默认训练轮数，可据早停调整 |
| 批大小 | 8 | 场景需求书 | 默认批大小，按显存调整 |
| 学习率 | 0.001 | 场景需求书 | 默认学习率 |
| 随机种子 | 42 | 场景需求书 | 可复现性保障 |
| 早停耐心 | 15 epochs | 场景需求书 | 验证损失不改善时的等待轮数 |
| 默认切分比 | train 0.7 / val 0.15 / test 0.15 | 场景需求书 | 按对象轨迹切分 |
| 验收指标 | relative_L2, RMSE, conservation_residual, boundary_error | 场景需求书 | 统计+物理双重验收 |
| 相对误差门限 | 0.1 | 场景需求书 | 测试集放行阈值 |
| 推理设备 | CUDA（默认） | 场景需求书 | 可选CPU |

## 边界与分流

- **数据缺失必填字段**：返回BLOCKED，列出缺项，不得编造数据
- **域外工况**：若外推测试FAIL，模型不得宣称工程可用，需标注适用域限制并建议CFD复核
- **模型结构不兼容预训练权重**：拒绝加载，回退为随机初始化训练
- **训练/验证损失非有限值**：判定训练失败，检查数据与超参数后重试
- **物理约束违反（守恒残差/边界误差超标）**：即使统计误差达标也REJECT

## 质量检查

- 数据清单可追溯性验证
- 切分互斥性检查（无轨迹泄漏）
- 训练过程可复现性（种子+环境锁定）
- 推理结果完整性（逐样本唯一、单位正确）
- 物理一致性双指标门禁（统计+物理同时达标）

## 回退策略

- 训练失败：检查数据质量→调整超参数→增加数据增强→更换模型架构
- 推理异常：检查checkpoint完整性→验证数据契约→降低批大小重试
- 适用域不足：增加域外训练数据→采用自适应条件化→标注适用域边界

## 资源召回建议

- 本卡片适用于所有需要对PDE数据进行连续时间或随机生成算子学习的CFD任务
- 配套召回：cfd-pde-neural-operator-prediction-workflow（工作流规划）
- 若需要具体步骤的详细执行指南，召回对应的task卡片

## 证据来源

[1] CFO: Learning Continuous-Time PDE Dynamics via Flow-Matched Neural Operators, arXiv:2303.08797, 2023
[2] Wavelet Diffusion Neural Operator, 2024
[3] Neural Stochastic PDEs: Resolution-Invariant Learning of Continuous Spatiotemporal Dynamics, 2023
[4] Variational Autoencoding Neural Operators, 2023
[5] Learning Semilinear Neural Operators: A Unified Recursive Framework for Prediction and Data Assimilation, 2023
[6] Boosting Generalization in Parametric PDE Neural Solvers through Adaptive Conditioning, 2023
[7] Convolutional Neural Operators for Robust and Accurate Learning of PDEs, 2023
[8] Deep Equilibrium Based Neural Operators for Steady-State PDEs, 2023
[9] Representation Equivalent Neural Operators: a Framework for Alias-free Operator Learning, 2023
[10] Newton Informed Neural Operator for Solving Nonlinear Partial Differential Equations, arXiv:2207.05748, 2022
[11] Linearization Turns Neural Operators into Function-Valued Gaussian Processes, 2023
[12] Optimization for Neural Operators can Benefit from Width, 2023
[13] KANO: Kolmogorov-Arnold Neural Operator, arXiv:2406.14495, 2024
[14] Riesz Neural Operator for Solving Partial Differential Equations, 2023
