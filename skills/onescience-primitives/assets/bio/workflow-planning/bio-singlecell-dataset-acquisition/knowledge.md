# 单细胞RNA-seq数据集公开获取流程

## 适用范围
面向单细胞转录组分析任务，从公开数据平台获取标准化H5AD格式数据集。适用于需要免疫细胞图谱（immune atlas）、组织图谱或跨疾病比较数据的研究场景。

## 输入
- 目标数据集名称或描述（如"immune_atlas.h5ad"、"人类免疫细胞图谱"）
- 目标物种（人/小鼠）
- 所需细胞类型或组织类型

## 输出
- H5AD格式数据文件（包含基因表达矩阵、细胞元数据、基因标识符）
- 数据集元信息（版本、来源、数据血缘）

## 流程节点

### 1. 数据源选择
根据研究需求选择合适的数据平台：

| 平台 | 特点 | 适用场景 |
|------|------|----------|
| **CZ CELLxGENE** | 33M+ cells, 436 datasets, 2.7K+ cell types | 标准化单细胞数据、跨研究比较 |
| **Human Cell Atlas (HCA)** | 多组织图谱、高质量注释 | 组织特异性研究 |
| **Single Cell Expression Atlas (SCEA)** | EBI维护、集成分析 | 跨物种比较 |
| **Gene Expression Omnibus (GEO)** | 原始数据存储 | 特定研究数据 |

### 2. 数据检索与下载
以CZ CELLxGENE为例：
1. 访问 https://cellxgene.cziscience.com/
2. 使用搜索功能查找目标数据集（如"immune atlas"）
3. 进入数据集详情页，查看细胞数量、细胞类型、组织类型
4. 点击"Download"按钮，选择H5AD格式下载

### 3. 文件完整性验证
下载后执行以下检查：
```python
import scanpy as sc
adata = sc.read_h5ad("immune_atlas.h5ad")
# 检查必要字段
assert "X" in adata.obsm or adata.X is not None  # 表达矩阵
assert "cell_type" in adata.obs or "cell_ontology_class" in adata.obs  # 细胞类型注释
assert adata.n_vars > 0  # 基因数量
assert adata.n_obs > 0  # 细胞数量
```

### 4. 数据血缘追踪
记录以下元信息：
- 数据集DOI或访问号
- 下载日期
- 原始出版物引用
- 数据版本（如有）

## 关键参数

### 数据集选择判据
| 参数 | 推荐值 | 说明 |
|------|--------|------|
| 细胞数量 | >10,000 | 统计检验样本量要求 |
| 细胞类型数量 | >5 | 支持跨类型比较 |
| 基因数量 | >20,000 | 覆盖主流基因集 |
| 数据质量 | QC通过率>90% | 低双联体/低死亡细胞比例 |

### H5AD格式核心字段
| 字段 | 位置 | 必需 | 说明 |
|------|------|------|------|
| 表达矩阵 | adata.X / adata.obsm | 是 | 原始计数或标准化值 |
| 细胞元数据 | adata.obs | 是 | 细胞类型、供体、批次等 |
| 基因元adata.var | 是 | 基因名称、Ensembl ID |
| 嵌入坐标 | adata.obsm | 否 | UMAP/t-SNE坐标 |

## 边界与分流

### 异常处理
- **数据集不存在**：尝试替代数据集（如Tabula Sapiens替代特定组织图谱）
- **格式不兼容**：使用anndata转换工具（如scanpy.external）进行格式转换
- **下载失败**：检查网络连接，尝试镜像站点或API下载

### 降级策略
- 优先使用CZ CELLxGENE（标准化程度最高）
- 次选HCA Data Portal（数据质量高但格式多样）
- 最后考虑GEO（原始数据，需自行处理）

## 质量检查

### 数据完整性检查
1. 文件大小检查（>10MB为合理范围）
2. H5AD格式可读性（scanpy可正常加载）
3. 必要字段存在性（表达矩阵、细胞注释）
4. 维度一致性（细胞数×基因数矩阵完整）

### 生物学合理性检查
1. 细胞类型分布合理（无过度代表的类型）
2. 基因表达分布正常（无极端异常值）
3. 批次效应可接受（如有多批次数据）

## 回退策略
- 如目标数据集不可获取，使用同类替代数据集
- 如H5AD格式不可用，尝试其他格式（如Loom、CSV）并转换
- 如数据质量不达标，执行额外QC过滤

## 资源召回建议
- 需要获取单细胞数据集时召回本卡片
- 配套资源：bio-singlecell-foundation-model-weights（模型权重获取）
- 配套资源：bio-singlecell-data-preprocessing（数据预处理流程）

## 证据来源
[D1] CZ CELLxGENE Discover, Chan Zuckerberg Initiative, 2026, URL: https://cellxgene.cziscience.com/（权威平台，交叉验证）
[D2] Human Cell Atlas Data Portal, HCA Consortium, URL: https://data.humancellatlas.org/（权威平台）
[D3] Single Cell Expression Atlas, EBI, URL: https://www.ebi.ac.uk/xa/（权威平台）