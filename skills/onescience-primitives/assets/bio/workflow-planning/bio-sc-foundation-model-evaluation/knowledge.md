# 单细胞基础模型评测方法知识

## 适用范围

**触发条件**：
- 任务需要评估单细胞基础模型的生物学一致性
- 需要执行扰动预测、空间结构保持或跨模态一致性检验
- 概念纯度评测需要补充其他生物学验证指标

**适用场景**：
- 单细胞基础模型性能比较
- 模型可解释性评估
- 细胞状态表征质量验证

**不适用场景**：
- 纯计算性能评测（速度、内存）
- 临床诊断性能验证（需要临床数据）
- 未经实验验证的计算预测

## 输入

| 输入项 | 说明 |
|--------|------|
| 模型表征 | 细胞嵌入向量（Geneformer/scGPT） |
| 真实标签 | 细胞类型、批次、扰动条件 |
| 空间坐标 | 空间转录组坐标（可选） |
| 多组学数据 | RNA+ATAC表达矩阵（可选） |

## 输出

| 输出项 | 说明 |
|--------|------|
| 评测指标 | 概念纯度、扰动响应准确率、空间保持性、跨模态一致性 |
| 统计检验 | p值、效应量、置信区间 |
| 可视化 | UMAP嵌入、热图、散点图 |
| 评测报告 | 指标汇总、失败案例、适用边界 |

## 流程节点

### 步骤1：概念纯度评测

**操作**：计算模型表征的生物学概念组织质量

**概念纯度定义**：
- 嵌入空间中相同细胞类型的细胞是否聚集
- 不同细胞类型是否分离
- 生物学相关概念（如分化轨迹）是否保持

**计算方法**：

```
concept_purity = mean(
    intra_class_cohesion / inter_class_separation
)
```

**评估指标**：

| 指标 | 定义 | 方向 | 阈值 |
|------|------|------|------|
| Adjusted Rand Index (ARI) | 聚类与真实标签一致性 | 越高越好 | >0.5 |
| Normalized Mutual Information (NMI) | 互信息归一化 | 越高越好 | >0.5 |
| Silhouette Score | 类内紧密度/类间分离度 | 越高越好 | >0.3 |
| Homogeneity | 纯度（每簇单一类型） | 越高越好 | >0.6 |

**分层报告**：
- 按细胞类型分层计算
- 按供体/批次分层计算
- 按组织/空间区域分层计算

### 步骤2：扰动预测评估

**操作**：评估模型预测基因敲除/过表达后细胞状态变化的能力

**扰动预测任务**：
1. **反事实响应预测**：给定基因X敲除，预测细胞状态变化
2. **扰动方向一致性**：预测的差异表达方向是否与真实一致
3. **细胞类型特异性**：不同细胞类型对同一扰动的响应是否可区分

**评估框架**：

| 评估维度 | 方法 | 指标 | 说明 |
|----------|------|------|------|
| 表达变化方向 | Spearman相关 | rho | 预测vs真实差异表达 |
| 细胞类型分离 | ARI/NMI | score | 扰动后细胞类型聚类 |
| 扰动强度 | 效应量 | Cohen's d | 扰动组vs对照组 |
| 跨条件泛化 | 交叉验证 | accuracy | 未见扰动条件 |

**参考数据集**：
- scPerturb（Broad Institute）
- Norman et al. 2019（CRISPR筛选）
- Gasperini et al. 2019（启动子扰动）

### 步骤3：空间结构保持性检验

**操作**：验证模型表征是否保持空间邻近关系

**适用数据**：空间转录组（Visium、MERFISH、Stereo-seq）

**检验方法**：

| 方法 | 定义 | 指标 | 说明 |
|------|------|------|------|
| Moran's I | 空间自相关 | I | 嵌入值空间聚集度 |
| Geary's C | 空间异质性 | C | 邻近细胞相似度 |
| Ripley's K | 空间分布模式 | K(r) | 点模式分析 |
| 保留最近邻 | KNN保持率 | accuracy | 空间邻接是否保持 |

**空间保持性指标**：

```
spatial_preservation = mean(
    spatial_knn_accuracy @ multiple_radius
)
```

