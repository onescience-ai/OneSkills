# 单细胞基础模型权重获取知识

## 适用范围

**触发条件**：
- 任务需要加载Geneformer或scGPT预训练权重
- 模型权重未找到或版本不匹配
- 需要验证模型架构与数据格式兼容性

**适用场景**：
- 单细胞基础模型推理与微调
- 跨模型可解释性比较
- 细胞类型注释、扰动预测、基因网络推断

**不适用场景**：
- 从零训练自定义模型（需要训练代码而非权重）
- 非Transformer架构模型
- 未公开发布的模型

## 输入

| 输入项 | 说明 |
|--------|------|
| 模型名称 | Geneformer、scGPT或其他单细胞基础模型 |
| 版本要求 | v2、v3或特定日期版本 |
| 设备信息 | GPU类型、显存大小、CPU-only |
| 任务类型 | 推理、微调、特征提取 |

## 输出

| 输出项 | 说明 |
|--------|------|
| 权重文件 | .pt/.pth/.bin格式 |
| 配置文件 | model_config.json |
| 分词器 | gene vocabulary文件 |
| 验证报告 | 权重完整性、架构匹配性 |

## 流程节点

### 步骤1：模型源定位

**操作**：根据任务需求定位官方模型仓库

**主流单细胞基础模型**：

| 模型 | 官方仓库 | 权重版本 | 许可证 | 特点 |
|------|----------|----------|--------|------|
| Geneformer | ctheodoris/Geneformer | v2 | MIT | 基因词汇表，表达水平排序 |
| scGPT | bowang-lab/scGPT | v1 | MIT | 多组学支持，Transformer架构 |
| scBERT | yanolab/scBERT | v1 | MIT | 预训练语言模型 |
| scFoundation | 409287594/scFoundation | v1 | Apache-2.0 | 大规模预训练 |
| GeneCompass | jiacheng2023/GeneCompass | v1 | MIT | 跨物种，知识注入 |

**HuggingFace Model Hub检索**：

```
https://huggingface.co/models?search=single+cell+foundation
```

**质量门禁**：
- 确认仓库为官方维护
- 检查模型版本与任务兼容
- 验证许可证允许商用/学术使用

### 步骤2：权重下载与验证

**操作**：下载权重文件并验证完整性

**下载命令示例**：

```bash
# Geneformer v2
git clone https://huggingface.co/ctheodoris/Geneformer
# 或使用huggingface-cli
huggingface-cli download ctheodoris/Geneformer --local-dir ./geneformer_weights

# scGPT
git clone https://huggingface.co/bowanglab/scgpt
# 或
huggingface-cli download bowanglab/scgpt --local-dir ./scgpt_weights
```

**验证检查点**：

| 检查项 | 方法 | 通过标准 |
|--------|------|----------|
| 文件完整性 | sha256校验 | 与官方校验值匹配 |
| 权重可加载 | torch.load() | 无报错加载 |
| 架构匹配 | config.json检查 | 模型类名一致 |
| 参数维度 | state_dict.keys() | 关键层维度匹配 |

### 步骤3：模型架构与输入规格

**Geneformer v2规格**：

| 参数 | 值 | 说明 |
|------|-----|------|
| 架构 | Transformer Encoder | 仅编码器 |
| 基因词汇表 | ~20,000基因 | 按表达水平排序 |
| 输入格式 | 基因列表（排序后） | 表达水平决定位置 |
| 最大序列长度 | 2048 | 基因token数 |
| 隐藏维度 | 768 | 默认配置 |
| 注意力头数 | 12 | 多头注意力 |
| 预训练任务 | 掩码基因预测 | MLM |

**scGPT规格**：

| 参数 | 值 | 说明 |
|------|-----|------|
| 架构 | Transformer Encoder | 编码器架构 |
| 基因表示 | 连续值嵌入 | 表达值直接输入 |
| 输入格式 | 基因表达向量 | 稀疏矩阵 |
| 最大基因数 | 3,000 | 默认配置 |
| 隐藏维度 | 512 | 默认配置 |
| 注意力头数 | 8 | 多头注意力 |
| 预训练任务 | 多任务 | 表达预测+细胞类型分类 |

**预处理要求对比**：

| 预处理步骤 | Geneformer | scGPT |
|------------|------------|-------|
| 归一化 | 无需（使用原始计数排序） | Log归一化 |
| 基因选择 | 按表达水平排序 | 保留高变基因 |
| 批次编码 | 不需要 | 需要批次标签 |
| 缺失值处理 | 填充为0 | 填充为0 |

### 步骤4：许可证与使用限制

**许可证兼容性**：

| 模型 | 许可证 | 商用 | 修改 | 分发 |
|------|--------|------|------|------|
| Geneformer | MIT | ✅ | ✅ | ✅ |
| scGPT | MIT | ✅ | ✅ | ✅ |
| scBERT | MIT | ✅ | ✅ | ✅ |
| scFoundation | Apache-2.0 | ✅ | ✅ | ✅ |

**使用限制**：
- 需引用原始论文
- 不得用于临床诊断决策
- 部分数据集有额外使用条款

## 关键参数

| 参数 | Geneformer | scGPT | 来源 | 说明 |
|------|------------|-------|------|------|
| 权重格式 | .pt | .pt | [1][2] | PyTorch权重 |
| 配置格式 | config.json | args.json | [1][2] | 模型配置 |
| 基因词汇表 | vocab.json | gene_id_map.csv | [1][2] | 基因标识映射 |
| 最大序列长度 | 2048 | 3000 | [1][2] | 输入截断长度 |

## 边界与分流

**异常处理**：
- 权重下载失败 → 检查网络，使用镜像源
- 版本不兼容 → 降级或升级代码版本
- 显存不足 → 使用CPU推理或模型并行

**分支条件**：
- 任务需要微调 → 检查微调接口文档
- 任务需要特征提取 → 使用模型中间层输出
- 任务需要多组学 → scGPT支持ATAC+RNA联合

## 质量检查

| 检查点 | 阈值 | 失败处理 |
|--------|------|----------|
| 权重文件大小 | >100MB | 重新下载 |
| 参数维度匹配 | 100% | 检查模型版本 |
| 推理输出有限值 | 100% | 检查预处理流程 |
| 无NaN/Inf | 100% | 检查输入数据 |

## 回退策略

1. **首选**：从HuggingFace下载官方权重
2. **备选**：从GitHub Releases下载
3. **兜底**：使用模型作者提供的Colab笔记本验证

## 资源召回建议

**何时召回本卡片**：
- 模型权重加载失败
- 需要验证模型版本与数据兼容性
- 需要获取Geneformer或scGPT官方权重

**配套资源**：
- bio-sc-data-public-dataset-acquisition：数据获取
- bio-sc-foundation-model-evaluation：评测方法

## 证据来源

[1] Zero-shot evaluation reveals limitations of single-cell foundation models, Genome Biology, 2025, DOI: 10.1186/s13059-025-03574-x

[2] A foundation model of transcription across human cell types, Nature, 2025, DOI: 10.1038/s41586-024-08391-z

[3] GeneCompass: deciphering universal gene regulatory mechanisms with a knowledge-informed cross-species foundation model, Cell Research, 2024, DOI: 10.1038/s41422-024-01034-y
