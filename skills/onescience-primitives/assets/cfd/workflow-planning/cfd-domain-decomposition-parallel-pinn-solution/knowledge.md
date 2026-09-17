# 区域分解并行PINN大域求解

## 适用范围

**触发条件**：
- 单个PINN在大域或多尺度PDE求解中收敛困难或精度不足
- 网络规模与配点数量导致优化问题过于复杂
- 需要利用多GPU/多核并行加速PINN训练

**适用场景**：
- 大空间域或长时间域的PDE正/逆问题求解
- 多尺度、多物理场耦合PDE问题
- 需要分区分治策略的复杂几何域PDE求解
- 对训练时间有严格要求的工程仿真场景

**不适用场景**：
- 小域简单PDE问题（单PINN即可高效求解）
- 离散数据稀疏且无法提供PDE配点的纯数据驱动问题
- 需要全局一致性严格解析解的高精度认证场景

## 输入

- 分区PDE配点与界面条件数据（含残差配点、边界配点、界面配点）
- PDE定义（微分算子、源项、边界条件类型）
- 几何域定义与子域划分方案
- 数据契约：变量名称、单位、坐标系、网格拓扑

## 输出

- 训练好的子域模型权重与全局解场
- PDE残差场与边界残差
- 物理一致性评估（相对L2误差、PDE残差范数、守恒误差）
- 适用域报告（含最差样本分析与域外工况复核建议）

## 流程节点

### 节点1：数据接入与契约核验
- **操作**：接入分区PDE配点与界面条件数据，核验样本数、变量、单位、网格坐标及许可
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏

### 节点2：预处理与数据切分
- **操作**：统一物理量与表示，按几何、工况或时间构造无泄漏切分；对多工况数据以完整轨迹为单位切分
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏

### 节点3：模型配置与训练
- **操作**：配置FBPINN/XPINN/Parallel PINN模型，加载切分与统计量，执行训练并记录逐轮指标
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现

### 节点4：方程求解与物理残差恢复
- **操作**：在查询配点或网格上恢复解场、导数、边界值与方程残差
- **质量门禁**：解场导数与残差均为有限值；边初值逐项满足门限；独立数值解或解析解可对照

### 节点5：任务验收与适用域判定
- **操作**：评估统计误差、关键物理约束、泛化能力和计算收益；执行外推测试并明确适用域
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议

## 关键参数

### 通用判据（方法层）

| 参数 | 判据 | 来源 | 说明 |
|------|------|------|------|
| 子域重叠方式 | 必须重叠（overlap > 0） | [1] | 无重叠子域无法保证界面连续性 |
| 窗口函数 | 可微、子域外近零、子域内大于零 | [1] | 常用sigmoid型，参数控制过渡区宽度 |
| 界面连续性 | 弱约束（loss项）或构造约束（ansatz） | [1][2] | 弱约束可能引入不连续；构造约束严格但灵活性较低 |
| 子域归一化 | 每子域独立[-1,1]归一化 | [1] | 缓解谱偏差：子域内有效频率降低 |
| 并行度 | 子域数可独立于配点数扩展 | [1][4] | 理论上线性扩展，实际受通信开销约束 |
| 训练调度 | 支持灵活调度（active/fixed/inactive模型） | [1] | 可从边界向外顺序求解，类似时间推进 |

### 校准数值（CFD_S041体系参考值）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型类型 | FBPINN、XPINN、Parallel PINN | [场景需求书] | 场景默认三种方法 |
| 框架 | PyTorch | [1][场景需求书] | 自动微分支持 |
| 训练轮次 | 100 epochs（默认） | [场景需求书] | 可据收敛调整 |
| 批大小 | 8（默认） | [场景需求书] | 按显存调整 |
| 学习率 | 0.001（默认） | [1][场景需求书] | Adam优化器 |
| 早停耐心 | 15（默认） | [场景需求书] | 防过拟合 |
| 相对L2门限 | ≤ 0.1 | [场景需求书] | 测试集放行阈值 |

## 边界与分流

- **子域划分不当（过粗/过细）**：过粗则子域内频率仍高、收敛差；过细则子域数过多、通信开销增大、训练点不足导致过拟合。应根据PDE解的局部复杂度自适应调整子域密度 [1][3]。
- **界面条件冲突**：弱约束（XPINN方式）在界面处可能出现不连续，需增加界面损失权重或切换为构造约束（FBPINN方式）[1][2]。
- **并行通信瓶颈**：子域重叠区域需要线程间同步，子域数过多时通信开销可能超过计算收益，需评估并行效率 [1][4]。
- **域外工况不适用**：模型仅在训练覆盖的几何/工况范围内有效，域外外推需经CFD数值解复核 [场景需求书]。

## 质量检查

- 解场导数与残差均为有限值
- 边界条件误差逐项满足门限
- 相对L2误差 ≤ 设定阈值（默认0.1）
- PDE残差范数在测试集上可接受
- 最差样本误差可追溯
- 适用域报告包含外推测试结论

## 回退策略

- 若并行PINN精度不足：尝试增加子域重叠宽度或调整窗口函数参数
- 若训练不稳定：降低学习率、增加早停耐心、检查PDE残差权重
- 若子域数过多导致通信开销过大：合并邻近子域或减小子域粒度
- 若整体不收敛：回退到标准PINN小域验证，确认PDE定义与配点正确性

## 资源召回建议

- 当用户需要大域PDE求解、多尺度PDE求解、或PINN训练加速时召回本卡
- 配套资源：`cfd-overlapping-domain-decomposition-pinn`（子域划分与窗口函数技术细节）、`cfd-hard-constraint-pinn-complex-geometry-solution`（硬约束边界条件技术）、`cfd-spectral-pinn-multiscale-pde-solution`（谱增强PINN互补方案）

## 证据来源

[1] B. Moseley, A. Markham, T. Nissen-Meyer, "Finite Basis Physics-Informed Neural Networks (FBPINNs): A Scalable Domain Decomposition Approach for Solving Differential Equations", Advances in Computational Mathematics, 2023, DOI: 10.1007/s10444-023-10065-9

[2] Z. Hu, A.D. Jagtap, G.E. Karniadakis, K. Kawaguchi, "When Do Extended Physics-Informed Neural Networks (XPINNs) Improve Generalization", SIAM Journal on Scientific Computing, Vol. 44, Iss. 5, 2022, DOI: 10.1137/21M1447039

[3] A. Bonfanti, I. Medina, R. List, B. Staeves, R. Santana, M. Ellero, "PINN Balls: Scaling Second-Order Methods for PINNs with Domain Decomposition and Adaptive Sampling", arXiv:2510.21262, 2025

[4] "Parallel Physics-Informed Neural Networks via Domain Decomposition", Journal of Computational Physics, 2022, DOI: 10.1016/j.jcp.2021.110683

[5] "Meta Learning of Interface Conditions for Multi-Domain Physics-Informed Neural Networks"
