# component_info

ProteinMPNN 是蛋白质 inverse folding 和骨架条件序列设计原语，核心功能是根据固定或部分固定的蛋白骨架几何生成氨基酸序列；它适合工程化设计约束场景，支持固定链、固定位点、PSSM、omit AA 与 tied positions 等控制。

# architecture_overview

ProteinMPNN 用蛋白质骨架几何作为条件生成或打分氨基酸序列，适合蛋白设计、固定链/设计链控制、PSSM / tied positions / omit AA 等工程化 inverse folding 场景。

补充说明：

- 任务方向与 OpenFold / Protenix 相反：不是从序列预测结构，而是从结构骨架设计序列
- 训练版和推理版实现分别在 `model_utils.py` 与 `protein_mpnn_utils.py`
- example 主入口是 `examples/biosciences/ProteinMPNN/protein_mpnn_run.py`

# parameter_scale

- `num_letters=21`
- `hidden_dim=128`
- `num_encoder_layers=3`
- `num_decoder_layers=3`
- `k_neighbors=32`
- `augment_eps=0.1`
- `dropout=0.1`
- example 默认模型名：`v_48_020`
- 常见采样温度：`0.1`, `0.15`, `0.2`, `0.25`, `0.3`

# architecture_structure

- `ProteinFeatures`
  - 从 `N, CA, C, O` 推导 `Cb`
  - 基于 CA kNN 取邻居
  - 构造 RBF 距离特征、链内/链间位置编码和 edge embedding
- Encoder layers
  - 对骨架图做无掩码消息传递
- Decoder layers
  - 按 `chain_M` 和随机 decoding order 做自回归序列建模
- Output projection
  - 输出 21 类氨基酸 log probability

# input_schema

- 训练简化版 `featurize(batch, device)` 返回：
  - `X`: `(Batch, L_max, 4, 3)`，骨架原子顺序为 `N, CA, C, O`
  - `S`: `(Batch, L_max)`，氨基酸整数标签
  - `mask`: `(Batch, L_max)`
  - `lengths`
  - `chain_M`: `(Batch, L_max)`，1 表示需要预测 / 设计的位置
  - `residue_idx`: `(Batch, L_max)`
  - `mask_self`: `(Batch, L_max, L_max)`
  - `chain_encoding_all`: `(Batch, L_max)`
- 模型 forward：
  - `ProteinMPNN.forward(X, S, mask, chain_M, residue_idx, chain_encoding_all)`

# output_schema

- `log_probs`: `(Batch, L, 21)`
- 推理工具还支持：
  - `sample`
  - `tied_sample`
  - `conditional_probs`
  - `unconditional_probs`
  - score / probs / FASTA 输出

# shape_transformations

- backbone coordinates: `(B, L, 4, 3)`
- edge features after kNN: `(B, L, K, edge_features)`
- node hidden: `(B, L, hidden_dim)`
- sequence embedding: `(B, L, hidden_dim)`
- output log probs: `(B, L, 21)`

# key_dependencies

- `featurize`
- `ProteinFeatures`
- `EncLayer`
- `DecLayer`
- `ProteinMPNN`
- 推理版 `parse_PDB`, `tied_featurize`, `StructureDatasetPDB`

# common_modification_points

- 只设计部分链时，优先使用 `chain_id_jsonl` 或 `pdb_path_chains`，不要在模型 forward 中硬改 mask
- 固定位点、omit AA、PSSM、tied positions 这类约束优先走 helper JSON，而不是改模型主体
- 若使用 CA-only 权重，必须同步打开 `--ca_only` 并走 CA-only 解析逻辑
- 新 PDB 批量输入优先转为 JSONL / `StructureDatasetPDB` 可读结构

# implementation_risks

- `X` 的 4 个原子顺序固定为 `N, CA, C, O`，顺序错会导致几何特征全部错位
- `chain_M` 是设计位置控制的核心 mask，不能和普通 padding `mask` 混用
- 推理版 `protein_mpnn_utils.py` 比训练版支持更多约束，二者同名类不能盲目替换
- `max_length`、batch size 和 kNN 邻居数会显著影响显存

# code_references

- `{onescience_path}/onescience/src/onescience/models/proteinmpnn/model_utils.py`
- `{onescience_path}/onescience/src/onescience/models/proteinmpnn/protein_mpnn_utils.py`
- `{onescience_path}/onescience/examples/biosciences/ProteinMPNN/protein_mpnn_run.py`
- `{onescience_path}/onescience/examples/biosciences/ProteinMPNN/README.md`
