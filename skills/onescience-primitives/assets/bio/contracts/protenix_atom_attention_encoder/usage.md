# launch

```sh
python -c "from onescience.modules import OneEncoder; enc=OneEncoder(style='ProtenixAtomAttentionEncoder', has_coords=False, c_token=384); print(type(enc).__name__)"
```

# input_schema

准备 Protenix atom reference feature dict。静态输入编码设置 `has_coords=False`；diffusion atom 编码设置 `has_coords=True` 并额外提供 noisy coordinates、single trunk 和 pair trunk。

# runtime_interfaces

- `OneEncoder(style="ProtenixAtomAttentionEncoder", ...)`
- `forward(input_feature_dict, r_l=None, s=None, z=None, ...)`

# main_functions

- `forward`

# execution_resources

计算量与 `N_atom`、`N_token`、`n_queries/n_keys` 和 local trunk 数相关；长复合物推理会有明显显存压力。

# operation_limits

不接受普通 FASTA、OpenFold atom37 或裸坐标张量。`atom_to_token_idx` 错误会导致 token 聚合整体错位。
