# Contract: ProtenixAttention

## 基本信息

- 组件名：`ProtenixAttention / ProtenixAttentionPairBias / ProtenixAttentionPairBiasWithLocalAttn`
- 所属模块族：`attention`
- 统一入口：`OneAttention`
- 注册名：`style="ProtenixAttention"`, `style="ProtenixAttentionPairBias"`, `style="ProtenixAttentionPairBiasWithLocalAttn"`

## 组件职责

Protenix attention 组件提供 AF3 / Protenix 风格的 gated multi-head attention、pair bias attention，以及适配 atom 局部窗口的 local attention。

补充说明：

- `ProtenixAttention` 是底层多头注意力实现，支持 gating、pair bias 和局部 attention 入口
- `ProtenixAttentionPairBias` 用 pair representation `z` 生成 attention bias，常用于 Pairformer single update
- `ProtenixAttentionPairBiasWithLocalAttn` 支持局部窗口和 cross-attention mode，常用于 diffusion transformer 与 atom transformer

## 支持输入

- 2D 输入：`not_applicable`
- 3D 输入：`not_applicable`
- `ProtenixAttention` 输入：
  - `q_x`: `[..., Q, c_q]`
  - `kv_x`: `[..., K, c_k]`
  - `attn_bias`: `[..., Q, K]` 或 `[..., H, Q, K]`
  - `trunked_attn_bias`: `[..., H, n_trunks, n_queries, n_keys]`
- `ProtenixAttentionPairBias` 输入：
  - `a`: `[..., N_token, c_a]`
  - `s`: `[..., N_token, c_s]` 或 `None`
  - `z`: `[..., N_token, N_token, c_z]`
- `ProtenixAttentionPairBiasWithLocalAttn` 输入：
  - `a`: `[..., N, c_a]`
  - `s`: `[..., N, c_s]`
  - `z`: global 模式为 `[..., N, N, c_z]`，local 模式为 `[..., n_trunks, n_queries, n_keys, c_z]`
  - `n_queries`, `n_keys`

内部统一做法：

- q/k/v 先按 head 维度重排，并对 q 做 `sqrt(c_hidden)` 缩放
- pair representation 经 LayerNorm 和无 bias 线性层变成每个 head 的 attention bias
- gating 打开时，attention 输出会乘以由 query 或 single 表征生成的 gate
- local 模式下通过 `n_queries/n_keys` 与 trunked bias 控制局部 atom attention

## 构造参数

- `ProtenixAttention`
  - `c_q`, `c_k`, `c_v`, `c_hidden`, `num_heads`
  - `gating=True`
  - `q_linear_bias=True`
  - `local_attention_method="global_attention_with_bias"`
  - `use_efficient_implementation=False`
  - `zero_init=True`
- `ProtenixAttentionPairBias`
  - `has_s=True`
  - `create_offset_ln_z=False`
  - `n_heads=16`
  - `c_a=768`
  - `c_s=384`
  - `c_z=128`
  - `biasinit=-2.0`
- `ProtenixAttentionPairBiasWithLocalAttn`
  - 同上，并额外支持 `cross_attention_mode=False`

## 输出约定

- `ProtenixAttention` 输出：`[..., Q, c_q]`
- pair bias attention 输出：更新后的 `a`，最后一维通常为 `c_a`

如果有明确边界条件，也写在这里：

- `c_a % n_heads == 0`
- `attn_bias` 维度要么含 head 维，要么可在 head 维 broadcast
- local 模式中 `n_queries/n_keys` 必须与 trunked bias 的对应维一致
- `cross_attention_mode=True` 时 query 与 key/value 会走分开的归一化路径

## 典型调用位置

- `ProtenixPairformerBlock` 的 single representation update
- `ProtenixDiffusionTransformerBlock` 的 pair bias attention
- `ProtenixAtomTransformer` 的局部 atom attention

## 典型参数

- Pairformer single update：
  - `OneAttention(style="ProtenixAttentionPairBias", has_s=False, c_a=c_s, c_z=c_z)`
- Diffusion transformer block：
  - `OneAttention(style="ProtenixAttentionPairBiasWithLocalAttn", has_s=True, c_a=c_a, c_s=c_s, c_z=c_z, n_heads=n_heads)`
- Atom local attention：
  - `OneAttention(style="ProtenixAttention", local_attention_method="local_cross_attention")`

## 风险点

- 这是 Protenix 内部 attention，不是天气模型的窗口 attention，输入语义不能与 `EarthAttention2D/3D` 混用
- pair bias 来自 `z`，若 `z` 未经过正确 trunk 或局部重排，attention 仍会运行但语义错误
- `ProtenixAttentionPairBias` 与 `ProtenixAttentionPairBiasWithLocalAttn` 都可更新 `a`，但后者才覆盖 atom 局部窗口场景
- `use_efficient_implementation=True` 会走 PyTorch SDPA，需确认当前 mask/bias 形态兼容

## 源码锚点

- `./onescience/src/onescience/modules/attention/oneattention.py`
- `./onescience/src/onescience/modules/attention/protenixattention.py`
- `./onescience/src/onescience/modules/pairformer/protenixpairformer.py`
- `./onescience/src/onescience/modules/transformer/protenixtransformer.py`

