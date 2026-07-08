# description

用于规划 ProToken latent 解码的表征恢复阶段，将离散/量化 latent 转回 single/pair 表征。

# when_to_use

- 已有 ProToken latent 或 vq_act。
- 需要从 latent 恢复结构表征。
- 需要 distogram 作为质量或几何约束。

# inputs

- vq_act。
- seq_mask 和 residue_index。
- decoder 配置。

# outputs

- single/pair 表征。
- distogram logits。
- 后续坐标解码建议。

# procedure

1. 校验 latent channel 和长度。
2. 构造 relative position pair。
3. 执行 pair/single/co-update。
4. 输出 distogram 并接 protein decoder。

# constraints

- 不输出最终坐标。
- latent 必须与 codebook/decoder 匹配。
- residue_index 错误会影响几何。

# next_phase_recommendation

接 ProToken protein decoder 生成 atom positions。

# fallback

若 latent 不兼容，回到同 checkpoint 的 encoder/bottleneck 重新生成。
