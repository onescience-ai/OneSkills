# description

用于规划蛋白 single/pair 表征的结构更新，补充 diffusion transformer 中的 pair representation 构造能力。

# when_to_use

- 需要从 single residue 表征生成 pair 更新。
- 需要 AF2/ESMFold 风格 outer product/difference。
- 需要 pair transition 更新。

# inputs

- single 表征。
- neighbor single 表征。
- pair 表征。
- masks。

# outputs

- pair update。
- transition 更新结果。
- 模块组合建议。

# procedure

1. 检查 single/pair 维度。
2. 用 OuterProduct 或 OuterDifference 构造 pair update。
3. 用 Transition 做非线性更新。
4. 将结果输入 attention 或 diffusion block。

# constraints

- 不输出坐标。
- 不包含完整 trunk。
- dense pair 表征成本高。

# next_phase_recommendation

接入 PT-DiT attention 或 protein decoder 前的 pair 更新链路。

# fallback

若 pair 表征过大，使用稀疏邻居或降低 pair channel。
