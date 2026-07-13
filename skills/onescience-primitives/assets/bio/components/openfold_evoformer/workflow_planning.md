# description

该卡用于 OpenFold trunk 组件选择、替换和显存策略规划，尤其是 AF2-style PyTorch folding 中的 MSA/pair 表征更新。

# when_to_use

- 任务是 OpenFold 训练、微调或推理。
- 需要修改 MSA attention、triangle update、chunk/offload 策略。
- 需要在 AF2 PyTorch 路线中定位 Evoformer。

# inputs

- OpenFold batch 与 model config。
- 序列长度、MSA 深度、extra MSA 数量。
- attention 实现和显存约束。

# outputs

- 选择 `EvoformerStack` 或 `ExtraMSAStack`。
- chunk/offload/attention 策略。
- 是否需要补 `OneTransformer` 适配层。

# procedure

1. 先确认任务属于 OpenFold 而非 Protenix/AF3。
2. 检查 `m`、`z`、mask 和 recycling 维度。
3. 根据序列长度选择 chunk、offload 或 attention 实现。
4. 若要接 StructureModule，确认输出 `s` 与 `z` 的维度。

# constraints

- 不将 OpenFold trunk 与 Protenix feature dict 混用。
- 不同时启用互斥 attention 路线。
- 不把 `blocks_per_ckpt` 当作层数。

# next_phase_recommendation

若需要结构输出，继续读取 `openfold_structure_module`；若需要 AF3 风格 trunk，切换到 Protenix Pairformer 或 AlphaFold3 JAX Pairformer。

# fallback

显存不足时优先降低 chunk、启用 offload 或换 low-memory attention；接口不匹配时回到 OpenFold 原生 `AlphaFold.iteration`。
