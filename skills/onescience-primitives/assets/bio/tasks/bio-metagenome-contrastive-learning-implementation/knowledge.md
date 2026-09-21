# 宏基因组分箱对比学习实现方法

## 适用范围
本卡片服务于将对比学习方法落地为可运行代码的宏基因组分箱任务。适用于已有组装后的contigs数据，需要通过对比学习生成高质量表征向量并进行聚类分箱的场景。不适用于从原始reads直接分箱的场景（需先完成组装），也不适用于非对比学习方法（如VAE、图神经网络）的分箱实现。

## 输入
- **序列数据**：组装后的contigs（FASTA格式），最短长度阈值1000bp
- **覆盖度数据**：每个contig在各测序样本中的覆盖度（从BAM文件计算）
- **模型权重**：CLMB/COMEBin预训练权重文件（.pt格式）
- **参考数据库**（可选）：GTDB等分类学数据库用于辅助编码

## 输出
- **表征向量**：每个contig的低维嵌入表示（用于聚类）
- **分箱结果**：contig到bin的分配
- **中间产物**：k-mer频率矩阵、覆盖度矩阵、增强视图

## 流程节点

### s01 数据标准化与长度过滤
- **操作**：过滤短序列、质量控制、格式统一
- **参数**：最短序列长度阈值1000bp（CLMB模型最小输入长度要求）
- **工具**：seqkit（`seqkit seq -m 1000 input.fasta > filtered.fasta`）
- **质量门禁**：输出过滤后序列长度分布报告，确认短序列已过滤；过滤后序列数应≥原始序列数的50%
- **I/O契约**：输入FASTA → 输出过滤后FASTA（同格式，序列ID不变）

### s02 k-mer分词与特征提取
- **操作**：将DNA序列转换为k-mer频率向量
- **步骤**：
  1. **k-mer频率计算**：使用4-mer（四核苷酸频率，TNF），考虑反向互补，维度136
  2. **覆盖度编码**：计算每个contig在各样本中的覆盖度均值和标准差，维度2M（M=样本数）
  3. **特征拼接**：将TNF和覆盖度向量拼接为复合特征向量
- **工具**：COMEBin内置`get_coverage.py`和`get_kmer.py`；或自定义脚本使用` khmer`/` scikit-bio`库
- **关键实现**：
  ```python
  # k-mer频率计算示例（4-mer, 反向互补）
  from collections import Counter
  import numpy as np
  
  def compute_tnf(seq, k=4):
      """计算四核苷酸频率（考虑反向互补）"""
      bases = 'ACGT'
      # 生成所有k-mer（含反向互补）
      kmers = []
      for kmer in itertools.product(bases, repeat=k):
          kmer_str = ''.join(kmer)
          rc = reverse_complement(kmer_str)
          if kmer_str <= rc:  # 取字典序较小的代表
              kmers.append(kmer_str)
      kmers = sorted(set(kmers))
      # 统计频率
      counts = Counter()
      for i in range(len(seq) - k + 1):
          kmer = seq[i:i+k]
          rc = reverse_complement(kmer)
          counts[min(kmer, rc)] += 1
      total = sum(counts.values()) or 1
      return np.array([counts[k] / total for k in kmers])
  ```
- **质量门禁**：TNF维度=136，覆盖度维度=2M，无NaN值
- **I/O契约**：输入过滤后FASTA+BAM → 输出特征矩阵（n_contigs × (136+2M)）

### s03 对比学习表征生成
- **操作**：使用对比学习模型生成contig嵌入
- **步骤**：
  1. **数据增强**：为每个contig生成多个增强视图（随机片段提取，最小长度1000bp；添加高斯噪声）
  2. **对比学习**：最大化同一contig不同视图的相似性，最小化不同contig视图的相似性
  3. **损失函数**：使用InfoNCE/NT-Xent损失
  4. **表征生成**：使用训练好的编码器生成低维嵌入
- **关键实现**：
  ```python
  # InfoNCE损失函数
  import torch
  import torch.nn.functional as F
  
  def info_nce_loss(z_i, z_j, temperature=0.1):
      """
      z_i, z_j: 同一batch中两个增强视图的嵌入向量
      temperature: 温度系数τ（推荐0.1-0.3）
      """
      batch_size = z_i.shape[0]
      z_i = F.normalize(z_i, dim=1)
      z_j = F.normalize(z_j, dim=1)
      # 拼接两个视图
      z = torch.cat([z_i, z_j], dim=0)
      # 计算相似度矩阵
      sim = torch.mm(z, z.T) / temperature
      # 掩码：对角线为自身，不参与对比
      mask = torch.eye(2 * batch_size, dtype=torch.bool)
      sim.masked_fill_(mask, -1e9)
      # 正样本：同一contig的不同视图
      labels = torch.cat([
          torch.arange(batch_size, 2 * batch_size),
          torch.arange(0, batch_size)
      ])
      return F.cross_entropy(sim, labels)
  ```
- **参数**：批次大小、温度系数τ=0.1-0.3、增强视图数4-6个
- **工具**：COMEBin/CLMB内置训练模块；或自定义PyTorch训练循环
- **质量门禁**：监控对比损失收敛（通常50-200个epoch），验证嵌入质量（t-SNE可视化应显示不同基因组的contig形成可分离的簇）
- **I/O契约**：输入特征矩阵 → 输出嵌入矩阵（n_contigs × embedding_dim）

