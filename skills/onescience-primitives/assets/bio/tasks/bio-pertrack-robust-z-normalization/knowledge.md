# 逐轨迹 Robust Z-Score 标准化与变异筛选

## 适用范围

**触发条件**：
- 需要对多轨迹变异效应值执行跨可比性标准化
- 需要按效应大小筛选高影响变异候选
- 需要基于背景变异集建立效应分布基线

**适用场景**：
- AlphaGenome 预测结果的跨轨迹标准化（ATAC、CAGE、RNA-seq 等）
- 组织特异的增强子变异候选筛选
- 效应阈值和秩阈值联合过滤

**不适用场景**：
- 单轨迹效应值的绝对值解释（z-score 仅反映相对排名）
- 编码区变异的致病性评分

## 输入

| 输入 | 格式 | 说明 |
|------|------|------|
| 变异效应值 | JSONL，每行含多轨迹 delta 值 | AlphaGenome predict_variant 输出 |
| 背景变异集 | VCF 格式 | mm10_matched_background.vcf |
| 效应阈值 | 数值（如 2） | z-score 绝对值阈值 |
| 轨迹内秩阈值 | 数值（如 0.95） | 仅保留 top 5% 变异 |

## 输出

| 输出 | 格式 | 说明 |
|------|------|------|
| 标准化效应值表 | CSV | 含 z-score、rank、effect_size |
| 组织特异排序 | CSV | 按效应排序的候选列表 |
| 适用边界报告 | JSON | 含标准化公式、MAD 回退记录 |

## 流程节点

### Step 1：加载背景分布
- **操作**：读取 mm10_matched_background.vcf，按轨迹计算 median 和 MAD
- **参数**：背景样本量、按染色体和等位基因频率匹配
- **工具**：Python pandas/numpy
- **质量门禁**：背景变异数 ≥ 100、各轨迹有足够样本

### Step 2：逐轨迹 robust z-score 计算
- **操作**：对每个轨迹独立计算 z = (x - median) / MAD
- **参数**：MAD = median(|x - median|)
- **工具**：自定义 robust_z_score 函数
- **质量门禁**：MAD > 0（否则触发回退规则）

### Step 3：MAD=0 回退处理
- **操作**：当 MAD=0 时，使用标准差 std 替代 MAD 或标记为不可标准化
- **参数**：回退策略选择（std 或 skip）
- **工具**：条件判断逻辑
- **质量门禁**：回退记录写入适用边界报告

### Step 4：轨迹内秩排序
- **操作**：对每个轨迹的 z-score 排序，计算秩百分位
- **参数**：rank_threshold=0.95（保留 top 5%）
- **工具**：numpy.argsort + 百分位计算
- **质量门禁**：秩值在 [0, 1] 范围内

### Step 5：效应阈值筛选
- **操作**：筛选 |z-score| > effect_threshold 的变异
- **参数**：effect_threshold=2（可配置）
- **工具**：布尔索引筛选
- **质量门禁**：筛选后变异数 > 0

### Step 6：跨轨迹聚合（可选）
- **操作**：对筛选后的变异计算跨轨迹聚合分数
- **参数**：聚合策略（max、mean 或加权组合）
- **工具**：numpy 聚合函数
- **质量门禁**：聚合值范围合理

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| robust_z 公式 | z = (x - median) / MAD | [1][2] | 基于中位数和中位绝对偏差 |
| MAD 定义 | median(|x - median|) | [2] | 对异常值鲁棒 |
| MAD=0 回退 | 使用 std 或标记 skip | [2] | 当所有值相同或几乎相同时触发 |
| 效应阈值 | 2（默认） | [1] | z-score 绝对值 |
| 轨迹内秩阈值 | 0.95 | [1] | 仅保留每个轨迹中排名前 5% 的变异 |
| per_track 约束 | 各轨迹独立标准化 | [1] | 不跨轨迹混合原始值 |
| 背景匹配规则 | 按染色体、等位基因频率 | [1] | 确保背景分布可比 |
| 聚合策略 | max / mean / weighted | [1] | 跨轨迹聚合方式 |

## MAD=0 回退规则详解

当计算得到的 MAD = 0 时（即所有观测值相同或中位数附近的偏差为零），robust z-score 公式的分母为零，无法直接计算。回退策略：

1. **使用标准差替代**：z = (x - mean) / std，适用于数据有方差但 MAD 恰好为零的场景
2. **标记为不可标准化**：在适用边界报告中记录该轨迹为 MAD=0，跳过标准化
3. **添加微小扰动**：z = (x - median) / (MAD + epsilon)，epsilon 为极小值（不推荐，可能引入偏差）

## 边界与分流

- **背景变异集不足**：报告警告，使用全基因组随机变异作为替代背景
- **某轨迹 MAD=0**：触发回退规则，记录到报告
- **所有轨迹均不可标准化**：标记 BLOCKED，提供原始效应值
- **聚合策略选择不确定**：默认使用 max（最保守）

## 质量检查

| 检查项 | 阈值 | 失败处理 |
|--------|------|----------|
| MAD > 0 | 各轨迹独立检查 | 触发回退规则 |
| z-score 范围 | 通常 [-5, 5] | 异常值检查 |
| 秩百分位范围 | [0, 1] | 计算验证 |
| 筛选后变异数 | ≥ 1 | 降低阈值或报告 |
| 背景样本量 | ≥ 100 | 使用替代背景 |

## 回退策略

- MAD=0 → 使用 std 或标记 skip
- 背景变异集缺失 → 从公共 VCF 生成随机背景
- 标准化后无变异通过筛选 → 降低效应阈值并记录

## 资源召回建议

- 当任务需要对多轨迹效应值进行跨可比性标准化时召回本卡
- 配套资源：AlphaGenome 模型配置卡（bio-alphagenome-regulatory-variant-model）

## 证据来源

[1] "Advancing regulatory variant effect prediction with AlphaGenome", Avsec et al., Nature, 2026, DOI: 10.1038/s41586-025-10014-0
[2] "GTEx pro enables accurate multi-tissue gene expression analysis using robust normalization and batch correction", Jothi, Scientific Reports, 2025, DOI: 10.1038/s41598-025-20697-0
[3] "Robust and rigorous identification of tissue-specific genes by statistically extending tau score", Lüleci & Yılmaz, BioData Mining, 2022, DOI: 10.1186/s13040-022-00315-9
