# 抗体-抗原亲和力预测特征工程

## 适用范围
基于序列的抗体-抗原亲和力预测特征工程，适用于从抗体和抗原氨基酸序列中提取特征以预测结合亲和力。适用于缺乏结构信息的序列数据，可应用于治疗性抗体设计、疫苗工程和抗体筛选。

## 输入
- **序列数据**：抗体轻链、重链和抗原的氨基酸序列（FASTA格式）
- **亲和力标签**：结合自由能（ΔG）或解离常数（KD）
- **突变信息**：突变位点和突变类型（可选）
- **数据集**：SAbDab（自然抗体）、AB-Bind（突变体）、SKEMPI 2.0（蛋白质复合物突变）

## 输出
- **特征向量**：多维特征向量，包含语义特征和残基特征
- **预测亲和力**：预测的ΔG值（kcal/mol）
- **特征重要性**：各特征对预测的贡献度（可选）

## 流程节点
1. **序列预处理** → 标准化序列格式，分离轻链、重链和抗原序列
2. **语义特征提取** → 使用预训练语言模型（如ProteinBERT）编码序列
3. **残基特征提取** → 从AAindex数据库提取理化性质特征
4. **特征融合** → 结合语义特征和残基特征
5. **模型训练** → 使用CNN和MLP进行特征学习和亲和力预测
6. **性能评估** → 计算RMSE、Pearson相关系数等指标

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 语义特征维度 | 768维 | [1] | ProteinBERT编码的向量长度 |
| 残基特征维度 | 20维 | [1] | AAindex1的544个理化指数经PCA降维 |
| 序列标准化长度 | 可变 | [1] | 训练时使用最长序列长度，测试时截断或填充 |
| 特征融合权重 | ω1, ω2 | [1] | CNN和MLP输出的加权平均 |
| 训练优化器 | SAM优化器 | [1] | 带SGD动量的SAM优化器 |
| 学习率 | 0.0001 | [1] | 初始学习率，训练过程中衰减 |
| 正则化 | L1正则化（0.0001）| [1] | 防止过拟合 |

## 边界与分流
- **结构信息可用**：可结合结构特征（如界面残基距离）提升性能
- **序列长度过长**：可能需要分段处理或使用注意力机制
- **数据不平衡**：自然抗体和突变体数据分布差异，需分别训练或使用迁移学习
- **低同源性序列**：预训练模型可能无法有效提取特征，需微调或使用领域特定模型

## 质量检查
- **特征完整性**：确保所有序列都成功提取特征
- **特征相关性**：检查特征与亲和力标签的相关性
- **模型性能**：验证RMSE和Pearson相关系数达到预期水平
- **泛化能力**：在独立测试集上评估模型性能

## 回退策略
- **序列特征不足**：可结合结构特征或使用更复杂的模型架构
- **数据量不足**：可使用迁移学习或数据增强技术
- **计算资源限制**：可使用轻量级模型或特征选择减少维度

## 资源召回建议
- **何时召回本卡片**：当任务涉及抗体亲和力预测、特征工程或序列分析时
- **配套资源**：
  - ANARCI抗体编号工具
  - 抗体结构预测工具（如AlphaFold2）
  - 抗体数据库（如SAbDab、IMGT）
  - 预训练蛋白质语言模型（如ProteinBERT、ESM-2）

## 证据来源
[1] Li M, Shi Y, Hu S, et al. MVSF-AB: accurate antibody–antigen binding affinity prediction via multi-view sequence feature learning. Bioinformatics. 2024;40(6):btae579. DOI: 10.1093/bioinformatics/btae579
[2] Yoshida M, Oda M. Affinity Maturation for Antibody Engineering: The Critical Role of Residues on CDR Loops of Antibodies in Antigen Binding. Molecules. 2025;30(3):532. DOI: 10.3390/molecules30030532
[3] Yang YX, Wang P, Zhu BT. Binding affinity prediction for antibody–protein antigen complexes: A machine learning analysis based on interface and surface areas. J Mol Graph Model. 2023;118:108364. DOI: 10.1016/j.jmgm.2022.108364