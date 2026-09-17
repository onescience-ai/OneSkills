# 单细胞RNA-seq数据集公开获取知识

## 适用范围

**触发条件**：
- 任务需要加载H5AD格式单细胞表达矩阵数据
- 需要获取immune_atlas.h5ad或类似免疫细胞图谱数据集
- 数据验证失败，需要定位公开数据源

**适用场景**：
- 单细胞转录组分析、细胞类型注释、扰动响应预测
- 跨数据集整合分析、批次效应校正
- 基础模型训练与评估

**不适用场景**：
- 空间转录组（需要额外空间坐标信息）
- 蛋白质组、代谢组等非RNA数据
- 私有临床数据集（需要机构授权）

## 输入

| 输入项 | 说明 |
|--------|------|
| 数据格式 | H5AD (AnnData)、Loom、Seurat RDS |
| 必要字段 | X/count矩阵、obs细胞元数据、var基因信息 |
| 可选字段 | spatial空间坐标、obsm嵌入、layers表达层 |
| 标识符 | 基因符号/Ensembl ID、细胞类型标签 |

## 输出

| 输出项 | 说明 |
|--------|------|
| 数据文件 | 标准化H5AD文件 |
| 验证报告 | 数据完整性、字段缺失、格式兼容性 |
| 元数据 | 版本标识、下载来源、数据血缘 |

## 流程节点

### 步骤1：数据源定位

**操作**：检索公开单细胞数据库，定位目标数据集

**主要数据源**：

| 数据源 | URL | 特点 | 适用数据类型 |
|--------|-----|------|--------------|
| CZ CELLxGENE | cellxgene.cziscience.com | 最大单细胞数据平台，436+数据集，33M+细胞 | H5AD标准化数据 |
| Human Cell Atlas | data.humancellatlas.org | 官方HCA数据门户 | 多模态单细胞数据 |
| Zenodo | zenodo.org | 学术数据存储库，DOI可追溯 | 各类格式 |
| GEO | ncbi.nlm.nih.gov/geo | NCBI基因表达数据库 | 10X、Smart-seq等 |
| scPerturb | perturbation.broadinstitute.org | 扰动数据集统一格式 | CRISPR筛选数据 |

**免疫细胞图谱常用数据集**：

| 数据集名称 | 来源 | 细胞数 | 描述 |
|------------|------|--------|------|
| 10X PBMC 3k/5k/10k | 10X Genomics | 3k-10k | 外周血单核细胞 |
| PBMC 68k | Zheng et al. | 68k | 外周血68k细胞 |
| Tabula Sapiens | CZ CELLxGENE | 多组织 | 人体多器官图谱 |
| HLCA | CZ CELLxGENE | 多组织 | 人类肺细胞图谱 |

**质量门禁**：
- 确认数据集DOI或版本号
- 检查许可证兼容性（CC0/CC-BY等）
- 记录下载日期和来源URL

### 步骤2：数据下载与格式验证

**操作**：下载数据文件并验证H5AD格式兼容性

**验证检查点**：

| 检查项 | 方法 | 通过标准 |
|--------|------|----------|
| 文件完整性 | MD5/SHA256校验 | 与官方校验值匹配 |
| H5AD可读性 | anndata.read_h5ad() | 无报错加载 |
| X矩阵维度 | adata.X.shape | 细胞数>0，基因数>0 |
| obs字段 | adata.obs.columns | 包含细胞类型/批次标签 |
| var字段 | adata.var.index | 基因标识符有效 |
| 缺失值检查 | adata.X.isnan().sum() | 缺失比例<20% |

**降级策略**：
- H5AD不可用 → 尝试Loom格式
- Loom不可用 → 尝试CSV/TSV矩阵+元数据
- 格式转换 → 使用anndata转换工具

### 步骤3：数据血缘追踪

**操作**：记录数据来源、版本和处理历史

**血缘信息**：

| 字段 | 说明 | 示例 |
|------|------|------|
| source_url | 下载地址 | https://cellxgene.cziscience.com/... |
| doi | 数据集DOI | 10.1016/j.cell.2023.xx |
| version | 数据版本 | v2024-01-15 |
| download_date | 下载日期 | 2026-09-15 |
| preprocessing | 预处理描述 | raw counts, no normalization |
| cell_count | 细胞数量 | 50000 |
| gene_count | 基因数量 | 20000 |

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| H5AD格式 | AnnData >= 0.8 | [1] | 标准单细胞数据格式 |
| 基因标识符 | Gene Symbol 或 Ensembl ID | [1] | 需统一转换 |
| 细胞类型标签 | cell_type 列 | [1] | 必需字段 |
| 批次标签 | batch/donor 列 | [1] | 跨数据集整合必需 |

## 边界与分流

**异常处理**：
- 数据集不可用 → 检查URL是否过期，联系数据库维护者
- 格式不兼容 → 使用转换工具或联系数据提供方
- 许可证限制 → 仅用于学术研究，遵守CC-BY条款

**分支条件**：
- 数据包含空间坐标 → 额外验证spatial字段
- 数据包含多组学 → 验证modality字段一致性
- 数据为扰动数据 → 验证perturbation字段完整性

## 质量检查

| 检查点 | 阈值 | 失败处理 |
|--------|------|----------|
| 文件可读性 | 100% | 重新下载或更换数据源 |
| 字段完整性 | >95% | 记录缺失字段，标注不可用部分 |
| 细胞类型覆盖 | >5种 | 警告细胞类型单一 |
| 基因标识唯一性 | 100% | 去重或使用官方标识符 |

## 回退策略

1. **首选**：从CellxGene下载标准化H5AD
2. **备选**：从GEO下载原始数据，自行转换
3. **兜底**：使用公开示例数据集（如10X PBMC 3k）

## 资源召回建议

**何时召回本卡片**：
- 任务需要加载单细胞数据但数据文件不存在
- 数据验证失败需要定位替代数据源
- 需要获取immune_atlas.h5ad或类似免疫图谱数据

**配套资源**：
- onescience-data-standardizer：数据格式转换
- onescience-data-profile：数据质量检查

## 证据来源

[1] CZ CELLxGENE Discover: a single-cell data platform for scalable exploration, analysis and modeling of aggregated data, Nucleic Acids Research, 2024, DOI: 10.1093/nar/gkae1142

[2] Single-cell multi-omics analysis of the immune response in COVID-19, Nature Medicine, 2021, DOI: 10.1038/s41591-021-01329-2

[3] scPerturb: harmonized single-cell perturbation data, Nature Methods, 2024, DOI: 10.1038/s41592-023-02144-y
