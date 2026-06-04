# Contract: ProtenixTransformer

## 基本信息

- 组件名：`ProtenixConditionedTransitionBlock / ProtenixDiffusionTransformerBlock / ProtenixDiffusionTransformer / ProtenixAtomTransformer`
- 所属模块族：`transformer`
- 统一入口：`OneTransformer`
- 注册名：`style="ProtenixConditionedTransitionBlock"`, `style="ProtenixDiffusionTransformerBlock"`, `style="ProtenixDiffusionTransformer"`, `style="ProtenixAtomTransformer"`

## 组件职责

Protenix transformer 组件负责 diffusion 表征更新和 atom 局部表征更新，是 Protenix diffusion module 内部连接 attention、conditioned transition 与坐标 decoder 的主干。

补充说明：

- `ProtenixConditionedTransitionBlock` 是受 single 条件调制的 gated transition
- `ProtenixDiffusionTransformerBlock` 组合 pair-bias attention 与 conditioned transition
- `ProtenixDiffusionTransformer` 是多层 block stack
- `ProtenixAtomTransformer` 把 diffusion transformer 用在 atom local attention window 上

## 支持输入

- 2D 输入：`not_applicable`
- 3D 输入：`not_applicable`
- conditioned transition 输入：
  - `a`: `[..., N, c_a]`
  - `s`: `[..., N, c_s]`
- diffusion transformer 输入：
  - `a`: `[..., N_token, c_a]`
  - `s`: `[..., N_token, c_s]`
  - `z`: `[..., N_token, N_token, c_z]` 或 local 模式下的 `[..., n_trunks, n_queries, n_keys, c_z]`
- atom transformer 输入：
  - `q`: `[..., N_atom, c_atom]`
  - `c`: `[..., N_atom, c_atom]`
  - `p`: `[..., n_trunks, n_queries, n_keys, c_atompair]`

内部统一做法：

- diffusion block 先用 `ProtenixAttentionPairBiasWithLocalAttn` 更新 `a`
- 再用 `ProtenixConditionedTransitionBlock` 做受 `s` 调制的前馈更新
- stack 通过 `checkpoint_blocks` 管理 activation checkpoint
- atom transformer 固定使用 `cross_attention_mode=True` 的 diffusion transformer，并校验局部窗口大小

## 构造参数

- `ProtenixConditionedTransitionBlock`
  - `c_a`
  - `c_s`
  - `n=2`
  - `biasinit=-2.0`
- `ProtenixDiffusionTransformerBlock`
  - `c_a`, `c_s`, `c_z`, `n_heads`
  - `biasinit=-2.0`
  - `drop_path_rate=0.0`
  - `cross_attention_mode=False`
- `ProtenixDiffusionTransformer`
  - `c_a`, `c_s`, `c_z`, `n_blocks`, `n_heads`
  - `cross_attention_mode=False`
  - `drop_path_rate=0.0`
  - `blocks_per_ckpt=None`
- `ProtenixAtomTransformer`
  - `c_atom=128`
  - `c_atompair=16`
  - `n_blocks=3`
  - `n_heads=4`
  - `n_queries=32`
  - `n_keys=128`
  - `blocks_per_ckpt=None`

## 输出约定

- conditioned transition 输出：`[..., N, c_a]`
- diffusion transformer block 输出：`(a, s, z)`
- diffusion transformer stack 输出：`a`
- atom transformer 输出：更新后的 `q`: `[..., N_atom, c_atom]`

如果有明确边界条件，也写在这里：

- `ProtenixAtomTransformer.forward` 会断言 `p.shape[-3] == n_queries` 且 `p.shape[-2] == n_keys`
- `z.shape[-2] > 2000` 且推理模式下，stack 会在 block 间清理 CUDA cache
- `blocks_per_ckpt` 只在梯度开启时生效

## 典型调用位置

- `ProtenixDiffusionModule` 中的 token diffusion transformer
- `ProtenixAtomAttentionEncoder` 中的 atom local transformer
- `ProtenixAtomAttentionDecoder` 中的 atom local transformer

## 典型参数

- Protenix diffusion token transformer：
  - `OneTransformer(style="ProtenixDiffusionTransformer", n_blocks=24, n_heads=16, c_a=768, c_s=384, c_z=128)`
- Protenix atom transformer：
  - `OneTransformer(style="ProtenixAtomTransformer", n_blocks=3, n_heads=4, c_atom=128, c_atompair=16, n_queries=32, n_keys=128)`

## 风险点

- 该组件族服务于 Protenix diffusion，不等同于通用 Transformer encoder
- atom transformer 的 `p` 是局部 atom pair trunk，不是完整 pair representation `z`
- 如果修改 `n_queries/n_keys`，必须同步 atom encoder、atom decoder 和 atom transformer
- diffusion transformer 只更新 `a`，不会直接输出坐标；坐标更新由 atom decoder 产生

## 源码锚点

- `./onescience/src/onescience/modules/transformer/onetransformer.py`
- `./onescience/src/onescience/modules/transformer/protenixtransformer.py`
- `./onescience/src/onescience/modules/diffusion/protenixdiffusion.py`
- `./onescience/src/onescience/modules/encoder/protenixencoding.py`

