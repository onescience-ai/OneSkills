# Contract: ProtenixAtomAttentionDecoder

## 基本信息

- 组件名：`ProtenixAtomAttentionDecoder`
- 所属模块族：`decoder`
- 统一入口：`OneDecoder`
- 注册名：`style="ProtenixAtomAttentionDecoder"`

## 组件职责

Protenix atom attention decoder 负责把 token 级 diffusion 表征解码回原子坐标更新，是 Protenix diffusion module 中生成 `r_update` 的最后一段。

补充说明：

- decoder 不独立完成完整结构预测，只输出一次 denoising step 的 atom coordinate update
- 它复用 atom attention encoder 产生的 `q_skip/c_skip/p_skip`
- 内部通过 `ProtenixAtomTransformer` 在 atom 局部窗口上更新 query

## 支持输入

- 2D 输入：`not_applicable`
- 3D 输入：`not_applicable`
- diffusion decoder 输入：
  - `input_feature_dict`
  - `a`: `[..., N_token, c_token]`
  - `q_skip`: `[..., N_atom, c_atom]`
  - `c_skip`: `[..., N_atom, c_atom]`
  - `p_skip`: `[..., n_trunks, n_queries, n_keys, c_atompair]`

内部统一做法：

- 先将 token 表征 `a` 投影到 atom 通道
- 使用 `atom_to_token_idx` 将 token 表征 broadcast 到 atom
- 与 encoder 传来的 `q_skip` 相加
- 经 `ProtenixAtomTransformer` 进行局部 atom attention
- LayerNorm 后投影为 3 维坐标更新

## 构造参数

- `n_blocks=3`
- `n_heads=4`
- `c_token=384`
- `c_atom=128`
- `c_atompair=16`
- `n_queries=32`
- `n_keys=128`
- `blocks_per_ckpt=None`

## 输出约定

- `r`: `[..., N_atom, 3]`

如果有明确边界条件，也写在这里：

- `input_feature_dict["atom_to_token_idx"]` 必须与 `a` 的 `N_token` 和 skip 的 `N_atom` 对齐
- `p_skip` 的 `n_queries/n_keys` 必须等于 decoder 构造参数
- 输出是坐标增量，不是最终采样坐标

## 典型调用位置

- `ProtenixDiffusionModule.f_forward`
- `ProtenixDiffusionModule.forward`
- Protenix confidence head 前 mini-rollout 的 diffusion step

## 典型参数

- Protenix diffusion 默认 decoder：
  - `OneDecoder(style="ProtenixAtomAttentionDecoder", n_blocks=3, n_heads=4, c_token=768, c_atom=128, c_atompair=16)`

## 风险点

- decoder 与 atom encoder 成对使用，单独构造时很容易缺少 `q_skip/c_skip/p_skip`
- `c_token` 在 diffusion 主体中常为 `768`，不要直接套 input embedder 的 token 维度
- 该模块依赖局部 atom attention，不适合作为通用坐标 MLP 或 OpenFold StructureModule 的替代品

## 源码锚点

- `./onescience/src/onescience/modules/decoder/onedecoder.py`
- `./onescience/src/onescience/modules/decoder/protenixdecoder.py`
- `./onescience/src/onescience/modules/diffusion/protenixdiffusion.py`
- `./onescience/src/onescience/modules/transformer/protenixtransformer.py`

