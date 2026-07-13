# component_info

`openfold_structure_module` 是 OpenFold 的结构解码组件契约，覆盖 `StructureModule`。原始 contract 中模块族为 `decoder`，目标统一入口为 `OneDecoder`，注册名为 `style="OpenFoldStructureModule"`，注册状态为 `contract_only`。

# purpose

用于把 Evoformer 输出的 single/pair 表征转换为蛋白三维结构，是 AF2-style folding 的坐标恢复模块。它适用于 OpenFold 结构恢复、IPA/angle resnet 修改和 atom14 到 atom37 输出分析；不适合作为 Protenix diffusion decoder。

# input_schema

```text
主输入:
  evoformer_output_dict["single"]: [*, N_res, C_s]
  evoformer_output_dict["pair"]: [*, N_res, N_res, C_z]
  aatype: [*, N_res]
  mask: [*, N_res]
```

# output_schema

```text
StructureModule:
  positions: 多个 block 的 atom14 坐标
  frames: 多个 block 的 backbone frames
  unnormalized_angles
  angles

AlphaFold 外层:
  final_atom_positions: [*, N_res, 37, 3]
  final_atom_mask
  final_affine_tensor
```

# parameters

- `c_s`, `c_z`, `c_ipa`, `c_resnet`
- `no_heads_ipa`, `no_qk_points`, `no_v_points`
- `dropout_rate`, `no_blocks`, `no_transition_layers`
- `no_resnet_blocks`, `no_angles`, `trans_scale_factor`
- `epsilon`, `inf`, `is_multimer=False`

# key_dependencies

- `structure_module.py`
- `model.py`
- `rigid_utils.py`
- `feats.py`

# usage_and_risks

模块先对 single/pair 表征 LayerNorm，初始化 residue 刚体 frame，再多轮执行 IPA、transition、backbone rigid update 和 angle resnet，生成 atom14 positions 并由外层转 atom37。`contract_only` 来自原始 contract，不表示 `OneDecoder(style="OpenFoldStructureModule")` 当前可直接实例化。`mask`、`single`、`pair` 的 `N_res` 必须一致；monomer/multimer IPA 与 backbone update 分支不同；输出 `positions[-1]` 才是最终 block 坐标。

# code_references

- `{onescience_path}/onescience/src/onescience/models/openfold/structure_module.py`
- `{onescience_path}/onescience/src/onescience/models/openfold/model.py`
- `{onescience_path}/onescience/src/onescience/utils/openfold/rigid_utils.py`
- `{onescience_path}/onescience/src/onescience/utils/openfold/feats.py`
