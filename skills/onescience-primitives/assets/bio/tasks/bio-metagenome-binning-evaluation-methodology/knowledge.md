# 宏基因组分箱评估方法

## 适用范围
本卡片服务于宏基因组分箱结果的标准化评估任务。适用于需要验证分箱性能真实性和跨物种泛化能力的场景，包括：使用真实参考标签计算分箱F1-score、在不同物种上测试泛化能力、处理未注释的未知类别。不适用于仅需快速原型验证的场景（可使用模拟标签进行初步检查），也不适用于非分箱类的宏基因组分析评估。

## 输入
- **分箱结果**：contig到bin的分配（TSV/CSV格式，含contig_id和bin_id列）
- **参考标签**：每个contig的真实物种标签或基因组来源（TSV/CSV格式，含contig_id和species/genome_id列）
- **参考数据集**：已知分箱的基准数据集（如CAMI II marine/gut dataset）
- **序列数据**（可选）：原始contigs FASTA，用于计算bp-level指标

## 输出
- **分箱质量指标**：F1-score（宏平均/微平均）、ARI、V-measure、Completeness、Purity
- **MAG质量评估**：CheckM2计算的完整性和污染度
- **跨物种泛化报告**：按物种划分的性能分析
- **评估可视化**：混淆矩阵、物种级别性能热图

## 流程节点

### s01 参考标签准备
- **操作**：准备真实的物种标签或基因组来源标签
- **关键原则**：
  - **禁止使用模拟标签**：评估必须使用真实参考标签（来自已知基因组的模拟数据集或已注释的真实数据）
  - 标签格式：每行一个contig，包含contig_id和对应的species/genome_id
  - 标签来源：CAMI基准数据集自带真实标签；真实数据需通过GTDB-Tk或其他分类工具获取
- **工具**：CAMI数据集下载、GTDB-Tk分类注释
- **质量门禁**：参考标签覆盖率≥90%（即≥90%的contig有对应标签）
- **I/O契约**：输入分箱结果+参考标签 → 输出对齐后的标签对

### s02 分箱F1-score计算
- **操作**：基于真实参考标签计算分箱F1-score
- **计算原理**：
  1. **逐bin匹配**：对每个预测bin，找到与其重叠最大的参考物种（最近邻匹配）
  2. **TP/FP/FN计算**：
     - TP：预测bin中属于匹配参考物种的碱基数
     - FP：预测bin中不属于任何匹配参考物种的碱基数
     - FN：参考物种中未被预测bin覆盖的碱基数
  3. **Precision = TP / (TP + FP)**，**Recall = TP / (TP + FN)**
  4. **F1 = 2 * Precision * Recall / (Precision + Recall)**
- **宏平均 vs 微平均**：
  - 宏平均：对所有参考物种分别计算F1后取平均（各物种权重相同）
  - 微平均：汇总所有TP/FP/FN后统一计算F1（大物种权重更高）
- **bp-level vs contig-level**：
  - bp-level：以碱基对为单位计算（更精确，推荐）
  - contig-level：以contig为单位计算（简单但可能不精确）
- **工具**：AMBER（https://github.com/rhysin/amber）、metaWRAP的`quantifyBinning.sh`
- **质量门禁**：分箱F1宏平均应>0.5（中等质量），>0.7为高质量

### s03 MAG质量评估
- **操作**：使用CheckM2评估每个bin的完整性和污染度
- **步骤**：
  1. 将每个bin的contigs合并为 fasta 文件
  2. 运行CheckM2 predict：`checkm2 predict -x fasta -t <threads> -o output <bin_dir>`
  3. 提取完整性和污染度指标
- **质量标准**（MIMAG标准）：
  - 高质量MAG：完整性>90%，污染度<5%，含rRNA和tRNAs
  - 中等质量MAG：完整性>50%，污染度<10%
  - 低质量MAG：完整性<50%或污染度>10%
- **工具**：CheckM2（https://github.com/chklovski/CheckM2）
- **质量门禁**：高质量MAG占比应>30%（对于复杂环境样本）

### s04 跨物种泛化评估
- **操作**：按物种划分测试集，评估分箱方法在未见物种上的泛化能力
- **设计方法**：
  1. **物种划分**：将参考数据集按物种分为训练集和测试集（如70%/30%）
  2. **训练集物种**：用于训练对比学习模型或参数调优
  3. **测试集物种**：模型未见过的物种，用于评估泛化能力
  4. **性能对比**：比较训练集物种和测试集物种上的F1差异
- **泛化性判据**：
  - F1下降<10%：泛化性良好
  - F1下降10%-30%：泛化性一般
  - F1下降>30%：泛化性差，需要更多训练数据或改进方法
- **工具**：自定义脚本（基于scikit-learn的train_test_split）
- **质量门禁**：测试集应包含≥3个不同物种

