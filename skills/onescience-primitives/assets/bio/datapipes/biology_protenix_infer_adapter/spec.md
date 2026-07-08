# pipeline_responsibility

将 Protenix/AF3 JSON 输入转换为 Protenix 推理特征。该原语是 biology protein 数据层与 Protenix 数据流水线之间的适配层，负责把 JSON sample 解析为实体、原子、token 和模型 feature，不负责训练采样或通用 FASTA/MSA 文件发现。

# pipeline_architecture

```text
ProteinDataset
  input_json_path
    -> 读取 Protenix/AF3 JSON
  data.extra.use_adapter=true
  data.extra.model_name=protenix_infer_adapter

Adapter Registry
  register_adapter("protenix_infer_adapter")
    -> ProtenixInferAdapter

JSON 样本
  sequences
    -> proteinChain / dnaSequence / rnaSequence
    -> ligand / ion
  covalent_bonds
    -> 跨实体连接

ProtenixInferAdapter.process_json_sample
  -> Protenix json_parser
  -> CCD / ligand / atom reference feature
  -> AtomArrayTokenizer
  -> SampleDictToFeatures
  -> feature_dict + atom_array + token_array
```

# data_loading

- 入口来自 `ProteinDataset.__getitem__` 的 `input_json_path` 分支。
- JSON 中的每个样本包含生物分子实体列表和可选共价键。
- ligand、ion 和非标准残基依赖 CCD 或分子构建逻辑。
- MSA 特征可由 Protenix 推理 MSA featurizer 生成或补 dummy MSA。

# sampling_strategy

- 按 JSON 样本索引逐条处理。
- 通常用于推理，DataLoader 侧保持 `batch_size=1`。
- 不执行训练集划分、随机采样、权重采样或多数据集平衡。

# data_transform

- JSON entity 转换为 polymer、ligand、ion 的 atom-level 表示。
- 添加参考坐标、原子元素、键、实体和链级 annotation。
- AtomArray 经 tokenizer 形成 TokenArray。
- 最终生成 Protenix feature dict，用于模型推理。
- 解析失败时返回错误信息或抛出依赖/格式错误。

# input_schema

```text
configs:
  input_json_path: Protenix/AF3 JSON 文件
  data.extra.use_adapter: true
  data.extra.model_name: protenix_infer_adapter

JSON sample:
  name: str
  sequences:
    - proteinChain | dnaSequence | rnaSequence | ligand | ion
  covalent_bonds: optional list
```

# output_schema

```text
adapter output:
  feature_dict: dict
    Protenix 推理所需模型特征
  atom_array: AtomArray
    原子级结构和 annotation
  token_array: TokenArray
    token 级结构表示

ProteinDataset item:
  result:
    features: feature_dict
    sample_name: str
    sample_index: int
  atom_array: AtomArray
  error_message: str | None
```

# constraints

- adapter 注册名必须是 `protenix_infer_adapter`。
- 输入必须符合 Protenix/AF3 JSON 语义，普通 FASTA 不能直接进入该 adapter。
- ligand、非标准残基和共价键依赖 CCD/rdkit/biotite 等分子处理能力。
- 不负责模型推理本身，也不负责训练数据过滤或分布式采样。
- 出错时应优先检查 JSON schema、实体名称、CCD code 和 covalent bond 索引。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/biology/adapters/adapter_registry.py`
- `{onescience_path}/onescience/src/onescience/datapipes/biology/adapters/base_adapter.py`
- `{onescience_path}/onescience/src/onescience/datapipes/biology/adapters/protenix_infer_adapter.py`
- `{onescience_path}/onescience/src/onescience/datapipes/protenix/json_parser.py`
- `{onescience_path}/onescience/src/onescience/datapipes/protenix/json_to_feature.py`
- `{onescience_path}/onescience/src/onescience/datapipes/protenix/tokenizer.py`
