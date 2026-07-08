# component_info

`protoken_vq_encoder` 是 ProToken 的结构 token 编码模块族，包含 feature initializer、VQ encoder 和 inverse folding module，用于将蛋白结构输入编码为 single/pair 表征。

# purpose

用于蛋白结构压缩表示、ProToken code 前置表征和 inverse folding 任务。适合 LaProteina 类蛋白生成任务的结构 latent 参考；不直接生成 SMILES 或处理配体图。

# input_schema

```text
seq_mask:
  Tensor[float|bool]: (Residues,)

aatype:
  Tensor[int]: (Residues,)

residue_index:
  Tensor[int]: (Residues,)

template_all_atom_masks / positions / pseudo_beta:
  template atom features

decoy_affine_tensor:
  Tensor[float]: structure frame initialization

torsion_angles_sin_cos / torsion_angles_mask:
  torsion features
```

# output_schema

```text
final_single_activations:
  Tensor[float]: residue single representation

single_activations:
  Tensor[float]: updated single representation

pair_activations:
  Tensor[float]: updated pair representation
```

# parameters

- `seq_len`: 序列长度。
- `common.single_channel`: single 表征维度。
- `common.pair_channel`: pair 表征维度。
- `pair_update_evoformer_stack_num`: pair 更新层数。
- `single_update_transformer_stack_num`: single 更新层数。
- `co_update_evoformer_stack_num`: 协同更新层数。
- `extended_structure_module`: 结构模块配置。

# key_dependencies

- `encoder.py`
- `flash_evoformer.py`
- `transformers.py`
- `structure.py`
- `templates.py`
- `head.py`

# usage_and_risks

输入需要完整 residue、template、torsion 与 affine 信息；缺失 template 或 mask 错误会影响 pair 初始化。该模块输出的是 latent 表征，不是最终离散 code，需要与 bottleneck 或后续 decoder 串联。

# code_references

- `{onescience_path}/onescience/src/onescience/flax_models/protoken/model`
