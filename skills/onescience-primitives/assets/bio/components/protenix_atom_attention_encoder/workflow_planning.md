# description

用于判断任务是否需要 Protenix atom attention encoder，以及如何区分静态 atom 编码和 diffusion 条件编码。

# when_to_use

- input feature embedder 需要 atom-to-token 表征。
- diffusion module 需要从 noisy atom 坐标构造 token/atom latent。

# inputs

- atom reference feature 字段。
- `atom_to_token_idx` 合法性。
- 是否启用 `has_coords`。
- local attention window 参数。

# outputs

```text
component_choice:
  name: protenix_atom_attention_encoder
  action: static_encode | diffusion_encode | fix_atom_mapping | reject
```

# procedure

1. 确认输入是 Protenix feature dict。
2. 校验 atom reference 字段和 mask。
3. 校验 atom-token 映射覆盖范围。
4. 根据场景选择 `has_coords`。
5. 检查 `n_queries/n_keys` 与 decoder/atom transformer 一致。

# constraints

不要把该组件作为通用结构 encoder；不要在缺失 `ref_space_uid`、`ref_atom_name_chars` 时强行运行。

# next_phase_recommendation

静态路径接 `protenix_embedding`；diffusion 路径接 `protenix_transformer` 和 `protenix_decoder`。

# fallback

字段缺失时回到 Protenix JSON parser/featurizer；显存不足时降低 atom 数或调整局部窗口。
