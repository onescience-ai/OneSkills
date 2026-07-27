
## content_principle
HyenaDNA 基因组 benchmark 集合 面向 biology 任务中的数据接入、检索、预处理和模型消费，核心目标是把 `/public/share/sugonhpcapp01/onestore/onedatasets/HyenaDNA` 中的真实目录组织成可复用的原语知识。

## data_schema
典型样本是序列、标签和任务划分，部分任务还会带染色体或物种元信息。

## directory_layout
```text
/HyenaDNA
├── genomic_benchmark/
│   ├── demo_*_v0.zip
│   ├── human_*_v0.zip
│   └── <task>/{train,test}/
├── species/
├── hg38/
└── nucleotide_transformer/
```

## storage_format
主要格式为 FASTA/文本序列、压缩 benchmark 包和任务级 train/test 分割；下游通常转换为 token、label 和 sequence length。

## scale_spec
规模特征以具体数据源为准：结构库通常按样本 ID 或链 ID 组织；蛋白-配体数据通常按复合物目录或 LMDB 组织；基因组数据通常按染色体、物种或 benchmark split 组织。

## coverage_spec
适用于启动子识别、增强子预测、基因组分类、物种分层和长序列语言建模。

## label_spec
若为训练集，标签可能是序列、坐标、亲和力、分类标签、问答对或结构目标；若为数据库集合，则通常不提供显式监督标签。

## split_strategy
先根据 benchmark 名称确定任务，再选择 FASTA/片段化序列或 token 化输出；如果任务是长序列模型，应显式控制截窗和分块策略。

## constraints
先确认 train/test 目录和任务标签口径，再核对序列长度和物种分布。
