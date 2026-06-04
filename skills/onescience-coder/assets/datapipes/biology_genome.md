# Datapipe: Biology Genome Dataset Family

## 基本信息

- Datapipe 名：`GenomeDataset / Evo2 SimpleFastaDataset`
- 数据类型：`biology / genome`
- 主要任务：`基因组 FASTA 读取、核苷酸编码与 Evo2 tokenized sequence 输入`
- 数据组织方式：`fasta / token ids / NeMo-Megatron batch`

## Datapipe 职责

biology genome datapipe family 负责把 DNA/RNA 序列组织成可处理的基因组样本。OneScience 中存在两条相关路径：通用 `GenomeDataset` 负责 FASTA 发现和核苷酸编码，Evo2 自带 `SimpleFastaDataset` 与 `Evo2Tokenizer` 负责模型推理所需的 token batch。

补充说明：

- `GenomeDataset` 继承 `BioDataset`
- `NucleotideEncoder` 支持 DNA / RNA，默认 DNA
- `get_genome_dataloader` 使用 `DistributedSampler`、`batch_size=1` 和原样 collate
- Evo2 的训练和推理主要依赖 `onescience.models.evo2.data` 与 examples 中的数据预处理脚本

## 输入配置

- `source.path`
  - FASTA 文件或目录
- `data.extra.sequence_type`
  - `"DNA"` 或 `"RNA"`，默认 `"DNA"`
- `data.extra.use_pipeline`
  - 是否启用 `UnifiedDataPipeline`，默认 True
- `data.extra.use_adapter`
  - 是否启用 biology adapter
- `data.extra.model_name`
  - 默认 `"evo2"`，但当前 adapter registry 未注册该名称
- `data.extra.use_msa`
  - genome pipeline 默认通常为 False
- `num_workers`
  - DataLoader 工作进程数
- Evo2 `SimpleFastaDataset`
  - `fasta_path`
  - `tokenizer`
  - `prepend_bos=True`

## 数据存储约定

- `GenomeDataset`
  - 文件路径是 FASTA 时直接解析
  - 目录路径时扫描 FASTA 文件
  - 当前目录扫描不递归
- `SimpleFastaDataset`
  - 使用 `NvFaidx` 读取 FASTA
  - `seqids` 来自 FASTA index keys，排序后作为 dataset index
- Evo2 训练 examples 支持：
  - 原始 FASTA 预处理
  - 预处理 JSON 转 mmap dataset

## 样本构造方式

- `GenomeDataset._load_data_list`
  - 每条序列构造 `sequence`, `description`
  - 目录输入额外保留 `file_path`
- `GenomeDataset.__getitem__`
  - 若有 adapter，调用 `adapter.process_sample(sample)`
  - 若有 pipeline，输出 `aatype`, `sequence`, `sequence_length`
  - 否则返回原始 sample
- `NucleotideEncoder`
  - DNA vocab: `A, T, G, C, N, -`
  - RNA vocab: `A, U, G, C, N, -`
  - vocab size: `6`
- `SimpleFastaDataset.__getitem__`
  - FASTA sequence 转大写
  - tokenizer 转 `tokenized_seq`
  - 若 `prepend_bos=True`，首位加 `tokenizer.eod`
  - 返回 `tokens`, `position_ids`, `seq_idx`, `loss_mask`

## DataLoader 约定

- `get_genome_dataloader(configs)`
  - dataset: `GenomeDataset(configs)`
  - sampler: `DistributedSampler(..., shuffle=False)`
  - batch size: `1`
  - collate: 原样保留 list batch
- Evo2 examples 的训练 loader 由 NeMo / Megatron 数据模块和预处理数据格式决定，不由 `get_genome_dataloader` 完整覆盖

## 适合优先使用的场景

- 需要简单读取 FASTA 并做 DNA/RNA 数值编码
- 需要先搭建一个 genome dataset skeleton，再自定义 Evo2 或其它模型 adapter
- Evo2 推理中需要用 FASTA 生成 `tokens/position_ids/loss_mask`
- 基因组训练数据需要先走 examples 中 FASTA 或 JSON 预处理脚本

## 风险点

- `GenomeDataset` 的 pipeline 使用 `UnifiedDataPipeline`，其中 `process_sequence` 默认是氨基酸编码器语义；用于 Evo2 时应优先使用 Evo2 tokenizer 路线或自定义 adapter
- adapter registry 当前没有注册 `evo2` adapter，`use_adapter=True` 且 `model_name="evo2"` 会失败
- `SimpleFastaDataset` 注释说明当前不直接覆盖 pretraining / fine-tuning 的 label offset 需求
- Evo2 依赖 `bionemo`, `nemo`, `megatron` 生态，数据协议不能简化为普通 `torch.utils.data.Dataset` 即可训练

## 源码锚点

- `./onescience/src/onescience/datapipes/biology/datasets/genome_dataset.py`
- `./onescience/src/onescience/datapipes/biology/common/sequence/sequence_encoder.py`
- `./onescience/src/onescience/datapipes/biology/dataloader.py`
- `./onescience/src/onescience/models/evo2/data/fasta_dataset.py`
- `./onescience/src/onescience/models/evo2/data/tokenizer.py`
