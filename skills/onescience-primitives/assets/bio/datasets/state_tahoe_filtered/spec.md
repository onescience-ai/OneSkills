## content_principle

State Tahoe 过滤后 smoke 数据。State Tahoe 本地 c36/c39/c44 单细胞药物扰动 smoke 数据，描述药物及剂量组合、细胞系、plate 和 HVG/State 表示，用于受控接口检查与局部泛化评测。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/State_dataset/State-Tahoe-Filtered-smoke`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。依据 State README 和全部三个 H5AD 的维度、字段、编码与类别元数据。卡片版本描述原语修订，不代表上游数据发布版本。

## data_schema

三文件 X 均为 CSR；obs 含 `drugname_drugconc,drug,cell_line,plate,gene,gem_group` 及 QC 字段；var 无额外列，读取索引确认基因；obsm 含 `X_hvg,X_state`。`drugname_drugconc` 保留药物、浓度、单位组合的字符串，不是单一药物 ID。

## directory_layout

```text
State-Tahoe-Filtered-smoke/
├── c36.h5ad
├── c39.h5ad
└── c44.h5ad
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

AnnData/HDF5 稀疏矩阵及 obsm 派生表示；本地只有 smoke 子集。

## scale_spec

HDF5 X 维度：c36 为 39,463×62,710；c39 为 30,394×62,710；c44 为 163,938×62,710。合计存储 233,795 行，不能等同于完整 Tahoe 图谱规模。

## coverage_spec

药物处理响应和 State HVG/SE 路线的接口检查。本地 State 总 README 将其用于 Tahoe 泛化/holdout，但该 smoke 目录未自带 Parse 那样的 TOML split。

## label_spec

输出目标为表达响应；drug、剂量/单位组合、cell_line 和 plate 是条件/分组。先从实际条件列表确认 control，不能用空字符串或任意药名作默认控制。

## split_strategy

不将 c36/c39/c44 名称自行解释为 train/validation/test。正式划分须绑定 Tahoe 实验配置或显式固定细胞系、药物/剂量和 plate holdout；smoke 结论只覆盖本地子集。

## constraints

同一药物不同剂量不可静默合并；相同基因维度不证明三文件基因顺序一致。X_hvg/X_state 与 X 采用不同坐标语义，使用前核对。
