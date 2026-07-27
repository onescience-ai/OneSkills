
## content_principle
Evo2 长基因组样本集合 面向 biology 任务中的数据接入、检索、预处理和模型消费，核心目标是把 `/public/share/sugonhpcapp01/onestore/onedatasets/evo2/data_mini` 中的真实目录组织成可复用的原语知识。

## data_schema
样本通常是超长染色体序列、token 化结果和窗口化训练片段。

## directory_layout
```text
/evo2/data_mini
├── chr20.fa
├── chr20.fa.gz
├── chr21.fa
├── chr21.fa.gz
├── chr22.fa
├── chr22.fa.gz
├── chr20_21_22.fa
├── genome_data/
└── preprocessed_data/
```

## storage_format
核心为染色体 FASTA 与预处理后的长序列样本；训练前要明确 tokenizer、窗口长度、position id 和 loss mask。

## scale_spec
规模特征以具体数据源为准：结构库通常按样本 ID 或链 ID 组织；蛋白-配体数据通常按复合物目录或 LMDB 组织；基因组数据通常按染色体、物种或 benchmark split 组织。

## coverage_spec
适用于 Evo2 预训练、长上下文语言建模、基因组切窗和序列回归任务。

## label_spec
若为训练集，标签可能是序列、坐标、亲和力、分类标签、问答对或结构目标；若为数据库集合，则通常不提供显式监督标签。

## split_strategy
优先使用专用 tokenizer 和预处理后的窗口数据；若直接读 FASTA，必须先定义 token 化、截窗和 loss mask。

## constraints
先检查染色体 FASTA 是否完整，再确认预处理数据与 tokenizer 版本一致。
