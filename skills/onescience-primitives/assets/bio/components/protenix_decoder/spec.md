# component_info

`protenix_decoder` 是 Protenix atom attention decoder，统一入口为 `OneDecoder`，注册名为 `ProtenixAtomAttentionDecoder`。

# purpose

将 token diffusion 表征 `a` broadcast 回 atom，并结合 atom encoder skip 表征输出 3D 坐标更新。它不独立完成完整结构预测。

# input_schema

```text
input_feature_dict:
  atom_to_token_idx
a: [..., N_token, c_token]
q_skip: [..., N_atom, c_atom]
c_skip: [..., N_atom, c_atom]
p_skip: [..., n_trunks, n_queries, n_keys, c_atompair]
```

# output_schema

```text
r: [..., N_atom, 3]
```

# parameters

- `n_blocks=3`, `n_heads=4`
- `c_token=384` 或 diffusion 默认 `768`
- `c_atom=128`, `c_atompair=16`
- `n_queries=32`, `n_keys=128`
- `blocks_per_ckpt=None`

# key_dependencies

- `onedecoder.py`
- `protenixdecoder.py`
- `protenixtransformer.py`
- `protenixdiffusion.py`

# usage_and_risks

必须与 atom encoder 成对使用。`p_skip` 的 `n_queries/n_keys` 必须等于 decoder 构造参数；`c_token` 在 diffusion 中常为 768，不要直接套 input embedder 的 384。

# code_references

- `{onescience_path}/onescience/src/onescience/modules/decoder/onedecoder.py`
- `{onescience_path}/onescience/src/onescience/modules/decoder/protenixdecoder.py`
- `{onescience_path}/onescience/src/onescience/modules/diffusion/protenixdiffusion.py`
- `{onescience_path}/onescience/src/onescience/modules/transformer/protenixtransformer.py`
