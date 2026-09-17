# scATAC-seq生物一致性评估任务

## 适用范围

**触发条件**：
- 需要验证细胞嵌入表征的生物学意义
- 需要评估通路信号在表征中的保留程度
- 需要检查细胞类型分离度和空间结构保持

**适用场景**：
- scATAC-seq表征学习后的质量评估
- 模型性能验证和比较
- 生物学有效性检查
- 跨数据集表征一致性评估

**不适用场景**：
- 无生物学知识注释的数据
- 纯技术性评估（如降维效果）
- 无细胞类型标签的数据

## 输入

- **细胞嵌入表征**：低维向量矩阵（n_cells × embedding_dim）
- **细胞类型标签**：真实细胞类型注释
- **基因集注释**：GO/KEGG通路注释文件
- **可选输入**：
  - 空间坐标信息（如有空间转录组数据）
  - 原始peak矩阵（用于可及性分析）

## 输出

- **生物一致性报告**：包含以下指标
  - 通路保持分数（Pathway Preservation Score）
  - 细胞类型分离度（Cell Type Separation Ratio）
  - 空间结构保持分数（Spatial Structure Preservation）
- **详细评估**：各指标的计算结果和解释
- **可视化**：UMAP/tSNE嵌入的细胞类型着色图

## 流程节点

### Step 1：通路保持评估
- **操作**：评估嵌入表征中通路信号的保留程度
- **方法**：
  1. 获取GO/KEGG通路基因列表
  2. 提取通路相关peak的嵌入向量
  3. 计算通路内细胞的嵌入相似度
  4. 与随机背景比较
- **实现**：
  ```python
  import numpy as np
  from scipy.stats import pearsonr
  
  def pathway_preservation_score(embeddings, pathway_genes, peak_gene_mapping):
      """
      计算通路保持分数
      embeddings: n_cells × n_peaks 嵌入矩阵
      pathway_genes: 通路相关基因列表
      peak_gene_mapping: peak到基因的映射
      """
      # 提取通路相关peak的嵌入
      pathway_peaks = [p for p, g in peak_gene_mapping.items() if g in pathway_genes]
      pathway_embeddings = embeddings[:, pathway_peaks]
      
      # 计算通路内细胞的平均相似度
      similarity = np.corrcoef(pathway_embeddings)
      within_pathway_sim = similarity[np.triu_indices_from(similarity, k=1)].mean()
      
      # 与随机背景比较
      random_peaks = np.random.choice(embeddings.shape[1], len(pathway_peaks), replace=False)
      random_embeddings = embeddings[:, random_peaks]
      random_sim = np.corrcoef(random_embeddings)[np.triu_indices_from(similarity, k=1)].mean()
      
      return within_pathway_sim / (random_sim + 1e-10)
  ```
- **质量门禁**：通路保持分数 > 0.5

### Step 2：细胞类型分离度评估
- **操作**：评估不同细胞类型在嵌入空间中的分离程度
- **方法**：
  1. 计算同类细胞的平均距离（类内距离）
  2. 计算不同类细胞的平均距离（类间距离）
  3. 计算分离度比值（类间/类内）
- **实现**：
  ```python
  from scipy.spatial.distance import pdist, squareform
  
  def cell_type_separation_ratio(embeddings, cell_types):
      """
      计算细胞类型分离度比值
      embeddings: n_cells × n_features
      cell_types: n_cells 细胞类型标签
      """
      # 计算距离矩阵
      dist_matrix = squareform(pdist(embeddings))
      
      unique_types = np.unique(cell_types)
      within_distances = []
      between_distances = []
      
      for i, t1 in enumerate(unique_types):
          mask1 = cell_types == t1
          # 类内距离
          within_d = dist_matrix[mask1][:, mask1]
          within_distances.append(within_d[np.triu_indices_from(within_d, k=1)].mean())
          
          # 类间距离
          for t2 in unique_types[i+1:]:
              mask2 = cell_types == t2
              between_d = dist_matrix[mask1][:, mask2]
              between_distances.append(between_d.mean())
      
      return np.mean(between_distances) / (np.mean(within_distances) + 1e-10)
  ```
- **质量门禁**：分离度比值 > 1.0

