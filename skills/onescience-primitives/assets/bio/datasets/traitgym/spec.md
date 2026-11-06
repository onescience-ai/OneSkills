## content_principle

TraitGym hg38 非编码变异效应评测。Carbon 本地 TraitGym Mendelian/complex traits 非编码变异评测数据，绑定 hg38 8192 bp ref/alt 窗口、因果标签与 match_group，保留匹配对照和全测试集评测协议。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/eval/traitgym`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。读取本地 README 和三个 Parquet footer；未全量复核全部窗口中心。卡片版本描述原语修订，不代表上游数据发布版本。

## data_schema

`chrom:string,pos:int64,ref:string,alt:string,label:int64,class:string,consequence:string,tss_dist:int64,match_group:string,ref_seq:string,var_seq:string,score`。complex 的 score 为 double，Mendelian 的 score 为 null。README 定义 pos 是 1-based hg38，ref_seq/var_seq 为 8192 bp、变异位于 0-based 索引 4096 的窗口。

## directory_layout

```text
Carbon/eval/
├── traitgym/
│   ├── README.md
│   ├── mendelian_traits_vep.parquet
│   └── complex_traits_vep.parquet
└── smoke/traitgym_mendelian.parquet
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

Parquet，一行是一项 SNV 及参考/变异窗口、匹配组和标签。

## scale_spec

Parquet footer 核实 Mendelian 3,380 行、complex 11,400 行；smoke 16 行。README 声明分别有 338 与 1,140 个候选因果变异，并匹配 9 倍对照；比例应在正式消费时再验证。

## coverage_spec

本地 README 声明重打包 songlab/TraitGym 的 matched_9 配置：Mendelian 疾病与复杂性状的非编码变异。参考窗口为 hg38，不与 BRCA2 的 hg19 缓存混用。

## label_spec

README 定义 label=1 为候选因果/阳性、0 为匹配对照，class 的 LOF/FUNC/INT 是评测兼容编码，并非所有位点的分子功能实验结论。complex score 是 PIP，不能当作模型预测分数。

## split_strategy

两个配置均为 test 评测入口，smoke 是独立接口样例。保留 match_group；若另做拟合/校准，按组和位点隔离并另命名协议，不拆散一组的因果变异与匹配对照。

## constraints

完整性检查须确认 ref/alt 与窗口中心、长度和参考一致。不要把 score/PIP 当作输入特征泄漏标签。跨染色体指标汇总与匹配分组均须遵循选定协议。
