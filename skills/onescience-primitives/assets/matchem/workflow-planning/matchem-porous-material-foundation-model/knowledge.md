# 多孔材料数据高效基础模型构建

## 适用范围

适用于多孔材料（金属有机框架MOF、沸石、多孔碳、多孔聚合物等）的性质预测、结构设计、虚拟筛选任务。当任务要求构建能处理原子级结构信息、具有预训练-微调能力、能进行迁移学习的"基础模型"时，必须使用图神经网络（GNN）架构，而非简单的线性回归或传统机器学习模型。

不适用场景：仅需对已有分子指纹做简单分类/回归的任务；数据量极小（<100样本）且无迁移学习需求的场景。

## 输入

- **结构数据**：原子坐标（Cartesian或分数坐标）、原子类型、晶胞参数（周期性材料）、键连接信息
- **数据来源**：Materials Project、ICSD、QMOF Database、CSD MOF子集、自定义DFT计算数据
- **数据格式**：CIF、POSCAR、XYZ、JSON（ASE原子对象格式）
- **预处理要求**：结构弛豫、删除重复结构、统一原子坐标系、计算原子间距离截断（通常5-6 Å）

## 输出

- **模型产物**：预训练基础模型权重、微调后模型权重、模型配置文件
- **预测产物**：材料性质预测值（吸附容量、带隙、力学性质等）
- **验证产物**：测试集性能指标（MAE/RMSE/R²）、与DFT/实验值对比图表

## 流程节点

### 阶段1：数据准备
1. **数据获取** → 从Materials Project/ICSD/QMOF下载结构数据
2. **数据清洗** → 去重、格式统一、质量筛选
3. **特征准备** → 原子坐标+类型+晶胞参数，无需手工特征（GNN端到端学习）

### 阶段2：模型选择与构建
4. **架构选择** → 根据任务特性选择GNN架构（见关键参数表）
5. **模型构建** → 实现消息传递机制、等变性约束、读出函数
6. **预训练** → 在大规模通用数据集（如Materials Project）上预训练

### 阶段3：微调与验证
7. **任务微调** → 在目标多孔材料数据集上微调
8. **独立验证** → 使用实验数据或高保真DFT计算结果验证
9. **性能评估** → 报告MAE/RMSE/R²，与baseline对比

## 关键参数

| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| 截断半径 | 5-6 Å | [Reiser2022] | 邻域定义，过大导致过平滑 |
| 消息传递层数 | 3-6层 | [Reiser2022] | 过多导致过平滑/过挤压 |
| 原子特征维度 | 64-256 | [Reiser2022] | 嵌入维度，过大增加计算开销 |
| 等变性约束 | SE(3)等变 | [Batatia2022] | MACE/NequIP必需，保证物理一致性 |
| 预训练数据集 | Materials Project | [Reiser2022] | 约15万结构，覆盖多数无机材料 |
| 微调数据量 | ≥500样本 | [Reiser2022] | 少于此量需考虑few-shot策略 |

## 边界与分流

- **数据量不足**（<100样本）：使用预训练模型+few-shot微调，或采用传统ML+手工特征
- **结构复杂度高**（柔性MOF）：使用允许结构弛豫的GNN变体（如DimeNet++）
- **周期性边界**：必须使用支持周期性的GNN（如SchNet、MACE），非周期性GNN不适用
- **多任务预测**：共享编码器+多头解码器架构

## 质量检查

- **收敛性检查**：训练loss稳定下降，验证loss不发散
- **物理一致性**：预测值在物理合理范围内（如吸附容量>0）
- **可复现性**：固定随机种子，记录环境信息（Python/PyTorch版本）
- **独立验证**：必须使用训练集外的数据验证，避免数据泄漏

## 回退策略

- 若GNN训练失败：回退到传统ML（Random Forest/XGBoost）+手工特征（Coulomb矩阵、SOAP等）
- 若预训练不可用：使用迁移学习策略，从相似材料域迁移
- 若计算资源不足：使用轻量级GNN（如SchNet）或降采样数据

## 资源召回建议

当任务涉及以下关键词时应召回本卡片：
- 多孔材料、MOF、沸石、多孔碳
- 基础模型、foundation model
- 图神经网络、GNN、图卷积
- 原子性质预测、分子性质预测
- 预训练、迁移学习
- 吸附、分离、催化

配套资源：`matchem-porous-material-data-sources`（数据获取与验证）

## 证据来源

[1] Reiser P, Neubert M, Eberhard A, et al. Graph neural networks for materials science and chemistry. Communications Materials, 2022, 3: 93. DOI: 10.1038/s43246-022-00315-6

[2] A graph neural network for the era of large atomistic models. npj Computational Materials, 2026. DOI: 10.1038/s41524-026-02146-2

[3] Batatia I, et al. MACE: Higher Order Equivariant Message Passing Neural Networks for Fast and Accurate Force Fields. NeurIPS, 2022.

[4] Schütt K, et al. SchNet: A continuous-filter convolutional neural network for modeling quantum interactions. NeurIPS, 2017.

[5] Gasteiger J, et al. DimeNet: Directional Message Passing for Molecular Graphs. ICLR, 2020.

[6] Zhong X, et al. Explainable machine learning in materials science. npj Computational Materials, 2022. DOI: 10.1038/s41524-022-00884-7

[7] Clayson IG, et al. High Throughput Methods in the Synthesis, Characterization, and Optimization of Porous Materials. Advanced Materials, 2020. DOI: 10.1002/adma.202002780