# component_info

ProToken 是蛋白质结构 tokenizer / VQ 编码解码组件，核心功能是把 PDB 结构和 residue/atom features 映射到离散结构 token，并从 token embedding 重建蛋白结构；它常作为 PT-DiT 的结构词表与 decoder 后端，不应被当作直接从序列预测结构的 AF2/AF3 模型。

# architecture_overview

PDB 编码路线:
  PDB
    -> protoken_basic_generator
    -> padded residue / atom features
    -> VQ_Encoder
    -> VQTokenizer
    -> vq_code_indexes

结构解码路线:
  vq_code_indexes
    -> codebook lookup
    -> VQ_Decoder
    -> Protein_Decoder
    -> reconstructed atom37 PDB

# parameter_scale

- `padding_len` 脚本中常见默认值为 `768`。
- ProToken vocabulary size 常见为 `512`。
- ProToken embedding 常见维度为 `32`。
- `EXCLUDE_NEIGHBOR=3` 用于构造 2D features。

# architecture_structure

- `VQ_Encoder`: feature initializer、pair update Evoformer stack、single residual transformer stack、co-update Evoformer stack、extended StructureModule。
- `VQTokenizer`: codebook lookup、L2 optional norm、nearest code、VQ losses。
- `VQ_Decoder`: ProToken activation 到 single/pair representation 与 distogram。
- `Protein_Decoder`: frame initializer、structure decoder、pLDDT head。
- `InferenceVQWithLossCell`: inference-time wiring of encoder、VQ tokenizer、decoder 和 loss aux。
- `BottleneckModel`: ProToken latent bottleneck 与可选 inverse folding head。

# input_schema

- PDB 编码入口:
  - `--pdb_path`。
  - `--save_dir_path`。
  - `--load_ckpt_path`。
  - `--padding_len`。
- `protoken_basic_generator` 关键字段:
  - `seq_mask`。
  - `aatype`, `fake_aatype`。
  - `residue_index`。
  - `template_all_atom_masks`。
  - `template_all_atom_positions`。
  - `template_pseudo_beta`。
  - `backbone_affine_tensor`。
  - `torsion_angles_sin_cos`, `torsion_angles_mask`。
  - `atom14_atom_exists`。
  - distance permutation / mask fields。
- `VQTokenizer.__call__` 输入:
  - `x`: `(N_res, D)` 或带 batch 的 residue activations。
  - `mask`: `(N_res,)`。

# output_schema

- PDB 编码输出:
  - `vq_code_indexes.pkl`。
  - reconstructed PDB。
  - `input_features.pkl`。
  - `aux.txt`。
- `VQTokenizer` 输出:
  - `quantized`。
  - `encoding_indices`。
  - `encodings`。
  - `code_count`。
  - training loss fields: `e_latent_loss`, `q_latent_loss`, `entropy_loss`。
- `decode_structure.py` 输出:
  - `aux_*.pdb`。

# shape_transformations

- PDB -> padded residue features: `N_res = padding_len`
- encoder single activation: `(N_res, single_channel)`
- encoder pair activation: `(N_res, N_res, pair_channel)`
- VQ code indexes: `(valid_N_res,)`
- codebook lookup: `(N_res, D_code)`
- decoder atom positions: `(N_res, 37, 3)` 语义的重建坐标

# key_dependencies

- `VQ_Encoder`
- `VQTokenizer`
- `VQ_Decoder`
- `Protein_Decoder`
- `InferenceVQWithLossCell`
- `BottleneckModel`
- `FlashEvoformerStack`
- `StructureModule`

# common_modification_points

- 修改输入长度要同步 `--padding_len`、encoder/decoder config 的 `seq_len`、PT-DiT 的 `nres`。
- 只需要 token indexes 时使用 `scripts/infer.py` 并读取 `vq_code_indexes.pkl`。
- 已有 token indexes 需要还原 PDB 时使用 `scripts/decode_structure.py`。
- 与 PT-DiT 联动时保持 ProToken checkpoint、embedding 文件和 PT-DiT checkpoint 一致。

# implementation_risks

- `padding_len` 小于真实残基数会截断或失败，过大浪费显存。
- 输入 PDB 的链、缺失原子和 residue constants 会影响 feature generator。
- VQ codebook 与 decoder checkpoint 必须配套。
- 结构重建是 tokenizer reconstruction，不是 AF2/AF3 置信结构预测。
- `decode_structure.py` 会使用 fake glycine aatype 参与解码，输出序列语义不能直接视为真实设计序列。

# code_references

- `{onescience_path}/onescience/src/onescience/flax_models/protoken/model/encoder.py`
- `{onescience_path}/onescience/src/onescience/flax_models/protoken/tokenizer/vector_quantization.py`
- `{onescience_path}/onescience/src/onescience/flax_models/protoken/model/decoder.py`
- `{onescience_path}/onescience/src/onescience/flax_models/protoken/model/bottleneck.py`
- `{onescience_path}/onescience/src/onescience/flax_models/protoken/inference/inference.py`
- `{onescience_path}/onescience/src/onescience/flax_models/protoken/scripts/infer.py`
- `{onescience_path}/onescience/src/onescience/flax_models/protoken/scripts/decode_structure.py`
