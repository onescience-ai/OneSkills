## content_principle

Replogle-Nadig 多细胞系遗传扰动数据。State 本地 Replogle-Nadig 遗传扰动单细胞数据原语，覆盖 HepG2、Jurkat、K562、RPE1 及 replogle 汇总文件，区分 raw/normalized 版本和扰动、细胞系、基因轴。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/State_dataset/Replogle-Nadig-Preprint`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。读取 State README，并逐个核查五个 H5AD 的 dense 维度和 obs/var/obsm；未全量判断数值归一化。卡片版本描述原语修订，不代表上游数据发布版本。

## data_schema

X 均为 dense cells × genes。obs 共有 `gene,gene_id,transcript,gene_transcript,sgID_AB,cell_line,gem_group,UMI_count` 等；K562/RPE1 还含 `core_scale_factor,core_adjusted_UMI_count`。四个单细胞系文件 var 含 `gene_name,chr,start,end,class,strand` 等；汇总 replogle.h5ad 的 var 是 HVG 统计列，obsm 有 `X_hvg`。

## directory_layout

```text
Replogle-Nadig-Preprint/
├── GSE264667_hepg2_raw_singlecell_01.h5ad
├── GSE264667_jurkat_raw_singlecell_01.h5ad
├── K562_essential_normalized_singlecell_01.h5ad
├── rpe1_normalized_singlecell_01.h5ad
└── replogle.h5ad
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

H5AD/HDF5 dense X，采用 backed 和按行分块读取。源文件名包含 raw/normalized 线索，但具体数值处理需结合上游协议确认。

## scale_spec

HepG2 145,473×9,624；Jurkat 262,956×8,882；K562 310,385×8,563；RPE1 247,914×8,749；汇总 replogle 643,413×6,642。不能将汇总文件与四文件行数相加作为独立细胞总数。

## coverage_spec

遗传扰动响应预测、跨细胞系泛化和 State HVG/SE 接入。目录包含不同预处理视图，并非五个互不重叠的独立队列。

## label_spec

gene/gene_id、sgID_AB 等描述干预身份，表达是响应目标，cell_line 为分组；control/non-targeting 的实际取值需独立核查。obs.gene 不是表达矩阵的 var 基因顺序。

## split_strategy

本地文件名没有统一 train/test 定义。按实验协议固定干预基因/细胞系 holdout，排除汇总视图与源文件之间的重复泄漏，不将五文件随机混合划分。

## constraints

raw 与 normalized 文件不可在未统一处理口径时直接合并。各文件基因维度不同，汇总文件也不能被当成四个文件的简单拼接。所有尺度拟合和 HVG 选择应明确训练来源。
