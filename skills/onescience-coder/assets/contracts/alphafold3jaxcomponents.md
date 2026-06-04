# Contract: AlphaFold3JAXComponents

## 基本信息

- 组件名：`AlphaFold3JAXPairformer / AlphaFold3JAXDiffusionHead / AlphaFold3JAXAtomCrossAttention / AlphaFold3JAXConfidenceHead`
- 所属模块族：`pairformer / diffusion / attention / head`
- 统一入口：`OnePairformer / OneDiffusion / OneAttention / OneHead`
- 注册名：`style="AlphaFold3JAXPairformer"`, `style="AlphaFold3JAXDiffusionHead"`, `style="AlphaFold3JAXAtomCrossAttention"`, `style="AlphaFold3JAXConfidenceHead"`
- 注册状态：`contract_only`

## 组件职责

AlphaFold3 JAX 组件负责把 AF3 folding input featurise 成 token/atom layout batch，经 Evoformer/Pairformer trunk、diffusion head 和 confidence heads 输出复合物结构样本与置信度。契约层按 OneScience 组件体系归一为 pairformer、diffusion、attention 和 head 四类入口。

补充说明：

- 源码当前仍是 JAX/Haiku AF3 推理实现；若要进入 OneScience `One*` 调用体系，需要按下表补薄适配与 registry
- 与 Protenix 功能相近但实现不同，不能共享 Protenix 的 `OneEmbedding/OnePairformer/OneDiffusion` 注册名
- 适合用于 AF3 JAX 推理脚本、data pipeline 和模型内部逻辑定位

## One* 归一映射

| 源码组件 | 所属模块族 | 统一入口 | 注册名 |
| --- | --- | --- | --- |
| `Evoformer / PairFormerIteration` | `pairformer` | `OnePairformer` | `style="AlphaFold3JAXPairformer"` |
| `DiffusionHead` | `diffusion` | `OneDiffusion` | `style="AlphaFold3JAXDiffusionHead"` |
| `atom_cross_att_encoder / atom_cross_att_decoder` | `attention` | `OneAttention` | `style="AlphaFold3JAXAtomCrossAttention"` |
| `ConfidenceHead / DistogramHead` | `head` | `OneHead` | `style="AlphaFold3JAXConfidenceHead"` |

## 支持输入

- 2D 输入：`not_applicable`
- 3D 输入：`not_applicable`
- 脚本入口：
  - `folding_input.Input`
  - JSON path / input dir
  - optional MSA/template/database config
- `Model.__call__` 输入：
  - `batch: features.BatchDict`
  - optional `key`
- `feat_batch.Batch` 关键字段：
  - `token_features`
  - `msa`
  - `templates`
  - `ref_structure`
  - `predicted_structure_info`
  - `atom_cross_att`
  - `pseudo_beta_info`
  - bond info layouts

内部统一做法：

- `create_target_feat_embedding` 拼接 token target features 和 per-atom conditioning
- `Evoformer` 生成 pair/single/target embeddings
- trunk 中处理 relative encoding、bond embedding、template、MSA stack 和 PairFormerIteration
- `DiffusionHead` 在 noisy dense atom positions 上做 atom cross attention、token transformer 和 atom decoder
- `ConfidenceHead` 对每个 diffusion sample 输出 pLDDT、PDE、PAE、resolved 等
- `Model.get_inference_result` 将 dense atom layout 映射回 flat output structure 并生成 ranking metadata

## 构造参数

- `Model.Config`
  - `evoformer`
  - `global_config`
  - `heads.diffusion`
  - `heads.confidence`
  - `heads.distogram`
  - `num_recycles=10`
  - `return_embeddings=False`
  - `return_distogram=False`
- `DiffusionHead.Config`
  - `eval_batch_size=5`
  - `conditioning.pair_channel=128`
  - `conditioning.seq_channel=384`
  - `eval.num_samples=5`
  - `eval.steps=200`
- `Evoformer.Config`
  - `seq_channel=384`
  - `pair_channel=128`
  - `num_msa=1024`
  - `pairformer.num_layer=48`

## 输出约定

- `Model.__call__`：
  - `diffusion_samples`
  - `distogram`
  - `predicted_lddt`
  - `predicted_experimentally_resolved`
  - `full_pde`
  - `average_pde`
  - `full_pae`
  - `tmscore_adjusted_pae_global`
  - `tmscore_adjusted_pae_interface`
  - optional embeddings
- `DiffusionHead.sample`：
  - `atom_positions`: `(N_sample, N_token, max_atoms_per_token, 3)`
  - `mask`: `(N_sample, N_token, max_atoms_per_token)`

如果有明确边界条件，也写在这里：

- `num_res >= 4000` 时源码中会把 trunk embeddings 强制走 bf16 初始化分支
- `flash_attention_implementation` 必须与硬件和安装环境匹配
- bucket size 影响 JAX 编译缓存和 padding，不是模型语义参数

## 典型调用位置

- `examples/biosciences/alphafold3/run_alphafold.py`
- `ModelRunner.run_inference`
- `process_fold_input`
- `predict_structure`

## 典型参数

- `--run_data_pipeline=false` 用于已有 MSA / features 的 JSON 推理
- `--use_mmseqs=true` 用于 MMseqs 搜索
- `--flash_attention_implementation=xla` 用于保守兼容
- `--num_diffusion_samples=5`
- `--num_recycles=10`
- 契约层目标调用：
  - `OnePairformer(style="AlphaFold3JAXPairformer", ...)`
  - `OneDiffusion(style="AlphaFold3JAXDiffusionHead", ...)`
  - `OneAttention(style="AlphaFold3JAXAtomCrossAttention", ...)`
  - `OneHead(style="AlphaFold3JAXConfidenceHead", ...)`

## 风险点

- AlphaFold3 JAX 与 Protenix 的 feature dict、layout 和权重不兼容
- 以上 `style` 是 skill 契约归一名，不表示当前源码已经在对应 `One*` registry 中可直接实例化
- ligand / CCD / RDKit / bond layout 对输入 JSON 质量敏感
- data pipeline 中 JackHmmer/Nhmmer 分片并行会消耗大量 CPU
- confidence head 输出是每个 diffusion sample 的评估，不要只取第一个 sample 当最终 ranking
- `return_embeddings` 和 `return_distogram` 可能产生很大的输出文件

## 源码锚点

- `./onescience/src/onescience/flax_models/alphafold3/model/model.py`
- `./onescience/src/onescience/flax_models/alphafold3/model/network/evoformer.py`
- `./onescience/src/onescience/flax_models/alphafold3/model/network/modules.py`
- `./onescience/src/onescience/flax_models/alphafold3/model/network/diffusion_head.py`
- `./onescience/src/onescience/flax_models/alphafold3/model/network/atom_cross_attention.py`
- `./onescience/src/onescience/flax_models/alphafold3/model/network/confidence_head.py`
- `./onescience/examples/biosciences/alphafold3/run_alphafold.py`
