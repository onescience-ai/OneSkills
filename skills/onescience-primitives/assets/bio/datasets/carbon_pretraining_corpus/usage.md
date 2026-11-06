## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/Carbon/pretrain`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/pretrain`。



已绑定的资源入口：

- `Carbon/pretrain/carbon-pretraining-corpus/eukaryote_generator`
- `Carbon/pretrain/carbon-pretraining-corpus/eukaryote_generator_10B_subset`
- `Carbon/pretrain/carbon-pretraining-corpus/mrna_evo2`
- `Carbon/pretrain/carbon-pretraining-corpus/mrna_splice_evo2`
- `Carbon/pretrain/carbon-pretraining-corpus/prokaryote_evo2`
- `Carbon/pretrain/smoke`

## data_schema

| 语料 | 已核查 Parquet 字段 |
| --- | --- |
| eukaryote_generator 及 10B_subset | `sequence`、`begin_of_sequence,end_of_sequence,begin_of_gene,end_of_gene,gene_type,species_type,strand,molecule_type,topology,taxonomy,record_id,start,end` |
| mrna_evo2 / mrna_splice_evo2 | `text,id,metadata`，metadata 含 `source` |
| prokaryote_evo2 | `text,id,metadata`，metadata 含 `record,source` |

样本为序列记录/片段，非统一长度或统一基因单位。smoke JSONL 已观察到 `text` 列；预 token 化 bin/idx 是派生训练输入，需配套 tokenizer。

## task_usage

用于基因组语言模型语料适配和本地 smoke 读取。按来源分流提取 sequence/text，再由明确 tokenizer 与训练配方构造输入。

## integration_paths

来源选择 → sequence/text 解析 → 元数据包装与特殊字符协议 → 流式 tokenization/packing；预处理输出与模型 tokenizer 版本一起登记。

## preparation_requirements

核对每个来源的 schema、ID、坐标语义和字符集合，检查长序列及同源/重复记录；固定混合权重、边界处理和 holdout。复用 smoke bin/idx 前核实 tokenizer 与 mask 索引对应。

## consumption_interfaces

统一适配后的文本或 token 流，附来源、record_id/id、物种/基因元数据及划分；语言建模标签由 collator 构造，不能从目录补造分类 label。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

不同来源使用不同列与文本包装；保留 `@`、物种/基因标签的语义并核对 tokenizer。来源 README 的混合比例和 6-mer 预算是训练配方，不应当成每个本地 shard 的统计。不同上游许可证分别继承。
