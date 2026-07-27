## content_principle
MACE 数据集原语描述 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/mace` 下的 MACE 训练与验证数据。该集合包含 ANI1x 量化化学数据、水体系、DMC 溶剂和 nanotube 结构，主要用于 equivariant 原子势模型的能量/力监督训练。

## data_schema
数据以多种格式存在：

- `extxyz`：ASE 可读的多帧结构文件，通常包含元素、坐标、能量、原子力、晶胞和 PBC 等属性。
- `HDF5`：ANI1x 的 train/val/test 分片，文件名按 split 和 shard 编号组织。
- `JSON statistics`：ANI1x 数据统计文件，可用于归一化、元素参考能量或数据质量检查。

MACE 消费时应转换为 AtomicData/PyG 风格字段：

```text
atomic_numbers / species
pos
cell
pbc
energy
forces
batch
natoms
```

## directory_layout
```text
/matchem/mace
├── ani1x
│   ├── ANI1x_cc_DFT_rc5_train/train_0.h5 ... train_7.h5
│   ├── ANI1x_cc_DFT_rc5_val/val_0.h5 ... val_7.h5
│   ├── ANI1x_cc_DFT_rc5_test/Default__0.h5 ... Default__7.h5
│   ├── ANI1x_cc_DFT_rc5_statistics.json
│   ├── ani1x_cc_dft.xyz
│   ├── ani1x_train.xyz
│   └── ani1x_test.xyz
├── water
│   ├── dataset_1593.xyz
│   ├── water_train.xyz
│   ├── water_test.xyz
│   └── gene_xyz.py
├── DMC
│   ├── solvent_xtb_train_200.xyz
│   └── solvent_xtb_test.xyz
└── nanotube
    ├── nanotube_large.xyz
    └── nanotube_test.xyz
```

## storage_format
`*.xyz` 和 `*.extxyz` 路径可优先通过 ASE 读取；HDF5 分片需要先确认内部 group/dataset 名称，再写入专用 adapter。`ani1x_train.xyz`、`ani1x_test.xyz` 已提供显式 split；HDF5 目录也按 train/val/test 分片。

## scale_spec
ANI1x HDF5 当前按 8 个 train shard、8 个 val shard 和 8 个 test shard 组织；water、DMC 和 nanotube 子集按单个或少量多帧 xyz 文件组织。实际样本数应通过 ASE 逐帧计数或 HDF5 内部索引统计。

## coverage_spec
覆盖有机分子量化化学、水体系、溶剂分子和纳米管结构，适合评估 MACE 类 E(3) 等变模型对分子势能面、周期/非周期结构和跨体系泛化的支持。

## label_spec
核心标签为结构级能量和原子级 forces。部分 extxyz 可能还携带 lattice、pbc、stress 或其它元数据；训练脚本应按文件实际 properties 读取，缺失字段不得静默补监督标签。

## split_strategy
优先使用文件名和目录中已有 split：

- ANI1x：`ANI1x_cc_DFT_rc5_train`、`ANI1x_cc_DFT_rc5_val`、`ANI1x_cc_DFT_rc5_test`。
- water：`water_train.xyz` 与 `water_test.xyz`。
- DMC：`solvent_xtb_train_200.xyz` 与 `solvent_xtb_test.xyz`。
- nanotube：`nanotube_large.xyz` 可作训练或大样本来源，`nanotube_test.xyz` 作测试。

## constraints
- 不同子集的能量标尺、元素覆盖和边界条件可能不同，混合训练前必须建立 dataset 标识和采样比例。
- HDF5 与 extxyz 不应假设字段名完全一致，需要单独探测。
- MACE 训练中的 `r_max`、元素表、平均能量和尺度参数应来自对应子集统计。
- 非周期分子若没有有效晶胞，需要在 datapipe 中居中并构造足够大的 cell。
