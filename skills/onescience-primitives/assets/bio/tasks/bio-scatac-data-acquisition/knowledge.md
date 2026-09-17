# scATAC-seq数据获取任务

## 适用范围

**触发条件**：
- 任务需要scATAC-seq数据但本地未找到pbmc_atac.h5ad
- 需要从公开数据源下载标准scATAC数据集
- 模拟数据无法替代真实生物学数据

**适用场景**：
- scATAC-seq数据分析任务的s01数据获取阶段
- 需要真实PBMC scATAC数据进行模型训练和评估
- 需要验证数据格式完整性（peak×cell矩阵、细胞类型注释）

**不适用场景**：
- 已有可用的scATAC-seq H5AD文件
- 需要自定义scATAC数据生成（如从FASTQ开始的完整流程）

## 输入

- **数据源要求**：公开可访问的scATAC-seq数据集
- **格式要求**：H5AD（AnnData）格式
- **必需字段**：
  - `X`：peak × cell 稀疏计数矩阵
  - `obs`：细胞元数据，必须包含 `cell_type` 列
  - `var`：特征元数据，必须包含染色体坐标信息

## 输出

- **数据文件**：`pbmc_atac.h5ad` 或等效H5AD文件
- **验证报告**：数据完整性检查结果
- **元数据摘要**：细胞数、peak数、细胞类型分布、批次分布

## 流程节点

### Step 1：确定数据源
- **操作**：检索可用的scATAC-seq公开数据源
- **候选数据源**：
  1. 10x Genomics官网（https://www.10xgenomics.com/resources/datasets）
  2. Zenodo（https://zenodo.org/）搜索"scATAC-seq"
  3. ModelScope（https://modelscope.cn/）搜索scATAC数据
  4. GEO数据库（https://www.ncbi.nlm.nih.gov/geo/）搜索ATAC-seq数据
- **质量门禁**：数据源可访问，数据格式为H5AD

### Step 2：下载数据
- **操作**：使用适当工具下载数据
- **工具**：
  - scanpy.datasets（如内置数据集可用）
  - wget/curl（直接下载）
  - Python requests库
- **参数**：超时设置=300s，重试次数=3
- **质量门禁**：下载成功，文件大小合理（通常>10MB）

### Step 3：验证数据完整性
- **操作**：检查H5AD文件结构和内容
- **检查项**：
  1. 文件可被anndata.read_h5ad加载
  2. X矩阵为稀疏矩阵，shape合理（如>1000 cells, >10000 peaks）
  3. obs包含cell_type列，且非空
  4. var包含染色体坐标信息（#Chromosome, hg38_Start, hg38_End）
  5. 无全零行或全零列
- **质量门禁**：所有检查项通过

### Step 4：生成验证报告
- **操作**：输出数据摘要信息
- **内容**：
  - 细胞总数、peak总数
  - 细胞类型分布（各类型细胞数）
  - 批次分布（如有batch列）
  - 数据稀疏度（非零元素比例）
- **质量门禁**：报告完整，无异常值

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 推荐数据源 | 10x Genomics PBMC scATAC | [1] | 标准测试数据集 |
| 数据格式 | H5AD (AnnData) | [1] | Python单细胞分析标准格式 |
| 最小细胞数 | 1000 | [2] | 确保统计显著性 |
| 最小peak数 | 10000 | [2] | 确保特征空间足够 |
| 稀疏度阈值 | <95%零值 | [2] | 过于稀疏的数据不适合分析 |

## 边界与分流

- **数据源不可访问**：尝试备选数据源，或使用scvi.data内置数据集
- **格式不匹配**：若数据为其他格式（如MTX、BED），需先转换为H5AD
- **数据质量差**：若QC指标不达标，标记BLOCKED并说明原因
- **网络受限**：离线环境下需预先下载数据或使用本地缓存

## 质量检查

- 验证点1：H5AD文件可正常加载，无损坏
- 验证点2：obs包含cell_type列，且有多种细胞类型
- 验证点3：var包含染色体坐标信息
- 验证点4：X矩阵非空，且维度合理

## 回退策略

- **首选**：从10x Genomics下载PBMC scATAC数据
- **备选1**：从Zenodo下载其他scATAC数据集
- **备选2**：使用scanpy.datasets内置数据（如可用）
- **最终方案**：标记BLOCKED，说明无法获取数据的原因

## 资源召回建议

- **召回场景**：当任务需要scATAC-seq数据但本地未找到时
- **配套资源**：
  - ChromFound预训练权重（模型需要scATAC数据作为输入）
  - scATAC-seq预处理流程（TF-IDF归一化）
  - 细胞类型注释评估工具

## 证据来源

[1] 10x Genomics. "10x Genomics Datasets". https://www.10xgenomics.com/resources/datasets, 2023
[2] Stuart, T. et al. "Signac: Analysis of Single-Cell Chromatin Data". Bioconductor, 2024
