# Model Card: AlphaFold

## 基本信息

- 模型名：`AlphaFold / AlphaFold-Multimer`
- 任务类型：`蛋白质结构预测 / AF2-style JAX inference`
- 当前状态：`stable`
- 主实现文件：`./onescience/src/onescience/flax_models/alphafold/model/model.py`

## 模型定位

AlphaFold 是 OneScience 中保留的 DeepMind AlphaFold v2 JAX/Haiku 推理流水线，适合需要复用原版 AF2/Multimer 特征、参数与推理脚本的场景。

补充说明：

- 它与 `OpenFold` 都是 AF2-style folding，但 `AlphaFold` 是 JAX/Haiku 原版风格，`OpenFold` 是 PyTorch/OpenFold 风格
- 它与 `Protenix`、`AlphaFold3` 不同：AlphaFold v2 走 Evoformer + StructureModule，不走 AF3 Pairformer + diffusion 生成
- example 主入口是 `examples/biosciences/alphafold/run_alphafold.py`
- 数据侧依赖 MSA、template search、feature processing 和可选 Amber relax，不适合作为轻量通用模型直接拼装

## 输入定义

- 原始入口：
  - FASTA 文件
  - `model_preset`: `monomer`, `monomer_casp14`, `monomer_ptm`, `multimer`
  - `db_preset`: `full_dbs` 或 `reduced_dbs`
  - `max_template_date`
- `RunModel.process_features` 输入：
  - `raw_features: FeatureDict`
  - monomer 下会调用 `features.np_example_to_features`
  - multimer 下直接使用已处理 features
- `RunModel.predict` 输入：
  - `feat: FeatureDict`
  - `random_seed`
- 典型 feature 字段：
  - sequence / residue：`aatype`, `residue_index`, `seq_length`
  - MSA：`msa`, `deletion_matrix`, `num_alignments`
  - template：`template_aatype`, `template_all_atom_positions`, `template_all_atom_masks`
  - mask：`seq_mask`, `msa_mask`, `template_mask`

## 输出定义

- `RunModel.predict` 返回 model output dict，并追加 confidence metrics：
  - `plddt`
  - `ranking_confidence`
  - pTM 模式下的 `ptm`
  - multimer 模式下的 `iptm`
  - 若存在 PAE head，则包含 predicted aligned error 相关输出
- 推理脚本输出：
  - `features.pkl`
  - `result_model_*.pkl`
  - `unrelaxed_model_*.pdb`
  - `ranked_*.pdb`
  - 可选 `relaxed_model_*.pdb`
  - `ranking_debug.json`, `timings.json`

## 主干结构

- `RunModel`
  - 构造 Haiku transform / jit 后的 forward
  - 管理随机初始化、feature processing 和 predict
- `AlphaFold`
  - monomer / multimer 分支的完整网络
- `AlphaFoldIteration`
  - recycling iteration
- `EmbeddingsAndEvoformer`
  - sequence、MSA、template embedding 与 Evoformer trunk
- `EvoformerIteration`
  - MSA attention、outer product mean、triangle multiplication / attention、transition
- `StructureModule`
  - IPA、backbone update、angle resnet、atom 坐标恢复
- `AmberRelaxation`
  - 推理后可选几何松弛

## 主要依赖组件

- `RunModel`
- `AlphaFold`
- `AlphaFoldIteration`
- `EmbeddingsAndEvoformer`
- `EvoformerIteration`
- `StructureModule`
- `DataPipeline / DataPipelineMultimer`
- `AmberRelaxation`

## 主要 Shape 变化

- FASTA sequence -> MSA/template feature arrays
- `msa`: `[N_seq, N_res]`
- MSA representation: `[N_seq, N_res, c_m]`
- Pair representation: `[N_res, N_res, c_z]`
- Single representation: `[N_res, c_s]`
- Structure output: `[N_res, 37, 3]` 语义的 atom37 坐标

## 默认关键参数

- `model_preset` 决定 monomer / multimer / pTM 分支
- `db_preset` 决定 MSA 数据库规模
- `max_template_date` 约束 template 可用日期
- `num_recycle`、ensemble、subbatch 等细节由 `alphafold/model/config.py` preset 决定

## 常见修改点

- 做原版 AF2 推理：优先改 example 脚本参数，不改模型主体
- 做批量推理：优先围绕 `RunModel.process_features`、`RunModel.predict` 和 MSA 预计算组织外层调度
- 做 monomer/multimer 切换：必须同步切换 FASTA 组织、feature pipeline 和 model preset
- 想复用 AF2 组件到 PyTorch 训练：优先看 `OpenFold`，不要直接跨框架搬 Haiku 模块

## 风险点

- AlphaFold JAX feature dict 与 OpenFold PyTorch batch 很像但不等价，不能直接互换训练入口
- 数据库、MSA 工具、template search 和参数文件是推理能否运行的主要约束
- multimer 模式不是简单把多条链拼接到 monomer FASTA，需要走 multimer pipeline
- relax 输出不是模型原始输出，若对模型误差做分析，应区分 relaxed / unrelaxed PDB

## 推荐检索顺序

1. 先看本模型卡
2. 再看 `alphafold/model/model.py` 的 `RunModel`
3. 再看 `alphafold/model/modules.py` 或 `modules_multimer.py`
4. 若涉及数据搜索，读 `alphafold/data/pipeline.py`、`pipeline_multimer.py`
5. 若涉及 example，读 `examples/biosciences/alphafold/run_alphafold.py`

## 组件契约入口

- `../contracts/alphafoldjaxcomponents.md`
- 当前 AlphaFold 不通过 OneScience `One*` wrapper 拼装，优先按 JAX/Haiku 原版流水线处理

## 源码锚点

- `./onescience/src/onescience/flax_models/alphafold/model/model.py`
- `./onescience/src/onescience/flax_models/alphafold/model/modules.py`
- `./onescience/src/onescience/flax_models/alphafold/model/modules_multimer.py`
- `./onescience/src/onescience/flax_models/alphafold/model/folding.py`
- `./onescience/src/onescience/flax_models/alphafold/data/pipeline.py`
- `./onescience/src/onescience/flax_models/alphafold/data/pipeline_multimer.py`
- `./onescience/examples/biosciences/alphafold/run_alphafold.py`
