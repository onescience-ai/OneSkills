# 单细胞基础模型预训练权重获取方法

## 适用范围
适用于需要获取Geneformer、scGPT等单细胞基础模型预训练权重进行下游任务（细胞类型分类、扰动预测、表征提取等）的场景。包括权重下载、架构验证、输入格式适配和许可证确认。

## 输入
- 目标模型名称（Geneformer/scGPT/Mouse-Geneformer等）
- 目标物种（human/mouse）
- 下游任务类型（分类/回归/扰动预测等）
- 计算资源要求（GPU内存、训练时间）

## 输出
- 可加载的模型权重文件
- 模型架构配置信息
- 输入格式说明（tokenization方法、最大序列长度）
- 许可证和使用条款

## 流程节点
1. 模型选择 → 2. 权重下载 → 3. 架构验证 → 4. 输入适配 → 5. 加载测试

### 1. 模型选择
根据任务需求选择合适的模型：

| 模型 | 架构 | 预训练数据 | 特点 | 来源 |
|------|------|-----------|------|------|
| Geneformer (Human) | BERT-like | ~30M human cells | Rank Value Encoding, 18层Transformer | HuggingFace: ctheodoris/Genecorpus-30M [1] |
| Mouse-Geneformer | BERT-like | ~21M mouse cells | 同Geneformer架构，SiLU激活函数 | HuggingFace: MPRG/Mouse-Genecorpus-20M [1] |
| scGPT | GPT-like | ~33M human cells | 支持多组学，零样本能力强 | GitHub: bowang-lab/scGPT [1] |
| GFCAB | BERT-like (增强) | 1M/30M cells | 累积分配+相似性正则化 | GitHub (论文附带) [2] |

### 2. 权重下载
**Geneformer系列（HuggingFace）**：
```bash
# 人类版本
from huggingface_hub import snapshot_download
snapshot_download(repo_id="ctheodoris/Genecorpus-30M", local_dir="./geneformer_weights")

# 小鼠版本
snapshot_download(repo_id="MPRG/Mouse-Genecorpus-20M", local_dir="./mouse_geneformer_weights")
```
- 需要安装 `huggingface_hub` 库
- 首次下载可能需要较长时间（模型文件较大）
- 建议使用 `cache_dir` 参数指定下载目录

**scGPT（GitHub）**：
```bash
git clone https://github.com/bowang-lab/scGPT.git
# 预训练权重在 models/ 目录下
```

### 3. 架构验证
- **Geneformer**：6层Transformer Encoder，4个注意力头，256维嵌入，512维前馈层，最大输入长度2048 [1][3]
- **scGPT**：GPT风格Transformer，支持最大2048个基因token
- **GFCAB**：同Geneformer架构 + CAB模块（累积分配+相似性正则化）[2]
- 验证模型参数数量：Geneformer约316M参数 [3]

### 4. 输入适配
**Geneformer输入格式（Rank Value Encoding）**：
1. 获取单细胞基因表达数据（AnnData对象）
2. 对每个细胞，按表达量降序排列基因
3. 将基因名转换为token ID（使用模型自带的基因词汇表）
4. 生成"cell sentences"：基因名作为token的序列
5. 添加[CLS]标记用于分类任务
6. 填充或截断至固定长度（默认1024）[1][3]

**scGPT输入格式**：
1. 基因表达值直接作为数值输入
2. 支持多种tokenization策略
3. 可选的基因嵌入层

**关键预处理要求**：
- 基因标识符需与模型词汇表匹配（Ensembl ID vs Gene Symbol）
- 输入数值必须为有限值（无NaN/Inf）
- 线粒体基因、核糖体基因的处理策略需一致

### 5. 加载测试
```python
# Geneformer加载示例
from transformers import BertForSequenceClassification
model = BertForSequenceClassification.from_pretrained("./geneformer_weights")

# 验证输入输出维度
import torch
dummy_input = torch.randint(0, 1000, (1, 1024))  # batch=1, seq_len=1024
output = model(dummy_input)
print(output.logits.shape)  # 应为 (1, num_classes)
```

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Geneformer层数 | 18层Transformer | [1][3] | 编码器层数 |
| 注意力头数 | 4 | [1] | 多头注意力 |
| 嵌入维度 | 256 | [1] | 隐藏层维度 |
| 最大序列长度 | 2048 | [1][3] | 基因token最大数 |
| 训练GPU | 8×V100 32GB | [1] | 预训练资源 |
| 预训练时间 | ~2天 | [1] | 8 GPU条件 |
| 基因词汇表大小 | ~60,000 | [1] | 包含所有Ensembl ID |

## 边界与分流
- **GPU内存不足**：使用模型并行或减少batch size；Gene-Chronos仅需0.4GB（冻结骨干+适配器）[3]
- **基因标识符不匹配**：使用MGI/HGNC数据库进行物种间基因名转换 [1]
- **许可证限制**：Geneformer使用CC-BY-NC-SA-4.0；scGPT使用MIT License
- **模型版本不兼容**：检查transformers库版本与模型要求的兼容性

## 质量检查
- 验证权重文件完整性（文件大小、SHA256校验）
- 确认模型可成功加载（无权重缺失警告）
- 测试前向传播输出维度正确
- 检查推理时间是否在预期范围内

## 回退策略
- 若HuggingFace不可用，使用镜像站点或手动下载
- 若scGPT GitHub不可用，尝试PyPI安装 `pip install scgpt`
- 若GPU资源不足，使用CPU推理（速度较慢）或冻结大部分层

## 资源召回建议
- 需要获取单细胞模型权重时召回本卡
- 配套使用：single-cell-rna-seq-dataset-access（数据获取）、single-cell-model-evaluation（评测方法）

## 证据来源
[1] Ito K et al. Mouse-Geneformer: A deep learning model for mouse single-cell transcriptome and its cross-species utility. PLOS Genetics, 2025, DOI: 10.1371/journal.pgen.1011420
[2] Chen J et al. Assessing scale and predictive diversity in models for single-cell transcriptomics based on Geneformer. PLOS Computational Biology, 2026, DOI: 10.1371/journal.pcbi.1013701
[3] Liu Y et al. Gene-Chronos: parameter-efficient developmental time inference using a pretrained single-cell foundation model. Briefings in Bioinformatics, 2026, DOI: 10.1093/bib/bbag469
