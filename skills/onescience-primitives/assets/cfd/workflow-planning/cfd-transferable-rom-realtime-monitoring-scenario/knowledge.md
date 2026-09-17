# 可迁移参数化ROM与实时状态监测

## 适用范围

本卡服务的问题类：面向跨几何参数的CFD仿真与稀疏监测数据，构建可迁移参数化降阶模型（ROM），并以该模型支撑实时状态监测。适用于以下场景：
- 需要在不同几何参数（如不同管道形状、不同翼型、不同流道结构）之间快速预测流场状态
- 监测传感器数量有限（稀疏监测），需从少量观测恢复全场信息
- 需要实时或近实时的流场预测能力（如在线监测、数字孪生）

不适用场景：
- 单一固定几何、无需跨几何迁移的ROM构建（可使用常规ROM方法）
- 全场高分辨率实时重建（需密集传感器或极高计算资源）
- 域外工况无CFD复核条件时直接部署

## 输入

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| CFD数据集 | doc | 是 | 跨几何参数的CFD仿真结果，含流场变量、网格、几何参数 |
| 稀疏监测数据 | doc | 是 | 有限传感器位置的时序或空间采样数据 |
| 数据契约 | object | 否 | 定义变量、单位、坐标系、网格拓扑（可由s01自动生成） |

## 输出

| 输出 | 说明 |
|------|------|
| 可迁移ROM模型 | 训练好的Transferable ROM或Shallow Recurrent Decoder权重 |
| 实时监测预测 | 给定稀疏输入后的全场预测结果 |
| 适用域报告 | 模型在不同几何/工况下的泛化能力评估 |
| 物理一致性评估 | 守恒残差、边界误差等物理约束验证结果 |
| PASS/REJECT/BLOCKED判定 | 基于统计误差与物理门限的验收结论 |

## 流程节点

数据接入与契约核验(s01) → 预处理与数据切分(s02) → 模型配置与训练(s03) → 批量推理与物理恢复(s04) → 任务验收与适用域判定(s05)

## 关键参数

### 通用判据

| 参数 | 判据 | 来源 | 说明 |
|------|------|------|------|
| 相对L2误差 | ≤ 0.1（默认门限） | 场景需求书s05 | 测试集放行阈值，可根据任务调整 |
| 守恒残差 | 需报告且为有限值 | 场景需求书s05 | 物理一致性核心指标 |
| 边界误差 | 需报告且为有限值 | 场景需求书s05 | 边界条件满足程度 |
| 切分策略 | 按几何/轨迹/工况为单位 | 场景需求书s02 | 避免同一轨迹帧打散造成泄漏 |
| OOD测试 | 域外工况需执行 | 场景需求书s05 | 适用域判定必要条件 |

### 校准数值（来自场景需求书默认配置，供量级参考）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 训练/验证/测试比例 | 0.7/0.15/0.15 | 场景需求书s02 | 其他体系需以自身证据重新锚定 |
| 随机种子 | 42 | 场景需求书s02/s03 | 复现性保障 |
| 默认框架 | PyTorch | 场景需求书s03 | 其他体系需以自身证据重新锚定 |
| 默认Epochs | 100 | 场景需求书s03 | 其他体系需以自身证据重新锚定 |
| 默认Batch Size | 8 | 场景需求书s03 | 其他体系需以自身证据重新锚定 |
| 默认学习率 | 0.001 | 场景需求书s03 | 其他体系需以自身证据重新锚定 |
| Early Stopping Patience | 15 | 场景需求书s03 | 其他体系需以自身证据重新锚定 |

## 边界与分流

- **数据不可读或缺少必填输入**：返回BLOCKED，列出缺项，不得编造数据
- **训练/验证损失出现非有限值**：判定训练异常，需检查数据与配置后重试
- **相对L2误差超过门限**：判定REJECT，需调整模型或数据策略
- **域外工况泛化能力不足**：明确标注适用域限制，域外工况必须经CFD复核
- **最佳权重无法重新加载**：判定训练产物无效，需重新训练

## 质量检查

- 统计指标与物理指标同时报告（缺一不可）
- 最差样本可追溯到具体测试样本ID
- 结论必须包含适用域限制与复核建议
- 不得仅凭平均误差宣称工程可用

## 回退策略

- 模型不收敛：检查数据质量、调整超参数、尝试不同ROM架构
- 物理约束不满足：在损失函数中增加物理正则项或后处理修正
- 适用域过窄：增加训练数据覆盖范围或采用更灵活的参数化方案

## 资源召回建议

当任务涉及以下关键词时应召回本卡片：
- 可迁移ROM、Transferable ROM、参数化降阶模型
- 实时监测、Real-time monitoring、Shallow Recurrent Decoder
- 跨几何CFD、稀疏传感器、sparse sensing
- 模型序降阶、Model Order Reduction

## 证据来源

[1] Real-Time Monitoring of MHD Liquid Metal Flows with Shallow Recurrent Decoders, arxiv:2608.28366, 2026
[2] Non-intrusive, transferable model for coupled turbulent channel-porous media flow based upon neural networks, arxiv:2311.15600, 2023
[3] Intrusive versus non-intrusive reduced-order modeling of generalized Newtonian fluid flows, arxiv:2608.18259, 2026
[4] Neural Network-Based Parametric Model Reduction for Predicting Turbulent Flow for Different Vehicle Geometries, 2023
[5] Reliable and efficient steady CFD from surrogate predictions through Newton-Krylov correction, 2023
[6] Numerically Solving Parametric Families of High-Dimensional Kolmogorov Partial Differential Equations via Deep Learning, arxiv:1607.06450, 2016
