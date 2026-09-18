# 长程DNA序列建模完整工作流

## 适用范围

适用于需要对基因组DNA序列进行长程依赖建模的任务，包括但不限于增强子-启动子远距离相互作用预测、3D基因组接触图预测、eQTL效应预测、转录起始信号预测等。适用于输入序列长度超过10kb、需要捕获跨越数十万至数百万碱基对的远程调控元件相互作用的场景。不适用于短序列（<1kb）的局部调控元件识别任务。

## 输入

- **基因组DNA序列**：FASTA格式，包含真实基因组坐标（chr:start-end），参考基因组版本hg38
- **功能标签**：根据任务类型不同，包括增强子活性标签、eQTL效应标签、接触频率矩阵、转录起始信号等
- **数据规模**：训练集通常需要数千至数万条序列区间

## 输出

- **预测结果**：根据任务类型输出分类概率、回归分数或接触矩阵
- **评估指标**：AUROC/AUPRC（分类）、Pearson相关系数/SCC（回归）、平均精度（AUPRC曲线下面积）
- **结果文件**：区间级result_table.tsv、变异级variant_scores.vcf

## 流程节点

### 1. 模型选择与权重获取
1. 选择合适的基础模型（Caduceus-Ph为首选，支持131K输入）
2. 从HuggingFace或GitHub获取预训练权重
3. 验证权重与模型架构匹配（torch.load + load_state_dict无key mismatch）

### 2. 真实基因组数据准备
1. 从DNALONGBENCH获取基准数据（5个任务，数据在Harvard DataVerse）
2. 或从ENCODE/UCSC/4DN下载原始基因组数据
3. 数据格式化为BED格式（包含基因组坐标）
4. 确保坐标位于hg38参考基因组范围内

### 3. 长窗口分块预处理
1. 将长序列（如1Mbp）按模型最大输入长度分块（如131Kbp）
2. 保持坐标连续性，中心坐标不偏移
3. 构建正反链方向映射表（RC(x)[i]=complement(x[N-1-i])）
4. 验证分块后可逆恢复

### 4. 模型推理与评估
1. 使用mean token pooling生成序列表示
2. 计算标准评估指标（AUROC/AUPRC/SCC/Pearson）
3. 输出区间级和变异级结果

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Caduceus-Ph最大输入长度 | 131,072 bp | [1] | 模型支持的最大序列长度 |
| Caduceus-Ph参数量 | ~35M | [3] | 可训练参数数量 |
| Caduceus-Ph嵌入维度 | 256 | [3] | 输出嵌入维度 |
| 3D接触图输入长度 | 1,000,000 bp | [2] | Akita模型输入长度 |
| 3D接触图分辨率 | 2,000 bp/bin | [2] | 接触图分辨率 |
| 接触图SCC最高值 | 0.233 | [2] | 专家模型Akita的最高SCC |
| 监管序列活性预测输入 | 196,608 bp | [2] | Enformer输入长度 |
| eQTL预测评估指标 | AUROC | [2] | 二分类评估指标 |
| 转录起始信号预测 | Pearson相关 | [2] | 回归任务评估指标 |

## 边界与分流

- **mamba-ssm无法安装时**：可尝试conda-forge预编译包、WSL2环境、或降级使用causal-conv1d（但会丧失选择性扫描能力）
- **无预训练权重时**：可从随机初始化开始训练，但需显著增加训练数据量和训练轮次
- **长序列超出GPU内存时**：采用分块推理策略，或使用滑动窗口+重叠区域融合
- **Transformer模型上下文受限时**：DNABERT-2/NT-v2对长序列有二次方复杂度限制，Caduceus/HyenaDNA更适合长序列任务

## 质量检查

- 权重加载验证：torch.load成功且model.load_state_dict不报key mismatch
- 数据验证：FASTA文件包含真实基因组坐标，序列长度分布合理
- 坐标验证：分块后中心坐标不偏移，正反链映射可逆
- 评估验证：AUPRC值与文献报告基线可比（≥0.6为可接受）

## 回退策略

- 权重获取失败：使用其他预训练DNA基础模型（HyenaDNA、DNABERT-2、NT-v2）
- 长程建模失败：降级为局部模型（CNN），但需在论文中说明局限性
- 评估指标异常：检查数据切分是否合理，是否存在数据泄露

## 资源召回建议

- 当任务涉及DNA序列长程依赖建模时召回本卡片
- 当需要选择DNA基础模型时参考bio-caduceus-model-specification卡片
- 当需要基准数据时参考bio-dnalongbench-benchmark-dataset卡片

## 证据来源

[1] Schiff Y, Kao CH, Gokaslan A, Dao T, Gu A, Kuleshov V. Caduceus: Bi-Directional Equivariant Long-Range DNA Sequence Modeling. ICML 2024. arXiv:2403.03234.
[2] Cheng W, Song Z, Zhang Y, et al. DNALONGBENCH: a benchmark suite for long-range DNA prediction tasks. Nature Communications, 2025. DOI: 10.1038/s41467-025-65077-4.
[3] Feng H, Wu L, Zhao B. Benchmarking DNA foundation models for genomic and genetic tasks. Nature Communications, 2025. DOI: 10.1038/s41467-025-65823-8.
[4] Veiner M, Supek F. The DNA dialect: a comprehensive guide to pretrained genomic language models. Molecular Systems Biology, 2026. DOI: 10.1038/s44320-025-00184-4.
