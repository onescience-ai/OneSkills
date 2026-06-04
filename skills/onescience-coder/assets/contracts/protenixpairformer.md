# Contract: ProtenixPairformer

## 基本信息

- 组件名：`ProtenixPairformerBlock / ProtenixPairformerStack`
- 所属模块族：`pairformer`
- 统一入口：`OnePairformer`
- 注册名：`style="ProtenixPairformerBlock"`, `style="ProtenixPairformerStack"`

## 组件职责

Protenix Pairformer 负责更新 token single representation 与 pair representation，是 Protenix trunk 的核心建模模块。

补充说明：

- `ProtenixPairformerBlock` 是单层 block，可单独用于 MSA block 内部的 pair update
- `ProtenixPairformerStack` 是主 trunk 中的多层堆栈
- block 同时包含 triangular multiplication、triangular attention、pair transition 和可选 single attention update

## 支持输入

- 2D 输入：`not_applicable`
- 3D 输入：`not_applicable`
- token-pair 输入：
  - `s`: `[..., N_token, c_s]` 或 `None`
  - `z`: `[..., N_token, N_token, c_z]`
  - `pair_mask`: `[..., N_token, N_token]` 或 `None`

内部统一做法：

- `z` 先经 outgoing / incoming triangular multiplication
- 再经 start / end triangular attention
- 再经 pair transition
- 如果 `c_s > 0`，使用 pair bias attention 更新 `s`
- stack 通过 `checkpoint_blocks` 管理激活 checkpoint

## 构造参数

- `ProtenixPairformerBlock`
  - `n_heads=16`
  - `c_z=128`
  - `c_s=384`
  - `c_hidden_mul=128`
  - `c_hidden_pair_att=32`
  - `no_heads_pair=4`
  - `dropout=0.25`
- `ProtenixPairformerStack`
  - `n_blocks=48`
  - `n_heads=16`
  - `c_z=128`
  - `c_s=384`
  - `dropout=0.25`
  - `blocks_per_ckpt=None`

## 输出约定

- block 输出：
  - `s`: `[..., N_token, c_s]` 或 `None`
  - `z`: `[..., N_token, N_token, c_z]`
- stack 输出同 block

如果有明确边界条件，也写在这里：

- `c_s=0` 时 single branch 不创建，适合作为纯 pair update
- inference 且 `N_token > 2000` 时 stack 会在 block 间清理 CUDA cache

## 典型调用位置

- Protenix 主 trunk：`ProtenixPairformerStack`
- Protenix MSA block：`ProtenixPairformerBlock(c_s=0)`
- Protenix template embedder 内部：`ProtenixPairformerStack(c_s=0)`

## 典型参数

- 主 Protenix trunk
  - `OnePairformer(style="ProtenixPairformerStack", **configs.model.pairformer)`
- MSA 内部 block
  - `OnePairformer(style="ProtenixPairformerBlock", c_z=c_z, c_s=0, dropout=pair_dropout)`

## 风险点

- `z` 的二阶 shape 是最主要的内存来源，长 token 场景必须关注 chunk、checkpoint 和 low-memory attention
- `pair_mask` 维度需要和 `z[..., N_token, N_token, :]` 对齐
- 该组件语义与天气 `fuser` 不同，不要因为都是 trunk 就放到 `OneFuser`

## 源码锚点

- `./onescience/src/onescience/modules/pairformer/onepairformer.py`
- `./onescience/src/onescience/modules/pairformer/protenixpairformer.py`
- `./onescience/src/onescience/modules/msa/protenixmsa.py`
