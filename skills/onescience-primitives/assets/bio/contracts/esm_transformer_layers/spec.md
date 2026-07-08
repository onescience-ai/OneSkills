# component_info

`esm_transformer_layers` 是 ESM 蛋白语言模型层组件族，包含普通 `TransformerLayer`、MSA `AxialTransformerLayer`、`NormalizedResidualBlock` 和 `FeedForwardNetwork`。

# purpose

用于蛋白 token 或 MSA token 的深层上下文编码。适合序列表征、masked LM、contact prediction 前的 trunk；不适合直接生成三维坐标或分子 SMILES。

# input_schema

```text
sequence activations:
  Tensor[float]: (SeqLen, Batch, EmbedDim)

MSA activations:
  Tensor[float]: (Rows, Cols, Batch, EmbedDim)

self_attn_mask / padding_mask:
  optional mask tensors
```

# output_schema

```text
updated activations:
  Tensor[float]: same layout as input activations

attention weights:
  optional Tensor[float]
```

# parameters

- `embed_dim`: token 表征维度。
- `ffn_embed_dim`: 前馈网络隐藏维度。
- `attention_heads`: 注意力头数。
- `dropout`: dropout 概率。
- `add_bias_kv`: 是否添加 bias key/value。
- `use_rotary_embeddings`: 是否使用旋转位置编码。

# key_dependencies

- `transformer.py`
- `esm_multihead_attention.py`
- `esm_axial_attention.py`
- `layer_norm.py`

# usage_and_risks

普通序列层与 MSA 轴向层输入布局不同，迁移时必须先确认维度顺序。长序列和大 MSA 会导致显存增长；若只需要下游对接或打分特征，应优先复用预训练 ESM 表征而不是重新训练该层。

# code_references

- `{onescience_path}/onescience/src/onescience/modules/esm`
