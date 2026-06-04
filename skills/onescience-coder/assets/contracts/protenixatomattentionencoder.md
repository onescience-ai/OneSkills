# Contract: ProtenixAtomAttentionEncoder

## 基本信息

- 组件名：`ProtenixAtomAttentionEncoder`
- 所属模块族：`encoder`
- 统一入口：`OneEncoder`
- 注册名：`style="ProtenixAtomAttentionEncoder"`

## 组件职责

Protenix atom attention encoder 负责把原子级输入特征编码为 token 级表示，并保留 diffusion 阶段 decoder 需要复用的 atom skip 表征。

补充说明：

- 这是 Protenix / AF3 风格输入特征进入 token trunk 前的关键原子编码器
- `has_coords=False` 时用于 input feature embedder 的静态原子特征编码
- `has_coords=True` 时用于 diffusion module，将 noisy atom coordinates、single trunk 和 pair trunk 条件注入原子局部注意力

## 支持输入

- 2D 输入：`not_applicable`
- 3D 输入：`not_applicable`
- atom-token 输入：
  - `input_feature_dict`
  - 必需 atom 特征：`ref_pos`, `ref_charge`, `ref_mask`, `ref_element`, `ref_atom_name_chars`, `ref_space_uid`
  - 必需映射特征：`atom_to_token_idx`
  - `has_coords=True` 时额外需要 `r_l`, `s`, `z`

内部统一做法：

- 先把参考坐标、电荷、元素、原子名和 mask 投影为 atom feature `c_l`
- 再按 `n_queries / n_keys` 构造局部 atom pair 表征 `p_lm`
- 如果提供 noisy coordinates，则把 token single / pair 条件 broadcast 到 atom 与局部 atom pair
- 通过 `ProtenixAtomTransformer` 更新 atom query
- 使用 `aggregate_atom_to_token` 汇聚为 token 表征 `a`

## 构造参数

- `has_coords`
  - 是否把坐标 `r_l`、single `s`、pair `z` 作为条件输入
- `c_token`
  - 输出 token 表征维度
- `c_atom=128`
- `c_atompair=16`
- `c_s=384`
- `c_z=128`
- `n_blocks=3`
- `n_heads=4`
- `n_queries=32`
- `n_keys=128`
- `blocks_per_ckpt=None`

## 输出约定

- `a`: `[..., N_token, c_token]`
- `q_l`: `[..., N_atom, c_atom]` 或带 sample 维的 atom query
- `c_l`: `[..., N_atom, c_atom]`
- `p_lm`: `[..., n_trunks, n_queries, n_keys, c_atompair]`

如果有明确边界条件，也写在这里：

- `atom_to_token_idx` 必须能把每个 atom 映射到有效 token
- `ref_mask` 会直接参与 atom feature masking
- `has_coords=True` 时 `r_l/s/z` 三者必须同时提供
- `n_queries/n_keys` 必须与后续 `ProtenixAtomTransformer` 配置一致

## 典型调用位置

- `ProtenixInputFeatureEmbedder` 内部：从参考 atom 特征生成 token input
- `ProtenixDiffusionModule` 内部：把 noisy coordinates 与 trunk 条件编码到 atom/token 表征

## 典型参数

- Protenix 输入特征编码：
  - `OneEncoder(style="ProtenixAtomAttentionEncoder", has_coords=False, c_token=384)`
- Protenix diffusion atom encoder：
  - `OneEncoder(style="ProtenixAtomAttentionEncoder", has_coords=True, c_token=768, c_s=384, c_z=128)`

## 风险点

- 该组件强依赖 Protenix feature dict，不能用普通 FASTA、PDB 坐标张量或 OpenFold batch 直接替代
- `ref_atom_name_chars` 在源码中按 `4 * 64` 展平，维度不匹配会在 concat 阶段失败
- 局部 attention 的 padded trunk 形态由 `rearrange_qk_to_dense_trunk` 产生，不要手工假设为完整 `N_atom x N_atom`
- 长 token 或长 atom 场景推理时源码会主动清理 CUDA cache，说明该组件显存压力较高

## 源码锚点

- `./onescience/src/onescience/modules/encoder/oneencoder.py`
- `./onescience/src/onescience/modules/encoder/protenixencoding.py`
- `./onescience/src/onescience/modules/transformer/protenixtransformer.py`

