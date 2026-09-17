# ADMET性质预测完整工作流契约

## 适用范围
适用于SMILES基础模型驱动的ADMET性质预测任务，包括数据准备、模型推理、性质筛选和评估验证。当任务需要从SMILES输入预测ADMET性质，并输出候选分子和AUROC评估时使用此工作流。

## 输入
- **s01输入核验**：标准化SMILES列表（admet_molecules.csv）和模型权重文件（smiles_mamba.pt）
- **s02权重加载**：预训练模型权重文件（.pt格式）和性质条件向量
- **s03分子生成**：标准化SMILES列表和靶点条件，生成1000个候选分子
- **s04性质筛选**：候选分子SDF文件和ADMET性质预测结果

## 输出
- **s01输出**：标准化SMILES列表和靶点条件
- **s02输出**：模型编码的性质条件向量
- **s03输出**：1000个候选分子的SDF文件
- **s04输出**：排序分子集、平均AUROC明细和性质多样性报告

## 流程节点
1. **s01输入核验** → 2. **s02权重加载** → 3. **s03分子生成** → 4. **s04性质筛选**

### s01输入核验
- **操作**：验证输入文件存在性和格式正确性
- **参数**：admet_molecules.csv（SMILES列表），smiles_mamba.pt（模型权重）
- **工具**：文件系统检查，CSV解析，PT文件验证
- **质量门禁**：文件存在，SMILES格式正确，无缺失值

### s02权重加载
- **操作**：加载预训练模型权重，编码性质条件向量
- **参数**：模型架构（如DCPM-ADMET的XLNet+GRU双组件），预训练权重
- **工具**：PyTorch模型加载，条件向量编码
- **质量门禁**：模型加载成功，条件向量维度正确

### s03分子生成
- **操作**：基于条件生成候选分子，输出SDF格式
- **参数**：生成数量（1000个），采样参数，温度控制
- **工具**：分子生成模型（如REINVENT），RDKit SDF写入
- **质量门禁**：生成1000个分子，SMILES有效性，化学合法性校验

### s04性质筛选
- **操作**：计算AUROC，应用QED/SA筛选，生成评估报告
- **参数**：AUROC计算方法，QED阈值（≥0.6），SA阈值（≤6）
- **工具**：scikit-learn AUROC计算，RDKit QED/SA计算
- **质量门禁**：平均AUROC计算正确，筛选后分子满足QED/SA阈值

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 分子生成数量 | 1000 | [1] | 标准ADMET预测任务要求 |
| QED阈值 | ≥0.6 | [1] | 药物样性筛选标准 |
| SA阈值 | ≤6 | [1] | 合成可及性筛选标准 |
| AUROC计算 | ROC-AUC | [2] | 分类任务主要评估指标 |
| 数据划分 | scaffold split | [3] | TDC标准划分方法 |
| 模型架构 | XLNet+GRU双组件 | [1] | DCPM-ADMET架构 |
| 指纹类型 | ECFP | [1] | 分子子结构特征编码 |

## 边界与分流
- **输入文件缺失**：执行公开数据获取fallback（如从PubChem、ChEMBL下载）
- **模型权重不可用**：使用替代预训练模型或从头训练
- **生成分子不足**：调整生成参数或使用不同采样策略
- **AUROC计算失败**：检查标签分布，处理类别不平衡

## 质量检查
- **验证点**：s04输出包含排序分子集、平均AUROC明细和性质多样性报告
- **阈值**：平均AUROC > 0.7（良好预测性能）
- **失败处理**：重新检查数据质量，调整模型参数，验证评估代码

## 回退策略
- **公开数据获取**：从PubChem、ChEMBL、TDC下载标准数据集
- **替代模型**：使用MoleculeNet基准中的其他预训练模型
- **简化评估**：仅计算核心ADMET端点的AUROC

## 资源召回建议
- **何时召回**：当任务涉及SMILES输入、ADMET性质预测、分子生成和性质筛选时
- **配套资源**：
  - ADMET数据集：TDC ADMET Benchmark Group
  - 预训练模型：DCPM-ADMET、KPGT、Mole-BERT
  - 评估工具：scikit-learn、RDKit、DeepChem

## 证据来源
[1] Zhang L, et al. DCPM-ADMET: fusion of dual-component pre-trained model and molecular fingerprints to enhance drug ADMET properties prediction. J Cheminform. 2026;18:126. DOI: 10.1186/s13321-026-01244-z
[2] Dhir R, et al. AI-driven computational drug design: tools, workflow and challenges. RSC Adv. 2026;16:37397-37422. DOI: 10.1039/d6ra02374f
[3] Koleiev I, et al. An End-User Audit of Reproducibility, Data Leakage, and Overfitting of the Top-Ranked ADMET Prediction Models in TDC Leaderboards. J Chem Inf Model. 2026;66:8045-8058. DOI: 10.1021/acs.jcim.6c00819