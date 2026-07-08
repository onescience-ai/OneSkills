# description

PT-DiT 规划知识用于把蛋白 de novo co-design、结构 token latent 生成、RePaint、插值或 PT-DiT + ProToken 联动任务组织成可执行计划。

# when_to_use

- 用户需要蛋白序列和结构表示协同生成。
- 用户明确使用 ProToken 结构 token、PT-DiT checkpoint 或相关 embedding。
- 用户需要 de novo design、latent interpolation、contextual scaffolding 或 RePaint。
- 不用于普通 FASTA folding、AF2/AF3 预测或 ProteinMPNN inverse folding。
- 若目标只是 PDB -> structure token 或 token -> PDB 重建，优先转 ProToken；若目标是骨架到序列设计，优先转 ProteinMPNN。
- 当端到端 workflow 的起点是 `token_or_codesign`、`latent_generation` 或用户明确要求 ProToken + AA embedding 协同生成时，PT-DiT 可以作为独立设计起点；常规 `protein_design_to_structure_validation` 的无 backbone 起点默认仍是 RFdiffusion。

# inputs

- 任务模式: de_novo、decode_structures、repaint、latent_interpolation。
- 模型资源: PT-DiT checkpoint、ProToken checkpoint、protoken_emb、aatype_emb。
- 采样参数: `nres`、`nsample_per_device`、diffusion timesteps。
- 输出需求: token indexes、sequence indexes、latent embedding、PDB。
- 端到端上下文: `workflow_type`、`starting_point=token_or_codesign`、`current_stage=latent_generation`、ProToken/AA embedding 版本、是否需要 ProToken decode 和结构验证。

# outputs

- 调用决策: 是否使用 PT-DiT。
- 执行计划: de_novo_design 或 notebook 路线、资源路径、采样参数。
- 结果产物: `result.pkl`、`result_flatten.pkl`、protoken indexes、aatype indexes、可选 PDB。
- 下游交接: 将 latent、protoken indexes、aatype indexes、decoded PDB、候选 ID 和资源版本交给 ProToken decode、SimpleFold/OpenFold 单体验证或 AlphaFold3/Protenix 复合物验证。

# procedure

1. 确认任务需要 ProToken + PT-DiT，而不是 folding 或 inverse folding。
2. 若是端到端 workflow，确认 `current_stage=latent_generation`，并记录 downstream validator，而不是把普通 FASTA/OpenFold batch 送入 PT-DiT。
3. 检查 embedding、PT-DiT checkpoint 和 ProToken checkpoint 是否配套。
4. 设置 `nres` 和采样规模。
5. 决定是否直接解码结构。
6. 运行 de novo 或对应 notebook 流程。
7. 检查输出 token、序列、PDB 和结构质量。
8. 进入下游结构预测复核或功能筛选。

# constraints

- PT-DiT 与 ProToken 资源必须版本一致。
- `nres` 必须满足 flash attention / padding 约束。
- 多设备采样 batch 要能按设备数整除。
- 输出不是最终实验验证结果。
- PT-DiT 需要 ProToken/AA latent 与 diffusion timesteps，不应直接接普通 FASTA、OpenFold batch 或 AF3 feature dict。
- 本卡只声明 `latent_generation` / `sequence_structure_codesign` stage contract；常规 RFdiffusion/ProteinMPNN 链路不应被 PT-DiT 自动替代。

# next_phase_recommendation

- 生成结构用 ProToken decode 后做几何检查。
- 候选序列可用 SimpleFold/OpenFold 做单体验证，binder 或复合物候选可用 AlphaFold3/Protenix 复核。
- 对设计任务保留 latent、token 和 PDB 三类产物便于回溯。

# fallback

- ProToken 解码失败时先只保存 token/latent。
- 显存不足时降低 `nsample_per_device` 或关闭结构解码。
- checkpoint 不匹配时回退到只做资源一致性检查。
