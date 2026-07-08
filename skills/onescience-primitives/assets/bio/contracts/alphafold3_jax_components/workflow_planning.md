# description

该卡用于 AF3 JAX 推理、组件定位和 OneScience 组件化迁移规划，帮助区分 JAX AF3 与 Protenix 的输入协议和模块边界。

# when_to_use

- 用户任务涉及 AlphaFold3 JAX 推理或 input JSON。
- 需要分析 Pairformer、DiffusionHead、atom cross attention、confidence head。
- 需要判断是否能迁移到 OneScience `One*` 组件体系。

# inputs

- AF3 input JSON 或 input directory。
- data pipeline 开关、MSA/template/CCD/RDKit 配置。
- diffusion sample 数、recycle 数、attention 实现。

# outputs

- 组件映射：pairformer、diffusion、attention、head。
- 推荐执行入口：原生 AF3 runner 或目标 `One*` 适配。
- 风险判断：layout、ligand、bond、资源和输出规模。

# procedure

1. 先确认任务是 AF3 JAX 原版，还是 PyTorch/Protenix 路线。
2. 若是 AF3 JAX，沿用 runner 和 JSON feature pipeline。
3. 若要迁移，按 Pairformer、DiffusionHead、AtomCrossAttention、ConfidenceHead 分别设计适配层。
4. 与 Protenix 组件比对时只比较职责，不共享输入 batch 或权重。

# constraints

- 不将 Protenix feature dict 直接送入 AF3 JAX 组件。
- 不把 AF3 confidence 输出简化为单样本指标。
- 不省略 ligand、CCD、bond layout 的输入质量检查。

# next_phase_recommendation

推理任务交给 runtime 检查 JAX 环境和数据库；组件化任务先补薄适配层和 shape 测试，再考虑注册目标 `One*` style。

# fallback

若 AF3 JAX 依赖或数据库不可用，保留 JSON/schema 检查和组件规划；若用户目标是 PyTorch AF3 风格模型，转向 Protenix 组件卡。