### s04 聚类分箱
- **操作**：使用聚类算法将嵌入向量分组为bins
- **步骤**：
  1. **构建KNN图**：使用嵌入向量构建k近邻图（边缘保留比例50%-100%）
  2. **聚类**：使用Leiden算法（COMEBin）或迭代medoid算法（CLMB）
  3. **后处理**：过滤过小bin（<200kbp），合并高度重叠的bin
- **参数**：聚类分辨率1-110（Leiden），需多次运行选择最佳
- **工具**：COMEBin使用Leiden（`leidenalg`库），CLMB使用medoid
- **质量门禁**：每个bin的contig来自同一基因组的比例（纯度）
- **I/O契约**：输入嵌入矩阵 → 输出分箱结果（TSV/CSV：contig_id, bin_id）

## 关键参数

### 通用判据（方法层，同类体系可参考）
| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| 最短序列长度 | 1000bp | [1] | 大多数分箱工具的最小输入要求 |
| k-mer大小 | 4 (四核苷酸频率) | [1] | TNF维度136（考虑反向互补） |
| 增强视图数 | 4-6个 | [1] | COMEBin使用6个视图，更多视图可提升性能 |
| 温度系数τ | 0.1-0.3 | [1] | NT-Xent损失函数中的温度参数 |
| 聚类分辨率 | 1-110 | [1] | Leiden算法参数，需多次运行选择最佳 |
| 边缘保留比例 | 50%-100% | [1] | KNN图构建时保留的边比例 |
| 最小bin大小 | 200kbp | [1] | 过滤过小bin |

### 校准数值（以下数值来自COMEBin/CLMB体系，供量级校准；其他体系需以自身证据重新锚定）
| 参数 | COMEBin值 | CLMB值 | 来源 | 说明 |
|------|-----------|--------|------|------|
| TNF维度 | 136 | 136 | [1] | 四核苷酸频率，k=4 |
| 覆盖度维度 | 2M (M=样本数) | 2M | [1] | 均值+标准差 |
| 最小增强片段长度 | 1000bp | N/A | [1] | COMEBin随机提取≥1000bp片段 |
| 网络结构 | 3层前馈网络 | 3层前馈网络 | [1] | Coverage Network和Combine Network |
| 聚类算法 | Leiden | 迭代medoid | [1] | COMEBin使用Leiden，CLMB使用medoid |
| 训练epoch | 50-200 | 50-200 | [1] | 对比损失收敛即可 |

## 边界与分流
- **数据类型分流**：短读长数据使用标准流程；长读长数据推荐SemiBin2的long-read模式；混合数据可获得最佳性能
- **样本数分流**：少于10个样本时，Coverage Network模块可保持性能；超过50个样本时覆盖度维度可能过大
- **序列长度分流**：contigs长度<1000bp时应过滤；长度分布异常时检查组装质量
- **计算资源分流**：GPU模式可显著加速对比学习训练；大规模数据（>100万contigs）需考虑内存限制
- **无参考数据库时**：跳过参考数据库编码步骤，仅使用无监督对比学习
- **对比学习收敛失败时**：尝试调整温度系数τ、批次大小或增强策略；如仍无法收敛，回退到非对比学习方法（如VAMB的VAE）
- **模型权重不可用时**：使用从头训练或公开预训练权重；如无法获取，标记BLOCKED

## 质量检查
- **特征提取验证**：TNF维度=136，覆盖度维度=2M，无NaN值
- **表征质量验证**：t-SNE可视化应显示不同基因组的contig形成可分离的簇
- **聚类结果验证**：每个bin的contig来自同一基因组的比例（纯度）
- **对比损失监控**：训练过程中损失应单调下降并趋于平稳
- **端到端验证**：使用标准评估指标（ARI、V-measure、Completeness、Completeness50）评估分箱质量

## 回退策略
- **对比学习无法收敛**：回退到非对比学习方法（如VAMB的VAE、MetaBat2的四核苷酸频率聚类）
- **GPU内存不足**：使用CPU模式或减小批次大小
- **分箱质量差**：尝试不同参数组合，或使用集成方法（MetaWRAP、MAGScoT）
- **模型权重不可用**：使用从头训练或公开预训练权重；如无法获取，标记BLOCKED
- **数据增强效果差**：尝试不同的增强策略（如随机替换、反转、裁剪组合）

## 资源召回建议
- 当任务涉及宏基因组序列分箱的对比学习实现时召回本卡片
- 配套资源：`bio-clmb-contrastive-metagenome-binning-model`（CLMB模型详情）、`bio-metagenome-binning-evaluation-methodology`（评估方法）、`bio-metagenome-data-model-sources`（数据与模型获取）
- 相关卡片：`bio-contrastive-metagenome-binning-workflow`（工作流规划框架）

## 证据来源
[1] Wang Z, You R, Han H, Liu W, Sun F, Zhu S. Effective binning of metagenomic contigs using contrastive multi-view representation learning. Nature Communications, 2024, 15:585. DOI: 10.1038/s41467-023-44290-z
[2] Han H, Wang Z, Zhu S. Benchmarking metagenomic binning tools on real datasets across sequencing platforms and binning modes. Nature Communications, 2025, 16:2865. DOI: 10.1038/s41467-025-57957-6
[3] Pan X, et al. SemiBin2: self-supervised contrastive learning leads to better MAGs for short- and long-read sequencing. Bioinformatics, 2023, 39(Supplement_1):i21-i31. DOI: 10.1093/bioinformatics/btad209
[4] Mallawaarachchi V, Wickramarachchi A, Xue H, et al. Solving genomic puzzles: computational methods for metagenomic binning. Briefings in Bioinformatics, 2024, 25(5):bbae372. DOI: 10.1093/bib/bbae372
