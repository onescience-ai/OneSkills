# component_info

OpenFold 是 AF2-style folding 模型原语，定位于基于 MSA、template 和 recycling 协议的蛋白结构预测；它的关键特征是以专用 feature dict 为输入，经 Evoformer 更新 MSA/pair/single 表征，再由 StructureModule 生成 atom37 坐标。

# architecture_overview

OpenFold 是 OneScience 中的 AlphaFold2 / OpenFold 风格结构预测实现，适合已有 AF2 特征流水线、MSA、template 和 recycling 协议的蛋白质结构预测任务。

补充说明：

- 模型类名是 `AlphaFold`
- 支持 monomer、multimer 与 seq embedding 相关配置分支
- 它与 Protenix 的主要差异是：OpenFold 使用 Evoformer + StructureModule 的 AF2 协议，Protenix 使用 Pairformer + diffusion 的 AF3 风格协议

# parameter_scale

- 具体参数来自 `onescience.configs.bio.openfold.config.model_config(...)`
- `config_preset` 决定 monomer / multimer / seq 模式
- `long_sequence_inference`、`use_deepspeed_evoformer_attention` 会影响推理内存与 attention 实现
- tracing 需要 `config.data.predict.fixed_size=True`

# architecture_structure

- InputEmbedder / InputEmbedderMultimer
  - 生成 MSA representation 与 pair representation
- RecyclingEmbedder
  - 把上一轮结构、MSA、pair 信息注入下一轮
- Template stack
  - 处理 template pair / template angle 等特征
- ExtraMSAStack
  - 处理 extra MSA
- EvoformerStack
  - 交替更新 MSA、pair、single 表征
- StructureModule
  - IPA 和结构更新，恢复 atom 坐标
- Aux heads
  - 按配置输出 distogram、pLDDT、masked MSA 等辅助头

# input_schema

- 主输入：`batch: dict[str, Tensor]`
- 每个 feature 的最后一维是 recycling 维度，forward 中逐 cycle 取 `t[..., cycle_no]`
- 核心字段：
  - `aatype`: `[*, N_res]`
  - `target_feat`: `[*, N_res, C_tf]`
  - `residue_index`: `[*, N_res]`
  - `msa_feat`: `[*, N_seq, N_res, C_msa]`
  - `seq_mask`: `[*, N_res]`
  - `msa_mask`: `[*, N_seq, N_res]`
  - `pair_mask`: `[*, N_res, N_res]`
  - `extra_msa_mask`: `[*, N_extra, N_res]`
  - template 相关字段：`template_aatype`, `template_all_atom_positions`, `template_all_atom_mask`, `template_pseudo_beta`, `template_pseudo_beta_mask`

# output_schema

- 主结构输出：
  - `final_atom_positions`
  - `final_atom_mask`
  - `final_affine_tensor`
- 中间表征：
  - `msa`
  - `pair`
  - `single`
- 辅助输出：
  - `num_recycles`
  - aux heads 输出，具体取决于配置

# shape_transformations

- `msa_feat`: `[*, N_seq, N_res, C_msa]`
- MSA embedding: `[*, N_seq, N_res, C_m]`
- Pair embedding: `[*, N_res, N_res, C_z]`
- Single representation: `[*, N_res, C_s]`
- Structure output atom37: `[*, N_res, 37, 3]`
- recycling 维度在 outer forward 中逐轮消去

# key_dependencies

- `InputEmbedder`
- `InputEmbedderMultimer`
- `RecyclingEmbedder`
- `ExtraMSAStack`
- `EvoformerStack`
- `StructureModule`

# common_modification_points

- 接入新数据时，优先复用 OpenFold feature pipeline，不要只生成 `aatype`
- 改 monomer/multimer 时，需要同时确认 input embedder、template searcher、feature processor 和配置 preset
- 若启用 seq embedding mode，alignment runner 只用于 template，序列表征来自 embedding generator
- 修改 recycling 次数或 fixed-size tracing 时，要同步检查 batch 最后一维和 padding

# implementation_risks

- OpenFold 的 batch 协议与 `onescience.datapipes.biology.ProteinDataset` 的通用特征不是一回事，需要专门 adapter 或 OpenFold feature pipeline
- `examples/biosciences/openfold/run_pretrained_openfold.py` 会使用 alignment、template、database 工具链，不能离线假设所有特征已存在
- monomer 和 multimer 使用不同 template searcher 与 input embedder，不能只改模型配置名

# code_references

- `{onescience_path}/onescience/src/onescience/models/openfold/model.py`
- `{onescience_path}/onescience/src/onescience/models/openfold/embedders.py`
- `{onescience_path}/onescience/src/onescience/models/openfold/evoformer.py`
- `{onescience_path}/onescience/src/onescience/models/openfold/structure_module.py`
- `{onescience_path}/onescience/examples/biosciences/openfold/run_pretrained_openfold.py`
