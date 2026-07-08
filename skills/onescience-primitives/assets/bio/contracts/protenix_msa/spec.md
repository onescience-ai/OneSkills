# component_info

`protenix_msa` 是 Protenix 的 MSA 更新模块，统一入口为 `OneMSA`，注册名为 `ProtenixMSAModule`。

# purpose

在 recycling 过程中使用 MSA 特征更新 pair representation `z`。缺少 MSA 或维度不足时直接返回原 `z`，因此它可安全降级但不会自动搜索 MSA。

# input_schema

```text
input_feature_dict:
  msa: [..., N_msa, N_token]
  has_deletion: [..., N_msa, N_token]
  deletion_value: [..., N_msa, N_token]
z: [..., N_token, N_token, c_z]
s_inputs: [..., N_token, c_s_inputs]
pair_mask: [..., N_token, N_token] 或 None
```

# output_schema

```text
updated_z:
  shape: [..., N_token, N_token, c_z]
```

# parameters

- `n_blocks=4`, `c_m=64`, `c_z=128`, `c_s_inputs=449`
- `msa_dropout=0.15`, `pair_dropout=0.25`
- `blocks_per_ckpt=1`, `msa_chunk_size=2048`, `msa_max_size=16384`
- `msa_configs.enable`, `strategy`, `sample_cutoff.train/test`, `min_size.train/test`

# key_dependencies

- `onemsa.py`
- `protenixmsa.py`
- `protenixpairformer.py`
- `protenixlinear.py`

# usage_and_risks

MSA one-hot 类别数固定为 32，不能用通用氨基酸 22 类编码替换。`msa_configs` 不能为 `None`。长 MSA 显存主要受 `N_msa_sampled * N_token` 和 `N_token^2` 影响。

# code_references

- `{onescience_path}/onescience/src/onescience/modules/msa/onemsa.py`
- `{onescience_path}/onescience/src/onescience/modules/msa/protenixmsa.py`
- `{onescience_path}/onescience/src/onescience/models/protenix/protenix.py`
