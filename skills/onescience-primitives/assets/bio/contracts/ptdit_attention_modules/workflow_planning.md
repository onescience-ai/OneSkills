# description

用于规划 PT-DiT 蛋白 latent transformer 中的注意力、结构感知注意力和 pair 条件注意力。

# when_to_use

- 需要蛋白 latent 或 residue 表征注意力。
- 需要 RoPE、hyper attention 或 IPA。
- 任务涉及蛋白结构感知生成。

# inputs

- single/pair 表征。
- mask、neighbor index。
- 可选旋转和平移框架。

# outputs

- attention 模块选择。
- dense/sparse 模式建议。
- 与 diffusion transformer 的连接方式。

# procedure

1. 判断是否需要结构帧。
2. 无结构帧时用 scalar attention。
3. 有 pair 条件时加入 hyper attention。
4. 有刚体帧时使用 invariant point attention。

# constraints

- mask 和邻居索引必须一致。
- flash attention 有设备限制。
- IPA 需要合法旋转和平移。

# next_phase_recommendation

继续接 PT-DiT diffusion transformer 或结构 transformer 更新模块。

# fallback

若 IPA 输入不完整，退回 scalar attention；若 flash attention 不可用，使用普通 attention kernel。
