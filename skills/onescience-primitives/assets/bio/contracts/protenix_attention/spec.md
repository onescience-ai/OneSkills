# component_info

`protenix_attention` 是 Protenix 内部 attention 组件族，包含底层 gated attention、pair bias attention 和 local atom attention。已有 contract 中描述了 `OneAttention` 统一入口，但当前源码注册状态需以 `oneattention.py` 为准。

# purpose

用于 Pairformer、diffusion transformer 和 atom local transformer 中更新 token/atom 表征。它不是 EarthAttention、window attention 或 ESM attention 的替代品。

# input_schema

```text
ProtenixAttention:
  q_x: [..., Q, c_q]
  kv_x: [..., K, c_k]
  attn_bias: [..., Q, K] 或 [..., H, Q, K]

ProtenixAttentionPairBias:
  a: [..., N_token, c_a]
  s: [..., N_token, c_s] 或 None
  z: [..., N_token, N_token, c_z]

Local attention:
  z: [..., n_trunks, n_queries, n_keys, c_z]
```

# output_schema

```text
attention_output:
  shape: [..., Q, c_q] 或 [..., N_token, c_a]
```

# parameters

- `c_q`, `c_k`, `c_v`, `c_hidden`, `num_heads`
- `gating=True`, `q_linear_bias=True`, `zero_init=True`
- `c_a=768`, `c_s=384`, `c_z=128`, `n_heads=16`
- `cross_attention_mode=False`

# key_dependencies

- `protenixattention.py`
- `protenixlinear.py`
- `protenixtransformer.py`
- `protenixpairformer.py`

# usage_and_risks

pair bias 必须来自正确 trunk 或局部重排后的 `z`。`c_a % n_heads == 0`；local 模式中 `n_queries/n_keys` 必须与 trunked bias 一致；`use_efficient_implementation=True` 需要确认当前 attention bias/mask 形态兼容。

# code_references

- `{onescience_path}/onescience/src/onescience/modules/attention/oneattention.py`
- `{onescience_path}/onescience/src/onescience/modules/attention/protenixattention.py`
- `{onescience_path}/onescience/src/onescience/modules/pairformer/protenixpairformer.py`
- `{onescience_path}/onescience/src/onescience/modules/transformer/protenixtransformer.py`