### Step 3：空间结构保持评估
- **操作**：评估空间邻近细胞在嵌入空间中的距离保持
- **方法**：（仅适用于有空间坐标的数据）
  1. 计算空间距离矩阵
  2. 计算嵌入距离矩阵
  3. 计算两者的Spearman相关性
- **实现**：
  ```python
  from scipy.stats import spearmanr
  
  def spatial_structure_preservation(spatial_coords, embeddings):
      """
      计算空间结构保持分数
      spatial_coords: n_cells × 2 (x, y坐标)
      embeddings: n_cells × n_features
      """
      spatial_dist = squareform(pdist(spatial_coords))
      embedding_dist = squareform(pdist(embeddings))
      
      # 计算Spearman相关性
      corr, _ = spearmanr(spatial_dist.flatten(), embedding_dist.flatten())
      return corr
  ```
- **质量门禁**：空间保持分数 > 0.3（如有空间数据）

### Step 4：综合评估
- **操作**：汇总所有评估指标
- **内容**：
  - 通路保持分数（所有通路的平均值）
  - 细胞类型分离度比值
  - 空间结构保持分数（如有）
  - 综合评分
- **质量门禁**：综合评分 > 0.5

### Step 5：生成可视化
- **操作**：生成UMAP/tSNE嵌入图
- **实现**：
  ```python
  import scanpy as sc
  import matplotlib.pyplot as plt
  
  # 创建AnnData对象
  adata = sc.AnnData(X=embeddings)
  adata.obs['cell_type'] = cell_types
  
  # 计算UMAP
  sc.pp.neighbors(adata)
  sc.tl.umap(adata)
  
  # 绘图
  sc.pl.umap(adata, color='cell_type', show=False)
  plt.savefig('umap_cell_types.png')
  ```
- **质量门禁**：可视化清晰，细胞类型分离明显

### Step 6：输出报告
- **操作**：生成结构化评估报告
- **格式**：JSON或Markdown
- **内容**：
  - 评估指标汇总
  - 各指标的解释
  - 改进建议（如指标不达标）
- **质量门禁**：报告完整，可读性强

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 通路保持阈值 | > 0.5 | [1] | 通路信号保留程度 |
| 分离度比值阈值 | > 1.0 | [2] | 细胞类型分离程度 |
| 空间保持阈值 | > 0.3 | [3] | 空间结构保持（如有） |
| 综合评分阈值 | > 0.5 | [1] | 整体生物学有效性 |
| 可视化方法 | UMAP | [4] | 降维可视化标准方法 |

## 边界与分流

- **无通路注释**：跳过通路保持评估，仅报告其他指标
- **无空间数据**：跳过空间结构保持评估
- **指标不达标**：提供改进建议（如增加训练数据、调整模型参数）
- **计算资源不足**：使用采样或近似算法

## 质量检查

- 验证点1：通路保持分数 > 0.5
- 验证点2：细胞类型分离度比值 > 1.0
- 验证点3：空间保持分数 > 0.3（如有空间数据）
- 验证点4：综合评分 > 0.5
- 验证点5：UMAP图显示细胞类型分离

## 回退策略

- **首选**：计算所有可用的生物一致性指标
- **备选1**：仅计算细胞类型分离度（最简单）
- **备选2**：使用ARI/NMI作为替代指标
- **最终方案**：标记评估跳过，说明缺少必要注释

## 资源召回建议

- **召回场景**：当需要验证细胞嵌入的生物学意义时
- **配套资源**：
  - GO/KEGG通路注释数据库
  - 细胞类型标签数据
  - 空间坐标数据（如有）
  - UMAP/tSNE可视化工具

## 证据来源

[1] Subramanian, A. et al. "Gene set enrichment analysis: A knowledge-based approach for interpreting genome-wide expression profiles". PNAS, 2005, DOI: 10.1073/pnas.0506580102
[2] Van der Maaten, L. & Hinton, G. "Visualizing Data using t-SNE". JMLR 9, 2008
[3] Wolf, F. et al. "SCANPY: large-scale single-cell gene expression data analysis". Genome Biology, 2018
[4] McInnes, L. et al. "UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction". arXiv:1802.03426, 2018
