# 单细胞染色质可及性基础表征与注释工作流

## 适用范围

**触发条件**：
- 需要分析scATAC-seq数据并构建细胞表征
- 需要对单细胞染色质可及性数据进行细胞类型注释
- 需要使用ChromFound预训练模型进行scATAC数据分析

**适用场景**：
- PBMC等外周血单细胞染色质可及性分析
- 组织特异性scATAC-seq数据处理
- 跨批次/跨平台scATAC数据整合
- 细胞类型特异性调控元件鉴定

**不适用场景**：
- scRNA-seq数据分析（应使用scRNA-seq专用流程）
- bulk ATAC-seq数据分析
- 无峰值调用（peak calling）的原始测序数据

## 输入

- **数据格式**：H5AD（AnnData）格式
- **必需字段**：
  - `X`：peak × cell 稀疏计数矩阵
  - `obs`：细胞元数据，必须包含 `cell_type` 列
  - `var`：特征元数据，必须包含：
    - `#Chromosome`：染色体索引（整数，参考 `chromosome_vocab.yaml`）
    - `hg38_Start`：0-based 起始基因组坐标
    - `hg38_End`：0-based 结束基因组坐标（exclusive）
- **可选字段**：
  - `obs.batch`：批次信息
  - `obs.n_features`：检测到的peak数量
  - `obs.tss富集分数`：TSS富集分数

## 输出

- **细胞嵌入表征**：低维向量（默认32维），存储于 `latent_representations.h5ad`
- **细胞类型注释**：Leiden聚类标签映射到真实细胞类型
- **生物一致性报告**：包含通路保持、细胞类型分离度评估
- **基因级结果**：目标基因的可及性分析结果

## 流程节点

### Step 1：数据获取与验证
- **操作**：从公开数据源下载scATAC-seq数据，验证H5AD格式完整性
- **参数**：数据源=10x Genomics/Zenodo/ModelScope，格式=H5AD
- **工具**：scanpy.datasets, scvi.data
- **质量门禁**：H5AD文件可加载，obs包含cell_type列，var包含染色体坐标信息

### Step 2：预处理（TF-IDF归一化）
- **操作**：对peak × cell矩阵进行TF-IDF归一化
- **参数**：TF=peak计数/细胞总计数，IDF=log(细胞总数/包含该peak的细胞数)
- **工具**：scanpy.pp.normalize_total, 自定义TF-IDF函数
- **质量门禁**：预处理后数据非负、稀疏、值域合理

### Step 3：ChromFound模型加载与推理
- **操作**：加载ChromFound预训练权重，生成细胞嵌入表征
- **参数**：
  - `--pretrain_checkpoint_path src/checkpoints`
  - `--pretrain_model_file model.pt`
  - `--pretrain_config_file chromfd_pretrain.yaml`
  - `--batch_size 16`
- **工具**：ChromFound (SAIS-LifeScience/ChromFound)
- **质量门禁**：模型输出维度与任务要求一致，嵌入表征无NaN

### Step 4：聚类与细胞类型注释
- **操作**：Leiden聚类 + 匈牙利算法标签映射
- **参数**：resolution=0.8, n_neighbors=15
- **工具**：scanpy.tl.leiden, scipy.optimize.linear_sum_assignment
- **质量门禁**：宏平均F1 > 0，各细胞类型F1分数合理

### Step 5：生物一致性评估
- **操作**：评估通路保持、细胞类型分离度、空间结构保持
- **参数**：相关性下限阈值=0.5
- **工具**：自定义评估函数
- **质量门禁**：通路保持相关性 > 0.5，细胞类型分离度 > 1.0

### Step 6：结果输出与验证
- **操作**：保存嵌入表征、注释结果、一致性报告
- **参数**：输出格式=H5AD + CSV + JSON
- **工具**：anndata.write, pandas.DataFrame.to_csv
- **质量门禁**：输出文件完整，可被下游工具加载

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 数据格式 | H5AD (AnnData) | [1] | 标准scATAC数据格式 |
| 预处理方法 | TF-IDF归一化 | [1][2] | scATAC专用，非scRNA-seq的normalize_total+log1p |
| 降维方法 | SVD | [1] | scATAC标准降维方法 |
| 预训练模型 | ChromFound | [1] | 1.97M细胞训练的基础模型 |
| 模型权重 | model.pt | [1] | HuggingFace或Google Drive下载 |
| 聚类算法 | Leiden | [1] | 图聚类算法 |
| 标签映射 | 匈牙利算法 | [3] | scipy.optimize.linear_sum_assignment |
| 评估指标 | 宏平均F1, ARI, NMI | [3] | 细胞类型注释质量评估 |

## 边界与分流

- **数据不可用**：若公开数据源无法访问，应明确标记BLOCKED并提供最小补充方案
- **模型权重缺失**：若chromfound.pt无法下载，可使用通用VAE从头训练（需降低预期）
- **预处理失败**：TF-IDF归一化失败时检查数据稀疏性和零值比例
- **标签映射失败**：宏F1=0时检查标签空间是否对齐

## 质量检查

- 验证点1：H5AD文件包含peak×cell矩阵、cell_type和batch元数据列
- 验证点2：预处理后数据分布符合TF-IDF归一化特征（非负、稀疏、值域合理）
- 验证点3：chromfound.pt可加载且模型输出维度与任务要求一致
- 验证点4：宏F1 > 0且各细胞类型F1分数合理
- 验证点5：生物一致性报告包含通路保持、空间结构保持和细胞类型分离度

## 回退策略

- **ChromFound不可用**：使用通用VAE或scVI等替代模型
- **TF-IDF失败**：检查数据格式，尝试binarize后重新计算
- **标签映射失败**：使用ARI/NMI等不需要标签映射的指标

## 资源召回建议

- **召回场景**：当用户需要分析scATAC-seq数据、进行细胞类型注释、或使用ChromFound模型时
- **配套资源**：
  - scATAC-seq公开数据集（10x Genomics PBMC scATAC）
  - ChromFound预训练权重（HuggingFace: YifengJiao/ChromFound）
  - Signac R包（scATAC分析标准工具）
  - scanpy/AnnData（Python scATAC分析）

## 证据来源

[1] Jiao, Y. et al. "ChromFound: Towards A Universal Foundation Model for Single-Cell Chromatin Accessibility Data", arXiv:2505.12638, 2025
[2] Stuart, T. et al. "Signac: Analysis of Single-Cell Chromatin Data", Bioconductor, 2024
[3] Pedregosa, F. et al. "Scikit-learn: Machine Learning in Python", JMLR 12, 2011
