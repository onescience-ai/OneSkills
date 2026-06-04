# Contract: PTDiTComponents

## 基本信息

- 组件名：`PTDiTDiffusionTransformer / PTDiTGaussianDiffusion`
- 所属模块族：`transformer / diffusion`
- 统一入口：`OneTransformer / OneDiffusion`
- 注册名：`style="PTDiTDiffusionTransformer"`, `style="PTDiTGaussianDiffusion"`
- 注册状态：`contract_only`

## 组件职责

PT-DiT 组件负责在 ProToken + amino acid embedding latent 上执行条件扩散去噪，用于蛋白质序列与结构 token 的协同生成、补全和 latent 操作。

补充说明：

- 契约层把 DiT 主干收束到 `OneTransformer`，把 Gaussian diffusion schedule 收束到 `OneDiffusion`
- 源码当前仍是 JAX/Flax 实现，进入 PyTorch `One*` 体系前需要补适配层
- 它的输入是 embedding latent，不是 FASTA token、PDB atom37、OpenFold batch 或 Protenix feature dict
- PT-DiT 与 ProToken 强耦合，通常需要同时读取 `protokencomponents.md`

## One* 归一映射

| 源码组件 | 所属模块族 | 统一入口 | 注册名 |
| --- | --- | --- | --- |
| `DiffusionTransformer / DiffusionTransformerBlock` | `transformer` | `OneTransformer` | `style="PTDiTDiffusionTransformer"` |
| `GaussianDiffusion` | `diffusion` | `OneDiffusion` | `style="PTDiTGaussianDiffusion"` |

## 支持输入

- 2D 输入：`not_applicable`
- 3D 输入：`not_applicable`
- `DiffusionTransformer.__call__`：
  - `tokens`: `(B, T, C)`
  - `tokens_mask`: `(B, T)`
  - `time`: `(B,)`
  - `label`: optional `(B,)`
  - `force_drop_ids`: optional
  - `tokens_rope_index`: `(B, T)`
- `GaussianDiffusion`：
  - `x_start`, `x_t`, `eps`: 同形状 latent
  - `t`: integer timestep vector
- example sampling：
  - `x`: `(Batch, N_res, D_protoken + D_aa)`
  - `seq_mask`: `(Batch, N_res)`
  - `residue_index`: `(Batch, N_res)`

内部统一做法：

- `TimestepEmbedder` 将 integer timestep 编码到 hidden condition
- 可选 `LabelEmbedder` 做 classifier-free guidance
- 输入 latent 先投影到 `hidden_size`
- 多层 `DiffusionTransformerBlock` 执行 adaLN attention + transition
- 输出层投影回原始 latent 维度，作为噪声预测或 denoising step 输入
- `GaussianDiffusion.p_mean_variance` 从 `x_t` 和预测噪声得到 posterior mean/variance
- example 用最近邻 embedding 把连续 latent clamp 回 ProToken / AA codebook

## 构造参数

- `DiffusionTransformer`
  - `config`
  - `global_config`
- 常见 config 字段：
  - `hidden_size`
  - `n_iterations`
  - `time_embedding.frequency_embedding_size`
  - `emb_label_flag`
  - `dit_block.attention`
  - `dit_block.transition`
  - `dit_block.adaLN`
  - `dit_output`
- `GaussianDiffusion`
  - `num_diffusion_timesteps`

## 输出约定

- `DiffusionTransformer`：
  - output latent: `(B, T, C)`，最后维与输入 `tokens` 一致
- `GaussianDiffusion.p_mean_variance`：
  - `model_mean`
  - `model_variance`
  - `model_log_variance`
- example final output：
  - `embedding`
  - `protoken_indexes`
  - `aatype_indexes`
  - `result.pkl`

如果有明确边界条件，也写在这里：

- `tokens_rope_index` 源码中会调用 `.astype(jnp.int32)`，不要传 `None`
- `eps.shape == x_start.shape`，`x_t.shape == eps.shape`
- pmap 场景中 batch 需要能被设备数整除
- ProToken embedding 维度与 AA embedding 维度要与 checkpoint 参数一致

## 典型调用位置

- `examples/biosciences/pt_dit/example_scripts/de_novo_design.py`
- PT-DiT denoise step / q_sample / latent design notebook
- ProToken decode structure 后处理

## 典型参数

- `num_diffusion_timesteps=500`
- `nres=256`
- `nsample_per_device=8`
- `n_eq_steps=50`
- `phasing_time=250`
- 契约层目标调用：
  - `OneTransformer(style="PTDiTDiffusionTransformer", ...)`
  - `OneDiffusion(style="PTDiTGaussianDiffusion", ...)`

## 风险点

- 上述 `style` 是 skill 契约归一名，不表示当前源码已经在对应 `One*` registry 中可直接实例化
- PT-DiT 输出的是 latent / code indexes，不是直接全原子坐标
- 与 ProToken checkpoint、embedding 文件、padding length 不匹配会导致 shape 或语义错误
- FlashAttention 配置要求 `NRES` 为 128 的倍数；不满足时需关闭或改长度
- 不能把 ProteinMPNN 或 RFdiffusion 输出直接作为 PT-DiT latent，必须先经过 ProToken/embedding 协议

## 源码锚点

- `./onescience/src/onescience/flax_models/Pt_DiT/model/diffusion_transformer.py`
- `./onescience/src/onescience/flax_models/Pt_DiT/train/schedulers.py`
- `./onescience/src/onescience/flax_models/Pt_DiT/model/transformer.py`
- `./onescience/examples/biosciences/pt_dit/example_scripts/de_novo_design.py`
- `./onescience/src/onescience/flax_models/Pt_DiT/README.md`
