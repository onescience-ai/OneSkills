# description

用于规划 PT-DiT 蛋白 latent 扩散噪声日程，与 denoiser 共同形成采样循环。

# when_to_use

- 需要对 ProToken latent 加噪或去噪采样。
- PT-DiT denoiser 已选定。
- 需要 DDIM 或 posterior 更新。

# inputs

- diffusion timestep 数。
- latent tensor、噪声和 timestep。
- denoiser 预测目标。

# outputs

- q_sample 训练加噪策略。
- p_ddim/p_mean_variance 推理策略。
- timestep 调度计划。

# procedure

1. 初始化调度器。
2. 训练时随机抽样 t 并加噪。
3. 推理时从噪声 latent 开始反向迭代。
4. 每步调用 denoiser 并更新 latent。

# constraints

- 不含 denoiser。
- 不处理结构解码。
- schedule 必须与训练一致。

# next_phase_recommendation

连接 PT-DiT diffusion transformer，再接 ProToken decoder。

# fallback

若采样发散，降低步长、裁剪 x0、改用 DDIM 或重新匹配训练 schedule。
