# component_info

AlphaFold3 是 JAX/Haiku 风格的多分子复合物结构预测组件，核心能力是把 AF3 JSON 输入、MSA/template/CCD/ligand/bond 等特征转换为 token 和 atom 布局，再通过 trunk 与 diffusion head 生成结构样本和置信度。该组件与 Protenix 同属 AF3-style 路线，但实现栈和 feature dict 不兼容。

# architecture_overview

静态流程:
  JSON fold input
    -> DataPipeline / featurise_input
    -> features.BatchDict
    -> feat_batch.Batch
    -> token / pair / atom layout
    -> Evoformer + PairFormerIteration
    -> DiffusionHead
    -> ConfidenceHead / DistogramHead
    -> post-processing outputs

# parameter_scale

- `num_recycles=10` 是常见推理默认值。
- `num_diffusion_samples=5` 是常见推理默认值。
- diffusion eval 默认采样步数常见为 `steps=200`。
- bucket 默认覆盖从 `256` 到 `5120` 的 token 档位。
- `flash_attention_implementation` 支持 `triton`、`cudnn`、`xla`、`cutlass`。

# architecture_structure

- `ModelRunner`: 加载 Haiku 参数、JIT model forward，并抽取 inference results。
- `Model`: 构建 `feat_batch.Batch`，执行 target embedding、recycling trunk、diffusion sampling 和 confidence heads。
- `Evoformer`: 创建 target/single/pair embeddings，处理 template、MSA、bond embedding。
- `PairFormerIteration`: 更新 single/pair 表征。
- `DiffusionHead`: 基于 noisy atom positions、trunk embeddings 和 atom cross attention 生成坐标样本。
- `ConfidenceHead`: 输出 pLDDT、PAE、PDE、resolved 等置信度。
- `atom_cross_att_encoder` / `atom_cross_att_decoder`: 桥接 token atom layout 与局部 atom query/key layout。
- `DistogramHead`: 输出 contact/distogram 相关 logits。

# input_schema

- 推理脚本入口:
  - `--json_path` 或 `--input_dir`。
  - `--model_dir`。
  - `--output_dir`。
  - `--run_data_pipeline`。
  - `--run_inference`。
  - `--flash_attention_implementation`。
  - `--num_recycles`。
  - `--num_diffusion_samples`。
- JSON 输入可包含:
  - `proteinChain`。
  - `rnaSequence`。
  - `dnaSequence`。
  - `ligand`。
  - templates、MSA、user CCD、bonds 等 AF3 folding input 信息。
- 模型 forward 输入:
  - `batch: features.BatchDict`，内部转换为 `feat_batch.Batch`。
- 关键 batch 语义:
  - `token_features`, `msa`, `templates`, `ref_structure`。
  - `predicted_structure_info`, `atom_cross_att`。
  - polymer-ligand / ligand-ligand bond layouts。

# output_schema

- `Model.__call__` 输出:
  - `diffusion_samples`: `atom_positions`, `mask`。
  - `distogram`。
  - `predicted_lddt`。
  - `predicted_experimentally_resolved`。
  - `full_pde`, `average_pde`。
  - `full_pae`, `tmscore_adjusted_pae_global`, `tmscore_adjusted_pae_interface`。
  - 可选 `single_embeddings`, `pair_embeddings`。
- post-processing 输出:
  - 结构文件。
  - ranking score / metadata。
  - full PAE / PDE / contact probabilities。
  - 可选 embeddings / distogram 文件。

# shape_transformations

- JSON fold input -> `features.BatchDict`
- `target_feat`: `[N_token, C_target]`
- trunk single: `[N_token, 384]`
- trunk pair: `[N_token, N_token, 128]`
- diffusion dense atom positions: `[N_sample, N_token, max_atoms_per_token, 3]`
- post-processing 后映射到 flat output atom layout

# key_dependencies

- `Model`
- `ModelRunner`
- `Evoformer`
- `PairFormerIteration`
- `DiffusionHead`
- `ConfidenceHead`
- `DistogramHead`
- `atom_cross_att_encoder`
- `atom_cross_att_decoder`
- `DataPipeline`
- `featurise_input`

# common_modification_points

- 已有 MSA 的 JSON 推理设置 `--run_data_pipeline=false`。
- 只做 JackHmmer / MMseqs 搜索设置 `--run_inference=false`。
- GPU 或 attention 兼容问题优先切换 `--flash_attention_implementation=xla`。
- 保存 trunk 表征设置 `--save_embeddings=true`，但 pair embeddings 体积很大。
- 保存 distogram 设置 `--save_distogram=true`。

# implementation_risks

- AlphaFold3 JAX batch 与 Protenix feature dict 概念相近但不能共享 adapter。
- 模型参数和输出使用条款应由用户自行确认。
- data pipeline 可能启动大量 CPU 线程，尤其是 sharded JackHmmer / Nhmmer 数据库搜索。
- Triton/cuDNN flash attention 对 GPU 架构和环境要求更高，保守兼容可选 `xla`。
- 配体、CCD、RDKit conformer 和共价键路径对资源文件与化学组件数据敏感。

# code_references

- `{onescience_path}/onescience/src/onescience/flax_models/alphafold3/model/model.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold3/model/network/evoformer.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold3/model/network/modules.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold3/model/network/diffusion_head.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold3/model/network/atom_cross_attention.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold3/model/network/confidence_head.py`
- `{onescience_path}/onescience/examples/biosciences/alphafold3/run_alphafold.py`
- `{onescience_path}/onescience/examples/biosciences/alphafold3/README.md`
