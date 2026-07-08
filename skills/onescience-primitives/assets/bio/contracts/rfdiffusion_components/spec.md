# component_info

`rfdiffusion_components` 是 RFdiffusion 的组件契约，覆盖 `RFdiffusionSampler`、`RFdiffusionRoseTTAFoldModule` 和 `RFdiffusionDiffuser`。原始 contract 中模块族为 `diffusion / transformer`，目标统一入口为 `OneDiffusion / OneTransformer`，注册状态为 `contract_only`。

# purpose

用于把 contig、PDB、扩散配置和设计约束组织成蛋白骨架采样过程，并在 RoseTTAFold 风格结构轨道中迭代去噪生成骨架。适用于 motif scaffolding、binder design、partial diffusion 和对称设计规划；不直接负责序列和侧链设计。

# input_schema

```text
RoseTTAFoldModule.forward:
  msa_latent, msa_full
  seq, xyz, idx, t
  t1d, t2d, xyz_t, alpha_t
  msa_prev, pair_prev, state_prev
  motif_mask

推理配置:
  contigmap.contigs
  inference.input_pdb
  ppi.hotspot_res
  diffuser.partial_T
  inference.symmetry
  potentials.guiding_potentials
```

# output_schema

```text
return_raw=True:
  msa[:,0], pair, xyz, state, alpha_s[-1]

return_infer=True:
  raw outputs
  logits_aa
  pred_lddt

default forward:
  logits, logits_aa, logits_exp
  xyz, alpha_s, lddt

推理文件:
  .pdb, .trb, traj/
```

# parameters

- `RoseTTAFoldModule`: `n_extra_block`、`n_main_block`、`n_ref_block`、`d_msa`、`d_pair`、`d_templ`、`n_head_msa`、`n_head_pair`、`d_hidden`、`d_t1d`、`d_t2d`、`T`。
- `Diffuser`: `T`、`b_0`、`b_T`、`min_sigma`、`max_sigma`、`schedule_type`、`so3_schedule_type`、`so3_type`、`crd_scale`、`partial_T`。
- 常见 checkpoint：`Base_ckpt.pt`、`Complex_base_ckpt.pt`、`InpaintSeq_ckpt.pt`、`ActiveSite_ckpt.pt`、`Complex_beta_ckpt.pt`。

# key_dependencies

- `RoseTTAFoldModel.py`
- `Track_module.py`
- `Embeddings.py`
- `SE3_network.py`
- `diffusion.py`
- `model_runners.py`

# usage_and_risks

Sampler 负责 checkpoint 选择、Hydra 配置合并、contig、potential、symmetry 和 denoiser 初始化；Diffuser 处理 translation 和 SO(3) frame 加噪；RoseTTAFoldModule 执行 embedding、recycling、template 注入和 iterative simulator。`contract_only` 来自原始 contract，表示目标 `style` 不是已确认可直接运行的 `One*` registry 项。contig 字符串、motif mask、partial diffusion 长度和 checkpoint 选择会直接改变设计语义。

# code_references

- `{onescience_path}/onescience/src/onescience/models/rfdiffusion/RoseTTAFoldModel.py`
- `{onescience_path}/onescience/src/onescience/models/rfdiffusion/Track_module.py`
- `{onescience_path}/onescience/src/onescience/models/rfdiffusion/Embeddings.py`
- `{onescience_path}/onescience/src/onescience/models/rfdiffusion/SE3_network.py`
- `{onescience_path}/onescience/src/onescience/models/rfdiffusion/diffusion.py`
- `{onescience_path}/onescience/src/onescience/utils/rfdiffusion/inference/model_runners.py`
