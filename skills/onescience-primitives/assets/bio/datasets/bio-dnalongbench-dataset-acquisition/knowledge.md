# 公开基因组DNA序列数据集获取

## 适用范围

**触发条件**：
- 需要获取真实基因组DNA序列数据用于模型训练或评估
- 需要DNALONGBENCH等标准基准数据集进行公平比较
- 需要从ENCODE/UCSC等权威数据库下载特定基因组区间数据

**适用场景**：
- DNA语言模型的训练与评估
- 基因组功能预测任务（增强子活性、变异效应、3D接触）
- 长程DNA序列建模的基准测试

**不适用场景**：
- 非基因组数据（如蛋白质、RNA序列）
- 需要私有或受控访问数据的任务
- 非人类物种的基因组数据（需额外参考基因组）

## 输入

**输入要求**：
- 参考基因组版本（如hg38、mm10）
- 目标基因组区间（染色体:起始-终止）
- 数据类型需求（DNA序列、功能标签、变异信息）

**预处理要求**：
- 安装samtools/bcftools（处理BAM/VCF文件）
- 安装bedtools（区间操作）
- 安装wget/curl（数据下载）

## 输出

**输出产物**：
- FASTA文件：包含真实基因组坐标的DNA序列
- 功能标签文件：增强子活性、变异效应等注释
- 数据清单：记录样本数、序列长度分布、标签分布

**验证标准**：
- 序列坐标位于hg38参考基因组有效范围内
- 序列长度分布合理（≥1000bp区间占比>80%）
- 功能标签与序列一一对应

## 流程节点

### Step 1：确定数据源
- **操作**：根据任务需求选择合适的数据源
- **参数**：DNALONGBENCH（标准基准）/ ENCODE（原始数据）/ UCSC（定制区间）
- **工具**：文献调研、数据库检索
- **质量门禁**：数据源与任务类型匹配

### Step 2：下载数据
- **操作**：从选定数据源下载原始数据
- **参数**：版本号、参考基因组、文件格式
- **工具**：wget/curl + HuggingFace API
- **质量门禁**：下载文件完整无损坏

### Step 3：格式转换
- **操作**：将原始数据转换为模型可用格式
- **参数**：FASTA格式、坐标规范化、标签编码
- **工具**：bedtools, samtools, Python脚本
- **质量门禁**：格式符合规范，无解析错误

### Step 4：数据验证
- **操作**：验证数据质量和完整性
- **参数**：样本数、序列长度、标签分布
- **工具**：Python统计脚本
- **质量门禁**：数据统计与预期一致

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 参考基因组 | hg38 | [1][2] | 人类基因组参考版本 |
| DNALONGBENCH | InstaDeepAI/genomics-long-range-benchmark | [2] | 标准基准数据集 |
| 序列长度范围 | 1,000 - 131,072 bp | [1] | 长程建模窗口 |
| 功能任务 | 增强子、变异效应、3D接触 | [2] | 5个长程DNA预测任务 |
| 数据格式 | FASTA + TSV/VCF | [1][2] | 序列+标签 |
| 数据规模 | ≥10,000样本 | [2] | 统计显著性 |

## 边界与分流

**异常处理**：
- 下载失败→尝试镜像源或联系数据管理员
- 数据格式不匹配→使用格式转换工具处理
- 坐标超出范围→检查参考基因组版本一致性

**降级策略**：
- 标准基准数据不可用→使用ENCODE原始数据自行构建
- 长程数据获取困难→使用短窗口数据作为过渡
- 私有数据无法获取→使用公开数据作为代理评估

**分支条件**：
- 任务为标准基准评估→使用DNALONGBENCH
- 任务为特定基因组区间→从ENCODE/UCSC定制下载
- 任务为训练数据→下载大规模基因组区间集

## 质量检查

**验证点**：
1. 数据下载完整：文件大小与预期一致
2. 格式解析正确：FASTA/TSV/VCF无语法错误
3. 坐标有效性：所有区间位于hg38有效范围
4. 标签一致性：功能标签与序列一一对应

**阈值**：
- 下载成功率：100%
- 格式解析成功率：100%
- 坐标有效率：100%
- 标签覆盖率：≥99%

## 回退策略

**失败替代方案**：
- 标准基准数据不可用→使用BEND或其他公开基准
- ENCODE数据获取困难→使用UCSC Table Browser导出
- 长程数据不足→使用滑动窗口生成合成数据

## 资源召回建议

**何时召回**：
- 任务需要真实基因组DNA数据
- 需要标准基准数据集进行公平评估
- 需要从权威数据库获取特定基因组区间

**配套资源**：
- Caduceus模型：需要真实数据进行训练/评估
- DNALONGBENCH：标准基准数据集
- BEND：DNA语言模型基准评测

## 证据来源

[1] "Caduceus: Bi-Directional Equivariant Long-Range DNA Sequence Modeling", Schiff et al., ICML 2024, DOI: 10.48550/arXiv.2403.03234

[2] "BEND: Benchmarking DNA Language Models on biologically meaningful tasks", Marin et al., ICLR 2024, DOI: 10.48550/arXiv.2311.12570

## 补充证据

[D1] "DNALONGBENCH Dataset on HuggingFace", InstaDeepAI, 2024, URL: https://huggingface.co/datasets/InstaDeepAI/genomics-long-range-benchmark（accessed 2026-09-21，标准基准数据集）

[D2] "ENCODE Project", ENCODE Consortium, latest, URL: https://www.encodeproject.org/（accessed 2026-09-21，权威基因组数据源）

[D3] "UCSC Genome Browser", UC Santa Cruz, hg38, URL: https://genome.ucsc.edu/（accessed 2026-09-21，基因组数据定制下载）