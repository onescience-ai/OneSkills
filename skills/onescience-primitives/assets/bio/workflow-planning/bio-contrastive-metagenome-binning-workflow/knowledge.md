# 对比学习驱动的宏基因组分箱工作流

## 适用范围
本卡片服务于宏基因组序列分箱任务，即从混合微生物群落测序数据中，将组装得到的contigs按来源基因组分组为MAGs（Metagenome-Assembled Genomes）。适用于需要使用对比学习方法提升分箱表征质量的场景，包括短读长（Illumina mNGS）、长读长（PacBio HiFi/ONT）和混合测序数据。不适用于单细胞宏基因组或直接从reads分箱的场景（需先完成组装）。本卡片为通用方法论框架，适用于各种对比学习分箱工具（如CLMB、COMEBin、SemiBin等），具体实例工具的校准数值需参考各工具的原始论文。

## 输入
- **序列数据**：组装后的contigs（FASTA格式），推荐长度≥1000bp
- **覆盖度数据**：每个contig在各测序样本中的覆盖度（可从BAM文件计算）
- **测序样本数**：M个样本，覆盖度向量维度为2M（均值+标准差）
- **参考数据库**：可选，GTDB等分类学数据库用于评估和辅助分箱

## 输出
- **分箱结果**：contig到bin的分配（TSV/CSV格式）
- **表征向量**：每个contig的低维嵌入表示（用于聚类）
- **MAG质量评估**：使用CheckM2计算的完整性和污染度指标
- **分类注释**：使用GTDB-Tk对MAGs进行分类学注释

## 流程节点

### s01 数据标准化
- **操作**：过滤短序列、质量控制、格式统一
- **参数**：最短序列长度阈值（默认1000bp）
- **工具**：seqkit、BBTools、QUAST
- **质量门禁**：输出contigs长度分布报告，确认短序列已过滤

### s02 模型加载与特征编码
- **操作**：加载预训练模型权重，进行序列分词和特征提取
- **步骤**：
  1. 长度过滤：移除短于阈值的contigs
  2. k-mer分词：将序列转换为k-mer频率向量（通常k=4，维度136）
  3. 覆盖度编码：计算每个contig在各样本中的覆盖度均值和标准差
  4. 参考数据库编码（可选）：使用预训练模型对参考序列进行编码
- **工具**：CLMB/COMEBin/SemiBin内置特征提取模块
- **质量门禁**：验证特征维度正确，无缺失值

### s03 对比学习表征与聚类
- **操作**：使用对比学习模型生成contig嵌入，然后聚类
- **步骤**：
  1. 数据增强：为每个contig生成多个增强视图（随机片段提取/添加噪声）
  2. 对比学习：最大化同一contig不同视图的相似性，最小化不同contig视图的相似性
  3. 表征生成：使用训练好的编码器生成低维嵌入
  4. 聚类分箱：使用Leiden/medoid/DBSCAN等算法进行聚类
- **参数**：批次大小、温度系数τ、增强视图数、聚类分辨率
- **工具**：COMEBin、CLMB、SemiBin2
- **质量门禁**：监控对比损失收敛，验证嵌入质量（t-SNE可视化）

### s04 评估与质量控制
- **操作**：评估分箱质量，进行分类学注释
- **步骤**：
  1. MAG质量评估：使用CheckM2计算完整性和污染度
  2. 分类学注释：使用GTDB-Tk进行分类
  3. 跨物种泛化评估：按物种划分测试集评估泛化能力
  4. 未知类别处理：单独报告未分类bin
- **评估指标**：完整性、污染度、F1-score（bp）、ARI、准确率
- **工具**：CheckM2、GTDB-Tk、AMBER
- **质量门禁**：高质量MAG标准（完整性>90%，污染度<5%，含rRNA和tRNAs）

## 关键参数

### 通用判据（方法层，同类体系可参考）
| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| 最短序列长度 | 1000bp | [1] | 大多数分箱工具的最小输入要求 |
| k-mer大小 | 4 (四核苷酸频率) | [1] | TNF维度136（考虑反向互补） |
| 增强视图数 | 4-6个 | [1] | COMEBin使用6个视图，更多视图可提升性能 |
| 温度系数τ | 0.1-0.3 | [1] | NT-Xent损失函数中的温度参数 |
| 聚类分辨率 | 1-110 | [1] | Leiden算法参数，需多次运行选择最佳 |
| 边缘保留比例 | 50%-100% | [1] | KNN图构建时保留的边比例 |
| 高质量MAG标准 | 完整性>90%, 污染<5% | [2,3] | CAMI II和MIMAG标准 |
| 中等质量MAG标准 | 完整性>50%, 污染<10% | [2,3] | 最低可接受标准 |

