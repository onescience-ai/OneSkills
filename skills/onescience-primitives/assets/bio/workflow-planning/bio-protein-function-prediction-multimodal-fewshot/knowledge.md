# 低样本多模态蛋白功能预测工作流规划

## 适用范围

本卡面向蛋白质功能预测任务，覆盖从数据获取、多模态特征提取、few-shot学习到模型评估的完整工作流。适用于需要整合蛋白质序列、结构特征和功能文本描述进行功能注释预测的场景，特别针对训练样本稀缺（few-shot）的情况。

## 输入

- 蛋白质序列数据（氨基酸序列，标准20种氨基酸）
- 蛋白质结构特征（可选：AlphaFold2 pLDDT分数、二级结构、接触图）
- 功能文本描述（可选：PubMed文献摘要、功能注释文本）
- 目标功能标签（Gene Ontology术语：BP/MF/CC三个命名空间）

## 输出

- 功能预测模型（多模态融合架构）
- 预测结果（多标签分类概率、GO术语注释）
- 评估指标（per-class F1、macro/micro/weighted F1、AUPRC）
- 模型检查点（符合命名契约的权重文件）

## 流程节点

### 1. 数据获取与预处理

#### 1.1 公开数据集获取
- **CAFA挑战赛数据集**：标准蛋白质功能预测基准，包含多个版本（CAFA 1-5）
  - 数据格式：FASTA序列 + GO注释
  - 获取方式：https://www.biofunctionprediction.org/cafa/
  - 包含训练集、测试集和评估基准 [D1]
- **UniProtKB数据库**：权威蛋白质序列和功能注释源
  - REST API查询：https://rest.uniprot.org/uniprotkb/
  - 批量下载：https://www.uniprot.org/downloads
  - 关键字段：sequence、go_terms、ec_numbers、pfam_domains [D2]
- **Gene Ontology本体**：标准功能注释体系
  - OBO文件下载：https://current.geneontology.org/ontology/go.obo
  - 三个命名空间：Biological Process (BP)、Molecular Function (MF)、Cellular Component (CC)

#### 1.2 数据格式规范
- 输入CSV列定义：protein_id, sequence, structure_features, go_labels
- 序列字符合法性：仅允许ACDEFGHIKLMNPQRSTVWY（20种标准氨基酸）
- GO标签去重规则：同一功能描述不应对应多个GO ID

#### 1.3 数据切分策略
- **分层抽样**：使用sklearn.model_selection.train_test_split的stratify参数
- **多标签分层**：基于标签组合或单标签分层确保各类别分布一致
- **few-shot要求**：每个GO类别在各子集中至少有1个样本

### 2. 多模态特征提取

#### 2.1 序列编码器（ESM-2集成）
- **模型选择**：
  - ESM-2 (650M参数)：esm.pretrained.esm2_t33_650M_UR50D()
  - ESM-2 (3B参数)：esm.pretrained.esm2_t36_3B_UR50D()
- **输入格式**：
  - Tokenize：首位token + 氨基酸序列 + 末位token
  - 支持最大长度：512-2048（取决于模型版本）
  - Padding：统一到batch内最长序列
- **输出表征**：
  - Per-residue embeddings：(seq_len, hidden_dim)
  - Sequence embedding：平均池化得到固定维度向量
  - hidden_dim：ESM-2 (650M)为1280，ESM-2 (3B)为2560 [1]

#### 2.2 结构编码器（AlphaFold2特征提取）
- **特征类型**：pLDDT分数（每个残基的置信度分数）
- **提取方式**：从AlphaFold2预测的PDB文件中提取b_factor
- **维度**：每个残基1维标量，序列长度维度 [1]

#### 2.3 文本编码器（PubMedBERT集成）
- **模型**：microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext
- **输入**：蛋白质功能描述文本、文献摘要
- **输出**：[CLS] token embedding作为文本表征
- **维度**：768维 [1]

#### 2.4 多模态融合
- **融合方式**：拼接（concatenation）或注意力融合
- **输入维度**：ESM-2 (1280) + AlphaFold2 (seq_len) + PubMedBERT (768)
- **融合层**：线性层将拼接向量映射到统一维度

### 3. Few-shot学习策略

#### 3.1 数据增强
- **序列增强**：随机掩码、氨基酸替换、序列截断
- **结构增强**：pLDDT分数扰动
- **文本增强**：同义词替换、文本截断

#### 3.2 模型架构
- **元学习框架**：Prototypical Networks / MAML
- **度量学习**：学习样本间距离度量
- **标签传播**：利用GO层级关系进行标签传播

### 4. 训练配置

#### 4.1 超参数设置
| 参数 | 标准值 | 说明 |
|------|--------|------|
| batch_size | 32 | 批次大小 |
| learning_rate | 1e-4 | 学习率 |
| num_epochs | 50 | 训练轮数 |
| max_seq_len | 1024 | 最大序列长度 |
| random_seed | 11 | 随机种子 |
| threshold | 0.5 | 预测阈值 |

#### 4.2 权重文件命名契约
- **标准命名**：multimodal_protein.pt
- **存储路径**：checkpoints/multimodal_protein.pt
- **内容要求**：必须为预训练模型权重，非随机初始化

#### 4.3 可复现性规范
- 固定所有随机种子：
  - numpy.random.seed(seed)
  - torch.manual_seed(seed)
  - torch.cuda.manual_seed_all(seed)
  - torch.backends.cudnn.deterministic = True
- 设置PYTHONHASHSEED环境变量

### 5. 评估与验证

