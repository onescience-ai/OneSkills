# Contract: OneMSA

## 基本信息

- 组件名：`OneMSA`
- 所属模块族：`msa`
- 统一入口：`direct_import`
- 注册名：`style="<MSAStyle>"`

## 组件职责

为 MSA 模块提供统一入口，当前注册的主要实现是 Protenix 的 MSA 模块。

补充说明：

- wrapper 只负责按 `style` 分发
- shape、MSA 采样策略和 pair update 逻辑都由具体实现决定
- 当前常见调用者是 `Protenix`

## 支持输入

- 2D 输入：`not_applicable`
- 3D 输入：`not_applicable`
- 生信特征输入：`input_feature_dict + z + s_inputs + pair_mask`

内部统一做法：

- 从 `_MSA_REGISTRY` 中实例化具体 MSA 模块
- forward 时不改写参数，直接透传

## 构造参数

- `style`
  - 当前可用：`ProtenixMSAModule`
- `**kwargs`
  - 透传给具体 MSA 模块

## 输出约定

- 对 Protenix MSA：
  - 输入 `z`: `[..., N_token, N_token, c_z]`
  - 输出 updated `z`: `[..., N_token, N_token, c_z]`

如果有明确边界条件，也写在这里：

- 缺少 `msa` 或 `msa` 维度不足时，Protenix MSA 模块会直接返回原 `z`

## 典型调用位置

- Protenix recycling loop 中，在 template 更新之后、PairformerStack 之前

## 典型参数

- Protenix MSA
  - `style="ProtenixMSAModule"`
  - `n_blocks=4`
  - `c_m=64`
  - `c_z=128`
  - `c_s_inputs=449`
  - `msa_configs=configs.data.get("msa", {})`

## 风险点

- `OneMSA` 当前不是通用 MSA parser 或 featurizer，它是模型内 MSA 表征更新模块
- Protenix 的 MSA 输入需要 `msa/has_deletion/deletion_value`，不是 `MSAParser` 的原始对象
- MSA 数量大时显存压力很高，`sample_cutoff`、`msa_chunk_size` 和 `msa_max_size` 会影响内存

## 源码锚点

- `./onescience/src/onescience/modules/msa/onemsa.py`
- `./onescience/src/onescience/modules/msa/protenixmsa.py`
