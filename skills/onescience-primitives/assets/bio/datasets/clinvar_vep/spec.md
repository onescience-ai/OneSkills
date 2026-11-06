## content_principle

ClinVar coding/non-coding 变异评测表。Carbon 本地 ClinVar VEP coding 与 non-coding 评测数据原语，区分坐标标签表、预计算模型分数和非编码质控注释，说明缺少直接 ref/alt 序列窗口及参考版本核对要求。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/eval/clinvar-vep`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。读取本地 README 与四个完整/烟测 Parquet footer，确认列差异及没有窗口列。卡片版本描述原语修订，不代表上游数据发布版本。

## data_schema

coding 包含 `chrom,pos,ref,alt,label`、`type,refseq_id`，以及 CADD、phyloP、phastCons、GPN-MSA、NT、NT-v2、HyenaDNA、Evo2、GENERator 等来源模型分数。non_coding 包含坐标/等位基因、`gene_symbol,clinical_significance_terms,pathogenicity_group,qc_star_rating,qc_review_level,qc_is_reviewed,qc_is_high_confidence_review,variant_type,consequence_terms,region_group,region_subtype,coding_status,label`。两者均没有 `ref_seq,var_seq` 列。

## directory_layout

```text
Carbon/eval/
├── clinvar-vep/
│   ├── README.md
│   ├── coding/clinvar_coding.parquet
│   └── non_coding/clinvar_non_coding.parquet
└── smoke/clinvar_{coding,non_coding}.parquet
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

Parquet 变异位点表，部分字段为 list<string>，已有模型分数为数值列。重新跑序列模型前需在正确版本的参考基因组上生成 ref/alt 窗口。

## scale_spec

footer 核实 coding 39,473 行、non_coding 15,258 行，两个 smoke 各 16 行。README 列出 coding benign/pathogenic 为 17,231/22,242，non-coding 为 7,629/7,629；因此不能将 coding 宣称为严格平衡。

## coverage_spec

ClinVar 致病/可能致病与良性/可能良性二分类；coding 来源与 GenerTeam variant-effect-prediction 有关系，non-coding 为另行筛选的 reviewed intronic/UTR 变异。不是所有 ClinVar 记录的完整镜像。

## label_spec

依据本地 README，label=1 表示 pathogenic/likely pathogenic，0 表示 benign/likely benign。来源模型分数、review 和 consequence 是额外注释，不能默认作为无泄漏模型输入。

## split_strategy

本地 README 将两个配置均注册为 test。不是现成的训练/验证划分。比较历史模型分数或重新打分时使用同一位点清单和缺失值政策，smoke 不替代全量测试。

## constraints

不能把含模型分数的表当成原始序列训练集。重建窗口前必须确认参考基因组版本、pos 的坐标约定及 ref 一致性，不能仅因旁边有 hg38 文件就默认所有位点兼容。clinical 标签不等同于实验功能强度。
