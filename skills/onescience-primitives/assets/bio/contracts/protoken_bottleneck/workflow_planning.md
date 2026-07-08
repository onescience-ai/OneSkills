# description

用于规划 ProToken encoder 与 decoder 之间的量化瓶颈，把连续结构表征转换为可生成的离散或 compact latent。

# when_to_use

- 需要结构 token 化。
- 需要 PT-DiT 在 latent token 空间生成。
- 需要压缩蛋白结构表征。

# inputs

- encoder 输出 single 表征。
- residue mask。
- codebook 和量化配置。

# outputs

- quantized latent。
- token indexes。
- codebook 使用统计。
- 与 diffusion/decoder 的连接建议。

# procedure

1. 校验 latent dim。
2. 投影到瓶颈空间。
3. 执行量化并获得 token index。
4. 将量化 latent 送入 decoder 或 diffusion 模型。

# constraints

- codebook 必须与 checkpoint 匹配。
- 不输出结构坐标。
- 量化退化会影响生成质量。

# next_phase_recommendation

接 PT-DiT diffusion transformer 做 latent 生成，或接 ProToken decoder 做重建。

# fallback

若 codebook 利用率低，重新训练或调整 commitment/codebook 参数；若 checkpoint 不匹配，回退同源 encoder-decoder。
