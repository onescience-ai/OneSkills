# component_info

`proteinmpnn_components` 是 ProteinMPNN 的组件契约，覆盖 `ProteinMPNNFeatureEncoder` 和 `ProteinMPNNSequenceDecoder`。原始 contract 中模块族为 `encoder / decoder`，目标统一入口为 `OneEncoder / OneDecoder`，注册状态为 `contract_only`。

# purpose

用于从蛋白 backbone 构造 kNN 几何图，并在图上进行 encoder-decoder 自回归氨基酸序列建模。它是 inverse folding 路线：结构到序列，不是序列到结构；常作为 RFdiffusion 生成骨架后的序列设计步骤。

# input_schema

```text
训练版模型输入:
  X: (B, L, 4, 3), atom order = N, CA, C, O
  S: (B, L)
  mask: (B, L)
  chain_M: (B, L)
  residue_idx: (B, L)
  chain_encoding_all: (B, L)

推理版 tied_featurize:
  chain_M_pos
  omit_AA_mask
  pssm_coef, pssm_bias, pssm_log_odds_mask
  tied_pos_list_of_lists
  bias_by_res_all
```

# output_schema

```text
ProteinMPNN.forward:
  log_probs: (B, L, 21)

推理采样:
  sampled sequence ids
  per-position probabilities
  per-position log probabilities
  optional tied-position results
```

# parameters

- `num_letters=21`
- `node_features=128`
- `edge_features=128`
- `hidden_dim=128`
- `num_encoder_layers=3`
- `num_decoder_layers=3`
- `vocab=21`
- `k_neighbors=32`
- `augment_eps=0.1`
- `dropout=0.1`

# key_dependencies

- `model_utils.py`
- `protein_mpnn_utils.py`
- `protein_mpnn_run.py`
- `README.md`

# usage_and_risks

`ProteinFeatures` 从 `N/CA/C/O` 推导 `Cb`，用 CA 距离取 top-k 邻居，为原子对距离构造 RBF 特征，并拼接链内/链间位置编码；encoder 更新骨架图，decoder 按 chain mask 与 decoding order 自回归预测设计位置。`contract_only` 来自原始 contract，目标 `style` 不表示当前 `OneEncoder/OneDecoder` 可直接实例化。训练版与推理版同名类功能不完全一致，约束设计优先读推理版。

# code_references

- `{onescience_path}/onescience/src/onescience/models/proteinmpnn/model_utils.py`
- `{onescience_path}/onescience/src/onescience/models/proteinmpnn/protein_mpnn_utils.py`
- `{onescience_path}/onescience/examples/biosciences/ProteinMPNN/protein_mpnn_run.py`
- `{onescience_path}/onescience/examples/biosciences/ProteinMPNN/README.md`
