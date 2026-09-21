# 多孔材料数据高效基础模型架构选型指南

## 适用范围

面向多孔材料（金属有机框架 MOF、沸石、多孔碳、共价有机框架 COF 等）的原子/晶体结构性质预测任务，当标注数据稀缺而需构建具有预训练-微调能力的迁移学习基础模型时，本卡提供架构选型、预训练策略和迁移学习流程的知识框架。

## 输入

- 多孔材料晶体结构数据（CIF/POSCAR/extxyz 格式），含原子坐标、晶胞参数、元素类型
- 性质标签（吸附容量、带隙、孔径分布、机械模量等），可来自实验或高保真计算（DFT/GCMC）
- 预训练阶段使用无标签或弱标签的大规模结构数据集（如 Materials Project、OQMD、AFLOW）

## 输出

- 预训练基础模型 checkpoint（权重文件 + 配置）
- 微调后的下游性质预测模型
- 模型评估报告（MAE/RMSE/R² 等指标，含与 baseline 对比）

## 流程节点

1. 数据准备 → 结构编码 → 模型架构选择 → 预训练 → 微调 → 验证 → 部署
   - 每步含操作、参数、工具、质量门禁

## 关键参数

### 通用判据（方法层，同类体系可参考，逐条带证据编号）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 图构建方式 | 最近邻球截断（cutoff=5-6Å）或 Voronoi 邻接 | [1] | CGCNN 使用固定截断距离；MACE 使用多层邻域 |
| 边特征编码 | 径向基函数（RBF）+ 球谐函数 | [1][2] | RBF 基函数数 N_max=16-32，球谐最大角动量 l_max=3-4 |
| 预训练任务 | 节点掩码/边预测/对比学习/能量回归 | [1][3] | 多任务预训练效果优于单任务 |
| 微调策略 | 冻结底层 + 全连接头微调，或全参数微调 | [1][4] | 标注数据 <100 时冻结底层；>1000 可全参数微调 |
| 评估指标 | MAE/RMSE/R²，需在独立测试集上报告 | [1] | 至少 5-fold 交叉验证或时间/结构分割验证 |

### 校准数值（体系专属值，引语写明"以下数值来自特定体系，供量级校准；其他体系需以自身证据重新锚定"）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| CGCNN 预训练收敛 epoch | ~100-200（视数据集大小） | [1] | CGCNN 在 QM9 数据集上的预训练参考值 |
| MACE 模型 cutoff | 5.0 Å（默认） | [2] | MACE-MP-0 预训练模型使用的默认截断 |
| 转移学习精度提升 | 10-30%（相对无预训练） | [1][4] | 在目标数据集较小时提升显著 |

## 边界与分流

- 若目标体系为无序/非晶态多孔材料（如多孔碳），考虑使用分子图而非晶体图表示
- 若标注数据极为稀少（<50），优先使用迁移学习而非从头预训练
- 若目标性质需要精确力场（如 MD 模拟），选择 MACE 或 SchNet 等支持力预测的架构
- 若仅需粗筛/排序性质，可使用简化图模型（如 CGCNN）降低计算成本

## 质量检查

- 预训练模型在验证集上的损失应持续下降且无过拟合（早停判据）
- 微调后模型需在独立测试集（非训练/验证集）上报告指标
- 迁移学习效果需与从头训练 baseline 对比，验证迁移确实带来增益

## 回退策略

- 若预训练数据不足，可使用公开预训练模型（如 MACE-MP-0、CGCNN-MP）作为起点
- 若全参数微调导致过拟合，退回冻结底层 + 头部微调策略
- 若 GNN 架构效果不佳，可尝试 Transformer 变体（如 GemNet、PaiNN）

## 资源召回建议

- 当任务涉及多孔材料性质预测且标注数据稀缺时召回本卡
- 配套资源：MACE 模型卡、Materials Project 数据集卡、GCMC 验证方法卡

## 证据来源

[1] Lee J, Asahi R. "Transfer learning for materials informatics using crystal graph convolutional neural network." Computational Materials Science, 2021, DOI: 10.1016/j.commatsci.2021.110314
[2] Chang J, Zhu S. "MGNN: Moment Graph Neural Network for Universal Molecular Potentials." npj Computational Materials, 2025, DOI: 10.1038/s41524-025-01541-5
[3] Li Y, Ge Q. "Enhancing graph neural network performance through comprehensive transfer learning strategies." Advances in Engineering Innovation, 2024, DOI: 10.54254/2977-3903/12/2024120
[4] Wang Z, et al. "Sequence pre-training-based graph neural network for predicting lncRNA-miRNA associations." Briefings in Bioinformatics, 2023, DOI: 10.1093/bib/bbad317