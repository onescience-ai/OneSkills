# Model Card: ProteinMPNN

## 基本信息

- 模型名：`ProteinMPNN`
- 任务类型：`蛋白质骨架条件序列设计 / inverse folding`
- 当前状态：`stable`
- 主实现文件：`./onescience/src/onescience/models/proteinmpnn/model_utils.py`

## 模型定位

ProteinMPNN 用蛋白质骨架几何作为条件生成或打分氨基酸序列，适合蛋白设计、固定链/设计链控制、PSSM / tied positions / omit AA 等工程化 inverse folding 场景。

补充说明：

- 任务方向与 OpenFold / Protenix 相反：不是从序列预测结构，而是从结构骨架设计序列
- 训练版和推理版实现分别在 `model_utils.py` 与 `protein_mpnn_utils.py`
- example 主入口是 `examples/biosciences/ProteinMPNN/protein_mpnn_run.py`

## 输入定义

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

## 输出定义

- `log_probs`: `(Batch, L, 21)`
- 推理工具还支持：
  - `sample`
  - `tied_sample`
  - `conditional_probs`
  - `unconditional_probs`
  - score / probs / FASTA 输出

## 主干结构

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

## 主要依赖组件

- `featurize`
- `ProteinFeatures`
- `EncLayer`
- `DecLayer`
- `ProteinMPNN`
- 推理版 `parse_PDB`, `tied_featurize`, `StructureDatasetPDB`

## 主要 Shape 变化

- backbone coordinates: `(B, L, 4, 3)`
- edge features after kNN: `(B, L, K, edge_features)`
- node hidden: `(B, L, hidden_dim)`
- sequence embedding: `(B, L, hidden_dim)`
- output log probs: `(B, L, 21)`

## 默认关键参数

- `num_letters=21`
- `hidden_dim=128`
- `num_encoder_layers=3`
- `num_decoder_layers=3`
- `k_neighbors=32`
- `augment_eps=0.1`
- `dropout=0.1`
- example 默认模型名：`v_48_020`
- 常见采样温度：`0.1`, `0.15`, `0.2`, `0.25`, `0.3`

## 常见修改点

- 只设计部分链时，优先使用 `chain_id_jsonl` 或 `pdb_path_chains`，不要在模型 forward 中硬改 mask
- 固定位点、omit AA、PSSM、tied positions 这类约束优先走 helper JSON，而不是改模型主体
- 若使用 CA-only 权重，必须同步打开 `--ca_only` 并走 CA-only 解析逻辑
- 新 PDB 批量输入优先转为 JSONL / `StructureDatasetPDB` 可读结构

## 风险点

- `X` 的 4 个原子顺序固定为 `N, CA, C, O`，顺序错会导致几何特征全部错位
- `chain_M` 是设计位置控制的核心 mask，不能和普通 padding `mask` 混用
- 推理版 `protein_mpnn_utils.py` 比训练版支持更多约束，二者同名类不能盲目替换
- `max_length`、batch size 和 kNN 邻居数会显著影响显存

## 推荐检索顺序

1. 先看本模型卡
2. 若做训练或最小 forward，读 `model_utils.py`
3. 若做推理、设计约束或 PDB 输入，读 `protein_mpnn_utils.py`
4. 若写命令行适配，读 `examples/biosciences/ProteinMPNN/protein_mpnn_run.py`

## 组件契约入口

- `../contracts/proteinmpnncomponents.md`
- 当前 ProteinMPNN 未通过 OneScience `One*` wrapper 拼装，按模型工具函数、组件契约和 example 主入口对齐

## 源码锚点

- `./onescience/src/onescience/models/proteinmpnn/model_utils.py`
- `./onescience/src/onescience/models/proteinmpnn/protein_mpnn_utils.py`
- `./onescience/examples/biosciences/ProteinMPNN/protein_mpnn_run.py`
- `./onescience/examples/biosciences/ProteinMPNN/README.md`
