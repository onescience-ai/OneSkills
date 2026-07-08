# description

用于规划 Protenix 内部 attention 选择：普通 attention、pair-bias attention 或 local atom attention。

# when_to_use

- Pairformer 需要 single update。
- Diffusion transformer 需要 pair-bias token attention。
- Atom encoder/decoder 需要局部 atom attention。

# inputs

- `a/s/z` 形态。
- global 或 local attention 场景。
- `n_heads`、`n_queries`、`n_keys`。
- 是否使用高效 attention kernel。

# outputs

```text
component_choice:
  name: protenix_attention
  action: pair_bias | local_atom_attention | base_attention | reject
```

# procedure

1. 判断 attention 发生在 token pair 还是 atom local window。
2. 校验 `z` 是 global pair 还是 local trunked pair。
3. 校验 head 和通道整除关系。
4. 决定是否启用 efficient implementation。

# constraints

不要把局部 atom pair 当完整 pair representation；不要把 Protenix attention 替换为天气窗口 attention。

# next_phase_recommendation

Pairformer 场景接 `protenix_pairformer`；diffusion 场景接 `protenix_transformer`；atom 场景接 encoder/decoder。

# fallback

显存不足时使用 local attention、chunk 或减少 token；kernel 不兼容时关闭 efficient implementation。
