# component_info

`protoken_protein_decoder` 是 ProToken 的蛋白坐标解码模块，接收 single/pair 表征，通过 frame initializer 和 structure module 输出原子坐标、结构轨迹和 pLDDT。

# purpose

用于把 ProToken latent 解码链路中的结构表征转换为三维蛋白坐标。适合蛋白结构生成、重建和质量估计；不处理分子配体，也不执行 docking。

# input_schema

```text
single_act:
  Tensor[float]: (Batch, Residues, SingleChannels)

pair_act:
  Tensor[float]: (Batch, Residues, Residues, PairChannels)

seq_mask:
  Tensor[float|bool]: (Batch, Residues)

aatype:
  Tensor[int]: (Batch, Residues)
```

# output_schema

```text
final_atom_positions:
  Tensor[float]: atom coordinates

atom14_pred_positions:
  Tensor[float]: atom14 coordinates

structure_traj:
  Tensor[float]: iterative structure trajectory

normed_single / normed_pair:
  Tensor[float]: normalized representations

pLDDT_logits:
  Tensor[float]: quality logits
```

# parameters

- `ipa_share_weights`: IPA 是否共享权重。
- `extended_structure_module`: 结构模块配置。
- `frame_initializer`: 初始刚体帧配置。
- `predicted_lddt`: pLDDT head 配置。
- `seq_len`: 最大 residue 长度。

# key_dependencies

- `decoder.py`
- `structure.py`
- `head.py`

# usage_and_risks

该模块在源码中会将 aatype 置为 Gly 风格输入，迁移到真实序列设计时需核对残基类型处理。输入 single/pair 必须来自兼容的 VQ decoder 或 encoder，否则结构模块可能无法收敛到合理坐标。

# code_references

- `{onescience_path}/onescience/src/onescience/flax_models/protoken/model`
