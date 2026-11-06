## content_principle

State SE-167M-Human smoke 单细胞与基因 embedding。State SE-167M-Human 本地 smoke 数据原语，绑定四个 scbasecount H5AD 样例与基因 embedding PT，明确基因映射、样例范围和无通用监督标签边界。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/State_dataset/SE-167M-Human-smoke`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。依据 State README、四个 H5AD 元数据和非空 PT 文件存在性；PT 内部未加载。卡片版本描述原语修订，不代表上游数据发布版本。

## data_schema

四个 H5AD 的 X 为 CSR，var 含 `gene_symbols,feature_types` 和 QC 列；obs 含 `SRX_accession,gene_count,umi_count` 及计数 QC。未见 cell_type 监督标签列，未见额外 layers。PT 为配套基因 embedding 资源，其对象布局、向量维度和基因键顺序本轮未反序列化确认。

## directory_layout

```text
SE-167M-Human-smoke/
├── all_embeddings_Preprint-SE-167M-Human.pt
└── 19k_human_filtered_scbasecount/
    ├── SRX10188960.h5ad
    ├── SRX10188961.h5ad
    ├── SRX10188962.h5ad
    └── SRX10188963.h5ad
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

H5AD 稀疏表达矩阵与 PyTorch PT embedding。先检查 AnnData 元数据，再由匹配模型的受控读取接口验证 PT，不根据文件名猜测 embedding shape。

## scale_spec

四文件分别 4,820、4,686、1,321、2,957 行，均为 18,635 个基因，合计 13,784 行。SE-167M 是来源名称，本地 smoke 并不包含 1.67 亿个细胞，目录名中的 19k 也不是本次实测细胞数。

## coverage_spec

人类单细胞表达编码和 State SE 路线接口检查；不等同于完整 CELLxGENE Census、SE-167M 或 SE-600M 训练语料。

## label_spec

主体为表达与 QC/来源元信息，没有统一细胞类型/扰动监督目标。embedding 的基因键须与 var 索引或经核实的 gene_symbols 映射对齐，不能按 PT 与矩阵行号偶然一致来连接。

## split_strategy

四个 SRX 文件表示来源入口，不是预设四折或 train/test。下游划分按 accession/研究来源固定，并记录 smoke 范围。

## constraints

四文件基因维度相同仍需核对索引顺序。不能将基因 embedding 当作细胞 embedding，也不能从 PT 文件名推断 token 字典。
