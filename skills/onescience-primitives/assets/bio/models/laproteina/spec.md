# component_info

LaProteina 是蛋白生成模型组件，主要负责基于 flow matching 从噪声采样蛋白结构表示，并将生成结果格式化为 atom37 坐标和残基类型后写出 PDB；它同时包含训练、推理、motif 条件、partial autoencoder、结构指标和 designability 评估工具。

# architecture_overview

LaProteina 的核心是 `Proteina` LightningModule：

- 使用 `ProductSpaceFlowMatcher` 管理多个生成模态
- 默认模态包括 `bb_ca` 和 `local_latents`
- `bb_ca` 表示 CA 骨架坐标
- `local_latents` 表示由 autoencoder 学到的局部结构 latent
- 主网络为 `LocalLatentsTransformer` 或 motif 版本 `LocalLatentsTransformerMotifUidx`
- 采样阶段通过 `full_simulation` 从噪声逐步积分到结构样本

模型定位更接近蛋白骨架/结构生成器，而不是给定序列的折叠预测器。

# parameter_scale

- 常用网络配置名：`local_latents_score_nn_160M`
- Transformer 层数 `nlayers=14`
- token 维度 `token_dim=768`
- 注意力头数 `nheads=12`
- 条件向量维度 `dim_cond=256`
- 序列位置 embedding 维度 `idx_emb_dim=256`
- 时间 embedding 维度 `t_emb_dim=256`
- pair 表征维度 `pair_repr_dim=256`
- noisy pair distance bin 数 `xt_pair_dist_dim=30`
- self-conditioning pair distance bin 数 `x_sc_pair_dist_dim=30`
- 相对序列间隔 bin 数 `seq_sep_dim=127`
- 推理默认 `nsteps=20`，训练/正式采样配置可使用更大步数
- 无条件示例默认 `nres_lens=[100]`、`nsamples=2`、`max_nsamples_per_batch=1`

# architecture_structure

数据模态
  bb_ca
    -> CA 坐标: (Batch, N_res, 3)
    -> RDNFlowMatcher
  local_latents
    -> autoencoder latent: (Batch, N_res, latent_dim)
    -> RDNFlowMatcher

特征工厂
  noisy sample xt
    -> xt_bb_ca
    -> xt_local_latents
  self-conditioning
    -> x_sc_bb_ca
    -> x_sc_local_latents
  optional conditioning
    -> optional_ca_coors_nm_seq_feat
    -> optional_res_type_seq_feat
    -> motif features

主干网络
  sequence features
    -> token representation
  pair features
    -> pair representation
  LocalLatentsTransformer
    -> attention and transition blocks
    -> optional pair update / triangular multiplication
    -> output parameterization for bb_ca and local_latents

采样格式化
  generated product-space sample
    -> sample_formatting
    -> atom37 coordinates
    -> residue type tensor
    -> PDB writer

# input_schema

- 推理配置入口：
  - `--config_name`: Hydra 配置名，默认 `inference_base`
  - `--config_number`: 数字配置编号，默认 `-1`
  - `--job_id`: 多 job 切分 ID，默认 `0`
  - `--config_subdir`: 可选配置子目录
  - `--data_path`: 可选数据根目录，会写入 `DATA_PATH`
- 关键配置字段：
  - `ckpt_path`: 模型 checkpoint 目录
  - `ckpt_name`: 模型 checkpoint 文件名
  - `autoencoder_ckpt_path`: autoencoder checkpoint
  - `generation.args.nsteps`: 采样步数
  - `generation.args.self_cond`: 是否使用 self-conditioning
  - `generation.args.guidance_w`: guidance 权重
  - `generation.args.ag_ratio`: autoguidance 比例
  - `generation.dataset.nlens_cfg.nres_lens`: 指定生成长度
  - `generation.dataset.nsamples`: 每个长度或条件生成样本数
  - `generation.dataset.motif_task_name`: motif 任务名

# output_schema

- `Proteina.predict_step` 输出：
  - 生成样本列表
  - 每个样本为 `(coors_atom37, residue_type)`
  - `coors_atom37`: `(N_res, 37, 3)`
  - `residue_type`: `(N_res,)`
- 常规推理落盘：
  - 每个样本一个目录
  - PDB 文件名包含 `job_id`、长度、样本 ID 和 rank
- motif 推理落盘：
  - PDB 文件名包含 `job_id`、样本 ID 和 motif 任务名
  - 可附带 motif 信息 CSV
- 评估可生成 designability、codesignability、novelty、FID、motif RMSD 等指标表。

# shape_transformations

训练/采样批次
  coords: (Batch, N_res, 37, 3)
    -> mask: (Batch, N_res)
    -> clean sample x_1

flow matching
  x_0: reference noise
  x_1: data sample
  t: interpolation time
    -> x_t: noisy/interpolated sample
    -> nn_out: velocity or clean-sample parameterization

采样
  noise sample
    -> full_simulation(nsteps)
    -> gen_samples by data mode
    -> atom37: (Batch, N_res, 37, 3)
    -> residue_type: (Batch, N_res)
    -> mask: (Batch, N_res)

无条件长度采样
  nres_lens: [100]
    -> GenDataset
    -> batch["nres"]
    -> generated PDB length 100

# key_dependencies

- `Proteina`
- `ProductSpaceFlowMatcher`
- `RDNFlowMatcher`
- `LocalLatentsTransformer`
- `LocalLatentsTransformerMotifUidx`
- `FeatureFactory`
- `AutoEncoder`
- `GenDataset`
- `PDBDataset`
- `MotifMaskTransform`
- `ExtractMotifCoordinatesTransform`
- `write_prot_to_pdb`

# common_modification_points

- 无条件生成优先修改 `generation.dataset.nlens_cfg.nres_lens`、`nsamples` 和 `generation.args.nsteps`。
- motif scaffolding 优先选择 motif 配置，并修改 `motif_task_name`、motif PDB、contig 或 atom selection mode。
- 需要更高质量时增加 `nsteps`、启用 self-conditioning，或使用带 triangular pair update 的 checkpoint。
- 需要改变结构条件特征时修改 `feats_seq`、`feats_pair_repr` 和 motif 特征，不要直接改 PDB 写出逻辑。
- 显存不足时先减小 `max_nsamples_per_batch`、缩短生成长度或减少并行设备。
- 训练新模型时优先调整 LoRA、EMA、学习率、验证间隔和数据选择器。

# implementation_risks

- 推理代码要求 CUDA 可用；缺 GPU 会在 setup 阶段断言失败。
- `ckpt_name`、`ckpt_path` 和 `autoencoder_ckpt_path` 必须匹配，否则结构 latent 维度可能不一致。
- motif 配置对 residue numbering、chain ID、atom selection mode 非常敏感。
- `strict_feats=False` 会用默认值填补缺失特征，便于运行但可能掩盖数据准备问题。
- 生成 PDB 的 residue type 在部分 `bb_ca` 路径下可能是占位类型，不应直接视为最终可表达序列。
- designability 评估依赖外部折叠模型和 GPU，耗时远高于单纯生成。

# code_references

- `{onescience_path}/onescience/src/onescience/models/laproteina`
