# component_info

`molsculptor_graph_encoder` 是 MolSculptor 小分子图编码模块，将 atom/bond 离散特征 one-hot 化后输入 MOLCT-PLUS，输出 prefix atom latent 作为分子条件表征。

# purpose

用于小分子图到 latent 条件向量的编码，适合分子生成、分子优化、配体 latent 表征构造；不直接处理蛋白口袋坐标，也不输出 SMILES。

# input_schema

```text
atom_features:
  atom_type, formal_charge, num_H, aromaticity, hybridization, chiral, atom_mask
  shape: (Batch, NumAtoms)

bond_features:
  bond_type, stereo, conjugated, in_ring, graph_distance, bond_mask
  shape: (Batch, NumAtoms, NumAtoms)

neighbor_list:
  optional sparse neighbor index
```

# output_schema

```text
prefix_atom_feat:
  Tensor[float]: (Batch, NumPrefixAtoms, HiddenDim)
```

# parameters

- `config.num_prefix_atoms`: 前缀原子数量。
- `config.embedding.atom_embedding`: atom one-hot 类别数。
- `config.embedding.bond_embedding`: bond one-hot 类别数。
- `config.molct`: 图编码主干配置。
- `global_config.bf16_flag`: 数值精度开关。

# key_dependencies

- `encoder.py`
- `embedding.py`
- `molct_plus.py`
- `transformer.py`

# usage_and_risks

输入通常来自 RDKit 或同等分子特征化流程，离散类别必须与配置词表一致。prefix atom 会被拼接到真实原子前，mask 和 bond feature 也必须同步 padding，否则图表征会错位。

# code_references

- `{onescience_path}/onescience/src/onescience/flax_models/MolSculptor/net`
