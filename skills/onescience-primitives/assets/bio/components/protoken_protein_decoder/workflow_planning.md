# description

用于规划 ProToken 的最终蛋白坐标恢复阶段，将 single/pair 表征解码为原子坐标和质量估计。

# when_to_use

- 已有兼容的 single/pair 表征。
- 需要输出蛋白结构坐标。
- 需要 pLDDT 或结构轨迹。

# inputs

- single_act、pair_act。
- seq_mask、aatype。
- decoder 和 structure module 配置。

# outputs

- atom coordinates。
- structure trajectory。
- pLDDT logits。
- 结构后处理建议。

# procedure

1. 检查 single/pair 维度。
2. 初始化 frame。
3. 运行 structure module。
4. 输出坐标并评估 pLDDT。

# constraints

- 不负责 latent 采样。
- aatype 处理需核对。
- 结构质量依赖上游 latent。

# next_phase_recommendation

接 PDB 保存、结构质量评估、motif 检查或下游筛选。

# fallback

若坐标异常，检查上游 VQ decoder、mask、residue_index 和 aatype 处理。
