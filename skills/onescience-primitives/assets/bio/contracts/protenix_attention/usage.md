# launch

```sh
python -c "from onescience.modules.attention.protenixattention import ProtenixAttentionPairBias; m=ProtenixAttentionPairBias(c_a=384, c_s=384, c_z=128, n_heads=16); print(type(m).__name__)"
```

# input_schema

根据组件类型准备 `a/s/z` 或 `q_x/kv_x/attn_bias`。global pair bias 使用完整 `[..., N_token, N_token, c_z]`；atom local attention 使用 `[..., n_trunks, n_queries, n_keys, c_z]`。

# runtime_interfaces

- `ProtenixAttention`
- `ProtenixAttentionPairBias`
- `ProtenixAttentionPairBiasWithLocalAttn`
- `forward`

# main_functions

- `forward`

# execution_resources

global attention 主要受 `N_token^2` 影响；local attention 受 trunk 数、`n_queries/n_keys` 和 atom 数影响。

# operation_limits

不能与 ESM attention、Earth attention 或 window attention 混用。`z` 形态错误时可能不报 shape 错但语义错误。
