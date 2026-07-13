# component_info

`protenix_embedding` 是 Protenix/AF3 风格结构预测中的 embedding 组件族，统一入口为 `OneEmbedding`，注册名包括 `ProtenixInputFeatureEmbedder`、`ProtenixTemplateEmbedder` 和 `ProtenixFourierEmbedding`。它分别服务于 token 输入构造、template pair 表征更新和 diffusion noise level 条件编码。

# purpose

- `ProtenixInputFeatureEmbedder`: 把 atom 参考特征、restype/profile/deletion_mean 等输入整理成 `s_inputs`。
- `ProtenixTemplateEmbedder`: 在 recycling 中根据 template 特征更新 pair representation。
- `ProtenixFourierEmbedding`: 为 diffusion noise level 生成 Fourier 条件编码。
- 不适用场景：普通 FASTA token、OpenFold batch、ESM token batch 或天气/CFD embedding。

# input_schema

```text
ProtenixInputFeatureEmbedder:
  input_feature_dict:
    ref_pos, ref_charge, ref_mask, ref_element
    ref_atom_name_chars, atom_to_token_idx, ref_space_uid
    restype, profile, deletion_mean

ProtenixTemplateEmbedder:
  input_feature_dict: Protenix feature dict
  z: [..., N_token, N_token, c_z]

ProtenixFourierEmbedding:
  t_hat_noise_level: [..., N_sample]
```

# output_schema

```text
ProtenixInputFeatureEmbedder:
  s_inputs: [..., N_token, 449]

ProtenixTemplateEmbedder:
  template_pair_update: [..., N_token, N_token, c_z] 或 0

ProtenixFourierEmbedding:
  noise_embedding: [..., N_sample, c]
```

# parameters

- `ProtenixInputFeatureEmbedder`: `c_atom=128`, `c_atompair=16`, `c_token=384`
- `ProtenixTemplateEmbedder`: `n_blocks=2`, `c=64`, `c_z=128`, `dropout=0.25`, `blocks_per_ckpt=None`
- `ProtenixFourierEmbedding`: `c`, `seed=42`

# key_dependencies

- `oneembedding.py`
- `protenixembedding.py`
- `protenixencoding.py`
- `protenixlinear.py`
- `protenixpairformer.py`

# usage_and_risks

典型调用位于 Protenix `get_pairformer_output` 和 diffusion conditioning。`ProtenixInputFeatureEmbedder` 输出维度必须与 `configs.c_s_inputs` 对齐；template 分支在无 template 或 `n_blocks < 1` 时可能返回 `0`；Fourier embedding 的随机基底由 seed 固定，改变 seed 会改变 noise 条件语义。

# code_references

- `{onescience_path}/onescience/src/onescience/modules/embedding/oneembedding.py`
- `{onescience_path}/onescience/src/onescience/modules/embedding/protenixembedding.py`
- `{onescience_path}/onescience/src/onescience/modules/encoder/protenixencoding.py`
