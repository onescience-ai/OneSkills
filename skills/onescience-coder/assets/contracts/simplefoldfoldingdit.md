# Contract: SimpleFoldFoldingDiT

## 基本信息

- 组件名：`FoldingDiT`
- 所属模块族：`transformer`
- 统一入口：`OneTransformer`
- 注册名：`style="SimpleFoldFoldingDiT"`
- 注册状态：`contract_only`

## 组件职责

`FoldingDiT` 是 SimpleFold 的核心结构生成主干，负责把 noised atom coordinates、时间条件、原子/残基特征和 ESM token 表征融合后预测 atom velocity。

补充说明：

- 契约层统一收束到 `OneTransformer`，源码当前仍由 SimpleFold 自身直接实例化 `FoldingDiT`
- 它是 flow matching 折叠模型，不是 AF2 Evoformer 或 AF3 Pairformer/diffusion module
- 主要服务于 SimpleFold 训练、微调和采样，不适合作为通用 Transformer block 替换件

## 支持输入

- 2D 输入：`not_applicable`
- 3D 输入：`not_applicable`
- 主输入：
  - `noised_pos`: `(B, N_atom, 3)`
  - `t`: `(B,)`
  - `feats`: SimpleFold atom-token feature dict
  - `self_cond`: optional
- 关键 `feats` 字段：
  - `ref_pos`, `ref_charge`, `atom_pad_mask`, `ref_element`, `ref_atom_name_chars`
  - `atom_to_token`, `atom_to_token_idx`, `ref_space_uid`
  - `mol_type`, `res_type`, `pocket_feature`
  - `residue_index`, `entity_id`, `asym_id`, `sym_id`
  - `max_num_tokens`, `esm_s`

内部统一做法：

- 用时间 `t` 和可选长度条件生成 AdaLN 条件 `c_emb`
- 把 atom 静态特征与 noised coordinate embedding 拼接投影
- atom encoder transformer 在局部 atom 窗口上更新 atom latent
- 通过 `atom_to_token` 把 atom latent 聚合到 token latent
- 融合 ESM layer-weighted 表征后进入 residue trunk
- 将 token latent broadcast 回 atom，经过 atom decoder transformer 和 final layer 输出 velocity

## 构造参数

- `hidden_size=1152`
- `num_heads=16`
- `atom_num_heads=4`
- `output_channels=3`
- `atom_hidden_size_enc=256`
- `atom_hidden_size_dec=256`
- `atom_n_queries_enc=32`
- `atom_n_keys_enc=128`
- `atom_n_queries_dec=32`
- `atom_n_keys_dec=128`
- `esm_model="esm2_3B"`
- `esm_dropout_prob=0.0`
- `use_atom_mask=False`
- `use_length_condition=True`

## 输出约定

- `predict_velocity`: `(B, N_atom, 3)`
- `latent`: `(B, N_token, hidden_size)`

如果有明确边界条件，也写在这里：

- `atom_to_token` 形状必须是 `(B, N_atom, N_token)`
- `feats["esm_s"]` 的层数和 hidden 维必须与 `esm_model_dict[esm_model]` 对齐
- `ref_atom_name_chars` 源码中 reshape 为 `(B, N_atom, 4 * 64)`
- encoder / decoder 的 atom local attention mask 由 `atom_n_queries_* / atom_n_keys_*` 生成

## 典型调用位置

- `SimpleFold(pl.LightningModule)` 的 flow matching 训练 step
- SimpleFold sampler 中的 velocity model
- examples/biosciences/simplefold 的本地推理和训练配置

## 典型参数

- SimpleFold 默认 atom local window：
  - encoder: `atom_n_queries_enc=32`, `atom_n_keys_enc=128`
  - decoder: `atom_n_queries_dec=32`, `atom_n_keys_dec=128`
- 模型规模不要只改 `hidden_size`，应优先沿用 example/config 中成套 architecture 配置
- 契约层目标调用：
  - `OneTransformer(style="SimpleFoldFoldingDiT", ...)`

## 风险点

- `style="SimpleFoldFoldingDiT"` 是 skill 契约归一名，不表示当前源码已经在 `OneTransformer` registry 中可直接实例化
- SimpleFold 依赖 ESM 条件，缺少 `esm_s` 时不能只靠 FASTA token 直接 forward
- `atom_to_token` 同时参与 atom 聚合和 token broadcast，维度错会让结构语义整体错位
- `atom_feat_dim` 中有原子特征拼接维度假设，新增特征必须同步改投影层
- 该组件输出 velocity，不是最终坐标；坐标来自 sampler 对速度场积分

## 源码锚点

- `./onescience/src/onescience/models/simplefold/torch/architecture.py`
- `./onescience/src/onescience/models/simplefold/simplefold.py`
- `./onescience/src/onescience/models/simplefold/torch/sampler.py`
- `./onescience/src/onescience/models/simplefold/flow.py`
