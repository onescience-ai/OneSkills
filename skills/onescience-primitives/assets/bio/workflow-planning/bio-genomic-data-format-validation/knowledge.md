# 基因组数据格式验证规范

## 适用范围
本卡片提供基因组数据格式验证的通用规范，包括BED格式字段定义与坐标系统、VCF格式REF/ALT等位基因合法性检查、参考基因组FASTA文件验证规则。适用于小鼠mm10 (GRCm38)等参考基因组的增强子区间、变异文件的数据质控。

## 输入
- BED格式文件（增强子区间、基因注释等）
- VCF格式文件（变异调用结果）
- 参考基因组FASTA文件（如mm10_reference.fasta）

## 输出
- 格式验证报告（每个文件的验证状态）
- 坐标质控报告（坐标系统一致性检查）
- 数据质量评估（字段完整性、合法性检查）

## 流程节点

### 步骤1：BED格式验证
- **操作**：验证BED文件字段完整性和坐标有效性
- **参数**：必需字段（chrom, chromStart, chromEnd）、可选字段（name, score, strand等）
- **工具**：自定义BED验证函数或bedtools
- **质量门禁**：所有记录包含必需字段、chromStart < chromEnd、chrom在参考范围内

### 步骤2：VCF格式验证
- **操作**：验证VCF文件格式规范和字段合法性
- **参数**：VCF 4.3+格式、CHROM/POS/ID/REF/ALT字段完整性
- **工具**：pysam或bcftools
- **质量门禁**：POS为正整数、REF/ALT为合法DNA字符（ACGTN）、REF与参考基因组匹配

### 步骤3：参考基因组验证
- **操作**：验证FASTA文件格式和染色体完整性
- **参数**：FASTA文件可读性、染色体命名规范（chr1-chrY/chrM）
- **工具**：samtools faidx或自定义验证
- **质量门禁**：文件可读、染色体计数正确、碱基字符合法（ATCGN）

### 步骤4：坐标系统一致性检查
- **操作**：验证不同文件间的坐标系统一致性
- **参数**：BED 0-based half-open、VCF 1-based inclusive
- **工具**：坐标转换函数
- **质量门禁**：坐标转换正确、无越界记录

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| BED坐标系统 | 0-based half-open [start, end) | [UCSC] | chromStart包含，chromEnd不包含 |
| VCF坐标系统 | 1-based inclusive [POS, POS] | [VCF规范] | POS从1开始计数 |
| 合法碱基字符 | A, C, G, T, N | [VCF规范] | REF/ALT字段 |
| BED必需字段 | chrom, chromStart, chromEnd | [UCSC] | 最少3列 |
| BED可选字段 | name, score, strand, thickStart, thickEnd, itemRgb, blockCount, blockSizes, blockStarts | [UCSC] | 最多12列 |

### 校准数值（mm10参考基因组）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| mm10染色体命名 | chr1-chr19, chrX, chrY, chrM | [UCSC] | 小鼠GRCm38参考基因组 |
| mm10 FASTA来源 | UCSC Genome Browser | [UCSC] | mm10.2bit或FASTA格式 |
| VCF版本要求 | 4.3+ | [VCF规范] | 标准格式要求 |
| 坐标转换公式 | browser_start = chromStart + 1, browser_end = chromEnd | [UCSC] | BED到浏览器坐标转换 |

## 边界与分流
- **BED字段缺失**：补充缺失字段为"."（如name字段为空时）
- **VCF格式不兼容**：尝试使用bcftools进行格式转换
- **坐标系统不一致**：执行坐标转换后重新验证
- **参考基因组缺失**：从UCSC或Ensembl下载对应版本

## 质量检查
- 验证BED文件每行字段数一致（3-12列）
- 检查BED文件chromStart < chromEnd
- 验证VCF文件header包含contig定义
- 检查VCF文件POS为正整数且在染色体长度范围内
- 确认REF/ALT字段非空且仅含合法字符
- 验证FASTA文件染色体命名符合规范

## 回退策略
- BED验证失败时尝试使用bedtools sort进行排序
- VCF验证失败时尝试使用bcftools view进行过滤
- 参考基因组验证失败时使用硬编码参考序列
- 坐标验证失败时标记但继续处理其他记录

## 资源召回建议
- 何时应召回本卡片：处理基因组数据格式验证、坐标系统转换、参考基因组文件验证
- 配套资源：UCSC Genome Browser、samtools、pysam、bedtools

## 补充证据（开源文档）
[D1] UCSC Genome Browser FAQ: BED format, UCSC Genome Browser, 2026, URL: https://genome.ucsc.edu/FAQ/FAQformat.html（accessed_at，权威文档）

## 证据来源
[1] UCSC Genome Browser FAQ: BED format, UCSC Genome Browser, 2026, URL: https://genome.ucsc.edu/FAQ/FAQformat.html