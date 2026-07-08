# component_info

`protenix_transformer` 是 Protenix diffusion 和 atom local attention 使用的 transformer 组件族，统一入口为 `OneTransformer`。

# purpose

`ProtenixDiffusionTransformer` 更新 token diffusion latent；`ProtenixAtomTransformer` 在 atom local attention window 上更新 atom query；`ProtenixConditionedTransitionBlock` 用 single 条件调制前馈更新。

# input_schema

```text
ConditionedTransition:
  a: [..., N, c_a]
  s: [..., N, c_s]

DiffusionTransformer:
  a: [..., N_token, c_a]
  s: [..., N_token, c_s]
  z: [..., N_token, N_token, c_z]

AtomTransformer:
  q: [..., N_atom, c_atom]
  c: [..., N_atom, c_atom]
  p: [..., n_trunks, n_queries, n_keys, c_atompair]
```

# output_schema

```text
ConditionedTransition: [..., N, c_a]
DiffusionTransformerStack: [..., N_token, c_a]
AtomTransformer: [..., N_atom, c_atom]
```

# parameters

- `c_a`, `c_s`, `c_z`, `n_blocks`, `n_heads`
- `drop_path_rate=0.0`, `cross_attention_mode=False`, `blocks_per_ckpt=None`
- Atom: `c_atom=128`, `c_atompair=16`, `n_queries=32`, `n_keys=128`

# key_dependencies

- `onetransformer.py`
- `protenixtransformer.py`
- `protenixattention.py`
- `protenixlinear.py`

# usage_and_risks

`ProtenixAtomTransformer.forward` 会校验 `p.shape[-3] == n_queries` 和 `p.shape[-2] == n_keys`。该组件只更新 latent，不直接输出坐标；坐标更新由 decoder 完成。

# code_references

- `{onescience_path}/onescience/src/onescience/modules/transformer/onetransformer.py`
- `{onescience_path}/onescience/src/onescience/modules/transformer/protenixtransformer.py`
- `{onescience_path}/onescience/src/onescience/modules/diffusion/protenixdiffusion.py`
- `{onescience_path}/onescience/src/onescience/modules/encoder/protenixencoding.py`
