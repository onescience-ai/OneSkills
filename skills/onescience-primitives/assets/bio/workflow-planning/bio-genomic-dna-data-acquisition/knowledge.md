# 基因组DNA数据获取路径

## 适用范围

**触发条件**：
- 需要获取真实基因组DNA序列进行功能预测或变异效应分析
- 需要基准数据集评估DNA语言模型性能
- 需要训练数据进行基因组序列建模

**适用场景**：
- DNA语言模型训练和评估
- 基因组功能预测任务
- 变异效应预测和优先级排序
- 长程DNA序列建模

**不适用场景**：
- 无需真实基因组数据的合成序列分析
- 非人类物种的专用基因组数据（需额外验证）

## 输入
- 目标基因组版本：hg38/mm10/其他
- 数据类型：DNA-seq/ATAC-seq/ChIP-seq/变异数据
- 区间范围：特定染色体/基因组区域
- 格式要求：FASTA/BED/VCF/bigWig

## 输出
- 标准化的基因组DNA序列文件
- 功能标签和注释信息
- 数据质量报告和统计信息

## 流程节点
1. 数据源选择 → 2. 数据下载 → 3. 格式转换 → 4. 质量验证

### 步骤1：数据源选择
- **操作**：根据任务需求选择合适的数据源
- **参数**：data_source, genome_version, data_type
- **工具**：ENCODE, UCSC, BEND, Caduceus
- **质量门禁**：数据源权威性，版本一致性

### 步骤2：数据下载
- **操作**：从权威数据源下载基因组数据
- **参数**：download_url, file_format, compression
- **工具**：wget, curl, API调用
- **质量门禁**：文件完整性，下载成功

### 步骤3：格式转换
- **操作**：将下载数据转换为标准格式
- **参数**：input_format, output_format, coordinate_system
- **工具**：bedtools, samtools, custom scripts
- **质量门禁**：格式正确，坐标一致

### 步骤4：质量验证
- **操作**：验证数据质量和完整性
- **参数**：validation_metrics, threshold
- **工具**：Python验证脚本
- **质量门禁**：数据完整，格式正确，坐标有效

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 参考基因组 | hg38 | [1] | 人类参考基因组版本 |
| 数据格式 | FASTA/BED/VCF | [2] | 标准基因组数据格式 |
| 坐标系统 | 0-based/1-based | [2] | 坐标起始位置 |
| 数据来源 | ENCODE/UCSC/BEND | [1][2] | 权威数据源 |

### 校准数值
以下数值来自BEND基准测试数据集，供量级校准；其他数据集需以自身证据重新锚定：
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 人类基因组大小 | ~3.2Gb | [1] | hg38参考基因组 |
| BEND任务数 | 8个 | [1] | 基准测试任务 |
| 序列长度范围 | 1kb-1Mb | [1] | 不同任务的序列长度 |
| 功能标签类型 | 增强子/启动子/变异效应 | [1] | 生物学功能标签 |

## 边界与分流

**关键前提不成立时的改道方案**：
- **前提1：ENCODE/UCSC访问受限**
  - 改道方案：使用BEND基准数据集或Caduceus配套数据
- **前提2：基因组版本不匹配**
  - 改道方案：使用liftOver工具进行坐标转换
- **前提3：数据格式不兼容**
  - 改道方案：使用bedtools/samtools进行格式转换

## 质量检查
- **验证点**：文件完整性、坐标有效性、格式正确性、标签一致性
- **阈值**：文件大小合理，坐标在有效范围内，格式解析成功率100%
- **失败处理**：重新下载或尝试备用数据源

## 回退策略
- 主数据源不可用时：使用镜像源或备用数据源
- 数据格式错误时：使用格式转换工具
- 坐标越界时：检查基因组版本和坐标系统

## 资源召回建议
- 当需要获取真实基因组DNA序列进行建模时召回本卡片
- 配套资源：Caduceus模型、mamba-ssm安装指南、BEND基准测试

## 补充证据
[D1] ENCODE Project, ENCODE, 2024, URL: https://www.encodeproject.org/（accessed 2026-09-16，官方数据源）
[D2] UCSC Genome Browser, UCSC, 2024, URL: https://genome.ucsc.edu/（accessed 2026-09-16，官方数据源）
[D3] BEND GitHub Repository, GitHub, 2024, URL: https://github.com/frederikkemarin/BEND（accessed 2026-09-16，基准数据集）

## 证据来源
[1] Frederikke Isa Marin, Felix Teufel, Marc Horlacher, et al. BEND: Benchmarking DNA Language Models on biologically meaningful tasks. ICLR 2024. arXiv:2311.12570.
[2] Yair Schiff, Chia-Hsiang Kao, Aaron Gokaslan, Tri Dao, Albert Gu, Volodymyr Kuleshov. Caduceus: Bi-Directional Equivariant Long-Range DNA Sequence Modeling. ICML 2024. arXiv:2403.03234.
