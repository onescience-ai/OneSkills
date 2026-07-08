# launch

```sh
python -c "from onescience.modules import OneDiffusion; d=OneDiffusion(style='ProtenixDiffusionModule', c_atom=128, c_atompair=16, c_token=768, c_s=384, c_z=128, c_s_inputs=449); print(type(d).__name__)"
```

# input_schema

准备 Protenix trunk 输出 `s_inputs/s_trunk/z_trunk`、noisy coordinates、noise level 和完整 feature dict。完整采样时由 generator 多步调用。

# runtime_interfaces

- `OneDiffusion(style="ProtenixDiffusionModule", ...)`
- `forward`
- `f_forward`

# main_functions

- `forward`
- `f_forward`

# execution_resources

资源消耗来自 atom encoder/decoder、token diffusion transformer 和采样步数。完整推理常见 `N_sample=5`、`N_step=200`。

# operation_limits

不是完整采样器；不生成 trunk 表征；关闭 conditioning 或缺失 atom-token mapping 会破坏结构生成。
