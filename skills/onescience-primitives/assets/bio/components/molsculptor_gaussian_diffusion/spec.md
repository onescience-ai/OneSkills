# component_info

`molsculptor_gaussian_diffusion` 是 MolSculptor 的高斯扩散调度器，预计算 beta、alpha、posterior 系数，并提供前向加噪和反向采样所需公式。

# purpose

用于 latent diffusion 的噪声日程、训练采样和推理采样，适合分子 latent 生成流程；不包含 denoiser 网络，也不负责 SMILES 解码。

# input_schema

```text
config:
  diffusion_timesteps: int

x_start / x_t / eps / noise:
  Tensor[float]: arbitrary broadcastable latent shape

t:
  Tensor[int]: (Batch,)
```

# output_schema

```text
q_sample:
  noisy latent x_t

p_mean_variance:
  model_mean, model_variance, model_log_variance

p_ddim:
  next latent sample
```

# parameters

- `diffusion_timesteps`: 扩散步数。
- `beta_start`: 由步数缩放得到。
- `beta_end`: 由步数缩放得到。
- `clip`: 是否裁剪预测 x0。
- `clamp_x0_fn`: 可选 x0 约束函数。

# key_dependencies

- `scheduler.py`

# usage_and_risks

调度器要求 timestep 索引位于合法范围，噪声 tensor 与 latent shape 完全一致。它只定义数学日程，不会检查化学合法性、token mask 或模型预测目标。

# code_references

- `{onescience_path}/onescience/src/onescience/flax_models/MolSculptor/train`