**质量门禁**：
- Moran's I > 0.3（显著空间聚集）
- 空间KNN保持率 > 70%

### 步骤4：跨模态一致性验证

**操作**：验证不同组学数据的关联性在模型表征中是否保持

**适用场景**：RNA + ATAC多组学数据

**验证方法**：

| 方法 | 定义 | 指标 | 说明 |
|------|------|------|------|
| Canonical Correlation | 典型相关分析 | r | RNA-ATAC嵌入相关 |
| Cross-modal KNN | 跨模态最近邻一致性 | accuracy | 同细胞RNA/ATAC邻近 |
| 调控网络一致性 | 基因调控网络重叠 | Jaccard | 转录因子-靶基因关系 |
| 细胞类型对齐 | 跨模态细胞类型一致 | ARI | 细胞类型注释一致 |

**跨模态一致性指标**：

```
cross_modal_consistency = mean(
    canonical_correlation,
    cross_modal_knn_accuracy,
    regulatory_network_overlap
)
```

### 步骤5：指标互补性分析

**操作**：分析不同评测指标的互补关系

**指标互补性**：

| 指标组合 | 互补关系 | 说明 |
|----------|----------|------|
| 概念纯度 + 扰动预测 | 静态组织 vs 动态响应 | 聚类质量 vs 因果预测 |
| 概念纯度 + 空间保持 | 组织无关 vs 组织特异 | 通用表征 vs 空间约束 |
| 概念纯度 + 跨模态 | 单模态 vs 多模态 | 单一组学 vs 联合分析 |
| 扰动预测 + 空间保持 | 实验扰动 vs 自然变异 | 干预效果 vs 内在规律 |

**综合评分建议**：

```
comprehensive_score = (
    0.3 * concept_purity +
    0.3 * perturbation_accuracy +
    0.2 * spatial_preservation +
    0.2 * cross_modal_consistency
)
```

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| ARI阈值 | >0.5 | [1] | 聚类质量可接受 |
| Moran's I阈值 | >0.3 | [2] | 空间自相关显著 |
| 典型相关阈值 | >0.5 | [3] | 跨模态一致 |
| 扰动预测相关 | >0.4 | [1] | 方向一致 |

## 边界与分流

**异常处理**：
- 空间数据不存在 → 跳过空间保持性检验
- 多组学数据不存在 → 跳过跨模态一致性验证
- 扰动实验数据不存在 → 仅计算概念纯度

**分支条件**：
- 数据包含空间坐标 → 执行空间保持性检验
- 数据包含多组学 → 执行跨模态一致性验证
- 数据包含扰动实验 → 执行扰动预测评估

## 质量检查

| 检查点 | 阈值 | 失败处理 |
|--------|------|----------|
| 指标计算完整性 | 100% | 检查数据可用性 |
| 统计显著性 | p<0.05 | 增加样本量 |
| 分层报告完整性 | >80%细胞类型 | 标注缺失类型 |
| 可视化清晰度 | 可分辨 | 调整参数 |

## 回退策略

1. **首选**：执行完整4项评测（概念纯度+扰动+空间+跨模态）
2. **备选**：仅执行概念纯度+可用评测项
3. **兜底**：仅报告概念纯度，标注其他评测待补充

## 资源召回建议

**何时召回本卡片**：
- 任务需要评估单细胞模型的生物学一致性
- 需要执行扰动预测或空间结构检验
- 概念纯度评测需要补充验证

**配套资源**：
- bio-sc-data-public-dataset-acquisition：获取评测数据集
- bio-sc-foundation-model-weight-acquisition：加载模型权重
- bio-sc-rnaseq-statistical-testing：统计检验方法

## 证据来源

[1] Predicting cellular responses to complex perturbations in high-throughput screens, Molecular Systems Biology, 2023, DOI: 10.15252/msb.202211517

[2] Causal identification of single-cell experimental perturbation effects with CINEMA-OT, Nature Methods, 2023, DOI: 10.1038/s41592-023-02040-5

[3] Systema: a framework for evaluating genetic perturbation response prediction beyond systematic variation, Nature Biotechnology, 2025, DOI: 10.1038/s41587-025-02777-8
