## content_principle

Carbon 多来源基因组预训练语料。Carbon 本地 DNA/转录本预训练集合，覆盖 GENERator 真核语料及 10B 子集、Evo2 mRNA/splice/原核语料和 smoke 数据，区分 sequence 与 text schema、元数据标签和特殊分隔符。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/pretrain`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。读取来源 README，并对每个语料叶目录的一个 Parquet footer 核对 schema，抽查 smoke JSONL。卡片版本描述原语修订，不代表上游数据发布版本。

## data_schema

| 语料 | 已核查 Parquet 字段 |
| --- | --- |
| eukaryote_generator 及 10B_subset | `sequence`、`begin_of_sequence,end_of_sequence,begin_of_gene,end_of_gene,gene_type,species_type,strand,molecule_type,topology,taxonomy,record_id,start,end` |
| mrna_evo2 / mrna_splice_evo2 | `text,id,metadata`，metadata 含 `source` |
| prokaryote_evo2 | `text,id,metadata`，metadata 含 `record,source` |

样本为序列记录/片段，非统一长度或统一基因单位。smoke JSONL 已观察到 `text` 列；预 token 化 bin/idx 是派生训练输入，需配套 tokenizer。

## directory_layout

```text
Carbon/pretrain/
├── carbon-pretraining-corpus/
│   ├── README.md
│   ├── eukaryote_generator/<species_group>/*.parquet
│   ├── eukaryote_generator_10B_subset/<species_group>/*.parquet
│   ├── mrna_evo2/*.parquet
│   ├── mrna_splice_evo2/*.parquet
│   └── prokaryote_evo2/*.parquet
└── smoke/
    ├── carbon_smoke.jsonl
    ├── carbon_smoke_text_document{,_mask}.{bin,idx}
    └── cache/
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

Parquet 行组及 JSONL、Megatron 类 indexed bin/idx。Parquet 优先分批读取 sequence/text，不能将数 GB 文件全读进内存。smoke/cache 是运行派生索引，不能当作额外原始样本。

## scale_spec

本轮对 15 个语料叶目录各抽查一个 Parquet footer，未全量重计。来源 README 将 10B 子集描述为 6,562,876 行、60.0 Gbp，10B 指其 6-mer tokenization 预算，不是 100 亿条序列；该规模属于文档声明。

## coverage_spec

真核分组为 fungi、invertebrate、plant、protozoa、vertebrate_mammalian、vertebrate_other。README 将 GENERator 真核语料与 OpenGenome2 的 mRNA、带剪接增强 mRNA 和原核语料组成混合预训练集合。

## label_spec

没有统一监督分类标签；训练目标由因果语言建模构造。README 描述真核可加入 species/gene_type 元数据条件，mRNA splice 可含 `@` 拼接分隔符，不能强制把所有非 ACGT 字符删除。基因边界与元数据字段不是直接附加的生物功能标签。

## split_strategy

本地顶层语料目录和 shard 号不代表官方 train/validation/test。按记录、contig 或物种固定 holdout 与随机种子，避免同一来源片段跨 split；10B_subset 是原真核语料的子集，不能与完整真核语料当独立评测集。

## constraints

不同来源使用不同列与文本包装；保留 `@`、物种/基因标签的语义并核对 tokenizer。来源 README 的混合比例和 6-mer 预算是训练配方，不应当成每个本地 shard 的统计。不同上游许可证分别继承。
