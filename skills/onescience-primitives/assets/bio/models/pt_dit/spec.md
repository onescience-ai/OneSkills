# component_info

PT-DiT 是基于 ProToken 的蛋白序列-结构协同生成组件，核心功能是在 ProToken 结构词表与氨基酸词表构成的 latent 空间中执行 diffusion transformer 采样，并将结果映射回 `protoken_indexes` 和 `aatype_indexes`；它不是传统序列到结构预测，也不是 ProteinMPNN 式 backbone-to-sequence inverse folding。

# architecture_overview

PT-DiT 生成路线:
  ProToken id
    -> `protoken_emb`
  amino acid id
    -> `aatype_emb`
  concat latent
    -> GaussianDiffusion
    -> DiffusionTransformer
    -> nearest embedding lookup
    -> `protoken_indexes` + `aatype_indexes`
    -> optional ProToken decode
    -> PDB

# parameter_scale

- example `num_diffusion_timesteps=500`。
- example `nres=256`。
- example `nsample_per_device=8`。
- default ckpt:
  - `../ckpts/PT_DiT_params_2000000.pkl`。
  - `../ckpts/protoken_params_100000.pkl`。
- flash attention 要求序列长度 `NRES` 为 `128` 的倍数；可在配置中关闭。

# architecture_structure

- `TimestepEmbedder`: sinusoidal timestep embedding + MLP。
- `LabelEmbedder`: 可选 classifier-free guidance 标签嵌入。
- `DiffusionTransformerBlock`: adaLN conditioned attention + transition。
- `DiffusionTransformerOutput`: conditioned norm + projection 回原始 embedding 维度。
- `GaussianDiffusion`: beta schedule、`q_sample`、`p_mean_variance`、DDIM helper。
- `DeNovoDesign`: 加载 embeddings / checkpoint，执行 pmap denoise、q_sample、index_from_embedding 和 nearest codebook clamping。

# input_schema

- `DiffusionTransformer.__call__` 输入:
  - `tokens`: `(B, T, C)`。
  - `tokens_mask`: `(B, T)`。
  - `time`: `(B,)`。
  - `label`: optional `(B,)`。
  - `force_drop_ids`: optional。
  - `tokens_rope_index`: `(B, T)`。
- de novo example 输入:
  - `nres`。
  - `nsample_per_device`。
  - `protoken_emb.pkl`。
  - `aatype_emb.pkl`。
  - `PT_DiT_params_*.pkl`。
  - `protoken_params_*.pkl`。
- 采样初始化:
  - `x`: `(Batch, N_res, protoken_emb_dim + aatype_emb_dim)`。
  - `seq_mask`: `(Batch, N_res)`。
  - `residue_index`: `(Batch, N_res)`。

# output_schema

- `DiffusionTransformer` 输出:
  - 与输入 `tokens` 最后一维相同的 noise / residual prediction。
- example 输出:
  - `embedding`。
  - `seq_mask`。
  - `residue_index`。
  - `protoken_indexes`。
  - `aatype_indexes`。
  - `result.pkl`。
  - `result_flatten.pkl`。
- 可选结构解码:
  - 调用 ProToken decode。
  - 输出 PDB 结构。

# shape_transformations

- ProToken id -> `protoken_emb`: `(N_res, D_protoken)`
- amino acid id -> `aatype_emb`: `(N_res, D_aa)`
- concat latent: `(B, N_res, D_protoken + D_aa)`
- DiT hidden: `(B, N_res, hidden_size)`
- output latent: `(B, N_res, D_protoken + D_aa)`
- nearest embedding lookup -> `protoken_indexes`, `aatype_indexes`

# key_dependencies

- `DiffusionTransformer`
- `DiffusionTransformerBlock`
- `GaussianDiffusion`
- `TimestepEmbedder`
- `LabelEmbedder`
- `ProToken VQ_Decoder`
- `Protein_Decoder`
- `protoken_emb.pkl`
- `aatype_emb.pkl`

# common_modification_points

- 改生成长度优先改 `--nres`，并同步确认 ProToken decoder 的 `padding_len`。
- 改采样规模优先改 `--nsample_per_device`，注意设备数影响总 batch。
- 只生成 token latent 时不设置 `--decode_structures`。
- 需要 PDB 时设置 `--decode_structures` 并保证 ProToken checkpoint 可用。
- 上下文补全 / RePaint 优先参考 example notebook。

# implementation_risks

- PT-DiT 依赖 ProToken 结构词表，不能只提供普通 FASTA 或 PDB 直接训练。
- `protoken_emb.pkl` 与 `aatype_emb.pkl` 维度必须和 checkpoint/model config 一致。
- `tokens_rope_index` 不应省略。
- 多设备 pmap 要求 batch 能按设备数整除。
- 生成结果仍需 ProToken decoder 或后续结构评估，不等于实验可用蛋白设计。

# code_references

- `{onescience_path}/onescience/src/onescience/flax_models/Pt_DiT/model/diffusion_transformer.py`
- `{onescience_path}/onescience/src/onescience/flax_models/Pt_DiT/train/schedulers.py`
- `{onescience_path}/onescience/src/onescience/flax_models/Pt_DiT/README.md`
- `{onescience_path}/onescience/examples/biosciences/pt_dit/example_scripts/de_novo_design.py`
- `{onescience_path}/onescience/examples/biosciences/pt_dit/configs/dit_config.py`
- `{onescience_path}/onescience/examples/biosciences/pt_dit/configs/global_config.py`
