# Contract: ProTokenComponents

## 基本信息

- 组件名：`ProTokenVQEncoder / ProTokenVQTokenizer / ProTokenStructureDecoder`
- 所属模块族：`encoder / decoder`
- 统一入口：`OneEncoder / OneDecoder`
- 注册名：`style="ProTokenVQEncoder"`, `style="ProTokenVQTokenizer"`, `style="ProTokenStructureDecoder"`
- 注册状态：`contract_only`

## 组件职责

ProToken 组件负责把蛋白质结构编码为离散结构 token，并从 token / codebook embedding 解码重建蛋白质结构，是 PT-DiT 蛋白协同设计链路的结构表示基础。

补充说明：

- 契约层把结构编码与量化收束到 `OneEncoder`，把 VQ / protein 结构解码收束到 `OneDecoder`
- 源码当前仍是 JAX/Flax 实现，进入 PyTorch `One*` 体系前需要补适配层
- 它是 tokenizer / autoencoder 风格组件，不是 AF2/AF3 结构预测主模型
- `scripts/infer.py` 和 `scripts/decode_structure.py` 是最可靠的工程入口

## One* 归一映射

| 源码组件 | 所属模块族 | 统一入口 | 注册名 |
| --- | --- | --- | --- |
| `VQ_Encoder` | `encoder` | `OneEncoder` | `style="ProTokenVQEncoder"` |
| `VQTokenizer` | `encoder` | `OneEncoder` | `style="ProTokenVQTokenizer"` |
| `VQ_Decoder / Protein_Decoder` | `decoder` | `OneDecoder` | `style="ProTokenStructureDecoder"` |

## 支持输入

- 2D 输入：`not_applicable`
- 3D 输入：`not_applicable`
- `VQ_Encoder.__call__`：
  - `seq_mask`
  - `aatype`
  - `residue_index`
  - `template_all_atom_masks`
  - `template_all_atom_positions`
  - `template_pseudo_beta`
  - `decoy_affine_tensor`
  - `torsion_angles_sin_cos`
  - `torsion_angles_mask`
- `VQTokenizer.__call__`：
  - `x`: residue latent
  - `mask`: residue mask
- `VQ_Decoder.__call__`：
  - `vq_act`
  - `seq_mask`
  - `residue_index`
- `Protein_Decoder.__call__`：
  - `single_act`
  - `pair_act`
  - `seq_mask`
  - `aatype`

内部统一做法：

- feature initializer 生成 single / pair 初始表征
- encoder 用 pair update、single residual update、co-update stack 提取结构 latent
- VQTokenizer 用 codebook 最近邻量化 latent，并输出 code indexes / code usage
- VQ_Decoder 从 codebook embedding 恢复 single / pair 表征和 distogram
- Protein_Decoder 通过 frame initializer 和 StructureModule 输出 atom positions

## 构造参数

- `global_config`
  - `bf16_flag`
  - `use_dropout`
  - `norm_small`
- encoder / decoder config：
  - `seq_len`
  - `common.single_channel`
  - `common.pair_channel`
  - `pair_update_evoformer_stack_num`
  - `single_update_transformer_stack_num`
  - `co_update_evoformer_stack_num`
  - `extended_structure_module`
- VQ config：
  - `num_code`
  - `dim_in`
  - `l2_norm`
  - `stochastic_sampling`
  - `entropy_loss_type`

## 输出约定

- `VQ_Encoder`：
  - final single activations
  - intermediate single activations
  - pair activations
- `VQTokenizer`：
  - `quantized`
  - `encoding_indices`
  - `encodings`
  - `code_count`
  - optional VQ losses
- `VQ_Decoder`：
  - `single_act`
  - `pair_act`
  - `dist_logits`
  - `dist_bin_edges`
- `Protein_Decoder`：
  - `final_atom_positions`
  - `atom14_pred_positions`
  - `structure_traj`
  - `normed_single`
  - `normed_pair`
  - `pLDDT_logits`

如果有明确边界条件，也写在这里：

- `seq_len` 必须与 padding length 对齐
- decoder 中 `Protein_Decoder` 当前会把 `aatype` 置为 Glycine-like fake aatype，用于结构解码而不是序列预测
- codebook 与 encoder/decoder checkpoint 必须配套
- `VQTokenizer` train 模式才输出 VQ loss

## 典型调用位置

- `onescience.flax_models.protoken.scripts.infer`
- `onescience.flax_models.protoken.scripts.infer_batch`
- `onescience.flax_models.protoken.scripts.decode_structure`
- PT-DiT `de_novo_design.py` 解码阶段

## 典型参数

- `padding_len=768`
- `EXCLUDE_NEIGHBOR=3`
- ProToken vocabulary size 常见为 `512`
- ProToken embedding 常见为 `512 x 32`
- 契约层目标调用：
  - `OneEncoder(style="ProTokenVQEncoder", ...)`
  - `OneEncoder(style="ProTokenVQTokenizer", ...)`
  - `OneDecoder(style="ProTokenStructureDecoder", ...)`

## 风险点

- 上述 `style` 是 skill 契约归一名，不表示当前源码已经在对应 `One*` registry 中可直接实例化
- 输入 PDB 预处理失败会影响 tokenization，不应直接把任意结构文件当成已对齐 residue features
- `padding_len`、config `seq_len`、checkpoint 三者必须一致
- 重建结构用于 tokenizer 表示验证，不等于 AF2/AF3 预测置信结构
- 与 PT-DiT 联动时，`protoken_indexes` 和 `aatype_indexes` 的含义不同，不能混成同一个 vocab

## 源码锚点

- `./onescience/src/onescience/flax_models/protoken/model/encoder.py`
- `./onescience/src/onescience/flax_models/protoken/tokenizer/vector_quantization.py`
- `./onescience/src/onescience/flax_models/protoken/model/decoder.py`
- `./onescience/src/onescience/flax_models/protoken/model/bottleneck.py`
- `./onescience/src/onescience/flax_models/protoken/inference/inference.py`
- `./onescience/src/onescience/flax_models/protoken/scripts/infer.py`
- `./onescience/src/onescience/flax_models/protoken/scripts/decode_structure.py`
