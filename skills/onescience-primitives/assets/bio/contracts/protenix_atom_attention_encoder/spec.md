# component_info

`protenix_atom_attention_encoder` 是 AF3/Protenix 风格 atom-to-token 编码器，统一入口为 `OneEncoder`，注册名为 `ProtenixAtomAttentionEncoder`。

# purpose

把原子级参考特征编码成 token 表征，并在 diffusion 路径中把 noisy atom coordinates、single trunk 和 pair trunk 条件注入局部 atom attention。它不是通用 PDB 坐标 encoder。

# input_schema

```text
input_feature_dict:
  ref_pos, ref_charge, ref_mask, ref_element
  ref_atom_name_chars, ref_space_uid
  atom_to_token_idx

has_coords=True additional:
  r_l: [..., N_sample, N_atom, 3]
  s: [..., N_token, c_s]
  z: [..., N_token, N_token, c_z]
```

# output_schema

```text
a: [..., N_token, c_token]
q_l: [..., N_atom, c_atom]
c_l: [..., N_atom, c_atom]
p_lm: [..., n_trunks, n_queries, n_keys, c_atompair]
```

# parameters

- `has_coords`
- `c_token`, `c_atom=128`, `c_atompair=16`, `c_s=384`, `c_z=128`
- `n_blocks=3`, `n_heads=4`, `n_queries=32`, `n_keys=128`
- `blocks_per_ckpt=None`

# key_dependencies

- `oneencoder.py`
- `protenixencoding.py`
- `protenixtransformer.py`
- `protenixlinear.py`

# usage_and_risks

用于 `ProtenixInputFeatureEmbedder` 和 `ProtenixDiffusionModule`。`ref_atom_name_chars` 按 `4 * 64` 展平；`has_coords=True` 时 `r_l/s/z` 必须同时提供；局部 attention 使用 dense trunk 表示，不能手工当作完整 `N_atom x N_atom` pair。

# code_references

- `{onescience_path}/onescience/src/onescience/modules/encoder/oneencoder.py`
- `{onescience_path}/onescience/src/onescience/modules/encoder/protenixencoding.py`
- `{onescience_path}/onescience/src/onescience/modules/transformer/protenixtransformer.py`
