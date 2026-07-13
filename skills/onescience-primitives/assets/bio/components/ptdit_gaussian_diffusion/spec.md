# component_info

`ptdit_gaussian_diffusion` 是 PT-DiT 的蛋白 latent 扩散调度器，定义线性 beta schedule、前向加噪、从 eps 还原 x0、后验均值方差和 DDIM 更新。

# purpose

用于 PT-DiT denoiser 的训练和采样日程，适合蛋白 latent 生成任务；不负责 transformer 前向，也不解码结构。

# input_schema

```text
num_diffusion_timesteps:
  int

x_start / x_t / eps / noise:
  Tensor[float]: latent token tensor

t:
  Tensor[int]: (Batch,)
```

# output_schema

```text
q_sample / q_sample_step:
  noisy latent

p_mean_variance:
  posterior mean, variance, log_variance

p_ddim:
  next latent sample
```

# parameters

- `num_diffusion_timesteps`: 扩散总步数。
- `beta_start` / `beta_end`: 根据步数缩放。
- `clip`: 是否裁剪预测 x0。
- `clamp_x0_fn`: 可选 latent 约束函数。

# key_dependencies

- `schedulers.py`

# usage_and_risks

调度器与 denoiser 的预测目标必须一致。timestep 越界、latent shape 与 noise shape 不一致、采样步顺序错误都会导致生成质量下降或运行失败。

# code_references

- `{onescience_path}/onescience/src/onescience/flax_models/Pt_DiT/train`
