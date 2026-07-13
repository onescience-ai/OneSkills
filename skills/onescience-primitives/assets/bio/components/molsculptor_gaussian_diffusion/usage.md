# launch

Python API 方式调用，通常由训练或采样循环持有：

```sh
python -c "from onescience.flax_models.MolSculptor.train.scheduler import GaussianDiffusion; print(GaussianDiffusion.__name__)"
```

# input_schema

传入包含 `diffusion_timesteps` 的配置；训练时准备 `x_start`、timestep `t` 和噪声 `eps`，推理时准备当前 latent `x_t` 与模型预测噪声。

# runtime_interfaces

- `q_sample`: 从 x0 直接采样 xt。
- `q_sample_step`: 单步前向加噪。
- `p_mean_variance`: 计算反向后验参数。
- `p_ddim`: 执行 DDIM 更新。
- `alphas_cumprod_to_t`: 将 alpha 累积值映射回时间。

# main_functions

- `q_sample`
- `q_sample_step`
- `p_mean_variance`
- `p_ddim`
- `alphas_cumprod_to_t`

# execution_resources

数学调度器本身开销较低；主要资源由 denoiser 和采样步数决定。

# operation_limits

timestep 必须在合法范围内；输入 latent 和噪声 shape 必须一致。该模块不处理 mask、条件、分子合法性。
