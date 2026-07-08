# component_info

AlphaFold 是 JAX/Haiku 风格的 AF2/AlphaFold-Multimer 结构预测组件，核心功能是把蛋白 FASTA 经过 MSA、template search 和 feature processing 转成模型特征，再由 Evoformer 与 StructureModule 预测三维结构和置信度；保留原版 AF2 推理流水线的配置、参数和数据库依赖，适合复用成熟 AF2/Multimer 推理协议。

# architecture_overview

AlphaFold 的架构定位是 AF2-style folding。模型主体由 `RunModel` 包装 Haiku transform / JIT 后的 `AlphaFold` 网络，内部按 recycling iteration 重复执行 embedding、Evoformer trunk 和结构头。

输入组织:
  FASTA
    -> MSA 搜索
    -> template 搜索
    -> feature processing
    -> FeatureDict

模型主干:
  FeatureDict
    -> EmbeddingsAndEvoformer
    -> EvoformerIteration
    -> StructureModule
    -> confidence heads
    -> PDB / pLDDT / ranking

# parameter_scale

- 模型规模由 `model_preset` 决定，常见取值为 `monomer`、`monomer_casp14`、`monomer_ptm`、`multimer`。
- `db_preset` 决定数据库使用范围，常见取值为 `full_dbs` 和 `reduced_dbs`。
- `num_recycle`、ensemble、subbatch 等细节来自 `alphafold/model/config.py` 中的 preset。
- template 可用性由 `max_template_date` 控制。

# architecture_structure

- `RunModel`: 负责参数初始化、feature processing、JIT 后前向推理和 confidence metrics 追加。
- `AlphaFold`: 单体和 multimer 分支的完整 Haiku 网络。
- `AlphaFoldIteration`: recycling iteration 单元。
- `EmbeddingsAndEvoformer`: 序列、MSA、template embedding 与 Evoformer trunk。
- `EvoformerIteration`: MSA attention、outer product mean、triangle multiplication、triangle attention 和 transition。
- `StructureModule`: IPA、backbone update、angle resnet 和 atom 坐标恢复。
- `AmberRelaxation`: 推理后可选几何松弛。

# input_schema

- 原始入口输入:
  - FASTA 文件。
  - `model_preset`: `monomer`、`monomer_casp14`、`monomer_ptm` 或 `multimer`。
  - `db_preset`: `full_dbs` 或 `reduced_dbs`。
  - `max_template_date`。
- `RunModel.process_features` 输入:
  - `raw_features: FeatureDict`。
  - monomer 模式会调用 `features.np_example_to_features`。
  - multimer 模式直接使用已处理 features。
- `RunModel.predict` 输入:
  - `feat: FeatureDict`。
  - `random_seed`。
- 典型 feature 字段:
  - `aatype`, `residue_index`, `seq_length`。
  - `msa`, `deletion_matrix`, `num_alignments`。
  - `template_aatype`, `template_all_atom_positions`, `template_all_atom_masks`。
  - `seq_mask`, `msa_mask`, `template_mask`。

# output_schema

- `RunModel.predict` 返回 model output dict，并追加:
  - `plddt`。
  - `ranking_confidence`。
  - pTM 模式下的 `ptm`。
  - multimer 模式下的 `iptm`。
  - PAE head 存在时的 predicted aligned error 相关输出。
- 示例脚本输出:
  - `features.pkl`。
  - `result_model_*.pkl`。
  - `unrelaxed_model_*.pdb`。
  - `ranked_*.pdb`。
  - 可选 `relaxed_model_*.pdb`。
  - `ranking_debug.json`, `timings.json`。

# shape_transformations

- FASTA sequence -> MSA/template feature arrays
- `msa`: `[N_seq, N_res]`
- MSA representation: `[N_seq, N_res, c_m]`
- Pair representation: `[N_res, N_res, c_z]`
- Single representation: `[N_res, c_s]`
- Structure output: `[N_res, 37, 3]` 语义的 atom37 坐标

# key_dependencies

- `RunModel`
- `AlphaFold`
- `AlphaFoldIteration`
- `EmbeddingsAndEvoformer`
- `EvoformerIteration`
- `StructureModule`
- `DataPipeline`
- `DataPipelineMultimer`
- `AmberRelaxation`

# common_modification_points

- 原版 AF2 推理优先修改示例脚本参数，不改模型主体。
- 批量推理优先围绕 `RunModel.process_features`、`RunModel.predict` 和 MSA 预计算组织外层调度。
- monomer/multimer 切换必须同步调整 FASTA 组织、feature pipeline 和 model preset。
- 需要 PyTorch 训练或 OpenFold batch 时应转向 OpenFold，不要直接跨框架搬用 Haiku 模块。

# implementation_risks

- AlphaFold JAX feature dict 与 OpenFold PyTorch batch 语义相近但不等价，不能直接互换。
- 数据库、MSA 工具、template search 和参数文件是推理能否运行的主要约束。
- multimer 不是简单拼接多条链，必须使用 multimer pipeline。
- relaxed PDB 是后处理结果，不是模型原始输出；做误差分析时应区分 relaxed 与 unrelaxed。

# code_references

- `{onescience_path}/onescience/src/onescience/flax_models/alphafold/model/model.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold/model/modules.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold/model/modules_multimer.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold/model/folding.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold/data/pipeline.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold/data/pipeline_multimer.py`
- `{onescience_path}/onescience/examples/biosciences/alphafold/run_alphafold.py`
