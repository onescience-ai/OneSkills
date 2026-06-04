# Contract: ProtenixRelativePositionEncoding

## 基本信息

- 组件名：`ProtenixRelativePositionEncoding`
- 所属模块族：`encoder`
- 统一入口：`OneEncoder`
- 注册名：`style="ProtenixRelativePositionEncoding"`

## 组件职责

为 Protenix 的 pair representation 构造相对位置编码，覆盖残基相对位置、token 相对位置、链关系和 entity 关系。

补充说明：

- 该组件是 Protenix `z_init` 的关键输入之一
- 输入是 token 级元信息，不读取 atom 坐标
- 推理时对长 token 序列有 chunk 化路径以降低显存压力

## 支持输入

- 2D 输入：`not_applicable`
- 3D 输入：`not_applicable`
- token 元信息：
  - `asym_id`: `[..., N_token]`
  - `residue_index`: `[..., N_token]`
  - `entity_id`: `[..., N_token]`
  - `sym_id`: `[..., N_token]`
  - `token_index`: `[..., N_token]`

内部统一做法：

- 判断 same chain、same residue、same entity
- residual relative position 按 `r_max` 截断后 one-hot
- token relative position 按 `r_max` 截断后 one-hot
- chain relative position 按 `s_max` 截断后 one-hot
- 拼接后经 `ProtenixLinearNoBias` 投影到 `c_z`

## 构造参数

- `r_max=32`
  - residue / token 相对距离截断范围
- `s_max=2`
  - chain 相对距离截断范围
- `c_z=128`
  - pair embedding 维度

## 输出约定

- 输出 shape：`[..., N_token, N_token, c_z]`

如果有明确边界条件，也写在这里：

- 训练路径直接构造完整 pair one-hot
- eval 路径在 `Ntoken >= 3200` 时切成多个 chunk 做线性投影

## 典型调用位置

- Protenix `get_pairformer_output` 中加到 `z_init`
- Protenix diffusion conditioning 中与 `z_trunk` 拼接形成 pair conditioning

## 典型参数

- Protenix 默认
  - `style="ProtenixRelativePositionEncoding"`
  - `r_max=32`
  - `s_max=2`
  - `c_z=128`

## 风险点

- 该组件依赖 `token_index`，如果 datapipe 只提供 `residue_index` 会缺字段
- 输出是 `N_token^2` pair 特征，长序列和复合物会迅速增加显存压力
- `asym_id/entity_id/sym_id` 的语义错会影响链、实体和对称关系编码

## 源码锚点

- `./onescience/src/onescience/modules/encoder/oneencoder.py`
- `./onescience/src/onescience/modules/encoder/protenixencoding.py`
- `./onescience/src/onescience/models/protenix/protenix.py`
