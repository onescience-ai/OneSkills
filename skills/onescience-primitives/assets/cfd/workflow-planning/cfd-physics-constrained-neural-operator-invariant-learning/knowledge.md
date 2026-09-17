# 物理边界与不变量约束神经算子学习

## 适用范围
面向带守恒边界和无量纲约束PDE数据，训练物理约束神经算子以学习物理边界与不变量约束的映射关系。核心目标是在神经算子中嵌入物理先验（如边界条件、守恒律、无量纲不变量），使模型在预测PDE解场时同时满足统计精度和物理一致性。适用于需要从PDE数据中学习输入到解算子映射、并要求预测结果符合物理约束的CFD任务，不适用于纯数据驱动且无物理约束的神经算子学习。

## 输入
- **PDE数据集**：包含带守恒边界和无量纲约束的PDE数据，如Navier-Stokes方程、Burgers方程等流体力学问题的数值解
- **数据契约**：定义变量单位、网格坐标、边界条件类型和守恒律约束
- **训练配置**：神经算子架构参数、学习率、批次大小等超参数
- **物理约束定义**：边界条件类型（Dirichlet/Neumann/周期性）、守恒量（质量、动量、能量）、无量纲不变量（Reynolds数、Peclet数等）

## 输出
- **训练好的物理约束神经算子**：可复现的模型checkpoint，满足物理约束的预测能力
- **物理一致性评估报告**：包含边界误差、守恒残差、无量纲不变量偏差等指标
- **适用域报告**：明确模型在几何、工况、参数空间上的适用范围和限制
- **域外工况复核建议**：超出适用域时需经CFD复核的明确指示

## 流程节点
1. **数据接入与契约核验** → 检查PDE数据文件可读性、样本数、变量定义、单位、坐标系、边界条件和守恒约束
2. **预处理与数据切分** → 统一物理量表示，按几何、工况或时间进行无泄漏切分，保留边界掩膜和守恒约束
3. **模型配置与训练** → 训练Physics-constrained neural operator，嵌入物理约束作为损失项或架构约束
4. **批量推理与物理恢复** → 在独立测试集推理，恢复原始单位、网格和物理派生量，确保预测满足物理约束
5. **任务验收与适用域判定** → 评估统计误差、物理约束满足程度、泛化能力和计算收益，确定适用域

## 关键参数
### 通用判据
| 参数 | 判据 | 来源 | 说明 |
|------|------|------|------|
| 边界误差(boundary_error) | ≤ 任务物理门限 | [场景需求书] | 边界条件满足程度 |
| 守恒残差(conservation_residual) | ≤ 任务物理门限 | [场景需求书] | 质量/动量/能量守恒程度 |
| 相对L2误差(relative_L2) | ≤ 0.1 | [场景需求书] | 统计精度门限 |
| 无量纲不变量偏差 | ≤ 任务物理门限 | [场景需求书] | Reynolds数等无量纲量保持程度 |
| 最差样本误差 | 可追溯 | [场景需求书] | 极端情况性能保证 |

### 校准数值
以下数值来自典型CFD场景，供量级校准；其他体系需以自身证据重新锚定：
| 参数 | 典型值 | 来源 | 说明 |
|------|--------|------|------|
| 相对L2误差门限 | 0.1 | [场景需求书] | 测试集放行阈值 |
| 训练验证损失 | 有限值 | [场景需求书s03] | 避免NaN/Inf |
| 推理批大小 | 8 | [场景需求书s04] | 按显存调整 |

## 边界与分流
- **边界条件类型未知** → 转向通用PDE数据预处理流程，需人工确认边界条件类型
- **守恒律约束不明确** → 转向无物理约束的纯数据驱动神经算子学习，但需在适用域报告中声明物理一致性未保证
- **无量纲化困难** → 转向基于物理量纲的归一化方法，但需验证无量纲不变量保持能力
- **域外工况** → 超出适用域时，必须经CFD复核，不得直接使用模型预测

## 质量检查
- **数据完整性**：文件可读、样本可追溯、变量单位坐标定义完整
- **切分有效性**：训练/验证/测试集对象轨迹互斥，无泄漏
- **训练稳定性**：训练验证损失均为有限值，最佳权重可重新加载，随机种子可复现
- **推理正确性**：预测无NaN/Inf且形状单位正确，每个测试样本有唯一结果
- **物理一致性**：边界误差、守恒残差、无量纲不变量偏差满足物理门限
- **适用域明确性**：结论含适用域限制与复核建议，不得仅凭平均误差宣称工程可用

## 回退策略
- **物理约束无法满足** → 降低物理约束权重，转向软约束（损失惩罚）而非硬约束（架构约束）
- **训练不收敛** → 调整学习率、增加训练轮次、检查数据质量
- **泛化能力不足** → 增加训练数据多样性，引入数据增强或迁移学习
- **计算资源不足** → 降低模型复杂度或使用近似推理方法

## 资源召回建议
- **数据预处理**：需要无量纲化或守恒约束处理时，可召回相关预处理卡片
- **边界条件处理**：需要特定边界条件施加策略时，可召回边界条件处理卡片
- **物理约束训练**：需要物理约束损失设计或训练策略时，可召回相关训练卡片
- **适用域评估**：需要泛化能力评估或域外测试时，可召回适用域评估卡片

## 证据来源
[1] Guiding Continuous Operator Learning through Physics-Based Boundary Constraints, 2022, arXiv:2212.07477
[2] Holistic Physics Solver: Learning PDEs in a Unified Spectral-Physical Space, 2023
[3] Learn Singularly Perturbed Solutions via Homotopy Dynamics, 2023
[4] A Physics-preserved Transfer Learning Method for Differential Equations, 2025, arXiv:2505.01281
[5] Nonlocal Attention Operator: Materializing Hidden Knowledge Towards Interpretable Physics Discovery, 2023
[6] PAPM: A Physics-aware Proxy Model for Process Systems, 2023
[7] Training neural operators to preserve invariant measures of chaotic attractors, 2023
[8] Generic bounds on the approximation error for physics-informed (and) operator learning, 2023
[9] Buckingham pi-Invariant Test-Time Projection for Robust PDE Surrogate Modeling, 2024, arXiv:2410.03263
[10] Towards Generalizable PDE Dynamics Forecasting via Physics-Guided Invariant Learning, 2019, arXiv:1907.02893
[11] WAN3DNS: Weak Adversarial Networks for Solving 3D Incompressible Navier-Stokes Equations, 2025, arXiv:2509.26034
[12] Wrong-Physics Backdoors in Neural PDE Operators, 2026, arXiv:2608.20439