## content_principle

Carbon hg38 参考序列与预计算 VEP 结果包。Carbon/GENERator 本地 variant-effect-prediction 资源原语，分别登记 hg38 参考序列与 ClinVar 预计算模型结果，说明与 coding 子集、ref/alt 序列重建和新模型评测的关系。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/eval/variant-effect-prediction`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。读取 README 与两个 Parquet footer，核实大小写字段、行数及预计算结果列。卡片版本描述原语修订，不代表上游数据发布版本。

## data_schema

hg38.parquet 只有 **`ID,Sequence`**（大小写不可改），为 string 参考序列记录。ClinVar_VEP_results 为 `chrom,pos,ref,alt,label,type,refseq_id` 及 CADD/phyloP/phastCons/GPN-MSA/NT/HyenaDNA/Evo2/GENERator 等预计算分数，没有 ref_seq/var_seq 窗口。二者是不同样本单位。

## directory_layout

```text
variant-effect-prediction/
├── README.md
├── hg38.parquet
└── ClinVar_VEP_results.parquet
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

两个 Parquet：一个是大参考序列字符串表，另一个是位点与历史预测分数表。不要将两表直接按行号 join。

## scale_spec

footer 核实参考表 24 行、结果表 40,976 行。24 是参考记录数，不是变异数量；结果表与 clinvar-vep/coding 的 39,473 行不等规模，不能声明完全相同。

## coverage_spec

README 引用 NCBI GCF_000001405.40 参考来源和 SongLab ClinVar 评测表，并说明比较多个已有基因组模型。与 datasets/clinvar_vep 卡的专门 coding/non-coding 测试配置相关，但不构成相同版本证明。

## label_spec

参考表没有监督标签。结果表 label 与历史分数分别保留，label 详细映射需与 SongLab 来源协议核对；历史分数列不能作为新模型零样本输入。

## split_strategy

README 将 hg38 与 ClinVar_VEP_results 均列为 test 存储配置，但参考表的 test 标记不是监督测试样本划分。结果表用于历史结果复核；新划分或校准必须另定并防止位点泄漏。

## constraints

Sequence 为可能很长的字符串，流式/选择性读取，不一次复制整个参考到内存。基因组 ID、pos 坐标、assembly、ref 匹配未确认前不能据此为任意 ClinVar 表生成窗口。
