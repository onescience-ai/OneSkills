# 宏基因组数据与模型获取

## 适用范围
- **触发条件**：需要获取真实的宏基因组数据集或预训练模型权重。
- **适用场景**：开发或测试宏基因组分箱工具；进行基准测试；需要真实数据进行验证。
- **不适用场景**：当仅需模拟数据进行快速原型开发时；当网络访问受限时。

## 输入
- **需求描述**：所需数据的类型（短读长/长读长）、来源（环境/宿主）、样本数量。
- **模型需求**：所需模型（CLMB、SemiBin等）、版本、预训练权重。
- **预处理要求**：明确数据格式（FASTQ、FASTA）、质控标准。

## 输出
- **数据**：下载的宏基因组数据集（原始reads或组装contigs）。
- **模型**：预训练权重文件（.pt、.pth等）。
- **元数据**：样本信息、来源、质控报告。

## 流程节点
1. **数据源识别** → 2. **数据下载** → 3. **质控检查** → 4. **模型获取** → 5. **验证与集成**

### 步骤1：数据源识别
- **操作**：根据需求选择合适的数据源。
- **参数**：数据类型、来源环境、样本数量。
- **工具**：Web搜索、数据库查询。
- **质量门禁**：确保数据源权威、数据格式兼容。

### 步骤2：数据下载
- **操作**：从选定的数据源下载数据。
- **参数**：下载工具（wget、aspera）、并行下载数量。
- **工具**：NCBI SRA Toolkit、MGnify下载脚本。
- **质量门禁**：下载完整，无损坏文件。

### 步骤3：质控检查
- **操作**：检查下载数据的质量和完整性。
- **参数**：序列长度分布、碱基质量、污染度。
- **工具**：FastQC、MultiQC。
- **质量门禁**：数据符合质控标准，无异常值。

### 步骤4：模型获取
- **操作**：从官方渠道下载预训练模型权重。
- **参数**：模型版本、框架（PyTorch、TensorFlow）。
- **工具**：git clone、wget、huggingface-cli。
- **质量门禁**：模型文件完整，可正常加载。

### 步骤5：验证与集成
- **操作**：验证数据和模型的可用性。
- **参数**：数据格式验证、模型推理测试。
- **工具**：自定义脚本、单元测试。
- **质量门禁**：数据可用于分箱，模型可正确推理。

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 数据源 | NCBI SRA, MGnify, CAMI | [NCBI, MGnify] | 权威公开数据库 |
| 数据格式 | FASTQ（原始reads），FASTA（contigs） | [标准] | 常见格式 |
| 模型发布渠道 | GitHub, Zenodo, HuggingFace | [SemiBin2] | 官方发布平台 |
| 质控工具 | FastQC, MultiQC | [标准] | 广泛使用的质控工具 |
| 下载工具 | SRA Toolkit, wget, aspera | [NCBI] | 高效下载工具 |

## 边界与分流
- **异常处理**：
  - 如果数据下载失败，尝试替代数据源或联系数据库管理员。
  - 如果模型权重损坏，重新下载或使用校验和验证。
- **降级策略**：
  - 当无法获取真实数据时，使用模拟数据（如CAMISIM生成）。
  - 当官方模型不可用时，使用社区复现版本。
- **分支条件**：
  - 短读长数据优先从NCBI SRA下载。
  - 长读长数据可从MGnify或原始论文补充材料获取。

## 质量检查
- **验证点**：
  1. 数据完整性（文件大小、MD5校验和）。
  2. 模型可加载性（权重文件大小、格式）。
  3. 数据质控报告（FastQC结果）。
- **阈值**：
  - 数据下载成功率 > 99%。
  - 模型加载成功率 100%。
- **失败处理**：
  - 如果数据不可用，记录阻塞原因并标记为BLOCKED。
  - 如果模型不兼容，尝试转换格式或使用兼容版本。

## 回退策略
- **替代方案**：
  - 使用模拟数据（如CAMISIM生成）进行测试。
  - 使用轻量级模型（如预训练的k-mer模型）替代。
  - 使用公开的基准数据集（如CAMI II）进行标准化评估。
- **降级路径**：
  - 当网络受限时，使用本地缓存数据。
  - 当模型过大时，使用模型压缩或量化版本。

## 资源召回建议
- **何时召回本卡片**：
  - 需要获取宏基因组数据集时。
  - 需要下载预训练模型权重时。
  - 需要了解数据质控标准时。
- **配套资源**：
  - `bio-metagenome-binning-contrastive-learning`：对比学习分箱方法。
  - `bio-metagenome-binning-evaluation-benchmark`：分箱评估方法。
  - `bio-metagenome-quality-tools`：质量评估工具使用指南。

## 证据来源
[1] NCBI Resource Coordinators (2015). The NCBI BioSample database: models and ontologies. Database, 2015, bau094. DOI: 10.1093/database/bau094
[2] Richardson et al. (2020). MGnify: the microbiome analysis resource in 2020. Nucleic Acids Research, 48(D1), D570-D578. DOI: 10.1093/nar/gkz1035
[3] Meyer et al. (2022). Critical Assessment of Metagenome Interpretation: the second round of challenges. Nature Methods, 19, 559–564. DOI: 10.1038/s41592-022-01431-4
[4] Pan et al. (2023). SemiBin2: self-supervised contrastive learning leads to better MAGs for short- and long-read sequencing. Bioinformatics, 39(Supplement_1), i21-i31. DOI: 10.1093/bioinformatics/btad209