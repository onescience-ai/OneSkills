## content_principle

RoseTTAFold 本地 HH-suite 参考数据库包。RoseTTAFold 本地 BFD、PDB100_2021Mar03、UniRef30_2020_06 及 uniref30 别名参考数据库原语，登记 HH-suite 文件前缀、版本与软链接，明确别名实际指向 UniRef30_2021_03。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/RoseTTAFold`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。核对目录、非空大文件及全部别名软链接目标；未运行 HH-suite 查询。卡片版本描述原语修订，不代表上游数据发布版本。

## data_schema

HH-suite 参考库以 prefix + `_a3m/_hhm/_cs219` 的 `.ffdata/.ffindex` 成对组织，PDB100 另有 `_pdb.ffdata/.ffindex`。ffindex 定位条目 ID、偏移与长度，ffdata 为载荷；不是按行样本/label 表。

| 目录/入口 | 实际版本与前缀 |
| --- | --- |
| bfd | `bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt`，亦有 `bfd_*` 链接别名 |
| pdb100_2021Mar03 | `pdb100_2021Mar03` |
| UniRef30_2020_06 | `UniRef30_2020_06`，独立旧版文件 |
| uniref30/uniref30_* | 软链接到 `alphafold2.3.0/uniref30/UniRef30_2021_03_*` |

## directory_layout

```text
RoseTTAFold/
├── bfd/{bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt_*,bfd_*}
├── pdb100_2021Mar03/{pdb100_2021Mar03_*,LICENSE}
├── UniRef30_2020_06/{UniRef30_2020_06_*,UniRef30_2020_06.md5sums}
├── uniref30/uniref30_*                 # 指向 AF2 的 2021_03
├── tar/
├── new/
└── weights/                           # 权重，不是搜索库
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

HH-suite ffdata/ffindex 与已有归档，典型载荷很大。调用时给出工具要求的数据库前缀，不把某个 ffdata 路径误当 FASTA 输入；具体 hhsuite 版本和所需后缀由搜索器确定。

## scale_spec

已观察 BFD A3M ffdata 约 1.56 TB，PDB100 A3M 约 263 GB，UniRef30_2020_06 A3M 约 150 GB；这些是文件大小线索，不是序列条数。本次没有全库校验和或索引边界重算。

## coverage_spec

蛋白同源搜索、MSA 和结构模板检索；版本分别保留。bfd/bfd 还存在指向 AF2 BFD 的目录链接，不能递归算作第二个独立数据库。

## label_spec

参考库不提供统一监督 label 或训练 split。检索结果、比对和模板匹配由后续工具产生，不可把 PDB 条目存在性当作实验标签。

## split_strategy

参考数据库不是 train/test 数据。需要时间截止评测时按实际 release/条目日期约束检索范围，不能把 2021_03 别名宣称为 2020_06。

## constraints

检查软链接解析后的真实路径、成对文件、文件非空和搜索器版本兼容。归档/安装脚本、BLAST 程序和模型权重与参考库分开登记；存在 md5sums 不代表已执行校验。
