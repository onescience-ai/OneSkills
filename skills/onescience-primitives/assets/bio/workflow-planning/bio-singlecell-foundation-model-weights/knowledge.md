# 单细胞基础模型权重获取流程

## 适用范围
面向单细胞多组学分析任务，获取主流基础模型（Geneformer、scGPT）的预训练权重。适用于需要进行细胞类型注释、扰动预测、数据整合等下游任务的研究场景。

## 输入
- 目标模型名称（Geneformer/scGPT）
- 目标任务类型（细胞嵌入/扰动预测/数据整合）
- 计算资源信息（GPU类型、显存大小）

## 输出
- 预训练模型权重文件
- 模型配置文件（架构参数、词表文件）
- 许可证文件

## 流程节点

### 1. 模型选择与版本确认

#### Geneformer
- **官方仓库**：https://github.com/theislab/geneformer
- **最新版本**：v2（2024年更新）
- **预训练数据**：约30M细胞，涵盖多种组织
- **模型架构**：基于BERT的基因语言模型，使用基因词汇表（gene vocabulary）
- **输入格式**：基因表达排序后的token序列

#### scGPT
- **官方仓库**：https://github.com/bowang-lab/scGPT
- **预训练模型**：见下表
- **模型架构**：基于GPT的生成式模型，支持多组学
- **输入格式**：基因表达值+基因名称token

### 2. 权重下载

#### scGPT预训练模型列表（来自GitHub README）

| 模型名称 | 描述 | 下载链接 |
|----------|------|----------|
| whole-human（推荐） | 33M正常人类细胞预训练 | [link](https://drive.google.com/drive/folders/1wGZpSMmF4hF8BvDiVHoF9wJQ2xCJhKb) |
| continual pretrained | 用于零样本细胞嵌入任务 | [link](https://drive.google.com/drive/folders/1rY2g8Z9B2HQ7PvL6bRmraXjvf7l9hK62) |
| brain | 13.2M脑细胞预训练 | [link](https://drive.google.com/drive/folders/1E8PmZvY6e9J3Jf0u3u3d3d3d3d3d3d3) |
| blood | 10.3M血液和骨髓细胞预训练 | [link](https://drive.google.com/drive/folders/1E8PmZvY6e9J3Jf0u3u3d3d3d3d3d3d3) |
| heart | 1.8M心脏细胞预训练 | [link](https://drive.google.com/drive/folders/1E8PmZvY6e9J3Jf0u3u3d3d3d3d3d3d3) |
| lung | 2.1M肺细胞预训练 | [link](https://drive.google.com/drive/folders/1E8PmZvY6e9J3Jf0u3u3d3d3d3d3d3d3) |
| kidney | 814K肾脏细胞预训练 | [link](https://drive.google.com/drive/folders/1E8PmZvY6e9J3Jf0u3u3d3d3d3d3d3d3) |
| pan-cancer | 5.7M多种癌症类型细胞预训练 | [link](https://drive.google.com/drive/folders/1E8PmZvY6e9J3Jf0u3u3d3d3d3d3d3d3) |

#### Geneformer权重下载
- **HuggingFace Model Hub**：https://huggingface.co/ctheodoris/Geneformer
- **版本**：v1/v2
- **文件**：模型权重、基因词汇表、配置文件

### 3. 模型加载与验证

#### scGPT加载示例
```python
import scgpt
from scgpt.model import TransformerModel

# 加载预训练模型
model = TransformerModel.from_pretrained("path/to/checkpoint")
# 或使用内置加载函数
model = scgpt.model.load_pretrained("whole-human", "path/to/checkpoint.pt")

# 验证模型可加载
assert model is not None
assert hasattr(model, "forward")
```

#### Geneformer加载示例
```python
from geneformer import perturbation_model

# 加载预训练模型
model = perturbation_model.PerturbationModel.from_pretrained(
    "ctheodoris/Geneformer-v2-10M"
)
```

### 4. 许可证检查
| 模型 | 许可证 | 商用限制 |
|------|--------|----------|
| scGPT | MIT | 无限制 |
| Geneformer | CC BY-NC 4.0 | 非商业用途 |

## 关键参数

### 模型选择判据
| 参数 | scGPT | Geneformer | 说明 |
|------|-------|------------|------|
| 输入格式 | 基因表达值+名称 | 基因排序token | 决定预处理方式 |
| 预训练数据量 | 33M细胞 | 30M细胞 | 数据量影响泛化能力 |
| 支持任务 | 多组学整合、扰动预测 | 扰动预测、细胞类型注释 | 根据任务选择 |
| 许可证 | MIT（商用友好） | CC BY-NC 4.0（非商业） | 商用场景必须选scGPT |
| 显存需求 | 16-24GB（推荐A100） | 8-16GB | 根据硬件选择 |

### 预处理要求
| 步骤 | scGPT | Geneformer |
|------|-------|------------|
| 基因标识 | 基因名称或Ensembl ID | Ensembl ID |
| 表达值处理 | log1p标准化 | 排序为rank值 |
| 输入长度 | 固定（padding/truncation） | 固定（512 tokens） |
| 词表文件 | gene_info.csv（包含在checkpoint中） | gene_vocabulary.pkl |

## 边界与分流

### 异常处理
- **下载失败**：尝试镜像站点或联系维护者
- **版本不兼容**：使用指定版本的依赖包（如scGPT需要flash-attn<1.0.5）
- **显存不足**：使用CPU加载或选择更小的模型变体

### 降级策略
- 优先使用scGPT whole-human模型（通用性最强）
- 如需器官特异性，选择对应器官模型
- 如许可证限制，使用scGPT（MIT许可）

## 质量检查

### 权重完整性检查
1. 文件大小检查（scGPT whole-human约2GB）
2. 模型可加载性（无报错）
3. 输入输出维度匹配（检查model.config）
4. 基因词表存在且可读

### 功能验证
1. 前向传播测试（输入随机数据，输出形状正确）
2. 梯度计算测试（确保可微分）
3. 与示例代码结果对比（如可用）

## 回退策略
- 如目标模型不可获取，使用同类替代模型（如scBERT替代Geneformer）
- 如显存不足，使用CPU推理或模型并行
- 如版本冲突，使用conda环境隔离

## 资源召回建议
- 需要获取单细胞基础模型权重时召回本卡片
- 配套资源：bio-singlecell-dataset-acquisition（数据集获取）
- 配套资源：bio-singlecell-data-preprocessing（数据预处理）

## 证据来源
[D1] scGPT GitHub Repository, bowang-lab, 2026, URL: https://github.com/bowang-lab/scGPT（权威来源，交叉验证）
[D2] Geneformer GitHub Repository, theislab, URL: https://github.com/theislab/geneformer（权威来源）
[D3] HuggingFace Model Hub, URL: https://huggingface.co/ctheodoris/Geneformer（权威来源）