# component_info

`alphafold3_jax_components` 是 AlphaFold3 JAX/Haiku 组件契约，覆盖 `AlphaFold3JAXPairformer`、`AlphaFold3JAXDiffusionHead`、`AlphaFold3JAXAtomCrossAttention` 和 `AlphaFold3JAXConfidenceHead`。原始 contract 中组件族为 `pairformer / diffusion / attention / head`，目标统一入口为 `OnePairformer / OneDiffusion / OneAttention / OneHead`，注册状态为 `contract_only`。

# purpose

用于 AF3 JAX 推理脚本、data pipeline 和模型内部逻辑定位。该组件族处理 token/atom layout、template/MSA/pairformer trunk、diffusion sampling 与 confidence scoring。它与 Protenix 功能相近但实现、feature dict、layout 和权重不兼容，不能共享 Protenix 的注册名或输入协议。

# input_schema

```text
脚本入口:
  folding_input.Input
  JSON path 或 input dir
  optional MSA/template/database config

Model.__call__:
  batch: features.BatchDict
  key: optional PRNG key

feat_batch.Batch 关键字段:
  token_features, msa, templates
  ref_structure, predicted_structure_info
  atom_cross_att, pseudo_beta_info
  bond info layouts
```

# output_schema

```text
Model.__call__:
  diffusion_samples
  distogram
  predicted_lddt
  predicted_experimentally_resolved
  full_pde, average_pde, full_pae
  tmscore_adjusted_pae_global
  tmscore_adjusted_pae_interface
  optional embeddings

DiffusionHead.sample:
  atom_positions: (N_sample, N_token, max_atoms_per_token, 3)
  mask: (N_sample, N_token, max_atoms_per_token)
```

# parameters

- `Model.Config`: `evoformer`、`global_config`、`heads.diffusion`、`heads.confidence`、`heads.distogram`、`num_recycles=10`、`return_embeddings=False`、`return_distogram=False`。
- `DiffusionHead.Config`: `eval_batch_size=5`、`conditioning.pair_channel=128`、`conditioning.seq_channel=384`、`eval.num_samples=5`、`eval.steps=200`。
- `Evoformer.Config`: `seq_channel=384`、`pair_channel=128`、`num_msa=1024`、`pairformer.num_layer=48`。

# key_dependencies

- `model.py`
- `evoformer.py`
- `modules.py`
- `diffusion_head.py`
- `atom_cross_attention.py`
- `confidence_head.py`
- `run_alphafold.py`

# usage_and_risks

典型用法是 `process_fold_input` 准备 input，`ModelRunner.run_inference` 调用模型，`predict_structure` 汇总样本和 ranking。`contract_only` 来自原始 contract，表示目标 `style` 仅是 skill 契约归一名，当前源码不保证能直接通过 `One*` registry 实例化。ligand、CCD、RDKit、bond layout 对输入 JSON 质量敏感；`num_res >= 4000` 会触发特殊 bf16 trunk 分支；`return_embeddings` 和 `return_distogram` 可能产生大文件。

# code_references

- `{onescience_path}/onescience/src/onescience/flax_models/alphafold3/model/model.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold3/model/network/evoformer.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold3/model/network/modules.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold3/model/network/diffusion_head.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold3/model/network/atom_cross_attention.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold3/model/network/confidence_head.py`
- `{onescience_path}/onescience/examples/biosciences/alphafold3/run_alphafold.py`
