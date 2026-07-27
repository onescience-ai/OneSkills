## content_principle
OC20 数据集原语描述 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/oc20` 下的 S2EF 子集和 UMA 微调数据。它支持从吸附-催化结构到能量与力的监督学习，也支持 UMA 的 ASE LMDB 数据入口。

## data_schema
该目录包含两类数据入口：

- `extxyz` 解压结构：`s2ef_200k_uncompressed` 和 `s2ef_val_id_uncompressed`，每个文件可包含一个或多个结构帧。
- `ASE LMDB`：`uma_oc20_finetune/train` 与 `uma_oc20_finetune/val` 下的 `data.000*.aselmdb` 分片，配套 `metadata.npz`。

UMA 微调目录还包含：

- `data/uma_conserving_data_task_energy_force.yaml`：能量/力任务数据配置。
- `uma_sm_finetune_template.yaml`：小模型微调模板。
- `.lock`、`.failed`、`.log`：数据库生成或校验伴随文件，不应作为样本读取。

## directory_layout
```text
/matchem/oc20
├── s2ef_200k_uncompressed
│   ├── 0.extxyz
│   └── 1.extxyz
├── s2ef_val_id_uncompressed
│   ├── 0.extxyz
│   ├── 1.extxyz
│   ├── 2.extxyz
│   └── 3.extxyz
├── orig_data
│   ├── s2ef_200k_uncompressed
│   └── s2ef_val_id_uncompressed
└── uma_oc20_finetune
    ├── data/uma_conserving_data_task_energy_force.yaml
    ├── train/{data.0000.aselmdb ... data.0007.aselmdb, metadata.npz}
    ├── val/{data.0000.aselmdb ... data.0007.aselmdb, metadata.npz}
    └── uma_sm_finetune_template.yaml
```

## storage_format
`extxyz` 可用 ASE 读取；`aselmdb` 应通过 OneScience materials datapipe 的 ASE LMDB storage 读取。`metadata.npz` 用于样本数量、原子数或其它筛选信息时，应与同一 split 的 LMDB 分片配套使用。

## scale_spec
当前浅层 `s2ef_200k_uncompressed` 有 2 个 extxyz 文件，`s2ef_val_id_uncompressed` 有 4 个 extxyz 文件；`orig_data/s2ef_val_id_uncompressed` 有 200 个 extxyz 文件；UMA train/val 各有 8 个 `aselmdb` 分片。实际样本数以 extxyz 帧数或 LMDB 索引为准。

## coverage_spec
覆盖 OC20 S2EF 任务的吸附体系、催化表面和结构松弛相关样本，可用于能量预测、原子力预测、UMA 多任务微调和材料势模型验证。

## label_spec
核心标签为结构级能量和原子级 forces。OC20/UMA 样本还可能包含 fixed atoms、tags、sid/fid、cell、pbc 等字段；这些字段会影响表面/吸附体系构图和 loss mask，读取时应保留。

## split_strategy
浅层 `s2ef_200k_uncompressed` 可作为训练子集，`s2ef_val_id_uncompressed` 可作为验证子集；UMA 微调应直接使用 `uma_oc20_finetune/train` 和 `uma_oc20_finetune/val`。不要把 `orig_data` 和浅层解压目录重复计入同一次训练，除非确认它们不是同一数据的副本。

## constraints
- `.lock`、`.failed`、`.log` 文件不是样本文件。
- extxyz 与 ASE LMDB 可能表达同源样本，混合使用前必须去重或标记来源。
- 固定原子、tags、PBC 和 cell 语义不能丢失，否则 OC20 表面体系训练会偏离任务定义。
- `metadata.npz` 与 LMDB 分片必须来自同一 split。
