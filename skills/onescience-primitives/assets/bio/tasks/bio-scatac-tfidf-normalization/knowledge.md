# scATAC-seq TF-IDF归一化任务

## 适用范围

**触发条件**：
- 需要对scATAC-seq数据进行预处理
- 数据为peak × cell稀疏计数矩阵
- 需要替代scRNA-seq的normalize_total+log1p流水线

**适用场景**：
- scATAC-seq数据分析的预处理阶段
- 为ChromFound等模型准备输入数据
- 细胞类型注释前的标准化处理
- 跨平台/跨批次scATAC数据整合

**不适用场景**：
- scRNA-seq数据分析（应使用normalize_total+log1p）
- bulk ATAC-seq数据分析
- 已经完成TF-IDF归一化的数据

## 输入

- **数据格式**：H5AD（AnnData）格式
- **必需字段**：
  - `X`：peak × cell 稀疏计数矩阵（scipy.sparse）
  - 细胞数 > 0，peak数 > 0
- **可选字段**：
  - `obs`：细胞元数据
  - `var`：特征元数据

## 输出

- **归一化数据**：TF-IDF归一化后的peak × cell矩阵
- **数据特征**：
  - 非负值
  - 稀疏性保持
  - 值域合理（通常0-10之间）
- **元数据更新**：添加预处理信息到`uns`字段

## 流程节点

### Step 1：数据验证
- **操作**：检查输入数据格式和质量
- **检查项**：
  1. X为稀疏矩阵（scipy.sparse）
  2. 无全零行或全零列
  3. 数据非负（允许少量负值，但主体为非负）
- **质量门禁**：数据格式正确，无异常值

### Step 2：计算TF（Term Frequency）
- **操作**：计算每个peak在每个细胞中的频率
- **公式**：TF_ij = count_ij / sum_j(count_ij)
  - count_ij：细胞j中peak i的计数
  - sum_j(count_ij)：细胞j中所有peak的总计数
- **实现**：
  ```python
  import numpy as np
  from scipy.sparse import issparse
  
  # 计算每个细胞的总计数
  cell_totals = X.sum(axis=1).A1  # shape: (n_cells,)
  
  # 计算TF
  tf = X / cell_totals[:, None]  # 广播除法
  ```
- **质量门禁**：TF值在0-1之间，每行和为1

### Step 3：计算IDF（Inverse Document Frequency）
- **操作**：计算每个peak的逆文档频率
- **公式**：IDF_i = log(N / df_i)
  - N：细胞总数
  - df_i：包含peak i的细胞数
- **实现**：
  ```python
  # 计算包含每个peak的细胞数
  df = (X > 0).sum(axis=0).A1  # shape: (n_peaks,)
  
  # 计算IDF（避免除零）
  idf = np.log(N / (df + 1))  # 加1平滑
  ```
- **质量门禁**：IDF值为正，高频peak的IDF较低

### Step 4：计算TF-IDF
- **操作**：将TF和IDF相乘
- **公式**：TF-IDF_ij = TF_ij × IDF_i
- **实现**：
  ```python
  # TF-IDF计算
  tf_idf = tf.multiply(idf[None, :])  # 广播乘法
  
  # 转换为稀疏矩阵（如需要）
  from scipy.sparse import csr_matrix
  tf_idf_sparse = csr_matrix(tf_idf)
  ```
- **质量门禁**：TF-IDF值非负，稀疏性保持

### Step 5：验证归一化效果
- **操作**：检查归一化后数据的分布特征
- **检查项**：
  1. 值域合理（通常0-10之间）
  2. 无NaN或Inf值
  3. 稀疏度与原始数据相近
  4. 高可及性peak的TF-IDF值较高
- **质量门禁**：所有检查项通过

### Step 6：更新AnnData对象
- **操作**：将归一化结果保存到AnnData
- **实现**：
  ```python
  adata.X = tf_idf_sparse
  adata.uns['normalization'] = 'TF-IDF'
  adata.uns['normalization_params'] = {
      'method': 'TF-IDF',
      'smooth_idf': True
  }
  ```
- **质量门禁**：AnnData对象可正常保存和加载

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 归一化方法 | TF-IDF | [1][2] | scATAC专用预处理 |
| IDF平滑 | log(N/(df+1)) | [2] | 避免除零，平滑高频peak |
| 值域范围 | 0-10 | [1] | 合理的TF-IDF值域 |
| 稀疏性保持 | >90%零值 | [1] | 保持数据稀疏结构 |
| 与scRNA-seq区别 | TF-IDF vs normalize_total+log1p | [1] | 不同数据类型的预处理方法 |

## 边界与分流

- **数据过于稀疏**：若零值比例>99%，可能需要先进行peak filtering
- **数据包含负值**：检查原始数据质量，必要时进行binarize
- **内存不足**：使用分块计算或减小batch size
- **验证失败**：检查数据格式，确保为稀疏矩阵

## 质量检查

- 验证点1：TF-IDF值非负，无NaN或Inf
- 验证点2：值域合理（通常0-10之间）
- 验证点3：稀疏度与原始数据相近
- 验证点4：每行TF和为1（归一化正确）
- 验证点5：高频peak的IDF值较低

## 回退策略

- **首选**：使用TF-IDF归一化（标准scATAC预处理）
- **备选1**：使用简单的标准化（如z-score），但效果可能较差
- **备选2**：使用chromVAR的TF-IDF变体（带平滑）
- **最终方案**：标记预处理失败，说明原因

## 资源召回建议

- **召回场景**：当scATAC数据需要预处理时
- **配套资源**：
  - scATAC-seq数据获取任务（提供输入数据）
  - ChromFound模型加载任务（需要预处理后的数据）
  - 细胞类型注释评估任务（评估预处理效果）

## 证据来源

[1] Stuart, T. et al. "Signac: Analysis of Single-Cell Chromatin Data". Bioconductor, 2024
[2] Schep, A. et al. "chromVAR: inferring transcription factor dynamics from single-cell chromatin accessibility data". Nature Methods, 2017, DOI: 10.1038/nmeth.4463
