# DNALONGBENCH基准数据集

## 适用范围

适用于需要评估DNA基础模型长程依赖建模能力的场景，包括增强子-启动子远距离相互作用预测、3D基因组接触图预测、eQTL效应预测、转录起始信号预测等。DNALONGBENCH是目前最大的长程DNA预测任务基准套件，包含5个跨越不同长度尺度的生物学相关任务。适用于输入序列长度从100kb到1Mbp的任务评估。

## 输入

- **数据格式**：BED格式（包含基因组坐标chr:start-end）
- **参考基因组**：hg38（人类）
- **数据来源**：Harvard DataVerse（DOI链接见下方）
- **任务类型**：5个长程DNA预测任务

## 输出

- **评估指标**：AUROC/AUPRC（分类）、SCC/Pearson相关（回归）
- **结果粒度**：区间级、碱基级、变异级
- **基准报告**：模型性能对比表

## 流程节点

### 1. 数据获取
1. 访问Harvard DataVerse下载数据：
   - 增强子-启动子预测：10.7910/DVN/CTEQXX
   - 3D接触图预测：10.7910/DVN/AZM25S
   - 监管序列活性预测：10.7910/DVN/MNUEZR
   - eQTL预测：10.7910/DVN/YUP2G5
   - 转录起始信号预测：10.7910/DVN/VXQKWO
2. 或从GitHub获取处理后数据：https://github.com/ma-compbio/DNALONGBENCH
3. 解压并验证数据完整性

### 2. 任务定义
1. **增强子-启动子预测**：预测增强子是否与目标启动子相互作用（AUROC）
2. **3D接触图预测**：预测基因组位点间的空间接触频率（SCC）
3. **监管序列活性预测**：从DNA序列预测表观遗传信号（Pearson）
4. **eQTL预测**：预测变异是否影响基因表达（AUROC）
5. **转录起始信号预测**：预测转录起始信号强度（Pearson）

### 3. 数据切分
1. 训练/验证/测试集按8:1:1比例随机划分
2. 3D接触图任务使用虚拟contig划分（避免序列重叠）
3. eQTL任务使用分层抽样保持正负样本比例

### 4. 模型评估
1. 使用标准评估指标计算性能
2. 与专家模型（Akita/Puffin/ABC）比较
3. 与CNN基线模型比较
4. 与DNA基础模型（HyenaDNA/Caduceus）比较

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 任务数量 | 5 | [1] | 长程DNA预测任务数 |
| 增强子-启动子最大距离 | 450 kb | [1] | 增强子与TSS最大距离 |
| 3D接触图输入长度 | 1,000,000 bp | [1] | Akita模型输入长度 |
| 3D接触图分辨率 | 2,000 bp/bin | [1] | 接触图分辨率 |
| 3D接触图输出维度 | 448×448 | [1] | 预测接触图大小 |
| 监管序列活性输入 | 196,608 bp | [1] | Enformer输入长度 |
| 监管序列活性输出 | 5313条人类轨迹 | [1] | 预测表观遗传标记数 |
| eQTL组织数 | 9 | [1] | 评估的组织类型数 |
| 转录起始信号技术 | 5种 | [1] | CAGE/RAMPAGE/GRO-cap等 |
| 训练集规模 | 7008条 | [1] | 3D接触图训练集大小 |
| 测试集规模 | 413条 | [1] | 3D接触图测试集大小 |
| 最高SCC | 0.233 | [1] | 专家模型Akita最高SCC |
| 最高AUPRC | 0.733 | [1] | 专家模型Puffin最高AUPRC |

## 边界与分流

- **Transformer模型限制**：DNABERT-2/NT-v2因二次方复杂度无法处理>100kb序列，需使用Caduceus/HyenaDNA
- **专家模型不可用时**：使用CNN基线作为性能下界
- **数据下载失败**：从GitHub仓库获取处理后数据，或联系作者获取
- **评估指标异常**：检查数据切分是否合理，是否存在序列重叠导致的数据泄露

## 质量检查

- 数据完整性：BED格式包含正确的基因组坐标
- 坐标验证：所有坐标位于hg38参考基因组范围内
- 序列长度分布：验证输入序列长度符合任务要求
- 标签一致性：功能标签与序列一一对应

## 回退策略

- DNALONGBENCH不可用时：使用BEND或LRB基准作为替代
- 长程任务评估困难时：先在短程任务上验证模型，再扩展到长程
- 计算资源不足时：使用子采样评估，或使用更小的模型（如HyenaDNA-160K）

## 资源召回建议

- 当需要评估DNA基础模型的长程依赖建模能力时召回本卡片
- 当需要获取真实基因组DNA数据时优先使用DNALONGBENCH
- 配合bio-dna-long-range-modeling-workflow卡片使用
- 配合bio-caduceus-model-specification卡片选择合适的模型

## 证据来源

[1] Cheng W, Song Z, Zhang Y, et al. DNALONGBENCH: a benchmark suite for long-range DNA prediction tasks. Nature Communications, 2025. DOI: 10.1038/s41467-025-65077-4.
[2] Feng H, Wu L, Zhao B. Benchmarking DNA foundation models for genomic and genetic tasks. Nature Communications, 2025. DOI: 10.1038/s41467-025-65823-8.
