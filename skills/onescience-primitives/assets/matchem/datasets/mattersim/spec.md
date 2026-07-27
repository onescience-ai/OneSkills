## content_principle
MatterSim 数据集原语描述 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/mattersim` 下的高精度水体系 extxyz 数据。该集合面向 MatterSim 或通用材料势模型微调，提供周期水盒的能量和力监督。

## data_schema
`high_level_water.xyz` 为 extxyz 多帧文件。已观测首帧头信息：

```text
192
Lattice="13.7044938 ... 13.7044938" Properties=species:S:1:pos:R:3:forces:R:3 energy=-30011.49340274 cutoff=-1.0 nneightol=1.2 pbc="T T T"
```

单帧包含：

- 原子数：192。
- `species`：元素符号。
- `pos`：三维坐标。
- `forces`：三维原子力。
- `energy`：结构级能量。
- `Lattice`：三乘三晶胞。
- `pbc`：周期边界条件，样例为 `T T T`。
- `cutoff`、`nneightol`：构图或邻居相关元数据。

## directory_layout
```text
/matchem/mattersim
└── high_level_water.xyz
```

## storage_format
主格式为 extxyz，可通过 ASE 逐帧读取。读取后应转换为 AtomicData 字段：`atomic_numbers`、`pos`、`cell`、`pbc`、`energy`、`forces`、`natoms`、`batch`。

## scale_spec
当前目录包含一个多帧 extxyz 文件。实际样本数需要通过 ASE 或 extxyz parser 统计帧数，不应只按文件数估计。

## coverage_spec
覆盖周期水体系，适用于水分子动力学势能面微调、能量/力联合训练、邻居截断敏感性测试和 MatterSim pipeline smoke test。

## label_spec
监督标签为结构级 `energy` 和原子级 `forces`。该文件提供晶胞与 PBC，可用于周期构图。未观测到 stress 标签时，不应启用应力损失。

## split_strategy
若用于正式训练，应按帧索引做连续区间划分或预先固定随机种子抽样。对于 MD 轨迹型数据，优先使用时间隔离划分，避免相邻帧泄漏导致测试误差偏低。

## constraints
- 单帧 192 原子，batch 大小时需要考虑邻接边数量和显存。
- extxyz properties 是字段权威来源，不能假设所有帧都含同样的可选字段，首次接入需逐帧抽检。
- 若将数据与其它水体系混合训练，需核对能量单位和零点。
