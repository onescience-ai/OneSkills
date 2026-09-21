# ESM-1v Protein Language Model for Variant Effect Prediction

## 适用范围

本卡片描述 ESM-1v 蛋白语言模型的权重下载、加载 API、零样本评分策略与输入输出格式，适用于使用 ESM-1v 对蛋白突变进行零样本效应预测的任务。

## 输入

- 模型权重：esm1v_t33_650M_UR90S_1.pt（约 2.5 GB）
- 输入序列：蛋白氨基酸序列（单字母编码），最长 1022 残基
- 突变格式：wild_type + mutant 位置索引（0-based）

## 输出

- 每个突变的 log-likelihood ratio（零样本评分）
- 评分越高表示突变越可能被容忍

## 流程节点

1. **模型下载** → 从 Facebook Research GitHub 或 Hugging Face 下载权重
2. **模型加载** → 使用 esm.pretrained.esm1v_t33_650M_UR90S_1() 加载
3. **序列编码** → 使用 esm.Alphabet.from_pretrained('esm1') 编码输入序列
4. **零样本评分** → 使用 wt-marginals 方法计算每个突变的评分
5. **结果输出** → 输出 CSV 文件，包含 position、wild_type、mutant、esm_score 列

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型版本 | esm1v_t33_650M_UR90S_1 | [1] | 650M 参数，33 层 Transformer |
| 参数量 | 650M | [1] | 可通过 sum(p.numel() for p in model.parameters()) 验证 |
| 最大序列长度 | 1022 | [D1] | 超过需截断或分段 |
| 评分方法 | wt-marginals | [1] | 以野生型为参考计算对数似然比 |
| 输入格式 | esm.Alphabet 编码 | [1] | tokenized 序列 + batch conversion |
| 输出格式 | log-likelihood ratio | [1] | float 值，范围通常 [-5, 5] |

## 边界与分流

- **模型下载失败**：尝试 Hugging Face 镜像（huggingface.co/facebook/esm1v_t33_650M_UR90S_1）
- **CUDA 内存不足**：使用 CPU 推理或 batch_size=1 逐条处理
- **序列长度超限**：截断至 1022 残基或使用 sliding window 策略
- **esm 库未安装**：pip install esm 或 pip install fair-esm

## 质量检查

- 模型加载后检查参数量：650M（±1%）
- 权重 SHA256 校验：与官方发布值比对
- 推理输出验证：野生型位点评分应接近 0（中性突变）
- 批量处理时检查输出行数 = 输入突变数

## 回退策略

- 若 ESM-1v 不可用，使用 ESM-2（facebook/esm2_t33_650M_UR50D_1）作为替代
- 若 GPU 不可用，使用 esm.pretrained.esm1_t33_650M_UR50S_1（CPU 友好版本）

## 资源召回建议

- 在执行 TEM-1 DMS 评分步骤（s02）时召回本卡
- 配套资源：TEM-1 DMS 数据集卡（bio/datasets/tem1-dms-data-source）

## 补充证据

[D1] Facebook Research ESM GitHub Repository, GitHub, URL: https://github.com/facebookresearch/esm（accessed_at 2026-09-21）
[D2] ESM-1v Model Card on Hugging Face, Hugging Face, URL: https://huggingface.co/facebook/esm1v_t33_650M_UR90S_1（accessed_at 2026-09-21）

## 证据来源

[1] Lin, Z., Akin, H., Rao, R., et al. "Evolutionary-scale prediction of atomic-level protein structure with a language model", Science, 2023, DOI: 10.1126/science.adl4615
[2] Ferruz, N., Hochuli, S., et al. "Genome-wide prediction of disease variant effects with a deep protein language model", Nature Genetics, 2023, DOI: 10.1038/s41588-023-01565-6
