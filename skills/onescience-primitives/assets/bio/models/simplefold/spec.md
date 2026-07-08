# component_info

SimpleFold 是生成式蛋白质折叠原语，定位于用通用 Transformer/DiT 与 flow matching 目标进行结构预测；它不依赖 OpenFold/Protenix 的三角注意力或 Pairformer 协议，而是围绕原子特征、token latent、ESM 条件和速度场采样组织模型。

# architecture_overview

SimpleFold 是面向蛋白质折叠的生成式结构预测模型，核心训练目标是 flow matching，主干使用通用 Transformer / DiT 风格结构，而不是 OpenFold / Protenix 中的 Evoformer、Pairformer 或三角注意力堆栈。

补充说明：

- 主要输入对象是已经 token 化和原子级特征化后的蛋白质样本，不是普通 `(x, y)` 或 PyG 图协议
- 推理侧示例提供 FASTA 到结构输出的 CLI 路线，模型内部仍依赖 `feats` 字典中的原子、token、ESM 表征和几何参考特征
- PyTorch 与 MLX 都有 FoldingDiT 实现，OneScience 主训练模块是 `SimpleFold(pl.LightningModule)`

# parameter_scale

- CLI 模型规模：`simplefold_100M`, `simplefold_360M`, `simplefold_700M`, `simplefold_1.1B`, `simplefold_1.6B`, `simplefold_3B`
- 常见推理参数：`num_steps=500`, `tau=0.01`, `nsample_per_protein=1`
- `ema_decay=0.999`
- 默认 ESM 路线：`esm_model="esm2_3B"`
- atom local attention 常见窗口：encoder `n_queries=32, n_keys=128`，decoder `n_queries=32, n_keys=128`

# architecture_structure

- atom feature embedding：把参考坐标、残基类型、分子类型、电荷、元素、原子名等拼成原子特征
- atom encoder transformer：在原子局部窗口上建模，并聚合为 token latent
- ESM 条件融合：对 `esm_s` 的层表征加权组合后投影到 token 维度
- residue trunk：在 token 层运行通用 Transformer / DiT trunk
- atom decoder transformer：把 token latent 广播回原子层，输出坐标速度
- `SimpleFold` LightningModule：负责 EMA、flow path、smooth lDDT / pLDDT 相关训练逻辑与采样调度

# input_schema

- 主干输入：
  - `noised_pos`: `(Batch, N_atom, 3)`
  - `t`: `(Batch,)` 或可广播到 batch 的噪声时间
  - `feats`: token / atom feature dict
- 关键 `feats` 字段：
  - 原子几何：`ref_pos`, `ref_charge`, `ref_space_uid`, `atom_pad_mask`, `ref_element`, `ref_atom_name_chars`
  - atom-token 映射：`atom_to_token`, `atom_to_token_idx`, `max_num_tokens`
  - token 元信息：`mol_type`, `res_type`, `pocket_feature`, `residue_index`, `entity_id`, `asym_id`, `sym_id`
  - 语言模型条件：`esm_s`

# output_schema

- FoldingDiT 输出：
  - `predict_velocity`: `(Batch, N_atom, 3)`
  - `latent`: `(Batch, N_token, hidden_size)`
- `SimpleFold` 训练中用 `predict_velocity` 与 flow matching target 计算损失
- 推理或采样流程会把速度场经 sampler 积分为结构坐标，并可按配置输出 pLDDT

# shape_transformations

- `ref_pos`: `(B, N_atom, 3)`
- `atom_to_token`: `(B, N_atom, N_token)`
- 原子特征投影后：`(B, N_atom, hidden_size)`
- 原子聚合到 token：`(B, N_token, hidden_size)`
- ESM 融合后 token latent：`(B, N_token, hidden_size)`
- token latent 广播回 atom：`(B, N_atom, hidden_size)`
- 速度输出：`(B, N_atom, 3)`

# key_dependencies

- `FoldingDiT`
- `HomogenTrunk`
- `DiTBlock`
- `TransformerBlock`
- `EMSampler`
- `LinearPath`

# common_modification_points

- 更换模型规模时，优先改 example/config 中的 architecture 配置，不要只改 `hidden_size`
- 新数据接入时，先对齐 `feats` 字段，而不是直接把 `ProteinDataset` 的 `aatype/msa` 输出喂给 FoldingDiT
- 修改 atom 特征字段时，要同步检查 `atom_feat_dim` 中硬编码的拼接维度
- 关闭或替换 ESM 条件时，要同步处理 `esm_s_combine`、`esm_s_proj` 和 `esm_cat_proj`

# implementation_risks

- SimpleFold 的训练 / 推理特征协议与 OpenFold、Protenix 不同，不能仅凭都是蛋白质结构预测就互换 datapipe
- 主干需要 `esm_s`，如果上游没有预计算或在线 ESM 表征，需要先补特征生成路径
- `atom_to_token` 是原子到 token 的核心桥接矩阵，维度错会直接破坏 atom 聚合和广播
- examples 中的训练数据准备依赖 mmCIF 处理、tokenize 和配置文件，不能把 FASTA CLI 推理流程误当成训练 datapipe

# code_references

- `{onescience_path}/onescience/src/onescience/models/simplefold/simplefold.py`
- `{onescience_path}/onescience/src/onescience/models/simplefold/torch/architecture.py`
- `{onescience_path}/onescience/src/onescience/models/simplefold/torch/sampler.py`
- `{onescience_path}/onescience/src/onescience/models/simplefold/flow.py`
- `{onescience_path}/onescience/examples/biosciences/simplefold/README.md`
