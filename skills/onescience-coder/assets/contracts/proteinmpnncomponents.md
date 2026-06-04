# Contract: ProteinMPNNComponents

## 基本信息

- 组件名：`ProteinMPNNFeatureEncoder / ProteinMPNNSequenceDecoder`
- 所属模块族：`encoder / decoder`
- 统一入口：`OneEncoder / OneDecoder`
- 注册名：`style="ProteinMPNNFeatureEncoder"`, `style="ProteinMPNNSequenceDecoder"`
- 注册状态：`contract_only`

## 组件职责

ProteinMPNN 组件负责从蛋白骨架构造 kNN 几何图，并在图上进行 encoder-decoder 式自回归氨基酸序列建模。

补充说明：

- 这是 inverse folding 路线：结构到序列，不是序列到结构
- 契约层把 backbone graph 特征构造与 encoder 层收束到 `OneEncoder`，把自回归序列 decoder 收束到 `OneDecoder`
- 训练简化版在 `model_utils.py`，推理约束版在 `protein_mpnn_utils.py`
- 推理版支持固定链、固定位置、omit AA、PSSM、tied positions 和 residue bias 等工程约束

## One* 归一映射

| 源码组件 | 所属模块族 | 统一入口 | 注册名 |
| --- | --- | --- | --- |
| `ProteinFeatures / EncLayer` | `encoder` | `OneEncoder` | `style="ProteinMPNNFeatureEncoder"` |
| `DecLayer / ProteinMPNN.sample / tied_sample` | `decoder` | `OneDecoder` | `style="ProteinMPNNSequenceDecoder"` |

## 支持输入

- 2D 输入：`not_applicable`
- 3D 输入：`not_applicable`
- 训练版模型输入：
  - `X`: `(B, L, 4, 3)`，原子顺序为 `N, CA, C, O`
  - `S`: `(B, L)`
  - `mask`: `(B, L)`
  - `chain_M`: `(B, L)`
  - `residue_idx`: `(B, L)`
  - `chain_encoding_all`: `(B, L)`
- 推理版 `tied_featurize` 还会构造：
  - `chain_M_pos`
  - `omit_AA_mask`
  - `pssm_coef`, `pssm_bias`, `pssm_log_odds_mask`
  - `tied_pos_list_of_lists`
  - `bias_by_res_all`

内部统一做法：

- `ProteinFeatures` 从 `N/CA/C/O` 推导 `Cb`
- 以 CA 距离做 top-k 邻居
- 为 25 种原子对距离构造 RBF 特征，并拼接链内/链间位置编码
- encoder 在骨架图上无自回归 mask 地更新节点和边
- decoder 按 `chain_M` 与随机 decoding order 构造前向/后向 mask，自回归预测设计位置

## 构造参数

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

## 输出约定

- `ProteinMPNN.forward` 输出：
  - `log_probs`: `(B, L, 21)`
- 推理版采样输出包含：
  - sampled sequence ids
  - per-position probabilities / log probabilities
  - optional tied-position sampling results

如果有明确边界条件，也写在这里：

- `X[:, :, 0:4, :]` 的顺序必须是 `N, CA, C, O`
- `chain_M=1` 表示需要设计 / 预测的位置，不能和 padding mask 混用
- `k_neighbors` 不能超过有效残基数
- CA-only 权重必须走 CA-only featurize 和参数分支

## 典型调用位置

- `examples/biosciences/ProteinMPNN/protein_mpnn_run.py`
- RFdiffusion 生成骨架后的序列设计后处理
- PDB 批量 inverse folding / score / conditional probability 任务

## 典型参数

- 默认推理模型名：
  - `v_48_020`
- 常见采样温度：
  - `0.1`, `0.15`, `0.2`, `0.25`, `0.3`
- 常见邻居数：
  - `k_neighbors=32`
- 契约层目标调用：
  - `OneEncoder(style="ProteinMPNNFeatureEncoder", ...)`
  - `OneDecoder(style="ProteinMPNNSequenceDecoder", ...)`

## 风险点

- 上述 `style` 是 skill 契约归一名，不表示当前源码已经在对应 `One*` registry 中可直接实例化
- 训练版 `model_utils.py` 与推理版 `protein_mpnn_utils.py` 同名类功能不完全一致，做约束设计时优先读推理版
- 固定链、固定位置、PSSM 和 tied positions 应通过 helper JSON / runner 参数表达，不建议硬改 model forward
- 输入 PDB 解析失败或缺主链原子会直接影响几何图和序列设计结果
- RFdiffusion 输出骨架通常还缺可靠侧链，接 ProteinMPNN 时应按骨架设计协议处理

## 源码锚点

- `./onescience/src/onescience/models/proteinmpnn/model_utils.py`
- `./onescience/src/onescience/models/proteinmpnn/protein_mpnn_utils.py`
- `./onescience/examples/biosciences/ProteinMPNN/protein_mpnn_run.py`
- `./onescience/examples/biosciences/ProteinMPNN/README.md`
