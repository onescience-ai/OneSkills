# architecture_overview

ProteinMPNN 的完整公开实现位于 `protein_mpnn_utils.py`。`ProteinMPNN` 将 N/CA/C/O 骨架或 CA-only 坐标转为 kNN 几何图，经无掩码 encoder 更新骨架表征，再按设计 mask 与 decoding order 使用自回归 decoder 预测氨基酸。该文件同时提供约束特征化、采样和条件概率接口。

# parameter_scale

- `ProteinMPNN(num_letters, node_features, edge_features, hidden_dim, num_encoder_layers=3, num_decoder_layers=3, vocab=21, k_neighbors=64, augment_eps=0.05, dropout=0.1, ca_only=False)`。
- `num_letters` 控制输出类别数，常规蛋白序列模型与 `vocab=21` 配套。
- `k_neighbors=64` 与 `augment_eps=0.05` 是该完整实现的默认值；不要用另一实现或脚本中的值覆盖。

# architecture_structure

```text
backbone coordinates + masks + residue/chain indices
  -> ProteinFeatures or CA_ProteinFeatures
  -> edge projection
  -> EncLayer stack
sequence tokens + decoding order
  -> sequence embedding
  -> masked DecLayer stack
  -> W_out
  -> amino-acid log probabilities
```

# input_schema

- `forward(X, S, mask, chain_M, residue_idx, chain_encoding_all, randn, use_input_decoding_order=False, decoding_order=None)`。
- 全原子骨架 `X` 的典型 shape 为 `(B, L, 4, 3)`，原子顺序为 N、CA、C、O；CA-only 模式使用与其特征器匹配的坐标。
- `S` 是 `(B, L)` 残基 token；`mask` 是有效残基 mask；`chain_M` 是需要设计/预测的位置 mask。
- `residue_idx` 和 `chain_encoding_all` 为 `(B, L)`；`randn` 用于产生解码顺序。

# output_schema

- `forward` 返回 `(B, L, num_letters)` 的 log probability。
- `sample` 与 `tied_sample` 返回采样序列及概率/顺序等字典字段。
- `conditional_probs` 与 `unconditional_probs` 返回相应条件下的氨基酸 log probability。
- `tied_featurize` 返回模型输入张量和 PSSM、omit-AA、tied-position 等约束张量。

# shape_transformations

1. 骨架通过 kNN 转为 `(B, L, K, edge_features)`。
2. edge 投影到 `hidden_dim`，node hidden 初始化后经 encoder 更新。
3. `S` 嵌入为 `(B, L, hidden_dim)`。
4. decoding order 生成前向/后向邻接 mask，decoder 逐位置组合结构与已知序列信息。
5. 输出层映射到 `num_letters` 并执行 `log_softmax`。

# key_dependencies

- `proteinmpnn_components`

# common_modification_points

- 固定链、固定位点、omit AA、PSSM 和 tied positions 应通过 `tied_featurize` 的约束输入实现。
- 切换 CA-only 时同步使用 `CA_ProteinFeatures` 和匹配 checkpoint。
- 需要确定性 decoding order 时显式传 `use_input_decoding_order=True` 与 `decoding_order`。
- 训练使用 `forward` 的 log probability 和 `loss_nll`/`loss_smoothed`；推理使用 sample 系列方法。

# implementation_risks

- `chain_M` 与 padding `mask` 语义不同，混用会错误设计固定位置。
- 全骨架原子顺序错误会系统性破坏几何特征。
- `protein_mpnn_utils.py` 与 `model_utils.py` 存在不同实现细节，checkpoint 和默认参数不能跨实现混用。
- 约束 tensor 必须与 batch、链顺序和 residue index 对齐。

# code_references

- `{onescience_path}/onescience/src/onescience/models/proteinmpnn/protein_mpnn_utils.py`
- `{onescience_path}/onescience/src/onescience/models/proteinmpnn/model_utils.py`
