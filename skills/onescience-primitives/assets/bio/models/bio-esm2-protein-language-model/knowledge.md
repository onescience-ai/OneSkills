# ESM-2蛋白质语言模型

## 适用范围
- **触发条件**：需要蛋白质序列表征提取或功能预测
- **适用场景**：多模态蛋白功能预测、蛋白质表征学习、迁移学习
- **不适用场景**：仅需简单序列编码（one-hot）、蛋白质结构预测本身

## 输入
- 蛋白质氨基酸序列（ACDEFGHIKLMNPQRSTVWY）
- Tokenize格式：首位token、padding、truncation

## 输出
- 序列表征：embedding向量（640/1280维）
- 可选：per-residue表征（用于结构预测）

## 模型规格

| 模型名称 | 参数量 | Embedding维度 | 推荐用途 |
|----------|--------|---------------|----------|
| esm2_t33_650M_UR50D | 650M | 640 | 常规下游任务 |
| esm2_t36_3B_UR50D | 3B | 1280 | 高精度任务 |
| esm2_t48_15B_UR50D | 15B | 1280 | 研究级任务 |

## 使用方式

### 安装
```bash
pip install fair-esm
```

### 加载模型
```python
import esm
model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
```

### Tokenize序列
```python
batch_converter = alphabet.get_batch_converter()
data = [("protein_id", "MKWVTFISLLFLFSSAYSRGVFRR...")]
batch_labels, batch_strs, batch_tokens = batch_converter(data)
```

### 提取表征
```python
with torch.no_grad():
    results = model(batch_tokens)
    # 倒数第2层表征
    embedding = results["representations"][33]  # 650M模型
    # 序列级表征（mean pooling）
    seq_embedding = embedding[:, 1:-1, :].mean(dim=1)
```

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| model_name | esm2_t33_650M_UR50D | [Lin et al. 2023] | 推荐模型 |
| embedding_dim | 640 (650M) / 1280 (3B) | [Lin et al. 2023] | 输出维度 |
| max_seq_len | 2048 | [ESM-2] | 最大序列长度 |
| output_layer | 33 (650M) / 36 (3B) | [Lin et al. 2023] | 提取层 |

## 边界与分流
- GPU内存不足：使用CPU推理或650M模型
- 序列>2048：滑动窗口分块处理
- 模型下载失败：使用HuggingFace镜像

## 质量检查
- 模型加载成功（model.load_state_dict）
- forward pass输出维度正确
- 表征无NaN/Inf值

## 证据来源
[1] Lin et al., "Evolutionary-scale prediction of atomic-level protein structure with a language model", Science, 2023, DOI: 10.1126/science.ade2574