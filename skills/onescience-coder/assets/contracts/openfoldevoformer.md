# Contract: OpenFoldEvoformer

## 基本信息

- 组件名：`EvoformerStack / ExtraMSAStack`
- 所属模块族：`transformer`
- 统一入口：`OneTransformer`
- 注册名：`style="OpenFoldEvoformer"`, `style="OpenFoldExtraMSAStack"`
- 注册状态：`contract_only`

## 组件职责

OpenFold Evoformer 组件负责在 AF2 协议中交替更新 MSA representation、pair representation，并产生 StructureModule 所需的 single representation。

补充说明：

- 契约层统一收束到 `OneTransformer`，源码当前仍在 `onescience.models.openfold` 内部直接实例化
- 它与 Protenix Pairformer 目标相近但协议不同：OpenFold 保留 MSA trunk，Protenix 主 trunk 是 AF3 风格 Pairformer
- `ExtraMSAStack` 只更新 pair representation，`EvoformerStack` 输出 `m/z/s`

## 支持输入

- 2D 输入：`not_applicable`
- 3D 输入：`not_applicable`
- `EvoformerStack.forward` 输入：
  - `m`: `[*, N_seq, N_res, C_m]`
  - `z`: `[*, N_res, N_res, C_z]`
  - `msa_mask`: `[*, N_seq, N_res]`
  - `pair_mask`: `[*, N_res, N_res]`
  - `chunk_size`
  - `use_deepspeed_evo_attention`, `use_lma`, `use_flash`
- `ExtraMSAStack.forward` 输入：
  - `a`: `[*, N_extra, N_res, C_e]`
  - `z`: `[*, N_res, N_res, C_z]`
  - `extra_msa_mask`

内部统一做法：

- Evoformer block 内部包含 MSA attention、outer product mean、triangular multiplicative update、triangular attention 和 transition
- `EvoformerStack` 多层堆叠后用 `linear(m[..., 0, :, :])` 生成 single representation
- 推理可走 offload、chunk、DeepSpeed evo attention、low-memory attention 或 flash attention 分支

## 构造参数

- `c_m`, `c_z`, `c_s`
- `c_hidden_msa_att`
- `c_hidden_opm`
- `c_hidden_mul`
- `c_hidden_pair_att`
- `no_heads_msa`
- `no_heads_pair`
- `no_blocks`
- `transition_n`
- `msa_dropout`
- `pair_dropout`
- `no_column_attention`
- `opm_first`
- `fuse_projection_weights`
- `blocks_per_ckpt`
- `clear_cache_between_blocks`
- `tune_chunk_size`

## 输出约定

- `EvoformerStack` 输出：
  - `m`: `[*, N_seq, N_res, C_m]`
  - `z`: `[*, N_res, N_res, C_z]`
  - `s`: `[*, N_res, C_s]`
- `ExtraMSAStack` 输出：
  - `z`: `[*, N_res, N_res, C_z]`

如果有明确边界条件，也写在这里：

- `use_deepspeed_evo_attention`、`use_lma`、`use_flash` 是互斥路线
- offload forward 只在非训练且无梯度场景使用
- `blocks_per_ckpt` 用于 activation checkpoint，不是模型层数

## 典型调用位置

- `AlphaFold.iteration` 中 template 与 recycling 之后
- extra MSA features 处理之后
- StructureModule 之前

## 典型参数

- 具体参数来自 `onescience.configs.bio.openfold.config.model_config(...)`
- monomer / multimer / seq embedding mode 由 preset 控制，不能只局部替换 Evoformer 参数
- 契约层目标调用：
  - `OneTransformer(style="OpenFoldEvoformer", ...)`
  - `OneTransformer(style="OpenFoldExtraMSAStack", ...)`

## 风险点

- 以上 `style` 是 skill 契约归一名，不表示当前源码已经在 `OneTransformer` registry 中可直接实例化
- OpenFold batch 的最后一维是 recycling 维度，进入单次 iteration 后才取当前 cycle 特征
- `N_res x N_res x C_z` pair representation 是主要显存来源，长序列必须关注 chunk/offload/attention 实现
- OpenFold Evoformer 与 Protenix Pairformer 的输入 feature dict 不兼容，不要直接互换组件
- seq embedding mode 会关闭或改变部分 MSA column attention 行为，需要看配置 preset

## 源码锚点

- `./onescience/src/onescience/models/openfold/model.py`
- `./onescience/src/onescience/models/openfold/evoformer.py`
- `./onescience/src/onescience/models/openfold/msa.py`
- `./onescience/src/onescience/models/openfold/triangular_attention.py`
