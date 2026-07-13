# description

用于规划小分子 latent 扩散 denoiser，在 latent token 空间生成或优化分子表示。

# when_to_use

- 任务是小分子生成或 latent 优化。
- 已有 latent token 和 diffusion scheduler。
- 需要与 TargetDiff 类扩散生成做模块对照。

# inputs

- latent tokens、mask、time。
- 可选 label 条件。
- denoiser 配置和训练目标。

# outputs

- 去噪预测。
- 采样循环连接建议。
- 与 decoder 的衔接方式。

# procedure

1. 确认 latent 表征来源。
2. 选定 scheduler 和预测目标。
3. 在每个 timestep 调用 denoiser。
4. 将最终 latent 解码为 SMILES 或图结构。

# constraints

- 不含口袋条件。
- 不含化学合法性校验。
- 预测目标必须与训练一致。

# next_phase_recommendation

对 protein-ligand 任务，补充 pocket condition、reward 或 docking 筛选。

# fallback

如果 latent 扩散不适配三维任务，退回 TargetDiff 原生坐标扩散模型。
