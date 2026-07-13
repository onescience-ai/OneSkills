# component_info

`esm_axial_attention` 是 ESM MSA Transformer 的轴向注意力组件，包含 `RowSelfAttention` 和 `ColumnSelfAttention`，分别沿 MSA 行方向和列方向聚合蛋白同源序列信息。

# purpose

用于 MSA token 表征的长上下文建模，适合蛋白家族同源序列、残基-同源双轴输入；不适合单个小分子图或医学图像输入。

# input_schema

```text
MSA tokens / activations:
  Tensor[float]: (Rows, Cols, Batch, Channels)

self_attn_mask:
  optional Tensor[bool]

self_attn_padding_mask:
  optional Tensor[bool]: (Batch, Rows, Cols)
```

# output_schema

```text
updated activations:
  Tensor[float]: (Rows, Cols, Batch, Channels)

attention_weights:
  optional Tensor[float]
```

# parameters

- `embed_dim`: 输入通道维度。
- `num_heads`: 注意力头数。
- `dropout`: 注意力 dropout。
- `max_tokens_per_msa`: 大 MSA 分块计算阈值。

# key_dependencies

- `esm_axial_attention.py`

# usage_and_risks

适合 ESM-MSA 风格模型，长 MSA 会触发分块策略以控制显存。风险在于输入维度顺序与普通 batch-first transformer 不同，mask 维度错误会导致注意力泄漏或 shape mismatch。

# code_references

- `{onescience_path}/onescience/src/onescience/modules/attention`
