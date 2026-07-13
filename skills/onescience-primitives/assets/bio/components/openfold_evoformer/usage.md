# launch

```sh
python -c "from onescience.models.openfold.evoformer import EvoformerStack; print(EvoformerStack.__name__)"
```

# input_schema

从 OpenFold data pipeline 或 model iteration 获取 `m`、`z`、`msa_mask`、`pair_mask`。extra MSA 路线额外需要 `a` 和 `extra_msa_mask`。monomer、multimer、seq embedding mode 等 preset 会影响 batch 字段和 attention 行为。

# runtime_interfaces

- `EvoformerStack.forward`: 更新 MSA、pair 并生成 single representation。
- `ExtraMSAStack.forward`: 使用 extra MSA 更新 pair representation。
- `AlphaFold.iteration`: OpenFold 外层调用 trunk 的主要位置。

# main_functions

- `forward`
- `_forward_offload`

# execution_resources

长序列任务需要关注 pair representation 显存；可通过 chunk、offload、low-memory attention、flash attention 或 DeepSpeed evo attention 降低内存压力。

# operation_limits

`contract_only` 表示不能直接假设 `OneTransformer(style="OpenFoldEvoformer")` 可运行。offload forward 仅适合非训练、无梯度推理；OpenFold Evoformer 与 Protenix Pairformer 的输入协议不兼容。
