# Contract: MolSculptorComponents

## 基本信息

- 组件名：`MolSculptorGraphEncoder / MolSculptorSMILESDecoder / MolSculptorDiffusionTransformer / MolSculptorGaussianDiffusion`
- 所属模块族：`encoder / decoder / transformer / diffusion`
- 统一入口：`OneEncoder / OneDecoder / OneTransformer / OneDiffusion`
- 注册名：`style="MolSculptorGraphEncoder"`, `style="MolSculptorSMILESDecoder"`, `style="MolSculptorDiffusionTransformer"`, `style="MolSculptorGaussianDiffusion"`
- 注册状态：`contract_only`

## 组件职责

MolSculptor 组件负责小分子图编码、SMILES token 解码、latent diffusion 和分子 reward/optimization，是生信中 drug design / molecular generation 侧的模型族。

补充说明：

- 契约层把分子图编码收束到 `OneEncoder`，SMILES 解码收束到 `OneDecoder`，latent DiT 和 Gaussian schedule 分别收束到 `OneTransformer` / `OneDiffusion`
- 源码当前仍是 JAX/Flax + case pipeline 实现，进入 PyTorch `One*` 体系前需要补适配层
- 它不处理蛋白 FASTA/MSA/PDB folding batch
- docking reward 和 case pipeline 依赖外部化学工具，默认不要作为轻量验证步骤执行

## One* 归一映射

| 源码组件 | 所属模块族 | 统一入口 | 注册名 |
| --- | --- | --- | --- |
| `Encoder / InferEncoder` | `encoder` | `OneEncoder` | `style="MolSculptorGraphEncoder"` |
| `Decoder / InferDecoder / Inferencer` | `decoder` | `OneDecoder` | `style="MolSculptorSMILESDecoder"` |
| `DiffusionTransformer` | `transformer` | `OneTransformer` | `style="MolSculptorDiffusionTransformer"` |
| `GaussianDiffusion` | `diffusion` | `OneDiffusion` | `style="MolSculptorGaussianDiffusion"` |

## 支持输入

- 2D 输入：`molecular_graph`
- 3D 输入：`not_primary`
- graph features：
  - `atom_features`
  - `bond_features`
  - optional `neighbor_list`
- atom fields：
  - `atom_type`
  - `formal_charge`
  - `num_degree`
  - `num_H`
  - `aromaticity`
  - `hybridization`
  - `chiral`
  - `atom_mask`
- bond fields：
  - `bond_type`
  - `stereo`
  - `conjugated`
  - `in_ring`
  - `bond_mask`
  - `graph_distance`
- sequence features：
  - `tokens`
  - `mask`
  - optional `rope_index`
- diffusion inputs：
  - `tokens`
  - `tokens_mask`
  - `time`
  - optional `label`
  - `tokens_rope_index`

内部统一做法：

- RDKit 将 SMILES 标准化并转成 atom/bond feature arrays
- graph features padding 到固定 atom 数
- Encoder 生成 graph conditional latent
- Decoder / Inferencer 逐步生成 SMILES token
- L2SeqGenerator / MMDSeqGenerator 在训练中把 graph latent 投影到序列生成空间
- DiffusionTransformer / GaussianDiffusion 在 latent token 空间做扩散生成或优化
- reward helpers 计算分子属性、相似度和 docking score

## 构造参数

- `Inferencer`
  - `encoding_net`
  - `decoding_net`
  - `encoding_params`
  - `decoding_params`
  - `config`
- sampling config：
  - `sampling_method`
  - `beam_size`
  - `top_k`
  - `top_p`
  - `step_limit`
  - `device_batch_size`
  - `n_seq_length`
- diffusion config：
  - `diffusion_timesteps`
  - `hidden_size`
  - `n_iterations`
  - `dit_block`
  - `dit_output`

## 输出约定

- `InferEncoder`：
  - graph latent `(B, N_query, D_latent)`
- `InferDecoder`：
  - sequence logits `(B, N_seq, vocab_size)`
- `Inferencer`：
  - generated token sequences
  - log-prob cache for beam search
  - decoded SMILES
- `L2SeqGenerator`：
  - sequence logits
  - aux: `graph_feat`, `sim_feat`
- `DiffusionTransformer`：
  - latent tokens `(B, T, C)`
- reward / optimization：
  - scores, constraints, selected molecule candidates

如果有明确边界条件，也写在这里：

- graph padding 默认常见为 `64` atoms，超过上限时需要改 config 和数据处理
- `Inferencer.sampling_method` 必须在源码支持列表中
- RDKit `standardize` 失败时应丢弃样本或返回 None，不要继续送入 graph encoder
- docking reward 路径需要 PDBQT、外部脚本和缓存文件

## 典型调用位置

- `examples/biosciences/molsculptor/inference`
- `examples/biosciences/molsculptor/training`
- `examples/biosciences/molsculptor/cases`
- `flax_models/MolSculptor/train/inference.py`

## 典型参数

- `n_padding_atom=64`
- sampling methods:
  - `greedy`
  - `beam`
  - `top_p`
  - `top_k`
- reward:
  - `QED`
  - `SA`
  - `LogP`
  - `DSDP`
- 契约层目标调用：
  - `OneEncoder(style="MolSculptorGraphEncoder", ...)`
  - `OneDecoder(style="MolSculptorSMILESDecoder", ...)`
  - `OneTransformer(style="MolSculptorDiffusionTransformer", ...)`
  - `OneDiffusion(style="MolSculptorGaussianDiffusion", ...)`

## 风险点

- 上述 `style` 是 skill 契约归一名，不表示当前源码已经在对应 `One*` registry 中可直接实例化
- MolSculptor 是分子/药物设计模型，不应混入蛋白结构预测的 feature dict 规则
- SMILES 有效性、标准化、tautomer、fragment 处理会显著影响训练/推理结果
- docking reward 不可离线假设可用，路径和二进制缺失时要降级为只生成候选
- JAX/Flax 参数和普通 PyTorch module 不兼容

## 源码锚点

- `./onescience/src/onescience/flax_models/MolSculptor/train/inference.py`
- `./onescience/src/onescience/flax_models/MolSculptor/net/generator.py`
- `./onescience/src/onescience/flax_models/MolSculptor/net/encoder.py`
- `./onescience/src/onescience/flax_models/MolSculptor/net/decoder.py`
- `./onescience/src/onescience/flax_models/MolSculptor/src/model/diffusion_transformer.py`
- `./onescience/src/onescience/flax_models/MolSculptor/train/scheduler.py`
- `./onescience/src/onescience/flax_models/MolSculptor/train/rewards.py`
