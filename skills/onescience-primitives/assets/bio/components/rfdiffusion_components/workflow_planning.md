# description

该卡用于 RFdiffusion 骨架生成任务的组件选择和配置规划，覆盖 sampler、diffuser、RoseTTAFoldModule 与 SE(3) 结构轨道边界。

# when_to_use

- 用户任务是 motif scaffolding、binder design、partial diffusion 或 de novo backbone generation。
- 输入包含 contig、input PDB、hotspot、symmetry 或 guiding potentials。
- 需要理解 RFdiffusion 内部 sampler/diffuser/trunk 关系。

# inputs

- Hydra overrides。
- checkpoint 需求。
- contig 和 input PDB。
- diffusion steps、partial_T、symmetry、potential。

# outputs

- 推荐 runner 和 checkpoint。
- 采样配置和输出文件说明。
- 后续序列设计建议。

# procedure

1. 先解析任务类型和 contig。
2. 根据输入条件选择 checkpoint。
3. 初始化 Sampler、Diffuser 和 RoseTTAFoldModule。
4. 执行采样并写出 PDB/TRB/traj。
5. 若需要序列，进入 ProteinMPNN 后处理。

# constraints

- 不把骨架输出当作最终序列设计。
- 不随意 override checkpoint。
- 不优先修改 SE(3) 层，除非任务明确是结构轨道改造。

# next_phase_recommendation

生成骨架后优先接 `proteinmpnn_components` 做 inverse folding；如果要改等变结构轨道，继续读取 `se3_transformer_components`。

# fallback

contig 解析或 checkpoint 选择失败时，先降级为配置检查；若 IGSO3 cache 缺失，先生成或指定缓存路径。
