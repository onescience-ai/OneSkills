# launch

```sh
python -c "from onescience.modules import OneTransformer; t=OneTransformer(style='ProtenixDiffusionTransformer', n_blocks=1, n_heads=16, c_a=768, c_s=384, c_z=128); print(type(t).__name__)"
```

# input_schema

Token diffusion transformer 使用 global `z`；atom transformer 使用 local `p`。二者不要混用。

# runtime_interfaces

- `OneTransformer(style="ProtenixDiffusionTransformer", ...)`
- `OneTransformer(style="ProtenixAtomTransformer", ...)`
- `forward`

# main_functions

- `forward`

# execution_resources

Token transformer 受 `N_token^2` 影响；atom transformer 受 atom local window 和 trunk 数影响。梯度开启时 `blocks_per_ckpt` 可降低显存。

# operation_limits

不是通用 Transformer encoder，不输出最终坐标。修改 `n_queries/n_keys` 必须同步 atom encoder 和 atom decoder。
