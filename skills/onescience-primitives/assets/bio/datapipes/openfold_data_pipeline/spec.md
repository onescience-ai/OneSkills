# pipeline_responsibility

生成 OpenFold/AF2 风格的蛋白结构预测特征和训练/推理 batch。该原语覆盖 FASTA、MSA、template、PDB/mmCIF、单体/多聚体特征处理和 DataModule 组织，是 OpenFold 模型最匹配的数据入口。

# pipeline_architecture

```text
输入
  FASTA / PDB / mmCIF / 预计算 MSA / template database

解析与搜索
  parsers.py
    -> parse_fasta / parse_a3m / parse_stockholm / parse_hhr
  tools/*
    -> Jackhmmer / HHblits / HHsearch / Kalign / hmmsearch
  mmcif_parsing.py
    -> MmcifObject / atom coords / release date

特征生成
  data_pipeline.py
    -> make_sequence_features
    -> make_msa_features
    -> make_template_features
    -> make_pdb_features / make_mmcif_features

特征处理
  feature_pipeline.py
    -> np_to_tensor_dict
  input_pipeline.py
    -> 单体 transform
  input_pipeline_multimer.py
    -> 多聚体 transform
  feature_processing_multimer.py
    -> pair / merge / crop / final process

训练装配
  data_modules.py
    -> OpenFoldDataset
    -> OpenFoldDataLoader
    -> OpenFoldDataModule
```

# data_loading

- FASTA 由 parser 读取。
- A3M、Stockholm、HHR、tblout 等 MSA/template 相关文件由 `parsers.py` 解析。
- mmCIF 由 `mmcif_parsing.py` 解析链、残基、原子坐标和 release date。
- MSA 搜索可通过 `jackhmmer`、`hhblits`、`hmmsearch` 等 wrapper 调用外部工具。
- template 特征通过 HHsearch hit、PDB/mmCIF 数据和日期过滤生成。

# sampling_strategy

- `data_modules.py` 提供单体、多聚体 dataset、collator、loader 和 DataModule。
- 支持过滤条件：分辨率、氨基酸数量、序列长度等。
- 多聚体路径需要 chain pairing、homomer/heteromer 合并和 crop。
- 训练/验证划分依赖上游配置或数据模块配置，不由单个 parser 自动决定。

# data_transform

- 生成 sequence、MSA、deletion matrix、template、atom positions、mask 等 AF2/OpenFold 特征。
- 单体 transform 包含 MSA 采样、mask、extra MSA、template mask、crop、ensembled feature。
- 多聚体 transform 包含 masked MSA、nearest neighbor cluster、paired MSA、chain merge、spatial/contiguous crop。
- numpy feature dict 通过 FeaturePipeline 转为 tensor dict。

# input_schema

```text
推理输入:
  fasta_path: FASTA
  msa_output_dir: MSA 输出目录
  template_search_config: 数据库与工具路径

训练输入:
  mmcif_dir: mmCIF 结构目录
  alignment_dir: MSA/对齐目录
  chain_data_cache: 可选缓存
  data_config: OpenFold 数据配置

多聚体:
  fasta chains: 多链序列
  paired/unpaired MSA: 多链对齐特征
```

# output_schema

```text
OpenFold feature dict:
  aatype
  residue_index
  seq_length
  msa
  deletion_matrix
  template_aatype
  template_all_atom_positions
  template_all_atom_mask
  all_atom_positions
  all_atom_mask
  chain_index / asym_id / entity_id / sym_id: multimer 可选

DataLoader batch:
  tensor feature dict
  shape 由 data_config、crop_size、msa depth 和 template 数控制
```

# constraints

- 外部 MSA/template 工具和数据库路径必须正确配置。
- 单体、多聚体 feature 协议不同，不能混用。
- template 使用受 release date、序列一致性和结构质量过滤影响。
- MSA 和 template 处理耗时长，适合缓存。
- 输出是 OpenFold/AF2 协议，不应直接送入 Protenix/AF3 风格模型。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/openfold/data_modules.py`
- `{onescience_path}/onescience/src/onescience/datapipes/openfold/data_pipeline.py`
- `{onescience_path}/onescience/src/onescience/datapipes/openfold/feature_pipeline.py`
- `{onescience_path}/onescience/src/onescience/datapipes/openfold/input_pipeline.py`
- `{onescience_path}/onescience/src/onescience/datapipes/openfold/input_pipeline_multimer.py`
- `{onescience_path}/onescience/src/onescience/datapipes/openfold/feature_processing_multimer.py`
- `{onescience_path}/onescience/src/onescience/datapipes/openfold/mmcif_parsing.py`
- `{onescience_path}/onescience/src/onescience/datapipes/openfold/parsers.py`
- `{onescience_path}/onescience/src/onescience/datapipes/openfold/templates.py`
- `{onescience_path}/onescience/src/onescience/datapipes/openfold/tools`
