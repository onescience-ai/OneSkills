# launch

Python API 方式调用，作为 PT-DiT 采样调度器使用：

```sh
python -c "from onescience.flax_models.Pt_DiT.train.schedulers import GaussianDiffusion; print(GaussianDiffusion.__name__)"
```

# input_schema

传入 diffusion timestep 数；训练或采样时输入 latent、timestep 和噪声 tensor，shape 需要完全匹配。

# runtime_interfaces

- `q_sample`: 直接构造 xt。
- `q_sample_step`: 单步前向加噪。
- `p_mean_variance`: 估计反向后验。
- `p_ddim`: DDIM 反向更新。
- `alphas_cumprod_to_t`: alpha 到 timestep 的映射。

# main_functions

- `q_sample`
- `q_sample_step`
- `p_mean_variance`
- `p_ddim`
- `alphas_cumprod_to_t`

# execution_resources

调度器开销低；总体耗时由 denoiser 调用次数决定。

# operation_limits

不处理 latent mask 和结构解码。timestep 顺序、预测目标或采样公式与训练不一致会降低生成质量。
