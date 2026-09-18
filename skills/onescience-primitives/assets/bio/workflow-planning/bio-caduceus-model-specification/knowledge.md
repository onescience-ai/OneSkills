# Caduceus DNA基础模型规格

## 适用范围

适用于需要选择、获取和部署Caduceus系列DNA基础模型的场景，包括模型权重下载、架构理解、变体选择（Caduceus-Ph vs Caduceus-PS）、反向互补等变性实现验证等。Caduceus是首个支持反向互补等变性的双向长程DNA语言模型，适用于需要同时考虑DNA正反链信息的任务。

## 输入

- **模型选择需求**：任务类型（分类/回归）、输入序列长度、计算资源限制
- **权重文件**：caduceus.ckpt（PyTorch checkpoint格式）
- **模型架构**：BiMamba（双向）+ MambaDNA（RC等变）

## 输出

- **加载的模型**：可用于推理的Caduceus模型实例
- **序列表示**：256维嵌入向量（mean token pooling后）
- **预测结果**：根据下游任务输出分类概率或回归分数

## 流程节点

### 1. 权重获取
1. **HuggingFace Hub**：访问https://huggingface.co/MicPie/caduceus
2. **GitHub Releases**：访问https://github.com/MicPie/caduceus/releases
3. **下载checkpoint**：选择Caduceus-Ph-131K（最大上下文版本）
4. **验证文件完整性**：检查文件大小和MD5校验

### 2. 变体选择
1. **Caduceus-Ph**：预训练于人类参考基因组，适用于人类基因组任务
2. **Caduceus-PS**：预训练于多物种基因组，适用于跨物种泛化任务
3. **选择依据**：单物种任务选Ph，跨物种任务选PS

### 3. 模型加载与验证
1. 加载checkpoint：`checkpoint = torch.load('caduceus.ckpt')`
2. 初始化模型：`model = Caduceus(...)`
3. 加载权重：`model.load_state_dict(checkpoint)`
4. 验证无key mismatch错误

### 4. RC等变性验证
1. 对输入序列x计算前向传播：`y1 = model(x)`
2. 对x施加RC变换：`x_rc = RC(x)`（反向+互补）
3. 对x_rc计算前向传播：`y2 = model(x_rc)`
4. 验证y2 = RC(y1)（等变性条件）

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型参数量 | ~35M | [2] | Caduceus-Ph可训练参数 |
| 嵌入维度 | 256 | [2] | 输出嵌入向量维度 |
| 最大输入长度 | 131,072 bp | [1] | 支持的最大序列长度 |
| 架构 | BiMamba + MambaDNA | [1] | 双向+RC等变模块 |
| 预训练数据 | 人类参考基因组 | [2] | Caduceus-Ph训练数据 |
| 发表会议 | ICML 2024 | [1] | 顶会论文 |
| GitHub仓库 | MicPie/caduceus | [1] | 代码和权重 |

## 边界与分流

- **权重文件缺失**：无法从HuggingFace/GitHub下载时，可使用随机初始化训练，但需更多数据
- **mamba-ssm依赖问题**：Windows环境需WSL2或conda-forge安装，否则丧失选择性扫描能力
- **输入超长时**：超过131Kbp需分块处理，分块间需保持坐标连续性
- **RC等变性不满足**：检查MambaDNA模块是否正确实现碱基互补映射（A↔T, C↔G）

## 质量检查

- 权重加载：model.load_state_dict(checkpoint)无key mismatch
- 推理验证：输入已知序列，输出嵌入维度为256
- RC等变性：验证model(RC(x)) ≈ RC(model(x))
- GPU内存：131K输入约需16GB显存（A100）

## 回退策略

- Caduceus不可用时：使用HyenaDNA（支持更长输入但无RC等变性）或DNABERT-2（Transformer架构）
- 权重下载失败时：从论文提供的GitHub仓库手动下载
- RC等变性实现困难时：使用后验拼接方式（post-hoc conjoining）在推理时合并正反链预测

## 资源召回建议

- 当任务需要双向等变DNA序列建模时召回本卡片
- 当需要长程依赖建模（>100kb）时优先考虑Caduceus-Ph
- 当需要跨物种泛化时选择Caduceus-PS
- 配合bio-dna-long-range-modeling-workflow卡片使用

## 证据来源

[1] Schiff Y, Kao CH, Gokaslan A, Dao T, Gu A, Kuleshov V. Caduceus: Bi-Directional Equivariant Long-Range DNA Sequence Modeling. ICML 2024. arXiv:2403.03234.
[2] Feng H, Wu L, Zhao B. Benchmarking DNA foundation models for genomic and genetic tasks. Nature Communications, 2025. DOI: 10.1038/s41467-025-65823-8.
