## content_principle

State Parse 过滤后 PBMC 扰动数据。State Parse Biosciences 人类 PBMC 单细胞扰动数据原语，绑定 parse_concat_full.h5ad 和 few-shot/zero-shot TOML，保留供体、细胞类型与细胞因子划分以及 HVG/State 表示。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/State_dataset/State-Parse-Filtered`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。读取 State 总 README、Parse README、代表性 few-shot/zero-shot TOML，并读取 HDF5 维度、字段和 categorical 元数据。卡片版本描述原语修订，不代表上游数据发布版本。

## data_schema

X 为 CSR cells × genes。已核实 obs 含 `donor,cytokine,treatment,cell_type,donor_ct,cell_type_clean,donor_ct_clean`；var 没有额外注释列，基因身份须读 var 索引；obsm 含 `X_hvg,X_state`。TOML 有 `[datasets]`、`[training]`、`[zeroshot]`、`[fewshot]`，fewshot 以 `parse.<group>` 索引并列出 val/test 扰动。

## directory_layout

```text
State-Parse-Filtered/
├── parse_concat_full.h5ad
├── README.md
├── CC-NC-4.0-License.txt
├── celltype{,_zeroshot}.toml
├── donor{,_zeroshot}.toml
└── split_<1..5>{,_zeroshot}.toml
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

H5AD/HDF5 + TOML 配置。以 backed 或稀疏分块读取，避免把约 342 GiB 文件直接整体载入内存。TOML 中 `/data/parse_final_concat` 为原环境路径，接入时在配置副本中重定位。

## scale_spec

X 元数据为 9,697,974 个细胞 × 18,308 个基因；donor categorical 有 12 个供体，cell_type 有 18 类，donor_ct_clean 有 216 组。这是存储维度/类别元数据，未重计所有有效样本。

## coverage_spec

Parse Evercode WT v3 人类免疫细胞 PBMC 数据；本地 README 指向 Parse Biosciences 数据页面（访问日期 2025-05-27）。服务 State 的细胞因子响应、供体/细胞类型 few-shot 与 zero-shot 泛化。

## label_spec

表达响应是目标，`cytokine/treatment` 是条件，`donor/cell_type` 是分组。TOML 的 `B_Intermediate_Memory` 对应 clean 列，不能拿原始含空格/斜杠值直接匹配；控制处理的实际值需从数据确认。

## split_strategy

沿用所选 TOML：training 默认 parse=train，zeroshot 将整个组指定为 test，fewshot 为该组分别指定 val/test 扰动。例如 split_1_zeroshot 将 parse.B_Intermediate_Memory 整组留出。细胞类型、供体和 split_1..5 方案分别使用，不叠加为一个随机细胞划分。

## constraints

obsm 的 X_hvg/X_state 是派生表示，不能与 X 的基因轴互换。不得将 TOML 中的组名未经映射直接匹配 obs。保留 CC-NC-4.0-License.txt 和 README 的使用限制；元信息 visibility=public 不改变数据条款。
