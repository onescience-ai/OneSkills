## content_principle

Nucleotide Transformer 下游序列分类任务集。Carbon 本地 Nucleotide Transformer 下游 18 项 DNA 分类数据原语，登记 Parquet/FNA 双格式、sequence/name/label/task 与 train/test 划分，明确与 HyenaDNA 同类分支需核验后复用。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/finetune/nucleotide_transformer_downstream_tasks`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。完整核对本地 36 个 Parquet 的 schema/行数并确认 FNA 路径；跨 HyenaDNA 快照未做内容一致性验证。卡片版本描述原语修订，不代表上游数据发布版本。

## data_schema

所有已核查 Parquet 均为 `sequence:string,name:string,label:int32,task:string`，一行是一条序列及任务内类别。配套 `.fna` 是文本序列视图，不能假设单独读取 FNA 就具备与 Parquet 相同的 label/task 列。

另登记 `Carbon/finetune/smoke/gue_promoter/{train,test}.jsonl`：实际字段为 `sequence,name,label,task`，两文件 task 均为 `promoter_all`。该入口虽命名 gue_promoter，具体上游来源未核实，作为独立 smoke 样例接入，不据名称认定它与 GUE 或 NT 正式快照等价。

## directory_layout

```text
nucleotide_transformer_downstream_tasks/
├── README.md
├── H3*/{train,test}.{parquet,fna}
├── H4{,ac}/{train,test}.{parquet,fna}
├── {enhancers,enhancers_types}/{train,test}.{parquet,fna}
├── promoter_{all,no_tata,tata}/{train,test}.{parquet,fna}
└── splice_sites_{acceptors,all,donors}/{train,test}.{parquet,fna}
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

Parquet 与 FNA 两种本地视图；每个任务有 train/test，两种格式不能作为独立样本重复计数。

## scale_spec

本轮核实 18 个任务目录、36 个 Parquet footer，schema 相同；每个任务另有 train/test FNA。样本规模按任务报告，不把各任务总行数当独立 DNA 序列数。另有本地 JSONL smoke train 128 行、test 64 行，全部序列 300 bp，仅用于接口检查，不计入正式 NT/GUE 基准。

## coverage_spec

10 个组蛋白任务 H3/H3K14ac/H3K36me3/H3K4me1/H3K4me2/H3K4me3/H3K79me3/H3K9ac/H4/H4ac，加 enhancers、enhancers_types、3 个 promoter 与 3 个 splice_sites 任务。HyenaDNA/nucleotide_transformer 是已有相关本地入口，文件身份和任务名须另行比较。

## label_spec

label 是任务内分类 ID，task/name 保留；不同任务同一个 label 值不等价。enhancers_types 等可能为多分类，精确类数/语义与任务说明及完整值域核验后固定。

## split_strategy

保留每任务 train/test，没有本地统一 validation 文件。需要验证集时仅从 train 按来源/序列组划分，报告派生协议；不得从 test 调参。

## constraints

该集合不能因为包含 promoter/组蛋白任务就冒称 GUE 或 BEND。HyenaDNA 中存在 enhancer 等目录命名差异，未经内容比对不能自动认定为同一快照或互换 split。
