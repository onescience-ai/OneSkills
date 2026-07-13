# component_info

`ptdit_attention_modules` 是 PT-DiT 的注意力组件族，包含 attention kernel、QKV embedding、post attention、hyper attention、continuous convolution 和 flash invariant point attention。

# purpose

用于蛋白 latent transformer 中的序列注意力、pair 条件注意力和结构感知点注意力，适合蛋白结构/序列联合生成；不直接负责 diffusion schedule 或 ProToken 解码。

# input_schema

```text
scalar attention:
  q, k, v: (Batch, Query/Key, Heads, Channels)
  b: optional (Batch, Heads, Query, Key)
  m: optional sequence mask

attention embedding:
  single_act: (Batch, Residues, Features)
  pair_act: optional (Batch, Residues, Neighbors, PairFeatures)

IPA:
  s_i, masks, z_ij, rotation, translation, optional neighbor index
```

# output_schema

```text
attention output:
  Tensor[float]: (Batch, Query, Heads, Channels) or projected single features

IPA output:
  Tensor[float]: (Batch, Residues, OutputChannels)
```

# parameters

- `n_head`: 注意力头数。
- `n_channel`: 每头通道数。
- `has_bias`: 是否使用 pair bias。
- `flash_attention_flag`: 是否使用 flash attention。
- `kernel_type`: `hak` 或 `rope`。
- `sparse_flag`: 是否使用稀疏邻居模式。

# key_dependencies

- `attention.py`
- `transformer.py`
- `dense.py`

# usage_and_risks

该组件族 shape 约束严格，pair/neighborhood mask、RoPE index 和 sparse neighbor index 必须同步。启用 flash attention 时通常要求序列长度和设备支持满足实现限制；IPA 还需要旋转和平移坐标帧。

# code_references

- `{onescience_path}/onescience/src/onescience/flax_models/Pt_DiT/module`