### 校准数值（以下数值来自COMEBin/CLMB体系，供量级校准；其他体系需以自身证据重新锚定）
| 参数 | COMEBin值 | CLMB值 | 来源 | 说明 |
|------|-----------|--------|------|------|
| TNF维度 | 136 | 136 | [1] | 四核苷酸频率，k=4 |
| 覆盖度维度 | 2M (M=样本数) | 2M | [1] | 均值+标准差 |
| 最小增强片段长度 | 1000bp | N/A | [1] | COMEBin随机提取≥1000bp片段 |
| 网络结构 | 3层前馈网络 | 3层前馈网络 | [1] | Coverage Network和Combine Network |
| 聚类算法 | Leiden | 迭代medoid | [1] | COMEBin使用Leiden，CLMB使用medoid |
| 最小bin大小 | 200kbp | 200kbp | [1] | 过滤过小bin |

## 边界与分流
- **数据类型分流**：短读长数据使用标准流程；长读长数据推荐SemiBin2的long-read模式；混合数据可获得最佳性能
- **样本数分流**：少于10个样本时，COMEBin/Coverage Network模块可保持性能；超过50个样本时VAMB可能受限于覆盖度维度
- **序列长度分流**：contigs长度<1000bp时应过滤；长度分布异常时检查组装质量
- **计算资源分流**：GPU模式可显著加速对比学习训练；大规模数据（>100万contigs）需考虑内存限制
- **无参考数据库时**：跳过参考数据库编码步骤，仅使用无监督对比学习
- **对比学习收敛失败时**：尝试调整温度系数τ、批次大小或增强策略

## 质量检查
- **特征提取验证**：TNF维度=136，覆盖度维度=2M，无NaN值
- **表征质量验证**：t-SNE可视化应显示不同基因组的contig形成可分离的簇
- **聚类结果验证**：每个bin的contig来自同一基因组的比例（纯度）
- **MAG质量验证**：使用CheckM2评估完整性和污染度
- **评估指标验证**：分箱F1需使用真实参考标签计算，不能使用模拟标签
- **跨物种泛化验证**：在训练集未见过的物种上测试分箱性能

## 回退策略
- **对比学习无法收敛**：回退到非对比学习方法（如VAMB的VAE）
- **GPU内存不足**：使用CPU模式或减小批次大小
- **分箱质量差**：尝试不同参数组合，或使用集成方法（MetaWRAP、MAGScoT）
- **缺乏真实参考标签**：使用CAMI基准数据集进行评估，或标记BLOCKED
- **模型权重不可用**：使用从头训练或公开预训练权重

## 资源召回建议
- 当任务涉及宏基因组序列分箱时召回本卡片
- 配套资源：CAMI基准数据集、CheckM2、GTDB-Tk、COMEBin/CLMB工具
- 相关卡片：如有具体工具的使用指南卡片，可进一步召回

## 补充证据（开源文档/用户自有，可选）
[D1] CAMI Challenge数据集, CAMI Initiative, https://data.cami-challenge.org/, accessed 2026-09-17（交叉验证：与论文[2,3]中的数据集描述一致）
[D2] COMEBin GitHub仓库, https://github.com/CAMI-challenge/COMEBin, accessed 2026-09-17（交叉验证：与论文[1]中的方法描述一致）
[D3] CheckM2文档, https://github.com/chklovski/CheckM2, accessed 2026-09-17（单源参考）
[D4] GTDB-Tk文档, https://github.com/Ecogenomics/GTDBTk, accessed 2026-09-17（单源参考）

## 证据来源
[1] Wang Z, You R, Han H, Liu W, Sun F, Zhu S. Effective binning of metagenomic contigs using contrastive multi-view representation learning. Nature Communications, 2024, 15:585. DOI: 10.1038/s41467-023-44290-z
[2] Meyer F, Fritz A, Deng ZL, et al. Critical Assessment of Metagenome Interpretation: the second round of challenges. Nature Methods, 2022, 19(4):429-440. DOI: 10.1038/s41592-022-01431-4
[3] Han H, Wang Z, Zhu S. Benchmarking metagenomic binning tools on real datasets across sequencing platforms and binning modes. Nature Communications, 2025, 16:2865. DOI: 10.1038/s41467-025-57957-6
[4] Mallawaarachchi V, Wickramarachchi A, Xue H, et al. Solving genomic puzzles: computational methods for metagenomic binning. Briefings in Bioinformatics, 2024, 25(5):bbae372. DOI: 10.1093/bib/bbae372