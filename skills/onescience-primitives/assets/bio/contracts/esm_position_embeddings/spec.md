# component_info

`esm_position_embeddings` 是 ESM 蛋白序列位置编码组件，包含 learned positional embedding 与 sinusoidal positional embedding 两种实现，用于给 token 序列或 inverse folding 序列增加位置信息。

# purpose

用于蛋白语言模型和序列编码任务中的位置建模。适合处理 FASTA/token 序列、MSA 序列中的 residue index；不适合直接处理三维坐标、配体图或医学图像。

# input_schema

```text
input tokens:
  Tensor[int64]: (Batch, Length)
  padding_idx: int

position_ids:
  optional Tensor[int64]: (Batch, Length)
  未提供时由 token mask 自动生成
```

# output_schema

```text
position_embedding:
  Tensor[float]: (Batch, Length, EmbeddingDim)
```

# parameters

- `num_embeddings`: 位置表大小。
- `embedding_dim`: 位置向量维度。
- `padding_idx`: padding token 对应位置。
- `init_size`: 正弦编码初始化尺度。
- `auto_expand`: 长序列时是否扩展正弦权重缓存。

# key_dependencies

- `embeddings.py`

# usage_and_risks

使用时需要保证 padding token 与真实 residue token 区分清楚；若序列长度超过初始化上限，learned embedding 可能越界，sinusoidal embedding 可扩展但需关注缓存和设备一致性。它只提供位置向量，需与 token embedding 或 ESM transformer 联用。

# code_references

- `{onescience_path}/onescience/src/onescience/modules/esm`
