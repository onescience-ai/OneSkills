# Datapipe: Biology Protein Dataset Family

## 基本信息

- Datapipe 名：`ProteinDataset / MultimerDataset / ProtenixInferAdapter`
- 数据类型：`biology / protein / biomolecular structure`
- 主要任务：`蛋白质序列、MSA、结构文件读取与 Protenix 推理特征适配`
- 数据组织方式：`fasta / msa / pdb / cif / Protenix JSON`

## Datapipe 职责

biology protein datapipe family 负责把蛋白质 FASTA、MSA、结构文件或 Protenix JSON 输入整理成模型可消费的样本。当前代码同时提供通用 pipeline 和 Protenix 推理 adapter，但最完整、最明确的 `__getitem__` 路径是 `input_json_path + protenix_infer_adapter`。

补充说明：

- `BioDataset` 负责基础路径、MSA 路径、结构格式和通用 biology 配置
- `ProteinDataset` 负责发现和关联 FASTA、MSA、结构文件，并可选使用 `UnifiedDataPipeline` 或 adapter
- `MultimerDataset` 继承 `ProteinDataset`，补充 `max_chains` 与 `num_chains` 元信息
- `ProtenixInferAdapter` 负责把 Protenix / AF3 JSON 转成完整 feature dict、`AtomArray` 和 `TokenArray`
- `get_protein_dataloader` 与 `get_multimer_dataloader` 都使用 `DistributedSampler`、`batch_size=1`、`collate_fn=lambda batch: batch`

## 输入配置

- `source.path`
  - FASTA、MSA、结构文件或目录路径
- `input_json_path`
  - Protenix 推理 JSON 文件路径，当前 `ProteinDataset.__getitem__` 的主路径
- `data.extra.use_pipeline`
  - 是否启用 `UnifiedDataPipeline`，默认 True
- `data.extra.use_adapter`
  - 是否启用 adapter
- `data.extra.model_name`
  - adapter 名称；Protenix 推理应写 `protenix_infer_adapter`
- `data.extra.use_msa`
  - 是否处理 MSA
- `data.extra.use_structure`
  - 是否处理结构特征
- `data.extra.max_msa_seqs`
  - MSA 最大序列数
- `data.extra.recursive`
  - 目录扫描是否递归
- `data.extra.msa_dirs`
  - 额外 MSA 文件或目录
- `data.extra.structure_dirs`
  - 额外结构文件或目录
- `data.extra.default_chain_id`
  - 结构文件缺链标识时的默认链
- `data.extra.allow_dummy_sample`
  - 未发现数据时是否构造 dummy protein sample
- `num_workers`
  - DataLoader 工作进程数

## 数据存储约定

- 支持格式：
  - FASTA: `fasta`
  - MSA: `a3m`, `stockholm`
  - 结构: `pdb`, `mmcif`, `mmtf`
  - 基类登记格式还包括 `cif`, `sdf`, `mol2`
- MSA 目录惯例：
  - `pairing.a3m`
  - `non_pairing.a3m`
  - 或任意 `.a3m`
- Protenix JSON：
  - `sequences` 中可包含 `proteinChain`, `dnaSequence`, `rnaSequence`, ligand / ion 等实体
  - 可选 `covalent_bonds`

## 样本构造方式

- FASTA 发现：
  - 读取 sequence 和 description
  - 通过 description 或文件名归一化样本 id
- MSA 关联：
  - 先按归一化文件名匹配已有 sequence entry
  - 失败时尝试解析 MSA 第一条序列补建 entry
- 结构关联：
  - 按结构文件名或去掉链后缀的文件名前缀关联 entry
  - 可补 `chain_id`, `structure_format`
- `UnifiedDataPipeline.process_sample` 可输出：
  - `aatype`
  - `sequence`
  - `sequence_length`
  - `msa`
  - `deletion_matrix`
  - `msa_row_weights`
  - `num_alignments`
  - `all_atom_positions`
  - `all_atom_mask`
  - `ca_distance_matrix`
  - `ca_mask`
- `ProtenixInferAdapter.process_json_sample` 输出：
  - `feature_dict`
  - `atom_array`
  - `token_array`
- `ProteinDataset.__getitem__` 在 Protenix JSON 路径返回：
  - `result`: 包含 `features`, `sample_name`, `sample_index`
  - `atom_array`
  - `error_message`

## DataLoader 约定

- `get_protein_dataloader(configs)`
  - dataset: `ProteinDataset(configs)`
  - sampler: `DistributedSampler(..., shuffle=False)`
  - batch size: `1`
  - collate: 原样保留 list batch
- `get_multimer_dataloader(configs)`
  - dataset: `MultimerDataset(configs)`
  - 其余行为同 protein loader

## 适合优先使用的场景

- Protenix 统一推理，输入是 Protenix JSON
- 需要把 FASTA / MSA / PDB / mmCIF 先组织成通用 biology sample index
- 需要快速继承 `ProteinDataset`，自定义 `__getitem__` 适配新模型
- 多链蛋白或复合物任务中，需要先复用 `MultimerDataset` 的数据发现逻辑

## 风险点

- `ProteinDataset.__len__` 在没有 `input_json_path` 时当前返回 `None`，非 JSON 训练路径需要补全后才能直接接 DataLoader
- `ProteinDataset.__getitem__` 中存在 `config.fase_path` 分支拼写，且非 JSON 分支基本未实现，不要把它当成完整通用 datapipe
- `ProtenixInferAdapter` 只注册了 `protenix_infer_adapter`，注释掉了 `protenix`
- `process_json_sample` 依赖 `onescience.datapipes.protenix.*` 等 Protenix 特征化模块，缺依赖时会抛出 ImportError
- `MSAParser` 会检测 `clustal/phylip`，但真正实现的解析只有 `a3m` 和 `stockholm`
- `StructureFeaturizer` 当前按原子列表构造特征，结构 feature shape 不是 OpenFold / Protenix 的最终模型协议

## 源码锚点

- `./onescience/src/onescience/datapipes/biology/base.py`
- `./onescience/src/onescience/datapipes/biology/dataloader.py`
- `./onescience/src/onescience/datapipes/biology/datasets/protein_dataset.py`
- `./onescience/src/onescience/datapipes/biology/datasets/multimer_dataset.py`
- `./onescience/src/onescience/datapipes/biology/datasets/unified_dataset.py`
- `./onescience/src/onescience/datapipes/biology/adapters/protenix_infer_adapter.py`
