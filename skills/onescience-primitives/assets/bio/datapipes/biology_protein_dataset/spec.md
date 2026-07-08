# pipeline_responsibility

将蛋白质序列、MSA、结构文件或 Protenix JSON 组织成统一生物样本。该原语覆盖 `ProteinDataset` 和 `MultimerDataset` 的数据发现、样本索引、MSA/结构关联，以及可选的 `UnifiedDataPipeline` 或 adapter 特征转换。当前最完整的业务路径是 `input_json_path + protenix_infer_adapter`。

# pipeline_architecture

```text
输入配置
  source.path
    -> FASTA 文件/目录、MSA 文件/目录、结构文件/目录
  input_json_path
    -> Protenix/AF3 风格 JSON
  data.extra
    -> use_pipeline / use_adapter / model_name
    -> use_msa / use_structure / max_msa_seqs
    -> msa_dirs / structure_dirs / recursive

数据集初始化
  BioDataset
    -> 解析基础路径、格式、MSA/结构配置
  ProteinDataset
    -> 扫描 FASTA
    -> 关联 MSA
    -> 关联 PDB/mmCIF/MMTF 结构
  MultimerDataset
    -> 继承 ProteinDataset
    -> 增加 num_chains / max_chains 元信息

样本处理
  Protenix JSON 路径
    -> ProtenixInferAdapter.process_json_sample
    -> feature_dict + AtomArray + TokenArray
  普通蛋白路径
    -> UnifiedDataPipeline.process_sample
    -> sequence / msa / structure feature dict

DataLoader
  get_protein_dataloader / get_multimer_dataloader
    -> DistributedSampler(shuffle=False)
    -> batch_size=1
    -> collate_fn 保留原始 batch list
```

# data_loading

- FASTA 由统一 FASTA 解析器读取 sequence 和 description。
- MSA 支持 `.a3m` 与 Stockholm，目录惯例包含 `pairing.a3m`、`non_pairing.a3m` 或任意 `.a3m`。
- 结构文件支持 PDB、mmCIF、MMTF，基类登记格式还包含 CIF、SDF、MOL2。
- Protenix JSON 支持 `sequences` 中的 `proteinChain`、`dnaSequence`、`rnaSequence`、ligand、ion 等实体，并可包含 `covalent_bonds`。
- 文件发现会通过 description、文件名或去掉链后缀的结构名前缀建立样本关联。

# sampling_strategy

- 数据集样本由扫描得到的序列条目、MSA 条目和结构条目关联形成。
- Protenix JSON 路径按 JSON 样本列表或 JSON 文件内容索引。
- `get_protein_dataloader` 和 `get_multimer_dataloader` 默认使用 `DistributedSampler(..., shuffle=False)`。
- DataLoader 固定 `batch_size=1`，collate 阶段不合并特征，只保留原始 list。
- 当前通用非 JSON 路径的 `__len__` 和 `__getitem__` 不完整，直接训练前需要补齐或增加 adapter。

# data_transform

- FASTA 序列被编码为 `aatype`、`sequence`、`sequence_length`。
- MSA 被转换为 `msa`、`deletion_matrix`、`msa_row_weights`、`num_alignments`。
- 结构被转换为 `all_atom_positions`、`all_atom_mask`、`ca_distance_matrix`、`ca_mask`。
- Protenix JSON 通过 adapter 转换为 `feature_dict`、`atom_array`、`token_array`。
- 多链样本补充链数量和链级元信息；不负责自动 MSA 搜索、结构预测或质量过滤。

# input_schema

```text
configs:
  source.path: FASTA/MSA/结构文件或目录
  input_json_path: 可选，Protenix 推理 JSON 路径
  data.extra.use_pipeline: bool
  data.extra.use_adapter: bool
  data.extra.model_name: protenix_infer_adapter
  data.extra.use_msa: bool
  data.extra.use_structure: bool
  data.extra.max_msa_seqs: int
  data.extra.recursive: bool
  data.extra.msa_dirs: list[path]
  data.extra.structure_dirs: list[path]
  data.extra.default_chain_id: str
  data.extra.allow_dummy_sample: bool
  num_workers: int
```

# output_schema

```text
Protenix JSON 路径单样本:
  result:
    features: dict
    sample_name: str
    sample_index: int
  atom_array: AtomArray
  error_message: str | None

UnifiedDataPipeline 路径:
  aatype: ndarray/int tensor like
  sequence: str
  sequence_length: int
  msa: optional array
  deletion_matrix: optional array
  all_atom_positions: optional array
  all_atom_mask: optional array
  ca_distance_matrix: optional array
  ca_mask: optional array
```

# constraints

- `ProteinDataset.__len__` 在没有 `input_json_path` 时当前返回不完整，非 JSON 训练路径不能直接视为稳定 datapipe。
- `ProteinDataset.__getitem__` 的非 JSON 分支基本未实现，并存在 `config.fase_path` 拼写风险。
- `ProtenixInferAdapter` 注册名是 `protenix_infer_adapter`。
- MSA parser 主要实现 A3M 和 Stockholm；Clustal/Phylip 不应假定可完整解析。
- `StructureFeaturizer` 输出不是 OpenFold 或 Protenix 最终训练 batch 协议。
- 不执行 MSA 搜索、模板搜索、结构修复或 ligand 参数化。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/biology/base.py`
- `{onescience_path}/onescience/src/onescience/datapipes/biology/dataloader.py`
- `{onescience_path}/onescience/src/onescience/datapipes/biology/datasets/protein_dataset.py`
- `{onescience_path}/onescience/src/onescience/datapipes/biology/datasets/multimer_dataset.py`
- `{onescience_path}/onescience/src/onescience/datapipes/biology/datasets/unified_dataset.py`
- `{onescience_path}/onescience/src/onescience/datapipes/biology/adapters/protenix_infer_adapter.py`
