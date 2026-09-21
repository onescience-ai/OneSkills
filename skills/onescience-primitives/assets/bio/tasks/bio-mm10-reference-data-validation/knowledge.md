# 小鼠 mm10 参考基因组与增强子数据验证

## 适用范围

**触发条件**：
- 需要以 mm10 (GRCm38) 参考基因组为基准进行增强子变异分析
- 需要验证 FASTA、BED、VCF 文件的格式合法性和数据完整性
- 需要在不同基因组坐标体系之间进行转换（0-based half-open ↔ 1-based inclusive）

**适用场景**：
- 小鼠增强子变异的组织特异调控预测（如 AlphaGenome 输入数据准备）
- 基因组坐标质控（染色体命名、链方向、start<end 校验）
- 变异与增强子区间的邻域包含性检查

**不适用场景**：
- 非 mm10 物种的参考基因组验证（需替换染色体列表和版本号）
- 蛋白质序列或 RNA 序列的格式验证

## 输入

| 输入文件 | 格式要求 | 来源 |
|----------|----------|------|
| mm10_reference.fasta | 2-bit 或 multi-line FASTA，染色体命名 chr1-chr19/chrX/chrY/chrM | UCSC mm10 下载或本地已有 |
| mm10_liver_brain_enhancers.bed | BED6+ 格式：chrom/start/end/name/score/strand | ENCODE/FANTOM5 或项目提供 |
| mm10_enhancer_variants.vcf | VCF 4.3+ 格式，含 CHROM/POS/ID/REF/ALT/FILTER/INFO 字段 | 项目提供 |

## 输出

| 输出产物 | 格式 | 验证标准 |
|----------|------|----------|
| 验证后的增强子表 | BED6+ | chrom 在参考范围内、start<end、strand 为 +/-/. |
| 变异窗口 | 区间列表 | 变异位于 BED 邻域内、坐标可追溯 |
| 坐标质控报告 | JSON | 含 MD5、染色体列表、邻域包含性检查结果 |

## 流程节点

### Step 1：FASTA 验证
- **操作**：检查文件可读性、染色体计数、碱基字符合法性、MD5 完整性
- **参数**：期望染色体数=21（chr1-chr19/chrX/chrY/chrM），碱基字符集=[ATCGN]
- **工具**：自定义 ReferenceGenomeVerifier 或 samtools faidx
- **质量门禁**：所有染色体均存在、无非法字符、MD5 匹配

### Step 2：BED 验证
- **操作**：检查字段完整性、坐标合法性、链方向
- **参数**：chrom 在 FASTA 染色体列表中、start<end（0-based）、strand ∈ {+, -, .}
- **工具**：自定义 BedValidator 或 bedtools
- **质量门禁**：无越界坐标、无空 strand、无重叠区间警告

### Step 3：VCF 验证
- **操作**：检查 CHROM/POS/ID/REF/ALT 字段完整性、等位基因合法性
- **参数**：POS>0、REF 和 ALT ∈ [ATCGN]+、FILTER 为 PASS 或具体过滤标签
- **工具**：vcftools 或自定义 VcfValidator
- **质量门禁**：无缺失字段、REF/ALT 为合法核苷酸序列

### Step 4：坐标一致性检查
- **操作**：验证 VCF 变异是否落在 BED 增强子区间的邻域内
- **参数**：邻域窗口大小（如 ±500bp）、坐标体系对齐（BED 为 0-based half-open）
- **工具**：bedtools intersect 或自定义检查脚本
- **质量门禁**：所有变异均可追溯到至少一个增强子区间

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 参考基因组版本 | mm10 (GRCm38) | [1] | 小鼠参考基因组 |
| 染色体命名 | chr1-chr19, chrX, chrY, chrM | [1] | UCSC 风格命名 |
| FASTA 碱基字符集 | A, T, C, G, N | [1] | N 表示未知碱基 |
| BED 坐标体系 | 0-based half-open [start, end) | [2] | 与 UCSC 基因组浏览器一致 |
| VCF 版本 | 4.3+ | [3] | 支持多等位基因和结构变异 |
| VCF POS | 1-based inclusive | [3] | 与 BED 的 0-based 不同 |
| 坐标转换规则 | BED start = VCF POS - 1 | [2][3] | 0-based ↔ 1-based 转换 |
| 增强子邻域窗口 | ±500 bp（可配置） | [2] | 变异-BED 邻域包含性检查 |

## 边界与分流

- **FASTA 缺失或损坏**：标记 BLOCKED，从 UCSC Table Browser 下载 mm10 FASTA 或使用公共镜像
- **BED 文件非标准格式**：自动检测列数并尝试解析，失败时报告格式错误
- **VCF 含 indel 或 SV**：仅验证 SNV 的 REF/ALT 合法性，indel/SV 标记为"需人工审查"
- **坐标体系不一致**：检测 BED 和 VCF 的坐标体系并自动对齐，无法自动判断时输出警告

## 质量检查

| 检查项 | 阈值 | 失败处理 |
|--------|------|----------|
| FASTA 染色体完整性 | 21/21 全部存在 | 缺失染色体列报告，标记 BLOCKED |
| FASTA 碱基合法性 | 非法字符=0 | 定位非法字符位置并报告 |
| BED start<end | 100% 满足 | 报告违规行号 |
| VCF POS>0 | 100% 满足 | 报告违规行号 |
| VCF REF/ALT 合法性 | 非法序列=0 | 报告违规行号和序列 |
| 变异-BED 邻域包含 | 100% 命中（或报告未命中比例） | 未命中变异列表输出 |

## 回退策略

- mm10 FASTA 不可用 → 从 UCSC mm10 下载或使用 GRCm38.p6 版本
- 增强子 BED 不可用 → 从 ENCODE/FANTOM5 下载小鼠增强子注释
- VCF 验证工具不可用 → 使用 Python 自定义验证脚本

## 资源召回建议

- 当任务涉及小鼠基因组坐标操作时召回本卡
- 当需要验证基因组输入数据格式时召回本卡
- 配套资源：AlphaGenome 模型配置卡（bio-alphagenome-regulatory-variant-model）

## 证据来源

[1] "Advancing regulatory variant effect prediction with AlphaGenome", Avsec et al., Nature, 2026, DOI: 10.1038/s41586-025-10014-0
[2] "EAGLE: An algorithm that utilizes a small number of genomic features to predict tissue/cell type-specific enhancer-gene interactions", Gao & Qian, PLOS Computational Biology, 2019, DOI: 10.1371/journal.pcbi.1007436
[3] "A spectrum of free software tools for processing the VCF variant call format: vcflib, bio-vcf, cyvcf2, hts-nim and slivar", Garrison et al., PLOS Computational Biology, 2022, DOI: 10.1371/journal.pcbi.1009123
