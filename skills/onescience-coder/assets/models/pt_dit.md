# Model Card: PT-DiT

## 基本信息

- 模型名：`PT-DiT`
- 任务类型：`蛋白质序列-结构协同生成 / ProToken diffusion transformer`
- 当前状态：`stable`
- 主实现文件：`./onescience/src/onescience/flax_models/Pt_DiT/model/diffusion_transformer.py`

## 模型定位

PT-DiT 是基于 ProToken 的蛋白质序列与结构协同生成模型。它把结构 ProToken embedding 与氨基酸 embedding 拼成 token latent，通过 JAX/Flax Diffusion Transformer 采样兼容的序列/结构表示。

补充说明：

- 它不是传统序列到结构预测，也不是 ProteinMPNN 的结构到序列 inverse folding
- 它依赖 `ProToken` encoder/decoder、`protoken_emb.pkl`、`aatype_emb.pkl` 和 PT-DiT checkpoint
- example 中 `de_novo_design.py` 展示了 de novo co-design，并可调用 ProToken decoder 输出 PDB
- 该模型不走 OneScience `One*` wrapper，属于 JAX/Flax 生信设计工具链

## 输入定义

- `DiffusionTransformer.__call__` 输入：
  - `tokens`: `(B, T, C)`
  - `tokens_mask`: `(B, T)`
  - `time`: `(B,)`
  - `label`: optional `(B,)`
  - `force_drop_ids`: optional
  - `tokens_rope_index`: `(B, T)`
- de novo example 输入：
  - `nres`
  - `nsample_per_device`
  - `protoken_emb.pkl`
  - `aatype_emb.pkl`
  - `PT_DiT_params_*.pkl`
  - `protoken_params_*.pkl`
- 采样初始化：
  - `x`: `(Batch, N_res, protoken_emb_dim + aatype_emb_dim)`
  - `seq_mask`: `(Batch, N_res)`
  - `residue_index`: `(Batch, N_res)`

## 输出定义

- `DiffusionTransformer` 输出：
  - 与输入 `tokens` 相同最后维度的 noise / residual prediction
- example 输出：
  - `embedding`
  - `seq_mask`
  - `residue_index`
  - `protoken_indexes`
  - `aatype_indexes`
  - `result.pkl`
  - `result_flatten.pkl`
- 可选解码：
  - 调用 `onescience.flax_models.protoken.scripts.decode_structure`
  - 输出 PDB 结构

## 主干结构

- `TimestepEmbedder`
  - sinusoidal timestep embedding + MLP
- `LabelEmbedder`
  - 可选 classifier-free guidance 标签嵌入
- `DiffusionTransformerBlock`
  - adaLN conditioned attention + transition
- `DiffusionTransformerOutput`
  - conditioned norm + projection 回原始 embedding 维度
- `GaussianDiffusion`
  - beta schedule、`q_sample`、`p_mean_variance`、DDIM helper
- example `DeNovoDesign`
  - 加载 embeddings / ckpt
  - pmap denoise / q_sample / index_from_embedding
  - nearest codebook embedding clamping

## 主要依赖组件

- `DiffusionTransformer`
- `DiffusionTransformerBlock`
- `GaussianDiffusion`
- `TimestepEmbedder`
- `LabelEmbedder`
- `ProToken VQ_Decoder / Protein_Decoder`
- `protoken_emb.pkl`
- `aatype_emb.pkl`

## 主要 Shape 变化

- ProToken id -> `protoken_emb`: `(N_res, D_protoken)`
- amino acid id -> `aatype_emb`: `(N_res, D_aa)`
- concat latent: `(B, N_res, D_protoken + D_aa)`
- DiT hidden: `(B, N_res, hidden_size)`
- output latent: `(B, N_res, D_protoken + D_aa)`
- nearest embedding lookup -> `protoken_indexes`, `aatype_indexes`

## 默认关键参数

- example `num_diffusion_timesteps=500`
- example `nres=256`
- example `nsample_per_device=8`
- default ckpt:
  - `../ckpts/PT_DiT_params_2000000.pkl`
  - `../ckpts/protoken_params_100000.pkl`
- flash attention 要求序列长度 `NRES` 为 128 的倍数；可在配置中关闭

## 常见修改点

- 改生成长度：优先改 `--nres`，并同步确认 ProToken decoder 的 `padding_len`
- 改采样规模：改 `--nsample_per_device`，注意设备数会影响总 batch
- 只生成 token latent：不设置 `--decode_structures`
- 需要 PDB：设置 `--decode_structures` 并保证 ProToken checkpoint 可用
- 做上下文补全 / RePaint：优先看 `example_scripts/repaint.ipynb`

## 风险点

- PT-DiT 依赖 ProToken 结构词表，不能只提供普通 FASTA 或 PDB 直接训练
- `protoken_emb.pkl` 和 `aatype_emb.pkl` 的维度必须与 checkpoint 中 indicator / model 参数一致
- `tokens_rope_index` 不应省略；源码中会调用 `.astype(jnp.int32)`
- 多设备 pmap 要求 batch 能按设备数整除
- 生成结果仍需要 ProToken decoder 或后续结构评估，不等于已完成实验可用蛋白设计

## 推荐检索顺序

1. 先看本模型卡
2. 再看 `flax_models/Pt_DiT/README.md`
3. 再看 `model/diffusion_transformer.py` 与 `train/schedulers.py`
4. 若涉及 de novo 生成，读 `examples/biosciences/pt_dit/example_scripts/de_novo_design.py`
5. 若涉及结构解码，继续看 `protoken.md`

## 组件契约入口

- `../contracts/ptditcomponents.md`
- 若任务是结构 token 化或 PDB 重建，再读 `../contracts/protokencomponents.md`

## 源码锚点

- `./onescience/src/onescience/flax_models/Pt_DiT/model/diffusion_transformer.py`
- `./onescience/src/onescience/flax_models/Pt_DiT/train/schedulers.py`
- `./onescience/src/onescience/flax_models/Pt_DiT/README.md`
- `./onescience/examples/biosciences/pt_dit/example_scripts/de_novo_design.py`
- `./onescience/examples/biosciences/pt_dit/configs/dit_config.py`
- `./onescience/examples/biosciences/pt_dit/configs/global_config.py`
