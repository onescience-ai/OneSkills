# VCF文件解析与坐标验证

## 适用范围
- 触发条件：输入数据为VCF格式变异文件，需验证坐标有效性和参考等位基因匹配
- 适用场景：BRCA1调控变异预测、变异效应分析、基因组坐标验证
- 不适用场景：非VCF格式输入、非GRCh38参考基因组、已验证的标准化数据

## 输入
- VCF文件（VCF 4.3+格式），包含CHROM/POS/ID/REF/ALT标准列
- GRCh38参考基因组FASTA文件
- 目标基因坐标区间（如BRCA1: chr17:43044295-43125483, 1-based inclusive）

## 输出
- 标准化变异表（含chrom/pos/ref/alt/valid/ref_match/bounds_check字段）
- 坐标质控报告（每个变异的验证状态）
- VCF解析状态（PARSED/SIMULATED/FAILED）

## 流程节点

### 步骤1：VCF文件解析
- **操作**：使用pysam或自定义解析器读取VCF文件
- **参数**：VCF文件路径、header解析模式
- **工具**：pysam.VariantFile 或自定义VCFParser
- **质量门禁**：成功解析header和所有变异记录

### 步骤2：坐标有效性验证
- **操作**：验证每个变异的坐标格式和值范围
- **参数**：POS为1-based整数、REF/ALT为合法DNA字符（ACGTN）
- **工具**：自定义验证函数
- **质量门禁**：所有变异POS为正整数、REF/ALT仅含合法字符

### 步骤3：参考等位基因匹配
- **操作**：从FASTA提取变异位置序列与REF字段比对
- **参数**：变异位置、FASTA文件路径
- **工具**：pysam.FastaFile.fetch()
- **质量门禁**：提取的序列与REF字段完全匹配

### 步骤4：区间边界检查
- **操作**：验证变异POS是否在目标基因坐标范围内
- **参数**：基因起止坐标（如chr17:43044295-43125483）
- **工具**：自定义边界检查函数
- **质量门禁**：变异POS在[start, end]范围内

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| VCF版本 | 4.3+ | [VCF规范] | 标准格式要求 |
| 坐标系统 | 1-based inclusive | [VCF规范] | POS从1开始计数 |
| 合法碱基字符 | A, C, G, T, N | [VCF规范] | REF/ALT字段 |
| BRCA1坐标 | chr17:43044295-43125483 | [GRCh38] | 基因组区间（1-based） |
| 参考基因组 | GRCh38/hg38 | [NCBI] | 人类最新参考基因组 |

## 边界与分流
- **VCF解析失败**：记录错误日志，标记为FAILED状态
- **坐标越界**：标记bounds_check=FAIL，跳过后续验证
- **参考等位基因不匹配**：标记ref_match=FAIL，记录实际值
- **多等位基因变异**：仅处理第一个ALT等位基因

## 质量检查
- 验证VCF header包含contig定义
- 检查POS为正整数且在染色体长度范围内
- 确认REF/ALT字段非空且仅含合法字符
- 验证参考等位基因与FASTA序列一致

## 回退策略
- VCF解析失败时尝试使用bcftools工具解析
- 参考等位基因验证失败时使用硬编码参考序列
- 坐标验证失败时标记但继续处理其他变异

## 资源召回建议
- 何时应召回本卡片：处理VCF格式输入数据、验证变异坐标有效性
- 配套资源：GRCh38参考基因组、BRCA1基因注释、pysam库

## 证据来源
[1] Twelve years of SAMtools and BCFtools, Li H., GigaScience, 2021, DOI: 10.1093/gigascience/giab008
[2] A spectrum of free software tools for processing the VCF variant call format, Linard L., PLoS Computational Biology, 2022, DOI: 10.1371/journal.pcbi.1010303
[3] Standards and Guidelines for the Interpretation and Reporting of Sequence Variants, Richards S., Journal of Molecular Diagnostics, 2016, DOI: 10.1016/j.jmoldx.2015.12.004
[4] VCF-Miner: GUI-based application for mining variants and annotations stored in VCF files, Hart R.K., Briefings in Bioinformatics, 2015, DOI: 10.1093/biv080