### s05 未知类别处理
- **操作**：识别和报告无法归类到已知物种的contigs
- **处理规则**：
  1. **单独成bin**：将低置信度的contigs分配到"unknown" bin
  2. **置信度阈值**：使用分箱工具的置信度分数过滤低质量分配（如置信度<0.5的contigs标记为unknown）
  3. **单独报告**：在评估报告中单独列出unknown类别占比
  4. **不强制归类**：不将unknown contigs强行归入已知物种bin
- **工具**：自定义脚本
- **质量门禁**：unknown类别占比<30%为可接受

## 关键参数

### 通用判据（方法层，同类体系可参考）
| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| 参考标签覆盖率 | ≥90% | [2] | 评估结果的可信度依赖于标签覆盖率 |
| 分箱F1宏平均阈值 | >0.5（中等）, >0.7（高质量） | [2,3] | CAMI II标准 |
| 高质量MAG标准 | 完整性>90%, 污染<5% | [2,3] | MIMAG标准 |
| 中等质量MAG标准 | 完整性>50%, 污染<10% | [2,3] | 最低可接受标准 |
| 泛化性F1下降阈值 | <10%（良好）, <30%（一般） | [1] | 跨物种泛化判据 |
| unknown类别上限 | <30% | [1] | 过高说明分箱质量差 |
| 评估数据集 | CAMI II marine/gut | [2,3] | 标准基准数据集 |

### 校准数值（以下数值来自CAMI II基准测试，供量级校准；其他体系需以自身证据重新锚定）
| 参数 | CAMI II值 | COMEBin值 | 来源 | 说明 |
|------|-----------|-----------|------|------|
| 宏平均F1（最佳工具） | 0.64 | 0.73 | [1,2] | CAMI II最佳工具vs COMEBin |
| 完整性（高质量bin） | >90% | >90% | [2] | 一致标准 |
| 污染度（高质量bin） | <5% | <5% | [2] | 一致标准 |
| ARI（最佳工具） | 0.78 | 0.85 | [1,2] | 调整兰德指数 |
| V-measure | 0.72 | 0.80 | [1,2] | 同质性×完整性调和平均 |

## 边界与分流
- **无真实参考标签时**：使用CAMI基准数据集进行评估；如无法获取，标记BLOCKED并说明原因
- **模拟数据评估限制**：使用模拟数据时，应基于已知分箱的模拟数据集（如CAMISIM生成），并明确标注
- **跨物种泛化不可行时**：当数据集物种多样性不足时，改为报告物种内性能而非泛化性能
- **CheckM2不可用时**：使用CheckM（旧版）或GUNC作为替代评估工具
- **评估指标选择**：优先使用bp-level F1-score，contig-level作为补充

## 质量检查
- **参考标签验证**：检查标签覆盖率、标签一致性（同一contig不应有多个标签）
- **F1计算验证**：确保TP+FP+FN等于总碱基数
- **MAG质量验证**：CheckM2结果应包含完整性和污染度两项指标
- **跨物种验证**：测试集物种应与训练集物种无重叠
- **评估报告完整性**：报告应包含所有评估指标、可视化和物种级别分析

## 回退策略
- **无真实参考标签**：使用CAMI基准数据集；如无法获取，标记BLOCKED
- **CheckM2安装失败**：使用CheckM（`checkm lineage_wf`）作为替代
- **评估指标异常**：检查参考标签格式、contig ID匹配、碱基计数
- **跨物种泛化不可行**：改为物种内性能评估，或使用留一法交叉验证

## 资源召回建议
- 当任务涉及宏基因组分箱结果评估时召回本卡片
- 配套资源：`bio-metagenome-contrastive-learning-implementation`（分箱实现）、`bio-metagenome-data-model-sources`（数据获取）、`bio-contrastive-metagenome-binning-workflow`（工作流规划）
- 相关工具：AMBER、CheckM2、GTDB-Tk、metaWRAP

## 证据来源
[1] Han H, Wang Z, Zhu S. Benchmarking metagenomic binning tools on real datasets across sequencing platforms and binning modes. Nature Communications, 2025, 16:2865. DOI: 10.1038/s41467-025-57957-6
[2] Fritz A, Deng ZL, Hunt M, et al. Critical Assessment of Metagenome Interpretation: the second round of challenges. Nature Methods, 2022, 19(4):429-440. DOI: 10.1038/s41592-022-01431-4
[3] Meyer F, Robertson G, Deng ZL, et al. CAMI Benchmarking Portal: online evaluation and ranking of metagenomic software. Nucleic Acids Research, 2025. DOI: 10.1093/nar/gkaf369
[4] Yue Y, Huang H, Qi Z, et al. Evaluating metagenomics tools for genome binning with real metagenomic datasets and CAMI datasets. BMC Bioinformatics, 2020, 21:300. DOI: 10.1186/s12859-020-03667-3
