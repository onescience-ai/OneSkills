# pipeline_responsibility

为 Protenix/AF3 风格模型提供完整生物分子数据流水线，覆盖 JSON 输入解析、CCD/ligand 处理、MSA 特征化、atom/token 特征生成、训练数据过滤、多数据集采样、推理 dataset 和结构写出辅助能力。

# pipeline_architecture

```text
输入
  Protenix/AF3 JSON
  mmCIF / PDB / cluster / MSA
  CCD / ligand / ion / covalent bond

解析
  json_parser.py
    -> build_polymer / build_ligand / add_entity_atom_array
  parser.py
    -> MMCIFParser / DistillationMMCIFParser
  ccd.py
    -> CCD component / mol type / ref info

特征化
  tokenizer.py
    -> AtomArrayTokenizer
  msa_featurizer.py
    -> PROTMSAFeaturizer / RNAMSAFeaturizer / InferenceMSAFeaturizer
  json_to_feature.py
    -> SampleDictToFeatures
  featurizer.py
    -> Featurizer

数据集与采样
  dataset.py
    -> BaseSingleDataset / WeightedMultiDataset
  filter.py
    -> Filter
  dataloader.py
    -> WeightedSampler / DistributedWeightedSampler
    -> get_dataloaders

推理
  infer_data_pipeline.py
    -> InferenceDataset
    -> get_inference_dataloader
```

# data_loading

- JSON 输入由 `json_parser.py` 解析为 polymer、ligand、ion 和共价连接。
- mmCIF 训练数据由 `parser.py` 读取并添加 AtomArray annotation。
- MSA 数据由 `msa_utils.py` 和 `msa_featurizer.py` 解析，支持蛋白和 RNA 分支。
- CCD 组件用于非标准残基、ligand 和参考特征。
- cluster、权重和多数据集元信息用于训练采样。

# sampling_strategy

- `BaseSingleDataset` 表示单数据源。
- `WeightedMultiDataset` 支持多数据集组合。
- `WeightedSampler`、`DistributedWeightedSampler` 和 `KeySumBalancedSampler` 支持权重采样、分布式采样和平衡采样。
- 推理路径使用 `InferenceDataset` 和 `get_inference_dataloader`。
- 训练集划分依赖外部数据清单、配置和权重表。

# data_transform

- JSON/mmCIF 转 AtomArray。
- 添加参考特征、原子元素、键、实体、链、残基和 token annotation。
- MSA 转 tokenized MSA、profile 和多链合并特征。
- Featurizer 组装模型输入 feature dict。
- substructure permutation 处理 ligand 等价原子映射。
- utils 支持 dummy feature、dtype 转换、shape 字典和 CIF 写出。

# input_schema

```text
推理:
  input_json: Protenix/AF3 JSON
  msa_dir: 可选 MSA
  ccd_path: 可选 CCD

训练:
  dataset_config:
    data_root: 结构和特征数据根目录
    index/manifest: 样本清单
    weights: 可选权重
    filters: 过滤配置
  msa_config:
    max_msa_seqs
    protein/rna MSA 设置
```

# output_schema

```text
feature dict:
  token-level features
  atom-level features
  msa features
  bond/entity/chain features
  masks
  labels or coordinates: 训练路径可选

inference item:
  features: dict
  atom_array: AtomArray
  token_array: TokenArray
  sample metadata
```

# constraints

- Protenix feature dict 与 OpenFold/AF2 feature dict 不兼容。
- ligand、非标准残基和共价键依赖 CCD/化学解析。
- 多数据集训练需要权重、过滤和采样配置完整。
- MSA 特征路径区分蛋白和 RNA。
- 推理 JSON adapter 和完整训练 dataloader 是不同入口。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/protenix/data_pipeline.py`
- `{onescience_path}/onescience/src/onescience/datapipes/protenix/dataloader.py`
- `{onescience_path}/onescience/src/onescience/datapipes/protenix/dataset.py`
- `{onescience_path}/onescience/src/onescience/datapipes/protenix/featurizer.py`
- `{onescience_path}/onescience/src/onescience/datapipes/protenix/infer_data_pipeline.py`
- `{onescience_path}/onescience/src/onescience/datapipes/protenix/json_parser.py`
- `{onescience_path}/onescience/src/onescience/datapipes/protenix/json_to_feature.py`
- `{onescience_path}/onescience/src/onescience/datapipes/protenix/msa_featurizer.py`
- `{onescience_path}/onescience/src/onescience/datapipes/protenix/tokenizer.py`
- `{onescience_path}/onescience/src/onescience/datapipes/protenix/ccd.py`
