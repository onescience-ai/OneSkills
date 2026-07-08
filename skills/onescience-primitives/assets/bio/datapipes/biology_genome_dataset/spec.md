# pipeline_responsibility

读取 genome FASTA 文件或目录，将 DNA/RNA 序列组织为统一样本，并提供基础核苷酸编码能力。该原语适合轻量基因组数据接入、样本发现和简单编码；如果目标是 Evo2 训练或推理，需要进一步对齐 Evo2 tokenizer、位置编码和长序列 batch 协议。

# pipeline_architecture

```text
输入配置
  source.path
    -> FASTA 文件或目录
  data.extra.sequence_type
    -> DNA | RNA
  data.extra.use_pipeline
    -> 是否走 UnifiedDataPipeline
  data.extra.use_adapter
    -> 是否调用 adapter

数据加载
  GenomeDataset
    -> 继承 BioDataset
    -> 扫描 FASTA
    -> 读取 sequence / description
    -> 构造 data_list

序列编码
  NucleotideEncoder
    DNA: A/T/G/C/N/-
    RNA: A/U/G/C/N/-
    -> token ids 或 one-hot 风格基础表示

输出
  adapter 路径
    -> adapter.process_sample
  pipeline 路径
    -> aatype / sequence / sequence_length
  raw 路径
    -> 原始 sample

DataLoader
  get_genome_dataloader
    -> DistributedSampler(shuffle=False)
    -> batch_size=1
    -> collate_fn 保留原始 batch list
```

# data_loading

- `source.path` 是 FASTA 文件时直接解析。
- `source.path` 是目录时扫描 FASTA 文件；当前目录扫描不递归。
- 每条序列生成 `sequence` 和 `description`，目录输入还保留 `file_path`。
- Evo2 的 `SimpleFastaDataset` 使用 FASTA index 读取序列，并按 seqid 排序索引。

# sampling_strategy

- `GenomeDataset` 以 FASTA record 为样本单位。
- 目录输入按扫描得到的 FASTA 文件和记录构造顺序索引。
- `get_genome_dataloader` 使用 `DistributedSampler(..., shuffle=False)`。
- batch size 默认为 1，collate 保留原始样本列表。
- Evo2 训练数据划分和长序列采样不由该通用 dataloader 完整覆盖。

# data_transform

- DNA vocabulary: `A, T, G, C, N, -`。
- RNA vocabulary: `A, U, G, C, N, -`。
- `GenomeDataset.__getitem__` 可返回 adapter 处理结果、pipeline 特征或原始样本。
- 通用 pipeline 可能沿用氨基酸 `aatype` 语义；用于基因组语言模型时应避免误用。
- Evo2 相关路径应转换为 `tokens`、`position_ids`、`seq_idx`、`loss_mask`。

# input_schema

```text
configs:
  source.path: FASTA 文件或目录
  data.extra.sequence_type: DNA | RNA
  data.extra.use_pipeline: bool
  data.extra.use_adapter: bool
  data.extra.model_name: str
  data.extra.use_msa: false
  num_workers: int

Evo2 SimpleFastaDataset:
  fasta_path: FASTA 文件
  tokenizer: Evo2Tokenizer
  prepend_bos: bool
```

# output_schema

```text
GenomeDataset raw sample:
  sequence: str
  description: str
  file_path: optional str

GenomeDataset pipeline sample:
  aatype: encoded sequence field
  sequence: str
  sequence_length: int

Evo2 SimpleFastaDataset sample:
  tokens: token id array
  position_ids: position id array
  seq_idx: sequence index
  loss_mask: mask array
```

# constraints

- `GenomeDataset` 的 `UnifiedDataPipeline` 默认更偏蛋白序列语义，用于 Evo2 时应优先走 Evo2 tokenizer。
- adapter registry 当前没有通用 `evo2` adapter，`use_adapter=True` 且 `model_name='evo2'` 会失败。
- 目录扫描不递归。
- 不负责基因组切窗、反向互补增强、长序列 packing、mmap 数据生成或预训练 label offset。
- Evo2 训练依赖专用数据预处理与长序列 batch 协议。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/biology/datasets/genome_dataset.py`
- `{onescience_path}/onescience/src/onescience/datapipes/biology/common/sequence/sequence_encoder.py`
- `{onescience_path}/onescience/src/onescience/datapipes/biology/dataloader.py`
- `{onescience_path}/onescience/src/onescience/models/evo2/data/fasta_dataset.py`
- `{onescience_path}/onescience/src/onescience/models/evo2/data/tokenizer.py`
