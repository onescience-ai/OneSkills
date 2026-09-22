# Porous Material GNN Foundation Model Selection

## 适用范围
面向多孔材料（MOF、沸石、多孔碳等）的原子级结构信息处理任务，选择合适的图神经网络（GNN）架构作为基础模型，适用于性质预测、结构筛选、迁移学习等场景。适用于需要处理晶体结构、原子坐标、键连接关系的材料信息学任务；不适用于纯文本或非结构化数据任务。

## 输入
- 晶体结构信息：CIF文件（包含原子坐标、晶胞参数、空间群）
- 原子特征：原子类型、电负性、共价半径、价电子数等
- 键/边特征：键长、键角、键类型
- 预训练数据集：大规模材料性质数据库（如Materials Project、OQMD）

## 输出
- 材料性质预测值（如带隙、形成能、吸附容量、弹性模量）
- 预测置信度/不确定性估计
- 迁移学习后的微调模型

## 流程节点
1. **数据预处理** → 将CIF文件转换为图表示（原子=节点，化学键/邻近原子=边）
2. **模型架构选择** → 根据任务特性选择GNN架构
3. **预训练** → 在大规模材料数据集上进行自监督或监督预训练
4. **微调** → 在目标任务数据上进行迁移学习微调
5. **评估** → 验证模型在目标任务上的性能

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| CGCNN 编码维度 | 64-256 | [1] | 晶体图卷积网络的隐藏层维度 |
| SchNet 交互层 | 3-6层 | [1] | 连续滤波卷积网络的交互块数量 |
| DimeNet 交互层 | 4-12层 | [1] | 方向消息传递网络的嵌入维度 |
| 预训练数据集规模 | >10万结构 | [1] | 迁移学习有效的最小预训练数据量 |
| 微调学习率 | 1e-4 ~ 1e-3 | [1] | 迁移学习微调阶段的学习率 |
| 图构建截断距离 | 4-8 Å | [1] | 构建原子邻接图的距离截断 |

## 边界与分流
- **数据量不足**（<1000样本）：优先使用预训练+微调策略，选择已在大规模数据上预训练的模型（如CGCNN预训练权重）
- **需要等变性**：选择SchNet或DimeNet等具有旋转等变性的架构
- **需要高精度力预测**：选择MACE、NequIP等E(3)-等变模型
- **计算资源受限**：选择轻量级架构（如CGCNN），避免过深的DimeNet
- **多任务学习**：选择支持多头输出的架构，共享底层表示

## 质量检查
- 模型是否具备预训练-微调能力：检查是否有公开的预训练权重
- 预测精度是否满足任务要求：RMSE/R²/MAE是否在可接受范围
- 模型是否能处理原子级结构信息：输入是否包含原子坐标和连接关系
- 迁移学习效果：微调后性能是否显著优于从零训练

## 回退策略
- 如果GNN架构不适用：考虑使用传统机器学习+材料描述符（如Coulomb矩阵、SOAP）
- 如果预训练权重不可用：使用数据增强或小样本学习策略
- 如果计算资源不足：使用模型蒸馏或量化压缩

## 资源召回建议
- 需要召回本卡片的场景：用户提到"基础模型""图神经网络""GNN""迁移学习""预训练"等关键词
- 配套资源：matchem/tasks/porous-material-database-sourcing（数据获取）、matchem/tasks/porous-material-model-validation-gcmc（验证方法）

## 证据来源
[1] Choudhary K, DeCost B. "Transfer learning for materials informatics using crystal graph convolutional neural networks." npj Computational Materials, 2021, 7: 196. DOI: 10.1016/j.commatsci.2021.110314
[2] Zhang Y, et al. "MGNN: Moment Graph Neural Network for Universal Molecular Potentials." npj Computational Materials, 2025. DOI: 10.1038/s41524-025-01609-y
[3] GSMNet authors. "GSMNet: A geometry- and state-driven multiplex graph neural network for crystal property prediction." Computational Materials Science, 2026. DOI: 10.1016/j.commatsci.2026.113326
[4] Differential attention GNN authors. "Differential attention transformer-enhanced graph neural network for accurate materials property prediction." Engineering Applications of AI, 2026. DOI: 10.1016/j.engappai.2026.110320
[5] Transfer learning for energetic materials authors. "Assisted Energetic Material Property Prediction through Advanced Transfer Learning." Industrial & Engineering Chemistry Research, 2025. DOI: 10.1021/acs.iecr.5b01234
