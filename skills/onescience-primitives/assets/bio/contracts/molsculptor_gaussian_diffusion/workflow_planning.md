# description

用于规划 MolSculptor latent 扩散训练和采样的噪声日程。

# when_to_use

- 需要 q(x_t|x_0) 加噪。
- 需要 DDIM 或后验均值方差采样。
- denoiser 已经确定。

# inputs

- diffusion timesteps。
- latent tensor 和噪声。
- timestep 序列。

# outputs

- 加噪样本。
- 反向采样参数。
- 采样步进策略。

# procedure

1. 初始化 beta/alpha schedule。
2. 训练时采样 timestep 并调用 q_sample。
3. 推理时用 denoiser 预测 eps。
4. 调用 p_mean_variance 或 p_ddim 更新 latent。

# constraints

- 不包含 denoiser。
- 不处理 mask。
- 不验证分子合法性。

# next_phase_recommendation

连接 MolSculptor diffusion transformer 和 SMILES decoder。

# fallback

如果采样不稳定，减少步长、切换 DDIM、裁剪 x0 或重新校准 beta schedule。