#### 5.1 分层评估指标
- **per-class F1**：每个GO类别的F1分数
- **macro F1**：各类别F1的平均值（对类别不平衡敏感）
- **micro F1**：全局TP/FP/FN计算的F1
- **weighted F1**：按类别样本数加权的F1
- **AUPRC**：每类别的精确率-召回率曲线下面积

#### 5.2 不确定度估计
- **Bootstrap置信区间**：重采样计算指标的95%置信区间
- **Dropout MC**：多次前向传播估计预测方差
- **适用域声明**：明确模型在哪些功能类别上可靠

#### 5.3 跨家族泛化评估
- **数据划分**：按蛋白质家族划分训练/测试集
- **评估内容**：模型在未见家族上的泛化能力
- **报告格式**：按家族分层的性能表格

### 6. 质量门禁判定

#### 6.1 验收指标阈值
- **macro_f1_score > 0.7**：硬性门槛，低于此阈值标记为REJECT
- **其他指标**：参考具体任务要求

#### 6.2 质量门禁状态定义
- **PASS**：完全满足所有验收条件
- **PARTIAL**：部分满足，有改进空间
- **REJECT**：不满足核心验收指标
- **BLOCKED**：无法执行（依赖缺失、环境问题等）

## 关键参数

### 通用判据（方法层）

| 参数 | 判据 | 来源 | 说明 |
|------|------|------|------|
| 序列长度覆盖 | max_seq_len ≥ 1024可覆盖大部分蛋白 | [1] | 典型蛋白长度100-3000氨基酸 |
| ESM-2输入长度 | 512-2048（取决于模型版本） | [1] | 超长序列需分块处理 |
| GO标签唯一性 | 同一功能描述对应唯一GO ID | [D1] | 通过官方OBO文件验证 |
| 分层抽样 | 各类别在子集中分布一致 | 标准实践 | 避免类别缺失 |

### 校准数值（体系专属）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| ESM-2 (650M) hidden_dim | 1280 | [1] | 序列编码器输出维度 |
| ESM-2 (3B) hidden_dim | 2560 | [1] | 大模型输出维度 |
| PubMedBERT hidden_dim | 768 | [1] | 文本编码器输出维度 |
| 标准batch_size | 32 | 任务规范 | 默认批次大小 |
| 标准random_seed | 11 | 任务规范 | 确保可复现 |
| 标准max_seq_len | 1024 | 任务规范 | 序列长度上限 |

## 边界与分流

### 前提否定即改道
1. **若预训练模型不可用**：转向从头训练的简化架构（需明确标注性能预期下降）
2. **若公开数据集不可获取**：使用用户自有数据（需通过脱敏扫描和权威性验证）
3. **若计算资源不足**：使用ESM-2小模型版本（如esm2_t12_35M_UR50D）
4. **若GO注释不完整**：使用简化标签体系（需记录覆盖率和局限性）

### 异常处理
- 数据格式错误：返回具体错误信息和修正建议
- 模型加载失败：检查权重文件存在性和格式兼容性
- 训练中断：支持从checkpoint恢复训练

## 质量检查

### 验证点
1. **数据验证**：
   - GO ID在官方OBO文件中存在
   - 序列字符合法性检查
   - 标签唯一性验证
2. **模型验证**：
   - ESM-2权重加载成功
   - forward pass输出维度匹配
   - 多模态特征融合正确
3. **评估验证**：
   - 分层指标计算正确
   - 置信区间估计合理
   - 跨家族泛化评估完整

### 阈值
- macro_f1_score > 0.7（硬性门槛）
- 每个GO类别至少1个测试样本
- 置信区间宽度 < 0.1

### 失败处理
- 数据验证失败：返回错误详情和修正建议
- 模型验证失败：检查权重文件和模型架构
- 评估失败：重新划分数据集或调整评估参数

## 回退策略

### 数据获取失败
- 回退到CAFA挑战赛标准数据集
- 使用UniProtKB子集作为替代
- 生成合成数据（需明确标注并记录局限性）

### 模型集成失败
- 回退到单一模态（仅序列）
- 使用传统机器学习方法（如SVM+序列特征）
- 降级到简化GRU+MLP架构（需记录性能预期）

### 评估失败
- 使用替代评估指标（如accuracy、hamming loss）
- 简化评估维度（仅macro F1）
- 跳过跨家族泛化评估（需记录局限性）

## 资源召回建议

### 何时召回本卡片
- 任务涉及蛋白质功能预测
- 需要整合多模态数据（序列、结构、文本）
- 训练样本稀缺（few-shot场景）
- 需要符合CAFA/UniProt标准的工作流

### 配套资源
- onescience-primitives中的蛋白质序列数据集原语
- onescience-primitives中的ESM-2/AlphaFold2模型原语
- onescience-coder用于代码生成
- onescience-runtime用于训练执行

## 证据来源

[1] Lin, Z. et al. "Evolutionary-scale prediction of atomic-level protein structure with a language model." Science 379, 1123-1130 (2023). DOI: 10.1126/science.ade2574

[2] Rives, A. et al. "Biological structure and function emerge from scaling unsupervised learning to 250 million protein sequences." PNAS 118(15), e2016239118 (2021). DOI: 10.1073/pnas.2016239118

[3] Meier, J. et al. "Language models enable zero-shot prediction of the effects of mutations on protein function." bioRxiv (2021). DOI: 10.1101/2021.07.09.450648

[D1] CAFA Challenge Official Website. Function-SIG, 2024. URL: https://www.biofunctionprediction.org/cafa/

[D2] UniProt Consortium. UniProt: the Universal Protein Knowledgebase. 2024. URL: https://www.uniprot.org/