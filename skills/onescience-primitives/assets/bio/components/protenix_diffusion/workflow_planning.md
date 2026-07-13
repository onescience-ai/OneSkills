# description

用于规划 Protenix diffusion denoising step 与完整采样循环的边界。

# when_to_use

- 已有 Protenix trunk 输出，需要生成坐标。
- 训练中需要 denoising loss。
- 推理中需要 sample_diffusion 多步采样。

# inputs

- `x_noisy`、noise schedule。
- `s_inputs/s_trunk/z_trunk`。
- feature dict atom 字段。
- 采样步数和样本数。

# outputs

```text
component_choice:
  name: protenix_diffusion
  action: single_denoise_step | generator_sampling | mini_rollout | reject
```

# procedure

1. 判断是单步 forward 还是完整采样。
2. 校验 `N_sample` 与 noise level。
3. 校验 atom-token mapping 和 trunk 条件。
4. 选择 training/inference noise scheduler。

# constraints

不要把 diffusion module 当作完整模型；不要在没有 pairformer trunk 的情况下直接采样。

# next_phase_recommendation

推理接 Protenix generator；训练接 Protenix loss 和 symmetric permutation。

# fallback

坐标维度错时检查 atom 数；显存不足时降低 `N_sample/N_step` 或启用 chunk。
