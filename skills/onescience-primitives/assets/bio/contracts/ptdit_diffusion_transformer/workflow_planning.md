# description

用于规划 PT-DiT 蛋白 latent 扩散去噪主干，在 ProToken latent 空间执行蛋白生成、补全或编辑。

# when_to_use

- 已有 ProToken latent。
- 需要蛋白序列-结构联合生成。
- 任务类似 LaProteina 的蛋白生成但希望参考 latent diffusion。

# inputs

- latent tokens 和 mask。
- timestep 和可选标签。
- scheduler 与采样策略。

# outputs

- denoiser 调用计划。
- latent 采样流程。
- 与 ProToken decoder 的连接建议。

# procedure

1. 获取或采样初始 latent。
2. 根据 scheduler 准备 timestep。
3. 调用 PT-DiT denoiser。
4. 将最终 latent 交给 ProToken decoder 重建结构。

# constraints

- 不直接读写 PDB。
- 不输出坐标。
- 序列长度和 latent dim 必须匹配 checkpoint。

# next_phase_recommendation

接 ProToken bottleneck/decoder 或任务特定筛选器。

# fallback

若 latent 协议不匹配，退回 LaProteina 原生生成管线或先做 latent adapter。
