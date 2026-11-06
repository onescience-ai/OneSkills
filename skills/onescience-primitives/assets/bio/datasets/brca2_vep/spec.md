## content_principle

BRCA2 功能变异与成对窗口评测数据。Carbon 本地 BRCA2 VEP 表与来源缓存原语，绑定 6836 个变异的功能 score/class、8192 bp 成对窗口及 hg19 chr13/实验表缓存，区分实验功能类别和临床致病性。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/eval/brca2`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。核对 Parquet footer、完整 class 列、首条序列对和缓存文件存在性；未解析实验表以重建全部标签。卡片版本描述原语修订，不代表上游数据发布版本。

## data_schema

`chrom:int64,pos:int64,ref:string,alt:string,score:double,class:string,ref_seq:string,var_seq:string`。第一条窗口各 8192 bp；score 是来源功能测量/处理结果，class 为功能类别，不是模型输出。坐标协议与 score→class 阈值须从配套来源进一步核实。

## directory_layout

```text
Carbon/eval/
├── brca2/
│   ├── brca2_vep.parquet
│   └── brca2_cache/{chr13_hg19.fa,huang2025_brca2.xlsx}
└── smoke/brca2_vep.parquet
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

Parquet 变异与序列对，FASTA 参考缓存和 XLSX 实验来源缓存。xlsx/参考序列不是额外独立变异样本。

## scale_spec

footer 核实完整表 6,836 行，smoke 16 行；完整 class 列计数为 FUNC/INT 5,680、LOF 1,156。首条 class=FUNC/INT、ref_seq/var_seq 各 8192 bp；未全量复核窗口长度与中心。

## coverage_spec

BRCA2 变异功能影响评测与 DNA 模型对参考/变异序列打分。本地缓存名表明提供 hg19 chr13 和 Huang 2025 来源表，确切坐标/类别生成规则还需逐项对照。

## label_spec

class 保留原始功能类别，不默认映射为 ClinVar pathogenic/benign。score 的方向、阈值及类别合并方式未从当前缓存解析确认；不得将 score 当作新模型预测或输入特征。

## split_strategy

完整表为本地评测入口，没有显式 train/validation/test 列。smoke 仅支持接口检查。若用于学习，按位点/氨基酸或实验分组另定协议，不能把同位点变异泄漏到评测。

## constraints

重建窗口时先核实坐标与 hg19 参考缓存，不可与 TraitGym hg38 窗口混用。实验功能与临床致病性不同；阈值来源不清时只报告原始分数/类别。
