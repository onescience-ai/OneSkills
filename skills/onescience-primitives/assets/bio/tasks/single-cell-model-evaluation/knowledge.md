# 单细胞基础模型综合评测方法

## 适用范围
适用于对Geneformer、scGPT等单细胞基础模型进行全面评测的场景，包括细胞类型分类、扰动预测、空间结构保持性、跨模态一致性、注意力可解释性等多维度评估。

## 输入
- 待评测的单细胞基础模型（Geneformer/scGPT/GFCAB等）
- 评测数据集（测试集或独立验证集）
- 评测维度配置（分类/扰动/空间/跨模态/可解释性）
- 统计检验参数（样本量、显著性水平）

## 输出
- 多维度评测报告（各指标数值、置信区间、统计检验结果）
- 可视化结果（UMAP、热图、注意力图）
- 模型比较排名和结论

## 流程节点
1. 评测维度选择 → 2. 基准数据集准备 → 3. 指标计算 → 4. 统计检验 → 5. 结果解释

### 1. 评测维度选择
根据任务需求选择评测维度：

| 评测维度 | 适用场景 | 核心指标 | 参考基准 |
|----------|---------|----------|---------|
| 细胞类型分类 | 通用能力验证 | Accuracy, F1, AUC | Tabula Sapiens, Immune 330K [2] |
| 扰动预测 | 因果推理能力 | Cosine similarity, Wilcoxon p-value | Perturbation benchmarks [4] |
| 空间结构保持 | 空间转录组适用性 | Spatial autocorrelation, Moran's I | Spatial datasets [3] |
| 跨模态一致性 | 多组学整合能力 | Correlation between modalities | CITE-seq, SHARE-seq |
| 注意力可解释性 | 生物学可解释性 | GRN recovery, Attention scores | Curated GRN databases [1] |
| 零样本泛化 | 迁移学习能力 | Batch mixing, OOD accuracy | Cross-dataset benchmarks [2] |

### 2. 基准数据集准备
**分类任务数据集**：
- **Tabula Sapiens**：人类多组织单细胞图谱，59种细胞类型，9种组织 [2]
- **Immune 330K**：330K免疫细胞，用于批次整合评估 [2]
- **Pancreas 16K**：胰腺细胞，16K细胞用于零样本评估 [2]
- **PBMC 12K**：外周血单核细胞 [2]

**扰动预测数据集**：
- **Perturbation benchmarks**：大规模扰动数据集，包含基因敲除/激活后的细胞状态变化 [4]
- **COP1 KO microglia**：COP1基因敲除小胶质细胞数据 [1]
- **Diabetic nephropathy**：糖尿病肾病单细胞数据 [1]

**空间转录组数据集**：
- 包含空间坐标的单细胞数据（Visium, MERFISH, STARmap等）
- 需验证细胞在空间坐标上的邻近关系保持

### 3. 指标计算

**3.1 细胞类型分类指标**：
- **Accuracy**：整体分类准确率
- **Macro F1**：各类别F1的宏平均（处理类别不平衡）
- **Weighted F1**：按类别权重的F1
- **AUC**：ROC曲线下面积（多分类使用macro-averaging）[2]

**3.2 扰动预测指标**：
- **Cosine Similarity**：扰动前后细胞状态向量的余弦相似度 [1]
- **Wilcoxon Rank Sum Test**：比较扰动组与对照组的统计显著性 [1]
- **Perturbation Accuracy**：预测扰动目标基因的准确率
- **In Silico Perturbation Score**：模拟基因敲除/激活后细胞状态变化的量化

**3.3 空间结构保持指标**：
- **Moran's I**：空间自相关指数，衡量细胞在空间坐标上的聚集程度
- **Geary's C**：空间异质性指数
- **Spatial Silhouette Score**：基于空间坐标的轮廓系数

**3.4 跨模态一致性指标**：
- **Pearson/Spearman Correlation**：不同组学数据间的相关性
- **Canonical Correlation Analysis (CCA)**：典型相关分析得分
- **Integration Score**：批次整合质量（ASWbatch, GraphCon）[2]

**3.5 注意力可解释性指标**：
- **GRN Recovery Rate**：注意力权重恢复已知基因调控网络的准确率 [1]
- **Attention Entropy**：注意力分布的熵值（衡量注意力集中度）
- **Perturbation-target Prediction**：注意力分数预测扰动目标基因的能力 [1]

### 4. 统计检验
- **样本量要求**：单细胞分析通常需要数百个细胞的样本量
- **显著性水平**：α=0.05，使用Bonferroni校正多重检验
- **效应量报告**：Cohen's d（标准化效应量）
- **置信区间**：95% CI用于结果可靠性评估
- **配对检验**：使用Wilcoxon signed-rank test比较模型间差异 [2]

### 5. 结果解释
- **多维度综合评分**：AvgScore = 0.6×AvgBIO + 0.4×AvgBatch [2]
- **模型排名**：基于综合评分的模型比较
- **局限性说明**：明确标注数据规模、物种、组织特异性等限制

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 分类任务交叉验证 | 10次独立运行 | [2] | 减少随机性 |
| 扰动预测显著性 | Wilcoxon p<0.05 | [1] | 统计显著性 |
| 批次整合评估 | ASWbatch + GraphCon | [2] | 零样本评估 |
| 综合评分权重 | 0.6×BIO + 0.4×Batch | [2] | 平衡生物学与技术 |
| 注意力GRN恢复 | 已知GRN数据库 | [1] | 可解释性验证 |

## 边界与分流
- **无空间坐标数据**：跳过空间结构保持性评测
- **无多组学数据**：跳过跨模态一致性评测
- **无已知GRN**：使用文献报道的GRN或跳过可解释性评测
- **样本量不足**：增加数据量或使用bootstrap重采样

## 质量检查
- 确认所有评测维度均有对应数据集
- 验证指标计算的正确性（复现论文结果）
- 检查统计检验的假设条件（正态性、独立性）
- 确认可视化结果的可读性和准确性

## 回退策略
- 若某维度数据不可用，使用其他维度的评测结果
- 若统计检验不显著，增加样本量或使用非参数检验
- 若模型间差异无统计学意义，报告"无显著差异"而非强行排名

## 资源召回建议
- 需要评测单细胞模型时召回本卡
- 配套使用：single-cell-foundation-model-weights（模型权重）、single-cell-rna-seq-dataset-access（数据获取）

## 证据来源
[1] Kendiukhov I. Systematic evaluation of single-cell foundation model interpretability: attention-derived edge scores add no incremental value over gene-level features for perturbation-target prediction. BMC Genomics, 2026, DOI: 10.1186/s12864-026-12965-8
[2] De Waele G et al. A systematic assessment of single-cell language model configurations. NAR Genomics and Bioinformatics, 2026, DOI: 10.1093/nargab/lqag095
[3] Chen J et al. Assessing scale and predictive diversity in models for single-cell transcriptomics based on Geneformer. PLOS Computational Biology, 2026, DOI: 10.1371/journal.pcbi.1013701
[4] Chevalley M et al. A large-scale benchmark for network inference from single-cell perturbation data. Communications Biology, 2025, DOI: 10.1038/s42003-025-07764-y
