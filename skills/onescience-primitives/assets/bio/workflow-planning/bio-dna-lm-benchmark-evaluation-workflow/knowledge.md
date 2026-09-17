# DNA语言模型基准评测工作流

## 适用范围

**触发条件**：
- 需要加载和评测DNABERT-2、Caduceus等DNA语言模型
- 需要在BEND基准上进行多模型对比分析
- 需要按多维度分层报告模型性能
- 需要建立完整的数据血缘追溯链

**适用场景**：
- DNA语言模型的基准评测和排名
- 模型在调控、剪接、染色质等任务上的性能对比
- 识别模型在不同基因组子集上的优势和劣势
- 评估模型的适用域和外推风险
- 建立可复现的评测流水线

**不适用场景**：
- 非DNA序列的模型评测
- 仅需要整体性能指标而不关心分层分析的场景
- 蛋白质或RNA语言模型评测

## 输入

- **模型权重**：DNABERT-2或Caduceus的预训练权重
- **评测数据**：BEND基准数据集（标准化基因组区间）
- **参考基因组**：hg38（GRCh38）
- **评测配置**：任务列表、分层维度、评估指标

## 输出

- **模型对比报告**：多模型在各任务上的性能对比表
- **分层性能报告**：按染色体/基因/物种/细胞类型/变异类别分层的性能指标
- **数据血缘记录**：从输入数据到最终结果的完整追溯链
- **模型适用域分析**：模型在哪些子集上表现良好或较差

## 流程节点

### Step 1：模型获取与加载
- **操作**：从官方源下载模型权重，配置GPU环境，加载模型
- **DNABERT-2**：从HuggingFace下载（Zhihan1996/DNABERT-2-117M），约3GB，需要16GB+ GPU内存
- **Caduceus**：从GitHub获取（kuleshov-group/caduceus），支持双向建模和反向互补等变性
- **参数**：上下文长度=131072（DNABERT-2），tokenization=BPE（DNABERT-2）
- **工具**：transformers库（DNABERT-2），PyTorch（Caduceus）
- **质量门禁**：模型加载成功，输出形状正确

### Step 2：序列输入准备
- **操作**：将BEND基因组区间转换为模型输入格式
- **参数**：序列长度=任务相关，正反链处理=根据模型特性
- **工具**：biopython, pandas
- **质量门禁**：输入序列数量与BEND测试集一致

### Step 3：模型推理
- **操作**：使用加载的模型对输入序列进行推理
- **参数**：batch_size=根据GPU内存调整，推理模式=eval
- **工具**：PyTorch, transformers
- **质量门禁**：所有样本推理完成，无NaN输出

### Step 4：分层性能评估
- **操作**：按多个维度分别计算性能指标
- **分层维度**：
  - 染色体（chr1-chr22, chrX, chrY）
  - 基因（按基因名或基因ID）
  - 物种（人类基因组内的不同区域类型）
  - 细胞类型（如适用）
  - 变异类别（SNP、InDel等）
- **评估指标**：AUC-ROC、Accuracy、Pearson Correlation、F1-Score等
- **工具**：scikit-learn, pandas
- **质量门禁**：每个分层维度的样本数≥30

### Step 5：数据血缘记录
- **操作**：记录从输入到输出的完整数据血缘
- **必需字段**：
  - 输入数据来源（URL/路径）
  - 输入数据版本（哈希值/版本号）
  - 模型名称和版本
  - 数据划分策略
  - 随机种子
  - 环境配置（Python版本、库版本）
  - 处理步骤和参数
- **工具**：execution-manifest.json模板
- **质量门禁**：所有字段非空，可追溯

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 上下文长度 | 131072 tokens | [1] | DNABERT-2支持的最长上下文 |
| Tokenization | BPE（字节对编码） | [1] | DNABERT-2使用4096词表的BPE |
| 模型参数量 | 约117M（DNABERT-2） | [1] | DNABERT-2-base版本 |
| GPU内存需求 | ≥16GB | [1] | 推理所需最小GPU内存 |
| 双向建模 | Caduceus支持 | [2] | Caduceus使用BiMamba实现双向 |
| RC等变性 | Caduceus支持 | [2] | Caduceus支持反向互补等变性 |
| 预洗牌要求 | 必须预洗牌 | [3] | 消除硬件相关的数据加载伪影 |

### 校准数值（来自DNA语言模型评测体系，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| DNABERT-2词表大小 | 4096 | [1] | BPE词表大小 |
| DNABERT-2上下文窗口 | 232 tokens（典型使用） | [1] | 实际评测中常用的上下文长度 |
| Caduceus参数量 | 约130M | [2] | Caduceus-base版本 |
| 分层评估最小样本 | ≥30 | [3] | 统计显著性要求 |

## 边界与分流

- **模型权重不可用**：检查HuggingFace/GitHub链接，确认网络连接
- **GPU内存不足**：减小batch_size或使用CPU推理（性能会降低）
- **数据格式不匹配**：使用数据预处理脚本转换格式
- **分层样本数不足**：合并相邻分层维度或报告"样本不足"标记

## 质量检查

- **检查点1**：模型加载成功且输出形状正确
- **检查点2**：推理结果无NaN或异常值
- **检查点3**：分层评估覆盖所有预定义维度
- **检查点4**：数据血缘记录完整且可追溯
- **失败处理**：任何检查失败则停止并报告具体错误

## 回退策略

- **方案A**：使用HuggingFace提供的标准推理脚本
- **方案B**：参考BEND官方代码库中的评测实现
- **方案C**：联系模型作者获取支持

## 资源召回建议

- 当用户需要评测DNA语言模型时，应召回本卡片
- 配套资源：BEND基准数据集卡片
- 配套技能：onescience-runtime（执行评测作业）

## 补充证据

[D1] DNABERT-2 HuggingFace Model Card, https://huggingface.co/Zhihan1996/DNABERT-2-117M（accessed 2026-09-16，官方模型卡）
[D2] Caduceus GitHub Repository, https://github.com/kuleshov-group/caduceus（accessed 2026-09-16，官方代码库）
[D3] DNABERT-2 GitHub Repository, https://github.com/Zhihan1996/DNABERT_2（accessed 2026-09-16，官方代码库）

## 证据来源

[1] "DNABERT-2: Efficient Foundation Model and Benchmark For Multi-Species Genome", Zhou et al., ICLR 2024, arXiv:2306.15006
[2] "Caduceus: Bi-Directional Equivariant Long-Range DNA Sequence Modeling", Schiff et al., ICML 2024, arXiv:2403.03234
[3] "BEND: Benchmarking DNA Language Models on biologically meaningful tasks", Marin et al., ICLR 2024, arXiv:2311.12570
