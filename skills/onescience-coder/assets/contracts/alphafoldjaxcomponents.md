# Contract: AlphaFoldJAXComponents

## 基本信息

- 组件名：`AlphaFoldJAXEvoformer / AlphaFoldJAXStructureModule / AlphaFoldJAXConfidenceHead`
- 所属模块族：`transformer / decoder / head`
- 统一入口：`OneTransformer / OneDecoder / OneHead`
- 注册名：`style="AlphaFoldJAXEvoformer"`, `style="AlphaFoldJAXStructureModule"`, `style="AlphaFoldJAXConfidenceHead"`
- 注册状态：`contract_only`

## 组件职责

AlphaFold JAX 组件负责把 AF2 raw features 处理为模型 batch，经 Evoformer 和 StructureModule 输出蛋白结构与置信度指标。契约层按 OneScience 组件体系归一为 transformer、decoder 和 head 三类入口。

补充说明：

- 源码当前仍是 JAX/Haiku 原版流水线；若要在 OneScience 组件层复用，应按上面的 `style` 目标补注册适配层
- monomer 与 multimer 使用不同 module 文件：`modules.py` 与 `modules_multimer.py`
- 若要 PyTorch AF2-style 训练/微调，优先看 `OpenFold` 组件，而不是直接迁移 Haiku 模块
- `RunModel` 是推理编排器，不作为独立 `One*` 组件注册

## One* 归一映射

| 源码组件 | 所属模块族 | 统一入口 | 注册名 |
| --- | --- | --- | --- |
| `EmbeddingsAndEvoformer / EvoformerIteration` | `transformer` | `OneTransformer` | `style="AlphaFoldJAXEvoformer"` |
| `StructureModule` | `decoder` | `OneDecoder` | `style="AlphaFoldJAXStructureModule"` |
| `PredictedLDDTHead / PredictedAlignedErrorHead / DistogramHead` | `head` | `OneHead` | `style="AlphaFoldJAXConfidenceHead"` |

## 支持输入

- 2D 输入：`not_applicable`
- 3D 输入：`not_applicable`
- `RunModel.process_features`：
  - `raw_features: FeatureDict`
  - `random_seed`
- `RunModel.predict`：
  - `feat: FeatureDict`
  - `random_seed`
- 常见 feature 字段：
  - `aatype`
  - `residue_index`
  - `seq_mask`
  - `msa`, `msa_mask`, `deletion_matrix`
  - `template_aatype`
  - `template_all_atom_positions`
  - `template_all_atom_masks`

内部统一做法：

- `RunModel` 根据 `config.model.global_config.multimer_mode` 选择 monomer 或 multimer forward
- monomer raw features 经过 `features.np_example_to_features`
- `AlphaFoldIteration` 执行 recycling iteration
- `EmbeddingsAndEvoformer` 处理 sequence、MSA、template 和 pair 表征
- `StructureModule` 将 single/pair 表征转为 atom positions
- `get_confidence_metrics` 根据 predicted LDDT / PAE 输出 ranking confidence

## 构造参数

- `RunModel`
  - `config: ml_collections.ConfigDict`
  - `params: Optional[Mapping]`
- 关键 config 分支：
  - `model.global_config.multimer_mode`
  - model preset
  - data preset
  - ensemble / recycle / subbatch 相关字段

## 输出约定

- `RunModel.predict` 输出：
  - model raw output dict
  - `plddt`
  - `ranking_confidence`
  - optional `ptm`
  - optional `iptm`
  - optional predicted aligned error fields
- 推理脚本会进一步写出 PDB、pickle result、ranking json 和 timing json

如果有明确边界条件，也写在这里：

- multimer 模式下 `random_seed` 会影响 MSA sampling
- 若未传入 params，`RunModel.init_params` 会随机初始化并记录 warning；真实推理必须加载参数
- relax 后结构不是模型直接输出，应和 raw model result 分开处理

## 典型调用位置

- `examples/biosciences/alphafold/run_alphafold.py`
- AlphaFold monomer / multimer inference pipeline
- 批量 FASTA 推理外层封装

## 典型参数

- `model_preset=monomer`
- `model_preset=monomer_ptm`
- `model_preset=multimer`
- `db_preset=reduced_dbs` 或 `full_dbs`
- `max_template_date=YYYY-MM-DD`
- 契约层目标调用：
  - `OneTransformer(style="AlphaFoldJAXEvoformer", ...)`
  - `OneDecoder(style="AlphaFoldJAXStructureModule", ...)`
  - `OneHead(style="AlphaFoldJAXConfidenceHead", ...)`

## 风险点

- JAX/Haiku 参数树和 PyTorch state dict 不兼容
- 以上 `style` 是 skill 契约归一名，不表示当前源码已经在对应 `One*` registry 中可直接实例化
- AF2 monomer / multimer feature pipeline 不可混用
- MSA/template 数据库与外部工具是推理主依赖，不是模型 forward 内部自动解决
- 原始 AlphaFold v2 组件要进入 `One*` 体系时应先写薄适配层，不要直接跨框架搬 Haiku 模块

## 源码锚点

- `./onescience/src/onescience/flax_models/alphafold/model/model.py`
- `./onescience/src/onescience/flax_models/alphafold/model/modules.py`
- `./onescience/src/onescience/flax_models/alphafold/model/modules_multimer.py`
- `./onescience/src/onescience/flax_models/alphafold/model/folding.py`
- `./onescience/src/onescience/flax_models/alphafold/data/pipeline.py`
- `./onescience/examples/biosciences/alphafold/run_alphafold.py`
