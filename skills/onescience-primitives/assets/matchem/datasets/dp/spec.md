## content_principle
DP 数据集原语描述 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/dp` 下的 DeepMD 兼容材料势数据。它的核心价值是把水体系和 DPA3 微调体系的 `raw/npy` 目录组织、帧级坐标、晶胞、能量和力标签整理成可被势模型训练脚本消费的 schema。

## data_schema
样本以 DeepMD system 为基本单位。每个 system 目录通常包含：

- `type.raw`：原子类型索引，长度等于体系原子数。
- `type_map.raw`：原子类型到元素符号的映射；部分目录可能只在上层或部分 system 中出现。
- `set.000/coord.npy`：帧级原子坐标，shape 为 `[frames, atoms * 3]`。
- `set.000/box.npy`：帧级晶胞，shape 为 `[frames, 9]`。
- `set.000/energy.npy`：帧级总能量，shape 为 `[frames]`。
- `set.000/force.npy`：帧级原子力，shape 为 `[frames, atoms * 3]`。

已探测样例：

```text
water/data_0/set.000/coord.npy  : (80, 576), float32
water/data_0/set.000/box.npy    : (80, 9), float32
water/data_0/set.000/energy.npy : (80,), float32
water/data_0/set.000/force.npy  : (80, 576), float32
```

`576 = 192 * 3`，表示 water 样例每帧 192 个原子。

## directory_layout
```text
/matchem/dp
├── dpa3_finetune
│   ├── dpa3_ch_stat.hdf5
│   ├── train_data
│   │   ├── system_100
│   │   │   ├── type.raw
│   │   │   ├── type_map.raw
│   │   │   └── set.000/{box.npy, coord.npy, energy.npy, force.npy}
│   │   └── ...
│   └── val_data
│       ├── system_100
│       └── ...
└── water
    ├── data_0
    │   ├── type.raw
    │   ├── type_map.raw
    │   └── set.000/{box.npy, coord.npy, energy.npy, force.npy}
    ├── data_1
    ├── data_2
    └── data_3
```

## storage_format
主数据为 DeepMD `raw + npy` 格式；统计文件 `dpa3_ch_stat.hdf5` 可用于微调任务的元素统计、归一化或参考检查。DeepMD 的坐标和力通常是扁平数组，接入 AtomicData 时需要 reshape 为 `[frames, atoms, 3]`。

## scale_spec
`water` 子集包含 `data_0` 到 `data_3` 四个 system。`dpa3_finetune/train_data` 和 `dpa3_finetune/val_data` 按 `system_<id>` 组织大量 system；目录计数时应排除 split 根目录自身。具体帧数按每个 `set.*/*.npy` 第一维统计，不应只按 system 数估计训练步数。

## coverage_spec
覆盖小分子/凝聚相水体系和 CH 相关 DPA3 微调体系，适用于深度势能模型、能量-力联合训练、短程相互作用学习和跨 system 泛化验证。

## label_spec
监督标签为结构级总能量 `energy` 和原子级力 `force`。若训练任务要求每原子能量、virial、stress、电荷或自旋，必须先确认原始目录是否提供对应字段；当前已观测的核心标签为 `energy.npy` 和 `force.npy`。

## split_strategy
`dpa3_finetune/train_data` 与 `dpa3_finetune/val_data` 已显式划分训练/验证；不要重新随机混合 system。`water` 未见显式 train/val/test 文件，建议按 `data_0..data_3` 或帧索引建立可复现划分，并记录随机种子和帧区间。

## constraints
- 坐标、力、原子类型长度必须满足 `coord.shape[1] == force.shape[1] == len(type.raw) * 3`。
- `box.npy`、`coord.npy`、`energy.npy`、`force.npy` 第一维必须一致。
- 不同 system 的元素映射不能假设完全相同，训练前要读取 `type_map.raw`。
- DeepMD 扁平数组不能直接传给 PyG/AtomicData，需要先 reshape 并补齐 `cell`、`pbc`、`atomic_numbers`。
- 统计文件只能作为同一数据版本的辅助信息，不能和其它 CH/water 数据混用。
