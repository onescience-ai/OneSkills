# launch

```sh
python -c "from onescience.modules import OneDecoder; d=OneDecoder(style='ProtenixAtomAttentionDecoder', n_blocks=3, n_heads=4, c_token=768, c_atom=128, c_atompair=16); print(type(d).__name__)"
```

# input_schema

调用前需要 atom encoder 输出的 `q_skip/c_skip/p_skip`，以及 diffusion transformer 输出的 token latent `a`。

# runtime_interfaces

- `OneDecoder(style="ProtenixAtomAttentionDecoder", ...)`
- `forward(input_feature_dict, a, q_skip, c_skip, p_skip)`

# main_functions

- `forward`

# execution_resources

主要受 `N_atom`、local trunk 数和 `n_queries/n_keys` 影响。

# operation_limits

不能单独替代 diffusion module；输出是坐标增量，不是完整采样坐标。
