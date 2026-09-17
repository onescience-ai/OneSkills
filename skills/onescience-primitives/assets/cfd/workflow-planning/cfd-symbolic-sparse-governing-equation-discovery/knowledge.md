# Symbolic and Sparse Physics Learning for Governing Equation Discovery

## 适用范围
面向稀疏状态轨迹与导数观测数据，通过符号回归（Symbolic Regression）与稀疏正则化方法从数据中自动发现控制偏微分方程（PDE）的闭合形式。适用于流体力学、传热传质、多物理场耦合等领域的方程发现任务，尤其适合传感器稀疏布置或实验数据有限的场景。

**适用**：已知目标物理场的空间-时间采样点或网格数据，需要从数据中推断控制方程形式。
**不适用**：方程形式已知仅需参数反演的场景；纯数据驱动黑箱预测任务；高维几何复杂域上的完整CFD仿真替代。

## 输入
- **稀疏状态轨迹**：空间-时间域上的物理量采样（压力、速度、温度等），可来自实验、传感器或简化CFD数据。
- **导数观测**：部分或全部空间/时间导数信息，可通过自动微分或有限差分从原始数据中提取。
- **数据契约**：变量单位、网格拓扑、坐标系、时间/工况范围的结构化定义。

## 输出
- **发现的控制方程**：符号形式的PDE表达式（闭合形式或稀疏表示）。
- **模型权重**：可复现的训练检查点。
- **物理一致性评估**：PDE残差、守恒误差、边界误差的量化报告。
- **适用域报告**：泛化能力与工况边界说明。

## 流程节点
```
数据接入与契约核验 → 预处理与数据切分 → 模型配置与训练 → 方程求解与物理残差恢复 → 任务验收与适用域判定
```

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 相对误差门限 | 0.1（默认） | [场景需求书] | 测试集放行阈值，可按任务调整 |
| 验收指标集 | relative_L2, PDE_residual, boundary_error, conservation_error | [场景需求书] | 统计与物理指标必须同时报告 |
| 切分比例 | train:0.7 / val:0.15 / test:0.15 | [场景需求书] | 默认比例，按轨迹或工况分组 |
| 无量纲化 | 默认开启 | [场景需求书] | 统一跨工况量纲 |
| 早停耐心 | 15轮 | [场景需求书] | 防止过拟合的默认配置 |

### 校准数值
> 以下数值来自场景需求书的默认配置，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 框架 | PyTorch | [场景需求书] | 默认训练框架 |
| 训练轮数 | 100 | [场景需求书] | 默认上限，实际受早停控制 |
| 批大小 | 8 | [场景需求书] | 默认，按显存调整 |
| 学习率 | 0.001 | [场景需求书] | 默认优化器学习率 |
| 随机种子 | 42 | [场景需求书] | 默认种子，确保可复现 |

## 边界与分流
- **数据不满足契约**（缺少关键变量或坐标定义）：返回BLOCKED，不得编造数据。
- **训练验证损失为非有限值**：检查数据预处理和梯度流，回退至s02重新切分。
- **仅凭训练损失无法判定方程已求解**：必须恢复解场、导数和残差进行独立验证。
- **域外工况**：适用域判定为REJECT或BLOCKED时，须经CFD复核，不得直接宣称工程可用。
- **平均误差不足以代表工程可用性**：必须报告最差样本并给出适用域限制。

## 质量检查
1. 训练验证损失均为有限值（非NaN/Inf）。
2. 最佳权重可重新加载并产生一致推理结果。
3. 解场导数与残差均为有限值。
4. 边初值逐项满足门限。
5. 统计与物理指标同时报告，最差样本可追溯。
6. 结论含适用域限制与复核建议。

## 回退策略
- 训练失败：回退至s02检查切分配置，调整归一化策略。
- 残差恢复异常：检查自动微分设置或离散算子实现。
- 适用域判定REJECT：增加训练数据覆盖范围，或切换至更保守的稀疏正则化策略。

## 资源召回建议
- 当用户需要从数据中发现PDE方程形式时召回本卡片。
- 配套资源：cfd-symbolic-sparse-equation-discovery-workflow（工作流级）、cfd-sparse-data-intake-and-contract-verification（数据接入）、cfd-symbolic-pde-model-training（模型训练）、cfd-pde-residual-recovery（残差恢复）、cfd-equation-applicability-domain-evaluation（验收判定）。

## 证据来源
[1] Universal Physics-Informed Neural Networks: Symbolic Differential Operator Discovery with Sparse Data, 2022
[2] Symbolic Physics Learner: Discovering governing equations via Monte Carlo tree search, 2022
[3] Physics informed deep learning (Part II): Data-driven discovery of nonlinear partial differential equations, 2017
[4] Deep hidden physics models: Deep learning of nonlinear partial differential equations, 2018
[5] D-CIPHER: Discovery of Closed-form Partial Differential Equations, 2022
[6] Learning fluid physics from highly turbulent data using sparse physics-informed discovery of empirical relations, 2024
[7] Understanding Generalization in Physics Informed Models through Affine Variety Dimensions, 2025
