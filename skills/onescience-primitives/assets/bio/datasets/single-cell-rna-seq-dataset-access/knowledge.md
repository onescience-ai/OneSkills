# 单细胞RNA-seq公开数据集获取方法

## 适用范围
适用于需要获取单细胞RNA-seq数据集（特别是H5AD格式）进行下游分析、模型训练或基准评测的场景。包括免疫细胞图谱、癌症单细胞图谱、发育图谱等公开数据集的检索、下载与预处理。

## 输入
- 目标数据集名称或描述（如"immune atlas"、"cancer scRNA-seq"）
- 目标物种（human/mouse/zebrafish等）
- 数据格式要求（H5AD为标准格式）
- 质量控制参数阈值

## 输出
- 下载的H5AD文件，包含基因表达矩阵、细胞元数据（细胞类型、供体、批次等）、基因标识符
- 质量控制报告（过滤前后细胞数、保留率）
- 数据血缘记录（原始来源、版本、处理步骤）

## 流程节点
1. 数据检索 → 2. 数据下载 → 3. 格式验证 → 4. 质量控制 → 5. 标准化输出

### 1. 数据检索
- **主要门户**：
  - **CZ CELLxGENE Discover**（https://cellxgene.cziscience.com）：Chan Zuckerberg Initiative维护，提供标准化H5AD格式数据集集合（collections），支持按物种、组织、疾病筛选 [1]
  - **GEO**（Gene Expression Omnibus, https://www.ncbi.nlm.nih.gov/geo/）：NCBI维护，提供原始和处理后的单细胞数据，常用accession号如GSE115978、GSE123814 [2]
  - **Zenodo**（https://zenodo.org）：CERN维护，用于存储处理后的数据副本和分析脚本，支持DOI永久标识 [2]
  - **Broad Institute Single Cell Portal**（https://singlecell.broadinstitute.org）：提供多种格式的单细胞数据下载 [2]
  - **PanglaoDB**、**Single Cell Expression Atlas**、**ENCODE**、**10x Genomics**等补充来源 [3]
- **检索策略**：按物种、组织类型、疾病模型、测序平台组合筛选

### 2. 数据下载
- H5AD格式文件直接下载或通过API获取
- 大型数据集可能提供RDS（Seurat）、CSV、loom等替代格式
- 部分数据集提供pseudobulk汇总版本以减少存储和计算需求 [2]

### 3. 格式验证
- 验证H5AD文件可读性（scanpy.read_h5ad）
- 检查必要字段完整性：
  - `adata.X`：基因表达矩阵（cells × genes）
  - `adata.obs`：细胞元数据（cell type, donor, batch, condition等）
  - `adata.var`：基因元数据（gene symbols, Ensembl IDs）
  - `adata.obsm`：可选的空间坐标或嵌入

### 4. 质量控制
基于文献报道的标准QC流程 [2][3]：
- **线粒体基因比例**：过滤线粒体RNA表达超过总表达3个标准差的细胞；阈值通常<20% [2]
- **核糖体基因比例**：保留核糖体RNA表达>5%的细胞 [2]
- **基因检测数**：排除每细胞检测基因数<7的细胞（ambient RNA或空液滴）[3]
- **总表达量**：排除每细胞总表达>20,000的细胞（可能为doublets）[3]
- **Doublet检测**：使用DoubletFinder等工具识别并移除doublets [2]
- **最小细胞数**：每个患者/样本保留至少20个目标细胞 [2]

### 5. 标准化输出
- 统一基因标识符（Ensembl ID → Gene Symbol映射）
- 使用hSEGs（stably expressed genes）进行批次效应校正 [2]
- 生成处理后的AnnData对象，保存为H5AD格式

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 线粒体阈值 | <20% | [2] | PercentageFeatureSet计算 |
| 核糖体阈值 | >5% | [2] | 保留有活性的细胞 |
| 最小基因数 | >7 genes/cell | [3] | 排除空液滴 |
| 最大总表达 | <20,000 | [3] | 排除doublets |
| 最小细胞数 | ≥20 cells/patient | [2] | 保证统计可靠性 |

## 边界与分流
- **数据不可用**：若目标数据集未在公开门户发布，需联系原始作者或使用替代数据集
- **格式不兼容**：非H5AD格式数据需使用scanpy/anndata转换工具适配
- **批次效应严重**：多个数据集合并时需使用Harmony、scVI等批次校正方法
- **细胞类型注释不一致**：不同研究的细胞类型命名可能不同，需统一本体映射

## 质量检查
- 验证H5AD文件完整性（可读、维度一致）
- 检查细胞元数据字段完整性（cell type, batch, condition均有值）
- 确认基因标识符唯一性（无重复gene symbols）
- 统计过滤前后细胞数和基因数变化

## 回退策略
- 若CellxGene不可用，优先尝试GEO或Zenodo
- 若H5AD格式不可获取，使用loom或RDS格式并转换
- 若QC后细胞数不足，放宽QC阈值或使用替代数据集

## 资源召回建议
- 需要获取单细胞数据集时召回本卡
- 配套使用：single-cell-foundation-model-weights（模型权重获取）、single-cell-model-evaluation（模型评测）

## 证据来源
[1] Hall GT. Portable-CELLxGENE: standalone executables of CELLxGENE for easy installation. Gigabyte, 2025, DOI: 10.46471/gigabyte.151
[2] Gondal MN et al. Integrated cancer cell-specific single-cell RNA-seq datasets of immune checkpoint blockade-treated patients. Scientific Data, 2025, DOI: 10.1038/s41597-025-04381-6
[3] Ito K et al. Mouse-Geneformer: A deep learning model for mouse single-cell transcriptome and its cross-species utility. PLOS Genetics, 2025, DOI: 10.1371/journal.pgen.1011420
