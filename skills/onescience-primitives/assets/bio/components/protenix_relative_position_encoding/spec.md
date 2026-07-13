# component_info

`protenix_relative_position_encoding` 是 Protenix pair 初始化的相对位置编码组件，统一入口为 `OneEncoder`，注册名为 `ProtenixRelativePositionEncoding`。

# purpose

为 Protenix 的 `z_init` 构造 pair 级位置和链实体关系特征，覆盖 residue relative position、token relative position、chain relative position、same chain、same entity 等关系。

# input_schema

```text
input_feature_dict:
  asym_id: [..., N_token]
  residue_index: [..., N_token]
  entity_id: [..., N_token]
  sym_id: [..., N_token]
  token_index: [..., N_token]
```

# output_schema

```text
relative_position_encoding:
  shape: [..., N_token, N_token, c_z]
```

# parameters

- `r_max=32`: residue/token 相对距离截断范围
- `s_max=2`: chain 相对距离截断范围
- `c_z=128`: pair embedding 维度

# key_dependencies

- `oneencoder.py`
- `protenixencoding.py`
- `protenixlinear.py`

# usage_and_risks

该组件在 Protenix `get_pairformer_output` 中加到 `z_init`，也可参与 diffusion conditioning。它依赖 `token_index`；输出是 `N_token x N_token` 张量，长链和复合物会显著增加显存；`asym_id/entity_id/sym_id` 语义错误会污染链和实体关系。

# code_references

- `{onescience_path}/onescience/src/onescience/modules/encoder/oneencoder.py`
- `{onescience_path}/onescience/src/onescience/modules/encoder/protenixencoding.py`
- `{onescience_path}/onescience/src/onescience/models/protenix/protenix.py`
