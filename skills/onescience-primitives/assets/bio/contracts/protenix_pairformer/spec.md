# component_info

`protenix_pairformer` 是 Protenix token/pair trunk 组件族，统一入口为 `OnePairformer`，注册名为 `ProtenixPairformerBlock` 和 `ProtenixPairformerStack`。

# purpose

更新 token single representation `s` 与 pair representation `z`。`ProtenixPairformerBlock` 可用于 MSA block 内部的纯 pair update，`ProtenixPairformerStack` 是 Protenix 主 trunk 和 template 分支的多层堆栈。

# input_schema

```text
s: [..., N_token, c_s] 或 None
z: [..., N_token, N_token, c_z]
pair_mask: [..., N_token, N_token] 或 None
```

# output_schema

```text
s_out: [..., N_token, c_s] 或 None
z_out: [..., N_token, N_token, c_z]
```

# parameters

- Block: `n_heads=16`, `c_z=128`, `c_s=384`, `c_hidden_mul=128`, `c_hidden_pair_att=32`, `no_heads_pair=4`, `dropout=0.25`
- Stack: `n_blocks=48`, `n_heads=16`, `c_z=128`, `c_s=384`, `dropout=0.25`, `blocks_per_ckpt=None`

# key_dependencies

- `onepairformer.py`
- `protenixpairformer.py`
- `protenixattention.py`
- `protenixlinear.py`
- `protenixmsa.py`

# usage_and_risks

`c_s=0` 时 single branch 不创建，适合作为纯 pair update。`z` 是主要内存来源，长 token 场景必须关注 chunk、activation checkpoint、low-memory attention 和 inference cache 清理。

# code_references

- `{onescience_path}/onescience/src/onescience/modules/pairformer/onepairformer.py`
- `{onescience_path}/onescience/src/onescience/modules/pairformer/protenixpairformer.py`
- `{onescience_path}/onescience/src/onescience/modules/msa/protenixmsa.py`
