# Model Card: MolSculptor

## 基本信息

- 模型名：`MolSculptor`
- 任务类型：`小分子生成 / 分子优化 / 药物设计辅助`
- 当前状态：`stable`
- 主实现目录：`./onescience/src/onescience/flax_models/MolSculptor`

## 模型定位

MolSculptor 是 OneScience 生信 examples 中的小分子设计与优化工具链，围绕分子图编码、SMILES/序列解码、latent diffusion 和奖励函数做分子生成或优化。

补充说明：

- 它属于 biosciences / drug design 方向，但不是蛋白质结构预测或蛋白设计模型
- 输入核心是 SMILES / 分子图 / docking case，而不是 FASTA、MSA、PDB folding batch
- 依赖 JAX/Flax、RDKit，以及部分 case 中的 OpenBabel / DSDP docking 脚本
- example 目录没有顶层 README，优先以 `inference/`、`training/`、`cases/` 与源码为准

## 输入定义

- SMILES / graph inference 输入：
  - SMILES string
  - padded atom graph features
  - padded bond graph features
- `smi2graph_features` 生成字段：
  - atom: `atom_type`, `formal_charge`, `num_degree`, `num_H`, `aromaticity`, `hybridization`, `chiral`, `atom_mask`
  - bond: `bond_type`, `stereo`, `conjugated`, `in_ring`, `bond_mask`, `graph_distance`
- sequence decoder 输入：
  - `sequence_features["tokens"]`
  - `sequence_features["mask"]`
  - optional rope index
  - graph conditional latent
- diffusion 输入：
  - `tokens`: `(B, T, C)`
  - `tokens_mask`: `(B, T)`
  - `time`: `(B,)`
  - optional label / rope index

## 输出定义

- graph encoder 输出：
  - graph conditional features
  - latent graph tokens
- decoder / generator 输出：
  - SMILES token logits
  - generated SMILES
  - auxiliary graph latent features
- diffusion 输出：
  - denoised latent token prediction
- reward / optimization 输出：
  - `LogP`
  - `QED`
  - `SA`
  - Tanimoto similarity
  - DSDP docking reward
  - NSGA-II selected candidates

## 主干结构

- `Encoder`
  - 分子图 atom / bond feature 编码
- `Decoder`
  - 基于 graph latent 条件生成 SMILES tokens
- `InferEncoder / InferDecoder / Inferencer`
  - 推理期图编码、逐步解码、greedy/beam/top-k/top-p sampling
- `L2SeqGenerator / MMDSeqGenerator`
  - graph latent 投影与序列生成训练路径
- `DiffusionTransformer`
  - latent token diffusion transformer
- `GaussianDiffusion`
  - diffusion schedule 与 posterior mean/variance
- reward helpers
  - RDKit properties、similarity、docking reward、NSGA-II

## 主要依赖组件

- `Encoder`
- `Decoder`
- `InferEncoder`
- `InferDecoder`
- `Inferencer`
- `L2SeqGenerator`
- `MMDSeqGenerator`
- `DiffusionTransformer`
- `GaussianDiffusion`
- `TrainDataLoader / AEDataLoader`
- `dsdp_reward / NSGA_II`

## 主要 Shape 变化

- SMILES -> RDKit Mol -> atom/bond arrays
- atom features padded to `(N_atom_max,)`
- bond features padded to `(N_atom_max, N_atom_max)`
- graph encoder latent: `(B, N_query, D_latent)`
- sequence tokens: `(B, N_seq)`
- decoder logits: `(B, N_seq, vocab_size)`
- diffusion latent tokens: `(B, T, C)`

## 默认关键参数

- graph padding 常见 `n_padding_atom=64`
- `Inferencer.sampling_method` 支持 `greedy`, `beam`, `top_p`, `top_k`, `nucleus`
- diffusion timesteps 来自 `config.diffusion_timesteps`
- case 目录中有 PI3K、AR-GR、SEH-FAAH、JNK3-GSK3B 等优化脚本

## 常见修改点

- 修改分子过滤：优先改 `standardize` 和 RDKit feature checks
- 修改采样策略：改 `Inferencer` config 的 `sampling_method`、`beam_size`、`top_k`、`top_p`
- 修改图大小上限：同步改 padding、模型 config 和训练数据处理
- 修改 reward：优先在 `train/rewards.py` 或 case-local reward 文件中接入，不改基础 encoder/decoder

## 风险点

- MolSculptor 不是蛋白模型，不应接 `ProteinDataset`、OpenFold batch、Protenix feature dict 或 Evo2 tokenizer
- RDKit sanitize / standardize 失败时会返回 `None` 或中断候选分子
- docking reward 依赖外部二进制、PDBQT、case 脚本和缓存路径，不适合在轻量 skill 中默认运行
- 图 padding 长度、vocab、checkpoint 和 config 必须配套
- 生成 SMILES 需要再做化学有效性和任务 reward 筛选

## 推荐检索顺序

1. 先看本模型卡
2. 再看 `train/inference.py` 的 `Inferencer` 和 SMILES -> graph helpers
3. 若改生成模型，读 `net/generator.py`、`net/encoder.py`、`net/decoder.py`
4. 若改 diffusion，读 `src/model/diffusion_transformer.py` 与 `train/scheduler.py`
5. 若改具体药物设计 case，读 `examples/biosciences/molsculptor/cases/<case>/`

## 组件契约入口

- `../contracts/molsculptorcomponents.md`

## 源码锚点

- `./onescience/src/onescience/flax_models/MolSculptor/train/inference.py`
- `./onescience/src/onescience/flax_models/MolSculptor/net/generator.py`
- `./onescience/src/onescience/flax_models/MolSculptor/net/encoder.py`
- `./onescience/src/onescience/flax_models/MolSculptor/net/decoder.py`
- `./onescience/src/onescience/flax_models/MolSculptor/src/model/diffusion_transformer.py`
- `./onescience/src/onescience/flax_models/MolSculptor/train/scheduler.py`
- `./onescience/src/onescience/flax_models/MolSculptor/train/rewards.py`
- `./onescience/examples/biosciences/molsculptor/inference`
- `./onescience/examples/biosciences/molsculptor/cases`
