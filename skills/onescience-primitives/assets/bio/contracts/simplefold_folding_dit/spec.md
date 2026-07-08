# component_info

`simplefold_folding_dit` 是 SimpleFold 的 `FoldingDiT` 组件契约。原始 contract 中模块族为 `transformer`，目标统一入口为 `OneTransformer`，注册名为 `style="SimpleFoldFoldingDiT"`，注册状态为 `contract_only`。

# purpose

用于 SimpleFold 训练、微调和采样中的 velocity model。它把 noised atom coordinates、时间条件、SimpleFold atom-token feature dict 和 ESM token 表征融合后预测 atom velocity。它是 flow matching 折叠主干，不是 AF2 Evoformer、AF3 Pairformer 或通用 Transformer block。

# input_schema

```text
主输入:
  noised_pos: (B, N_atom, 3)
  t: (B,)
  feats: SimpleFold atom-token feature dict
  self_cond: optional

关键 feats:
  ref_pos, ref_charge, atom_pad_mask
  ref_element, ref_atom_name_chars
  atom_to_token, atom_to_token_idx
  ref_space_uid, mol_type, res_type
  pocket_feature, residue_index
  entity_id, asym_id, sym_id
  max_num_tokens, esm_s
```

# output_schema

```text
predict_velocity: (B, N_atom, 3)
latent: (B, N_token, hidden_size)
```

# parameters

- `hidden_size=1152`
- `num_heads=16`
- `atom_num_heads=4`
- `output_channels=3`
- `atom_hidden_size_enc=256`
- `atom_hidden_size_dec=256`
- `atom_n_queries_enc=32`, `atom_n_keys_enc=128`
- `atom_n_queries_dec=32`, `atom_n_keys_dec=128`
- `esm_model="esm2_3B"`
- `esm_dropout_prob=0.0`
- `use_atom_mask=False`
- `use_length_condition=True`

# key_dependencies

- `architecture.py`
- `simplefold.py`
- `sampler.py`
- `flow.py`

# usage_and_risks

典型流程是时间 embedding 与长度条件生成 AdaLN 条件，atom 静态特征与 noised coordinate embedding 拼接后进入 atom encoder，再聚合到 token latent，融合 ESM 表征后通过 residue trunk 和 atom decoder 输出 velocity。`contract_only` 来自原始 contract，表示 `style="SimpleFoldFoldingDiT"` 不是已确认可直接注册运行的 `OneTransformer` style。缺少 `esm_s`、`atom_to_token` 形状不对或 atom feature 拼接维度变化都会导致语义错位。

# code_references

- `{onescience_path}/onescience/src/onescience/models/simplefold/torch/architecture.py`
- `{onescience_path}/onescience/src/onescience/models/simplefold/simplefold.py`
- `{onescience_path}/onescience/src/onescience/models/simplefold/torch/sampler.py`
- `{onescience_path}/onescience/src/onescience/models/simplefold/flow.py`
