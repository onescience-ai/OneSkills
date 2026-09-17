# 域分解与非均匀几何神经算子学习场景

## 适用范围
本场景覆盖在非均匀采样与变形几何PDE数据条件下，通过域分解方法与神经算子结合完成PDE解算子学习的全流程。适用于以下任务：
- 非均匀网格或变形几何PDE数据的处理与建模
- 需要几何泛化能力的流场预测任务
- 域分解策略与神经算子结合的模型训练与评估
- 跨工况、跨几何的PDE解算子学习

不适用场景：
- 均匀规则网格上的标准PDE求解（无需域分解）
- 纯数据驱动的黑盒模型（无物理约束需求）
- 低维参数化PDE（可直接用传统神经算子）

## 输入
- 非均匀采样PDE数据（可能来自非结构网格、自适应网格或变形几何）
- 几何描述信息（边界形状、变形参数）
- 物理参数（雷诺数、边界条件等）
- 参考解或初始条件

## 输出
- 训练好的域分解神经算子模型
- 测试集预测结果与物理恢复量
- 统计误差与物理一致性评估报告
- 适用域判定与外推能力分析

## 流程节点
数据接入与契约核验 → 预处理与数据切分 → 模型配置与训练 → 批量推理与物理恢复 → 任务验收与适用域判定

## 关键参数

### 通用判据（方法层）
| 参数 | 判据 | 来源 | 说明 |
|------|------|------|------|
| 域分解策略 | 应基于物理特征或几何特征划分 | [1][2] | 如边界层/远场/尾流区域划分 |
| 神经算子类型 | 需支持非结构数据输入 | [1][5] | GNN/FNO变体等 |
| 几何编码 | 需显式编码几何信息 | [3][4] | 用于几何泛化 |
| 物理约束 | 应包含守恒律或边界条件约束 | [1][3] | 提升物理一致性 |
| 泛化测试 | 需包含域外工况测试 | [4][6] | 评估泛化能力 |

### 校准数值（场景专属值）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 域分解路由速度提升 | ~10,000x vs RANS | [1] | DD-RNO在AirfRANS上的加速比 |
| 边界误差降低 | ~38%相对L2 | [3] | GeoABC在近边界的改进 |
| 跨Reynolds数误差 | 46.68%相对L2 | [4] | FNO在10x Reynolds偏移下的误差 |
| 几何变形误差降低 | up to 80% | [2] | RNO相比基线模型的改进 |

## 边界与分流
- **非均匀数据处理**：若数据为非结构网格，需采用图神经网络或点云方法处理
- **几何变形处理**：若几何变形较大，需采用参考解方法或几何编码
- **域外工况**：若超出训练分布，需经CFD复核，不得仅凭平均误差宣称可用
- **计算资源**：大尺度3D问题需考虑并行化或模型压缩策略

## 质量检查
- 训练/验证损失均为有限值且收敛
- 测试集预测无NaN或Inf
- 物理约束残差在可接受范围内
- 最差样本误差可追溯
- 适用域边界明确

## 回退策略
- 若域分解效果不佳，可尝试调整划分策略或采用全局模型
- 若几何泛化不足，可增加几何增强或采用参考解方法
- 若物理约束违反严重，可增加物理损失权重或采用硬约束

## 资源召回建议
本卡片适用于以下场景的召回：
- 非均匀网格PDE求解
- 变形几何流场预测
- 域分解神经算子设计
- 几何泛化能力评估
- 跨工况PDE算子学习

配套资源：
- 数据处理类：非均匀网格预处理、几何编码
- 模型类：域分解神经算子、NUNO、DD-RNO
- 评估类：物理一致性验证、适用域判定

## 证据来源
[1] DD-RNO: A Domain-Decomposed Routed Neural Operator for Airfoil Flow Prediction, Mehta et al., 2026, arXiv:2608.13490
[2] Reference Neural Operators: Learning the Smooth Dependence of Solutions of PDEs on Geometric Deformations, Cheng et al., 2024, arXiv:2405.17509
[3] Geometry-Aware Anisotropic Boundary Correction for Aerodynamic Simulation, Zhang et al., 2026, arXiv:2606.09963
[4] Striding Across Reynolds Numbers: Representation Geometry in Neural PDE Generalisation, Shi, 2026, arXiv:2605.30112
[5] Neural Operator: Graph Kernel Network for Partial Differential Equations, Li et al., 2020, arXiv:2003.03485
[6] NUNO: A General Framework for Learning Parametric PDEs with Non-Uniform Data, 2023