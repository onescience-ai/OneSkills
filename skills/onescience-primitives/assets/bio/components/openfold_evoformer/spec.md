# component_info

`openfold_evoformer` 是 OpenFold 的 AF2-style trunk 组件契约，覆盖 `EvoformerStack` 和 `ExtraMSAStack`。原始 contract 中模块族为 `transformer`，目标统一入口为 `OneTransformer`，注册名为 `style="OpenFoldEvoformer"` 和 `style="OpenFoldExtraMSAStack"`，注册状态为 `contract_only`。

# purpose

用于交替更新 MSA representation、pair representation，并产生 StructureModule 所需的 single representation。适用于 OpenFold 训练、微调、推理和 AF2 PyTorch 组件化规划；不适用于 Protenix/AF3 feature dict，也不能直接替换 Protenix Pairformer。

# input_schema

```text
EvoformerStack.forward:
  m: [*, N_seq, N_res, C_m]
  z: [*, N_res, N_res, C_z]
  msa_mask: [*, N_seq, N_res]
  pair_mask: [*, N_res, N_res]
  chunk_size
  use_deepspeed_evo_attention
  use_lma
  use_flash

ExtraMSAStack.forward:
  a: [*, N_extra, N_res, C_e]
  z: [*, N_res, N_res, C_z]
  extra_msa_mask
```

# output_schema

```text
EvoformerStack:
  m: [*, N_seq, N_res, C_m]
  z: [*, N_res, N_res, C_z]
  s: [*, N_res, C_s]

ExtraMSAStack:
  z: [*, N_res, N_res, C_z]
```

# parameters

- 表征维度：`c_m`、`c_z`、`c_s`。
- hidden 维度：`c_hidden_msa_att`、`c_hidden_opm`、`c_hidden_mul`、`c_hidden_pair_att`。
- 层数与头数：`no_blocks`、`no_heads_msa`、`no_heads_pair`。
- 训练/推理控制：`transition_n`、`msa_dropout`、`pair_dropout`、`blocks_per_ckpt`、`clear_cache_between_blocks`、`tune_chunk_size`。

# key_dependencies

- `model.py`
- `evoformer.py`
- `msa.py`
- `triangular_attention.py`

# usage_and_risks

Evoformer block 内部包含 MSA attention、outer product mean、triangular multiplicative update、triangular attention 和 transition。`contract_only` 来自原始 contract，说明目标 `style` 不表示当前源码已在 `OneTransformer` registry 中可直接实例化。`N_res x N_res x C_z` 是主要显存来源；`use_deepspeed_evo_attention`、`use_lma`、`use_flash` 是互斥路线；OpenFold batch 的最后一维是 recycling 维度。

# code_references

- `{onescience_path}/onescience/src/onescience/models/openfold/model.py`
- `{onescience_path}/onescience/src/onescience/models/openfold/evoformer.py`
- `{onescience_path}/onescience/src/onescience/models/openfold/msa.py`
- `{onescience_path}/onescience/src/onescience/models/openfold/triangular_attention.py`
