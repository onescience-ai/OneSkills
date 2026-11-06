## content_principle

DNA Next K-mer 序列恢复与扩展视图。Carbon 本地 DNA Next K-mer Prediction 评测数据，覆盖 bacteria/eukaryote/others 的序列后续 128 bp 目标，并单列 schema 不同的 eukaryote/test_new 基因序列视图。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/eval/sequence-recovery`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。读取 README、四个 Parquet footer，并抽查 test_new 第一条，确认其 schema 与标准版不同。卡片版本描述原语修订，不代表上游数据发布版本。

## data_schema

三个标准 test 均有 `sequence:string,label:string`；bacteria 另有 record_id、taxonomy(list)、length、domain/phylum/class/type，others 有 record_id、taxonomy(list)、length、species_type，eukaryote 标准版仅再有 type。**test_new** 则为 `record_id,taxonomy:string,gene_type,species_type,strand,sequence,start,end,gene_sequence`，没有 label，taxonomy 类型也不同。

## directory_layout

```text
sequence-recovery/
├── README.md
├── bacteria/test.parquet
├── others/test.parquet
└── eukaryote/{test.parquet,test_new.parquet}
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

Parquet，标准 test 的 label 是 DNA 续写字符串；test_new 是单独的结构视图，不能套用同一 loader 假定存在 label。

## scale_spec

footer 核实 bacteria 26,267 行、others 23,938 行、eukaryote test 30,000 行、test_new 29,411 行。README 描述标准任务输入最长 96k bp、后续目标 128 bp；test_new 首条 sequence 长 192,000、gene_sequence 长 675，仅为抽查，不能据此宣称其符合标准 128 bp 任务。

## coverage_spec

来自 GENERator Next K-mer Prediction 的零样本基因组序列续写。test_new 提供基因片段及位置，但其任务与标准任务的对应关系本地 README 未说明。

## label_spec

标准 label 为紧接输入末端的后续 DNA 片段，不是分类 ID。test_new 中 gene_sequence 不能在未经协议说明时重命名成标准 label，也不能断言等于 sequence 的下一段。

## split_strategy

三个标准配置均为 test，无现成训练划分。test_new 是候选数据视图，不是天然 validation 或独立测试版本；未核实去重前不能合并规模。

## constraints

缩短标准输入时依据 README 采用 left truncation，保留靠近续写点的末端，并报告实际上下文长度。不能把 label 拼进模型输入，或把 gene_sequence 无依据截成 128 bp 目标。
