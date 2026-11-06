## content_principle

IGGM SAb-23 抗体/纳米抗体设计输入集。IGGM 本地 SAb-23-H2-Ab/Nano 抗体设计数据原语，绑定 native FASTA/PDB、prot_ids 与含 X 掩码的 CDR design FASTA，区分重轻链/抗原及两子集不同的 PDB 目录名。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/IGGM/dataset`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。核实 prot_ids/PDB/FASTA 数量，抽查两子集 native 链与 Ab h_cdr3 设计掩码。卡片版本描述原语修订，不代表上游数据发布版本。

## data_schema

prot_ids.txt 为复合物身份列表；native/design FASTA 使用 `>H`（重链）、`>L`（轻链，Nano 样本无该链）、`>A`（抗原）。抽查 native PDB 亦有 H/L/A 或 H/A 链，具体每个复合物仍需验证。design FASTA 的 CDR 区可含 `X` 掩码，不是已生成的完整设计序列。

## directory_layout

```text
IGGM/dataset/
├── SAb-23-H2-Ab/
│   ├── prot_ids.txt
│   ├── fasta.files.native/
│   ├── pdb.files.native/
│   └── fasta.files.design/{all_cdr,h_cdr1,h_cdr2,h_cdr3,l_cdr1,l_cdr2,l_cdr3}/
└── SAb-23-H2-Nano/
    ├── prot_ids.txt
    ├── fasta.files.native/
    ├── pdb.native.files/
    └── fasta.files.design/{all_cdr,h_cdr1,h_cdr2,h_cdr3}/
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

多记录 FASTA、PDB 与文本 ID 清单；按同一 prot_id 连接 native 序列、结构和各掩码设计输入。IGGM/checkpoints.tar.gz 是模型资源，不属于本数据集样本。

## scale_spec

Ab 的 prot_ids、native PDB、native FASTA 均为 60；Nano 对应均为 27。本轮抽查 native 与设计 FASTA、PDB 链；未完整核实所有设计目录的配对覆盖。

## coverage_spec

抗体-抗原和单域抗体-抗原复合物的 CDR 条件设计/序列恢复。目录名包含 SAb，但来源快照、结构筛选标准和 SAbDab 版本未核实，不称为 SAbDab 官方全集。

## label_spec

native 序列/结构为参考目标；design FASTA 的 X 标记待设计区域，非模型成功生成结果。CDR 的 Kabat/IMGT/Chothia 等编号体系未核实，不能仅据 h_cdr3 目录名宣布具体残基边界。

## split_strategy

Ab/Nano 是对象类型分组，各 CDR 目录是同一复合物的设计设置，不是 train/test。未发现已核实 split 清单；若学习则按复合物/同源簇分割，保证同一 native 的掩码变体同组。

## constraints

两子集 PDB 目录名不同，loader 必须显式分派。文件名中的 NA 不代表实际轻链。X 掩码必须保留给设计 adapter，不能删除后改变序列与坐标长度。
