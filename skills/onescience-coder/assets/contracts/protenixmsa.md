# Contract: ProtenixMSAModule

## 基本信息

- 组件名：`ProtenixMSAModule`
- 所属模块族：`msa`
- 统一入口：`OneMSA`
- 注册名：`style="ProtenixMSAModule"`

## 组件职责

ProtenixMSAModule 在 Protenix recycling 过程中使用 MSA 特征更新 pair representation。

补充说明：

- 输入 MSA 已经是模型 feature dict 中的 tensor，不是文件路径或 `MSA` dataclass
- 模块内部会采样 MSA 行、one-hot 编码 MSA token，并通过 MSA block 与 Pairformer block 更新 `z`
- 最后一层 MSA block 返回 `None, z`，外部只接收 updated `z`

## 支持输入

- 2D 输入：`not_applicable`
- 3D 输入：`not_applicable`
- 生信输入：
  - `input_feature_dict["msa"]`: `[..., N_msa, N_token]`
  - `input_feature_dict["has_deletion"]`
  - `input_feature_dict["deletion_value"]`
  - `z`: `[..., N_token, N_token, c_z]`
  - `s_inputs`: `[..., N_token, c_s_inputs]`
  - `pair_mask`: `[..., N_token, N_token]` 或 `None`

内部统一做法：

- 缺少 MSA 或维度不足时直接返回原 `z`
- 根据 train / test cutoff 随机无放回采样 MSA
- 把 `msa(32) + has_deletion(1) + deletion_value(1)` 拼接投影到 `c_m`
- 加上 `s_inputs` 投影
- 通过若干 `ProtenixMSABlock` 更新 `z`

## 构造参数

- `n_blocks=4`
- `c_m=64`
- `c_z=128`
- `c_s_inputs=449`
- `msa_dropout=0.15`
- `pair_dropout=0.25`
- `blocks_per_ckpt=1`
- `msa_chunk_size=2048`
- `msa_max_size=16384`
- `msa_configs`
  - `enable`
  - `strategy`
  - `sample_cutoff.train/test`
  - `min_size.train/test`

## 输出约定

- 输出 updated pair representation：
  - `[..., N_token, N_token, c_z]`

如果有明确边界条件，也写在这里：

- `n_blocks < 1` 时直接返回输入 `z`
- inference 且 token / MSA 很大时会主动清理 CUDA cache

## 典型调用位置

- Protenix `get_pairformer_output` recycling loop 中，在 template 分支后、PairformerStack 前

## 典型参数

- Protenix 主模型：
  - `OneMSA(style="ProtenixMSAModule", **configs.model.msa_module, msa_configs=configs.data.get("msa", {}))`

## 风险点

- `msa_configs` 在源码中直接调用 `.get`，传入 `None` 会失败，调用层应提供 dict
- `msa` one-hot 类别数固定为 32，不能直接使用通用 `AminoAcidEncoder` 的 22 类矩阵替代
- MSA 行数大时显存主要受 `N_msa_sampled * N_token` 与 `N_token^2` pair 表征共同影响

## 源码锚点

- `./onescience/src/onescience/modules/msa/onemsa.py`
- `./onescience/src/onescience/modules/msa/protenixmsa.py`
- `./onescience/src/onescience/models/protenix/protenix.py`
