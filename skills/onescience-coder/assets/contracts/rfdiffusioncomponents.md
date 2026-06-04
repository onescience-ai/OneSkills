# Contract: RFdiffusionComponents

## 基本信息

- 组件名：`RFdiffusionSampler / RFdiffusionRoseTTAFoldModule / RFdiffusionDiffuser`
- 所属模块族：`diffusion / transformer`
- 统一入口：`OneDiffusion / OneTransformer`
- 注册名：`style="RFdiffusionSampler"`, `style="RFdiffusionDiffuser"`, `style="RFdiffusionRoseTTAFoldModule"`
- 注册状态：`contract_only`

## 组件职责

RFdiffusion 组件负责把 contig/PDB/扩散配置转成蛋白骨架采样过程，并在 RoseTTAFold 风格结构轨道中迭代去噪生成骨架。

补充说明：

- 契约层将采样 / 加噪部分收束到 `OneDiffusion`，将 RoseTTAFold 网络主体收束到 `OneTransformer`
- 源码当前仍由 RFdiffusion Hydra runner 和模型工具直接实例化这些对象
- `Sampler` 负责 checkpoint 选择、Hydra 配置合并、contig、potential、symmetry 和 denoiser 初始化
- `RoseTTAFoldModule` 是神经网络主体，`Diffuser` 负责欧氏平移和 SO(3) frame 加噪

## One* 归一映射

| 源码组件 | 所属模块族 | 统一入口 | 注册名 |
| --- | --- | --- | --- |
| `Sampler / SelfConditioning / Denoise` | `diffusion` | `OneDiffusion` | `style="RFdiffusionSampler"` |
| `Diffuser / EuclideanDiffuser / IGSO3` | `diffusion` | `OneDiffusion` | `style="RFdiffusionDiffuser"` |
| `RoseTTAFoldModule / IterativeSimulator` | `transformer` | `OneTransformer` | `style="RFdiffusionRoseTTAFoldModule"` |
| `SE3TransformerWrapper` | `equivariant` | `OneEquivariant` | `style="SE3Transformer"` |

## 支持输入

- 2D 输入：`not_applicable`
- 3D 输入：`not_applicable`
- `RoseTTAFoldModule.forward` 输入：
  - `msa_latent`, `msa_full`
  - `seq`, `xyz`, `idx`, `t`
  - `t1d`, `t2d`, `xyz_t`, `alpha_t`
  - `msa_prev`, `pair_prev`, `state_prev`
  - `motif_mask`
- 推理配置输入：
  - `contigmap.contigs`
  - `inference.input_pdb`
  - `ppi.hotspot_res`
  - `diffuser.partial_T`
  - `inference.symmetry`
  - `potentials.guiding_potentials`

内部统一做法：

- `MSA_emb` 和 `Extra_emb` 生成 seed / extra MSA embedding
- `Recycling` 将上一轮 `msa/pair/state/xyz` 注入当前轮
- `Templ_emb` 注入 template、timestep、motif 和结构条件
- `IterativeSimulator` 按 extra block、main block、refinement block 更新 MSA、pair、frame 和 state
- `SE3TransformerWrapper` 在 structure track 内做 SE(3)-equivariant graph update
- `Diffuser` 分别处理 backbone translation 和 rotation diffusion
- auxiliary heads 输出 distogram、masked AA、experiment resolved 和 LDDT

## 构造参数

- `RoseTTAFoldModule`
  - `n_extra_block`
  - `n_main_block`
  - `n_ref_block`
  - `d_msa`, `d_msa_full`, `d_pair`, `d_templ`
  - `n_head_msa`, `n_head_pair`, `n_head_templ`
  - `d_hidden`, `d_hidden_templ`
  - `d_t1d`, `d_t2d`, `T`
  - `use_motif_timestep`, `freeze_track_motif`
- `Diffuser`
  - `T`, `b_0`, `b_T`
  - `min_sigma`, `max_sigma`
  - `schedule_type`, `so3_schedule_type`, `so3_type`
  - `crd_scale`, `partial_T`

## 输出约定

- `return_raw=True`：
  - `msa[:,0]`, `pair`, `xyz`, `state`, `alpha_s[-1]`
- `return_infer=True`：
  - raw 输出加 `logits_aa`, `pred_lddt`
- 默认 forward：
  - `logits`, `logits_aa`, `logits_exp`, `xyz`, `alpha_s`, `lddt`
- 推理文件：
  - `.pdb`, `.trb`, `traj/`

如果有明确边界条件，也写在这里：

- `motif_mask=True` 表示 motif residue 在 track 中可被冻结
- partial diffusion 的 contig 长度必须与输入结构长度一致
- `Diffuser.diffuse_pose` 会把未 mask 结构居中并按 `crd_scale` 缩放

## 典型调用位置

- `examples/biosciences/RFdiffusion/scripts/run_inference.py`
- `onescience.utils.rfdiffusion.inference.model_runners.Sampler`
- `onescience.utils.rfdiffusion.inference.model_runners.SelfConditioning`
- 需要改等变图结构轨道时，再看 `./se3transformercomponents.md`

## 典型参数

- 默认扩散步数：
  - `diffuser.T=50`
- partial diffusion：
  - `diffuser.partial_T=10` 或 `20` 等任务相关值
- checkpoint 选择：
  - `Base_ckpt.pt`
  - `Complex_base_ckpt.pt`
  - `InpaintSeq_ckpt.pt`
  - `ActiveSite_ckpt.pt`
  - `Complex_beta_ckpt.pt`
- 契约层目标调用：
  - `OneDiffusion(style="RFdiffusionSampler", ...)`
  - `OneDiffusion(style="RFdiffusionDiffuser", ...)`
  - `OneTransformer(style="RFdiffusionRoseTTAFoldModule", ...)`

## 风险点

- 上述 `style` 是 skill 契约归一名，不表示当前源码已经在对应 `One*` registry 中可直接实例化
- RFdiffusion 输出骨架，不能直接当作完成序列和侧链设计
- checkpoint 由输入条件自动选择，手动 override 时必须确认该权重支持当前输入特征
- 对称性、辅助势、motif scaffolding 和 binder design 都依赖 contig 语法，字符串错误会改变任务语义
- 首次推理可能需要生成 IGSO3 schedule cache
- SE(3) 等变层是内部结构轨道组件，普通推理适配不要优先改 `se3_transformer`

## 源码锚点

- `./onescience/src/onescience/models/rfdiffusion/RoseTTAFoldModel.py`
- `./onescience/src/onescience/models/rfdiffusion/Track_module.py`
- `./onescience/src/onescience/models/rfdiffusion/Embeddings.py`
- `./onescience/src/onescience/models/rfdiffusion/SE3_network.py`
- `./onescience/src/onescience/models/rfdiffusion/diffusion.py`
- `./onescience/src/onescience/utils/rfdiffusion/inference/model_runners.py`
