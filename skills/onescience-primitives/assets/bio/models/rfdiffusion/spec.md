# architecture_overview

RFdiffusion 是 OneScience 中面向蛋白质设计的骨架扩散生成模型，核心目标是在 contig、motif、binder hotspot、symmetry 或 partial diffusion 条件下生成蛋白质骨架，而不是从序列直接预测全原子结构或为骨架设计序列。

补充说明：

- 它适合无条件单体生成、基序支架、对称性设计、靶点结合蛋白设计和围绕已有结构的 partial diffusion
- 训练和推理代码应以 `onescience.models.rfdiffusion` 中的模型、扩散与采样接口为基础构建
- 输出骨架后，通常需要再接 ProteinMPNN / FastRelax / AF2 类筛选流程完成序列设计与评估

# parameter_scale

- `model.n_extra_block=4`
- `model.n_main_block=32`
- `model.n_ref_block=4`
- `model.d_msa=256`
- `model.d_pair=128`
- `diffuser.T=50`
- `diffuser.partial_T=null`
- `inference.num_designs=10`
- `inference.model_directory_path="${oc.env:ONESCIENCE_MODELS_DIR}/RFdiffusion/models"`

# architecture_structure

- `MSA_emb`
  - 编码 latent MSA、sequence 和 residue index
- `Extra_emb`
  - 编码 full / extra MSA
- `Recycling`
  - 把上一轮 `msa/pair/state` 和当前坐标反馈到输入
- `Templ_emb`
  - 注入 template / timestep / motif 相关条件
- `IterativeSimulator`
  - RoseTTAFold 风格 iterative structure track，内部含 MSA、pair、SE3 更新
- 预测头：
  - `DistanceNetwork`
  - `MaskedTokenNetwork`
  - `ExpResolvedNetwork`
  - `LDDTNetwork`

# input_schema

- 推理配置入口：
  - `contigmap.contigs`
  - `inference.input_pdb`
  - `inference.output_prefix`
  - `inference.num_designs`
  - `inference.ckpt_override_path`
  - `ppi.hotspot_res`
  - `diffuser.partial_T`
  - `contigmap.inpaint_seq`
  - `contigmap.inpaint_str`
  - `contigmap.provide_seq`
  - `inference.symmetry`
  - `potentials.guiding_potentials`
- `RoseTTAFoldModule.forward` 内部输入：
  - `msa_latent`
  - `msa_full`
  - `seq`
  - `xyz`
  - `idx`
  - `t`
  - `t1d`, `t2d`
  - `xyz_t`, `alpha_t`
  - recycling 输入：`msa_prev`, `pair_prev`, `state_prev`
  - 控制项：`return_raw`, `return_full`, `return_infer`, `use_checkpoint`, `motif_mask`, `i_cycle`, `n_cycle`

# output_schema

- 推理文件输出：
  - `.pdb`: 最终预测骨架；设计残基通常以 Glycine 输出，不包含可靠侧链
  - `.trb`: contig、完整配置、输入输出残基映射和 inpaint 信息
  - `traj/`: 扩散轨迹 PDB，包括 `pX0` 与 `Xt-1`
- `RoseTTAFoldModule.forward(return_raw=True)`：
  - `msa[:, 0]`, `pair`, `xyz`, `state`, `alpha_s[-1]`
- `RoseTTAFoldModule.forward(return_infer=True)`：
  - `msa[:, 0]`, `pair`, `xyz`, `state`, `alpha_s[-1]`, `logits_aa`, `pred_lddt`
- 默认 forward：
  - `logits`, `logits_aa`, `logits_exp`, `xyz`, `alpha_s`, `lddt`

# shape_transformations

- `msa_latent`: `B, N, L, ...`
- `msa_full`: `B, N_extra, L, ...`
- `seq`: `B, L`
- `xyz`: `B, L, atom, 3`
- trunk pair: `B, L, L, d_pair`
- iterative simulator 结构输出：
  - rotation `R`
  - translation `T`
  - torsion / angle `alpha_s`
- 默认 forward 的 `xyz`: `N_block, B, L, atom, 3` 风格中间骨架序列

# key_dependencies

- `rfdiffusion_components`
- `se3_transformer_components`

# common_modification_points

- 无条件生成：优先改 `contigmap.contigs=[100-200]` 这类长度范围
- motif scaffolding：优先改 `inference.input_pdb` 与 `contigmap.contigs`
- binder design：优先改目标链 contig、binder 长度与 `ppi.hotspot_res`
- partial diffusion：优先改 `diffuser.partial_T`，并保证 contig 长度与输入结构长度一致
- 使用特殊任务权重时，优先通过 `inference.ckpt_override_path` 指定，不要手动改模型结构

# implementation_risks

- RFdiffusion 生成的是骨架，不是完整侧链结构；设计残基输出为 Glycine 时需要后续序列设计
- 推理脚本会按输入特征自动选择 checkpoint；不支持该输入类型的 checkpoint 可能直接崩溃
- 一般不建议在推理时随意修改 `model`、`preprocess` 或 `diffuser` 中与训练强绑定的参数
- partial diffusion 要求输入结构长度和 contig 设计长度匹配，否则新增残基无法被正确加噪
- binder design 对目标裁剪、热点残基选择和后续筛选非常敏感，不能只看单条 PDB 输出判断成功
- 首次运行可能需要计算并缓存 IGSO3 schedule

# code_references

- `{onescience_path}/onescience/src/onescience/models/rfdiffusion/RoseTTAFoldModel.py`
- `{onescience_path}/onescience/src/onescience/models/rfdiffusion/Track_module.py`
- `{onescience_path}/onescience/src/onescience/models/rfdiffusion/Embeddings.py`
- `{onescience_path}/onescience/src/onescience/models/rfdiffusion/SE3_network.py`
- `{onescience_path}/onescience/src/onescience/models/rfdiffusion/diffusion.py`
- `{onescience_path}/onescience/src/onescience/utils/rfdiffusion/inference/model_runners.py`
