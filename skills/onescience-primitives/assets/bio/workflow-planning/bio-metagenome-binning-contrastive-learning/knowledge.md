# 对比学习在宏基因组分箱中的应用

## 适用范围
- **触发条件**：需要从宏基因组contigs中重建微生物基因组（MAGs），且希望利用对比学习提升表征质量。
- **适用场景**：短读长和长读长测序数据；单样本、多样本和共组装分箱模式；复杂微生物群落（如肠道、土壤、海洋）。
- **不适用场景**：当缺乏参考基因组或计算资源有限时；当数据噪声极高且对比学习无法有效收敛时。

## 输入
- **数据格式**：FASTA格式的contigs文件（长度通常>1000 bp）。
- **特征类型**：
  - k-mer频率（通常使用4-mer，136维向量）。
  - 覆盖度信息（多个样本的平均覆盖度和标准差）。
- **预处理要求**：
  - 长度过滤：移除短于阈值（默认1000 bp）的contigs。
  - k-mer计数：使用滑动窗口计算k-mer频率。
  - 覆盖度计算：将reads比对到contigs，计算每个样本的覆盖度。

## 输出
- **产物**：分箱结果（bins），每个bin包含一组contigs，预测来自同一基因组。
- **格式**：TSV或文本文件，每行一个contig ID及其所属bin ID。
- **验证标准**：
  - 使用CheckM/CheckM2评估完整性和污染度。
  - 高质量bins：完整性>90%，污染度<5%。

## 流程节点
1. **数据预处理** → 2. **特征提取** → 3. **对比学习表征** → 4. **聚类分箱** → 5. **质量评估**

### 步骤1：数据预处理
- **操作**：长度过滤、去除低质量contigs。
- **参数**：最短序列长度阈值（默认1000 bp）。
- **工具**：seqtk、BBTools。
- **质量门禁**：确保保留的contigs长度分布合理。

### 步骤2：特征提取
- **操作**：计算k-mer频率和覆盖度特征。
- **参数**：k值（通常为4），覆盖度归一化方法。
- **工具**：jellyfish（k-mer计数）、Bowtie2（比对）、samtools（覆盖度计算）。
- **质量门禁**：特征向量无零值，归一化后范围一致。

### 步骤3：对比学习表征
- **操作**：使用深度学习模型学习contig的低维嵌入。
- **样本对构造**：
  - **正样本对**：同一contig的不同增强视图（如随机裁剪、分割）。
  - **负样本对**：不同contig的视图（随机采样或基于分类注释）。
- **对比损失函数**：
  - **InfoNCE损失**：最大化正样本对相似性，最小化负样本对相似性。
  - **监督对比损失**：使用must-link和cannot-link约束。
- **模型架构**：
  - **SemiBin/SemiBin2**：深度孪生神经网络，输入k-mer和覆盖度特征，输出100维嵌入。
  - **COMEBin**：多视图对比学习，包含覆盖度网络和组合网络。
  - **CLMB**：基于VAMB的变分自编码器，添加噪声增强进行对比学习。
- **训练目标**：使同一基因组的contigs在嵌入空间中聚集，不同基因组的contigs分离。
- **质量门禁**：t-SNE可视化显示嵌入空间中的聚类分离度。

### 步骤4：聚类分箱
- **操作**：基于嵌入向量进行聚类。
- **参数**：聚类算法参数（如DBSCAN的ε值、Leiden的分辨率）。
- **工具**：
  - **短读长数据**：Infomap社区检测算法。
  - **长读长数据**：基于DBSCAN的集成算法。
- **质量门禁**：每个bin中单拷贝标记基因的拷贝数接近1。

### 步骤5：质量评估
- **操作**：使用CheckM/CheckM2评估bins的完整性和污染度。
- **参数**：完整性阈值（>90%），污染度阈值（<5%）。
- **工具**：CheckM、CheckM2、GUNC。
- **质量门禁**：输出高质量bins的统计信息。

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| k-mer大小 | 4 | [SemiBin2] | 4-mer频率提供136维特征向量 |
| 最短序列长度 | 1000 bp | [SemiBin2, COMEBin] | 过滤短序列以提高分箱质量 |
| 嵌入维度 | 100 | [SemiBin2] | 深度学习模型输出维度 |
| 对比损失温度系数 | 0.1 | [COMEBin] | 控制负样本的区分度 |
| 聚类算法 | Infomap（短读长），DBSCAN（长读长） | [SemiBin2] | 适应不同数据类型 |
| 质量阈值 | 完整性>90%，污染度<5% | [CAMI II] | 高质量bins的标准 |

## 边界与分流
- **异常处理**：
  - 如果对比学习收敛困难，可回退到传统分箱方法（如MetaBAT2）。
  - 如果覆盖度信息缺失，可仅使用k-mer特征。
- **降级策略**：
  - 当计算资源不足时，使用预训练模型（如SemiBin1的预训练模型）。
  - 当数据噪声高时，增加数据增强的多样性。
- **分支条件**：
  - 短读长数据使用Infomap聚类。
  - 长读长数据使用集成DBSCAN聚类。

## 质量检查
- **验证点**：
  1. 嵌入空间的分离度（t-SNE可视化）。
  2. 分箱结果的完整性（CheckM评估）。
  3. 跨数据集泛化能力（在多个真实数据集上测试）。
- **阈值**：
  - 完整性 > 90%，污染度 < 5%。
  - 高质量bins数量相比基线方法提升 > 10%。
- **失败处理**：
  - 如果分箱质量不达标，调整模型参数或增加训练数据。

## 回退策略
- **替代方案**：
  - 使用传统分箱工具（如MetaBAT2、MaxBin2）。
  - 使用半监督学习方法（如SemiBin1）。
  - 使用基于覆盖度的分箱方法（如CONCOCT）。
- **降级路径**：
  - 当对比学习模型无法训练时，使用PCA降维特征进行聚类。
  - 当参考数据库不可用时，使用自监督学习（如SemiBin2）。

## 资源召回建议
- **何时召回本卡片**：
  - 需要实现对比学习驱动的宏基因组分箱时。
  - 需要了解CLMB、SemiBin、COMEBin等模型的原理时。
  - 需要设计对比学习样本对构造或损失函数时。
- **配套资源**：
  - `bio-metagenome-binning-evaluation`：分箱评估方法。
  - `bio-metagenome-data-sources`：宏基因组数据获取渠道。
  - `bio-contrastive-learning-principles`：对比学习基础原理。

## 证据来源
[1] Pan et al. (2023). SemiBin2: self-supervised contrastive learning leads to better MAGs for short- and long-read sequencing. Bioinformatics, 39(Supplement_1), i21-i31. DOI: 10.1093/bioinformatics/btad209
[2] Pan et al. (2022). A deep siamese neural network improves metagenome-assembled genomes in microbiome datasets across different environments. Nature Communications, 13, 1464. DOI: 10.1038/s41467-022-29843-y
[3] Wang et al. (2024). Effective binning of metagenomic contigs using contrastive multi-view representation learning. Nature Communications, 15, 2038. DOI: 10.1038/s41467-023-44290-z
[4] Yazhini et al. (2025). Evaluation of metagenome binning: advances and challenges. Briefings in Bioinformatics, 26(6), bbaf617. DOI: 10.1093/bib/bbaf617
[5] Meyer et al. (2022). Critical Assessment of Metagenome Interpretation: the second round of challenges. Nature Methods, 19, 559–564. DOI: 10.1038/s41592-022-01431-4