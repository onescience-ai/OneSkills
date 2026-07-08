# launch

```sh
python -c "from onescience.modules import OnePairformer; p=OnePairformer(style='ProtenixPairformerStack', n_blocks=1, c_z=128, c_s=384, n_heads=16); print(type(p).__name__)"
```

# input_schema

主 trunk 传入 `s` 和 `z`；MSA/template 内部纯 pair update 可设置 `c_s=0` 并传 `s=None`。`pair_mask` 若提供，必须和 `z[..., N_token, N_token, :]` 对齐。

# runtime_interfaces

- `OnePairformer(style="ProtenixPairformerBlock", ...)`
- `OnePairformer(style="ProtenixPairformerStack", ...)`
- `forward(s, z, pair_mask=None, ...)`

# main_functions

- `forward`

# execution_resources

内存和计算主要由 `N_token^2 * c_z` 决定；stack 层数高时建议使用 checkpoint。

# operation_limits

不负责 MSA 采样、template 搜索或 diffusion 坐标生成。不能与 OpenFold/AlphaFold JAX pair trunk 直接互换。
