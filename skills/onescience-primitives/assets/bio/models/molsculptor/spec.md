# component_info

MolSculptor 是小分子图到序列生成与 latent diffusion 优化组件，核心功能是把 SMILES 转成 RDKit 分子图特征，经 Encoder/Decoder 或 DiffusionTransformer 生成候选分子，并用 LogP、QED、SA、Tanimoto、docking reward 和 NSGA-II 做筛选；它的输入语义是小分子，不是 FASTA、MSA、PDB folding batch 或 ProToken 结构 token。

# architecture_overview

MolSculptor 的架构由三条主线组成:

SMILES / graph 路线:
  SMILES
    -> RDKit Mol
    -> atom/bond graph features
    -> Encoder / MolCT
    -> graph latent tokens
    -> Decoder / SeqGenerator
    -> generated SMILES

latent diffusion 路线:
  latent tokens
    -> GaussianDiffusion
    -> DiffusionTransformer
    -> denoised latent tokens
    -> decoder / reward filtering

optimization 路线:
  generated molecules
    -> RDKit properties / similarity / docking reward
    -> NSGA-II selection
    -> candidate molecules

# parameter_scale

- graph padding 常见 `n_padding_atom=64`。
- `Inferencer.sampling_method` 支持 `greedy`、`beam`、`top_p`、`top_k`、`nucleus`。
- diffusion timesteps 来自 `config.diffusion_timesteps`。
- case 目录覆盖 PI3K、AR-GR、SEH-FAAH、JNK3-GSK3B 等分子优化场景。

# architecture_structure

- `Encoder`: 分子 atom / bond feature 编码。
- `Decoder`: 基于 graph latent 条件生成 SMILES tokens。
- `InferEncoder`, `InferDecoder`, `Inferencer`: 推理期图编码、逐步解码、greedy/beam/top-k/top-p sampling。
- `L2SeqGenerator`, `MMDSeqGenerator`: graph latent 投影与序列生成训练路径。
- `DiffusionTransformer`: latent token diffusion transformer。
- `GaussianDiffusion`: diffusion schedule、`q_sample`、posterior mean/variance。
- reward helpers: RDKit properties、similarity、docking reward、NSGA-II。

# input_schema

- SMILES / graph inference 输入:
  - SMILES string。
  - padded atom graph features。
  - padded bond graph features。
- `smi2graph_features` 生成字段:
  - atom: `atom_type`, `formal_charge`, `num_degree`, `num_H`, `aromaticity`, `hybridization`, `chiral`, `atom_mask`。
  - bond: `bond_type`, `stereo`, `conjugated`, `in_ring`, `bond_mask`, `graph_distance`。
- sequence decoder 输入:
  - `sequence_features["tokens"]`。
  - `sequence_features["mask"]`。
  - optional rope index。
  - graph conditional latent。
- diffusion 输入:
  - `tokens`: `(B, T, C)`。
  - `tokens_mask`: `(B, T)`。
  - `time`: `(B,)`。
  - optional label / rope index。

# output_schema

- graph encoder 输出:
  - graph conditional features。
  - latent graph tokens。
- decoder / generator 输出:
  - SMILES token logits。
  - generated SMILES。
  - auxiliary graph latent features。
- diffusion 输出:
  - denoised latent token prediction。
- reward / optimization 输出:
  - `LogP`。
  - `QED`。
  - `SA`。
  - Tanimoto similarity。
  - DSDP docking reward。
  - NSGA-II selected candidates。

# shape_transformations

- SMILES -> RDKit Mol -> atom/bond arrays
- atom features padded to `(N_atom_max,)`
- bond features padded to `(N_atom_max, N_atom_max)`
- graph encoder latent: `(B, N_query, D_latent)`
- sequence tokens: `(B, N_seq)`
- decoder logits: `(B, N_seq, vocab_size)`
- diffusion latent tokens: `(B, T, C)`

# key_dependencies

- `Encoder`
- `Decoder`
- `InferEncoder`
- `InferDecoder`
- `Inferencer`
- `L2SeqGenerator`
- `MMDSeqGenerator`
- `DiffusionTransformer`
- `GaussianDiffusion`
- `TrainDataLoader`
- `AEDataLoader`
- `dsdp_reward`
- `NSGA_II`

# common_modification_points

- 修改分子过滤优先改 `standardize` 和 RDKit feature checks。
- 修改采样策略优先改 `Inferencer` config 的 `sampling_method`、`beam_size`、`top_k`、`top_p`。
- 修改图大小上限要同步 padding、模型 config 和训练数据处理。
- 修改 reward 优先在 reward helper 或 case-local reward 文件中接入，不改基础 encoder/decoder。

# implementation_risks

- MolSculptor 不应接 `ProteinDataset`、OpenFold batch、Protenix feature dict 或 Evo2 tokenizer。
- RDKit sanitize / standardize 失败会返回 `None` 或中断候选分子。
- docking reward 依赖外部二进制、PDBQT、case 脚本和缓存路径，不适合默认轻量运行。
- graph padding、vocab、checkpoint 和 config 必须配套。
- 生成 SMILES 需要再做化学有效性和任务 reward 筛选。

# code_references

- `{onescience_path}/onescience/src/onescience/flax_models/MolSculptor/train/inference.py`
- `{onescience_path}/onescience/src/onescience/flax_models/MolSculptor/net/generator.py`
- `{onescience_path}/onescience/src/onescience/flax_models/MolSculptor/net/encoder.py`
- `{onescience_path}/onescience/src/onescience/flax_models/MolSculptor/net/decoder.py`
- `{onescience_path}/onescience/src/onescience/flax_models/MolSculptor/src/model/diffusion_transformer.py`
- `{onescience_path}/onescience/src/onescience/flax_models/MolSculptor/train/scheduler.py`
- `{onescience_path}/onescience/src/onescience/flax_models/MolSculptor/train/rewards.py`
- `{onescience_path}/onescience/examples/biosciences/molsculptor/inference`
- `{onescience_path}/onescience/examples/biosciences/molsculptor/cases`
