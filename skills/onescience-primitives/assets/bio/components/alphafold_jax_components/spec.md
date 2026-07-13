# component_info

`alphafold_jax_components` 是 AlphaFold v2 JAX/Haiku 实现的组件契约，覆盖 `AlphaFoldJAXEvoformer`、`AlphaFoldJAXStructureModule` 和 `AlphaFoldJAXConfidenceHead`。原始 contract 中组件族为 `transformer / decoder / head`，目标统一入口为 `OneTransformer / OneDecoder / OneHead`，注册名为 `style="AlphaFoldJAXEvoformer"`、`style="AlphaFoldJAXStructureModule"`、`style="AlphaFoldJAXConfidenceHead"`，注册状态为 `contract_only`。

# purpose

用于理解和规划 AF2 原版 monomer/multimer 推理中的核心模型组件：Evoformer 负责 MSA、template、pair/single 表征更新，StructureModule 负责结构坐标恢复，confidence heads 输出 pLDDT、PAE、PTM/IPTM 等置信度指标。它适用于 AlphaFold JAX 推理、组件定位和迁移规划，不适合作为已注册的 PyTorch `One*` 模块直接调用；若要 PyTorch AF2-style 训练或微调，优先查看 OpenFold 组件。

# input_schema

```text
RunModel.process_features:
  raw_features: FeatureDict
  random_seed: int

RunModel.predict:
  feat: FeatureDict
  random_seed: int

常见 feature 字段:
  aatype, residue_index, seq_mask
  msa, msa_mask, deletion_matrix
  template_aatype
  template_all_atom_positions
  template_all_atom_masks
```

# output_schema

```text
RunModel.predict:
  raw model output dict
  plddt
  ranking_confidence
  optional ptm
  optional iptm
  optional predicted aligned error fields

外层脚本:
  PDB
  result pickle
  ranking json
  timing json
```

# parameters

- `RunModel.config`: `ml_collections.ConfigDict`
- `RunModel.params`: optional parameter mapping
- 关键配置分支：`model.global_config.multimer_mode`、model preset、data preset、ensemble、recycle、subbatch。
- 典型 preset：`monomer`、`monomer_ptm`、`multimer`。

# key_dependencies

- `model.py`
- `modules.py`
- `modules_multimer.py`
- `folding.py`
- `pipeline.py`
- `run_alphafold.py`

# usage_and_risks

典型流程是 FASTA 和数据库搜索结果进入 AlphaFold data pipeline，`RunModel.process_features` 将 raw features 转换为模型 batch，`RunModel.predict` 执行 recycling、Evoformer、StructureModule 和 confidence 计算。`contract_only` 来自原始 contract，表示这些 `style` 是 skill 契约归一名，不表示当前源码已在对应 `One*` registry 中可直接实例化。JAX/Haiku 参数树与 PyTorch state dict 不兼容，monomer/multimer feature pipeline 不可混用，MSA/template 外部工具不是 forward 内部自动解决。

# code_references

- `{onescience_path}/onescience/src/onescience/flax_models/alphafold/model/model.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold/model/modules.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold/model/modules_multimer.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold/model/folding.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold/data/pipeline.py`
- `{onescience_path}/onescience/examples/biosciences/alphafold/run_alphafold.py`
