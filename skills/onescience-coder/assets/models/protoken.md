# Model Card: ProToken

## 基本信息

- 模型名：`ProToken`
- 任务类型：`蛋白质结构 tokenizer / VQ 编码解码 / 结构重建`
- 当前状态：`stable`
- 主实现目录：`./onescience/src/onescience/flax_models/protoken`

## 模型定位

ProToken 是 OneScience 中的蛋白质结构离散表示模型，用结构编码器把 PDB / atom features 映射到结构 token，再用 VQ decoder 和 protein decoder 重建结构。PT-DiT 依赖它提供结构词表、embedding 和解码能力。

补充说明：

- 它不是单独的结构预测模型，而是结构 tokenizer / representation learning 组件
- 它使用 JAX/Flax，不走 OneScience `One*` wrapper
- `scripts/infer.py` 用于 PDB -> ProToken -> reconstructed PDB
- `scripts/decode_structure.py` 用于 ProToken indexes -> PDB

## 输入定义

- PDB 编码入口：
  - `--pdb_path`
  - `--save_dir_path`
  - `--load_ckpt_path`
  - `--padding_len`
- `protoken_basic_generator` 生成的关键字段：
  - `seq_mask`
  - `aatype`, `fake_aatype`
  - `residue_index`
  - `template_all_atom_masks`
  - `template_all_atom_positions`
  - `template_pseudo_beta`
  - `backbone_affine_tensor`
  - `torsion_angles_sin_cos`
  - `torsion_angles_mask`
  - `atom14_atom_exists`
  - distance permutation / mask fields
- `VQTokenizer.__call__` 输入：
  - `x`: `(N_res, D)` 或带 batch 的 residue activations
  - `mask`: `(N_res,)`

## 输出定义

- PDB 编码输出：
  - `vq_code_indexes.pkl`
  - reconstructed PDB
  - `input_features.pkl`
  - `aux.txt`
- `VQTokenizer` 输出：
  - `quantized`
  - `encoding_indices`
  - `encodings`
  - `code_count`
  - training loss fields: `e_latent_loss`, `q_latent_loss`, `entropy_loss`
- `decode_structure.py` 输出：
  - `aux_*.pdb`

## 主干结构

- `VQ_Encoder`
  - feature initializer
  - pair update Evoformer stack
  - single residual transformer stack
  - co-update Evoformer stack
  - extended StructureModule
- `VQTokenizer`
  - codebook lookup、L2 optional norm、nearest code、VQ losses
- `VQ_Decoder`
  - ProToken activation -> single/pair representation + distogram
- `Protein_Decoder`
  - frame initializer + structure decoder + pLDDT head
- `InferenceVQWithLossCell`
  - inference-time wiring of encoder、VQ tokenizer、decoder 和 loss aux
- `BottleneckModel`
  - ProToken latent bottleneck / optional inverse folding head

## 主要依赖组件

- `VQ_Encoder`
- `VQTokenizer`
- `VQ_Decoder`
- `Protein_Decoder`
- `InferenceVQWithLossCell`
- `BottleneckModel`
- `FlashEvoformerStack`
- `StructureModule`

## 主要 Shape 变化

- PDB -> padded residue features: `N_res = padding_len`
- encoder single activation: `(N_res, single_channel)`
- encoder pair activation: `(N_res, N_res, pair_channel)`
- VQ code indexes: `(valid_N_res,)`
- codebook lookup: `(N_res, D_code)`
- decoder atom positions: `(N_res, 37, 3)` 语义的重建坐标

## 默认关键参数

- `padding_len` 默认在脚本中为 `768`
- README / PT-DiT 说明中的 ProToken vocabulary size 为 `512`
- ProToken embedding 常见维度为 `32`
- `EXCLUDE_NEIGHBOR=3` 用于构造 2D features

## 常见修改点

- 修改输入长度：同步改 `--padding_len`、encoder/decoder config 的 `seq_len`、PT-DiT `nres`
- 只要 token indexes：用 `scripts/infer.py`，读取 `vq_code_indexes.pkl`
- 已有 token indexes 要还原 PDB：用 `scripts/decode_structure.py`
- 与 PT-DiT 联动：保持 ProToken checkpoint、embedding 文件和 PT-DiT checkpoint 一致

## 风险点

- `padding_len` 小于真实残基数会截断或失败，过大则浪费显存
- 输入 PDB 的链、缺失原子和 residue constants 会影响 feature generator
- VQ codebook 与 decoder checkpoint 必须配套
- 结构重建结果是 tokenizer reconstruction，不是 AF2/AF3 置信结构预测
- `decode_structure.py` 会用 fake glycine aatype 参与解码，不能把输出序列语义当成真实设计序列

## 推荐检索顺序

1. 先看本模型卡
2. 再看 `scripts/infer.py`
3. 若解码 token，读 `scripts/decode_structure.py`
4. 若改模型，读 `model/encoder.py`、`tokenizer/vector_quantization.py`、`model/decoder.py`
5. 若与 PT-DiT 联动，再看 `pt_dit.md`

## 组件契约入口

- `../contracts/protokencomponents.md`
- 与 PT-DiT 共同使用时，再读 `../contracts/ptditcomponents.md`

## 源码锚点

- `./onescience/src/onescience/flax_models/protoken/model/encoder.py`
- `./onescience/src/onescience/flax_models/protoken/tokenizer/vector_quantization.py`
- `./onescience/src/onescience/flax_models/protoken/model/decoder.py`
- `./onescience/src/onescience/flax_models/protoken/model/bottleneck.py`
- `./onescience/src/onescience/flax_models/protoken/inference/inference.py`
- `./onescience/src/onescience/flax_models/protoken/scripts/infer.py`
- `./onescience/src/onescience/flax_models/protoken/scripts/decode_structure.py`
