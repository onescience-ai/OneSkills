# component_info

`esm_multihead_attention` 是 ESM 序列模型的多头注意力组件，支持自注意力、交叉注意力、增量状态缓存、mask 和可选 rotary position embedding。

# purpose

用于蛋白序列 encoder、decoder 或 inverse folding transformer 中的上下文混合。适合 token 表征序列；不负责 MSA 轴向拆分、分子图构造或扩散采样。

# input_schema

```text
query:
  Tensor[float]: (TargetLen, Batch, EmbedDim)

key/value:
  optional Tensor[float]: (SourceLen, Batch, EmbedDim)

key_padding_mask:
  optional Tensor[bool]: (Batch, SourceLen)

attn_mask:
  optional Tensor[float|bool]
```

# output_schema

```text
attn_output:
  Tensor[float]: (TargetLen, Batch, EmbedDim)

attn_weights:
  optional Tensor[float]: (Batch, Heads, TargetLen, SourceLen)
```

# parameters

- `embed_dim`: 输入/输出通道数。
- `num_heads`: 多头数量。
- `dropout`: attention dropout。
- `self_attention`: 是否为自注意力。
- `encoder_decoder_attention`: 是否为 encoder-decoder attention。
- `use_rotary_embeddings`: 是否启用旋转位置编码。

# key_dependencies

- `esm_multihead_attention.py`
- `esm_rotary_embedding.py`

# usage_and_risks

使用时必须保证 `embed_dim` 可被 `num_heads` 整除。增量推理时需要正确维护 incremental state；mask 类型和维度错误会导致注意力权重异常。若启用 rotary embedding，需要 query/key 长度与位置缓存匹配。

# code_references

- `{onescience_path}/onescience/src/onescience/modules/attention`
