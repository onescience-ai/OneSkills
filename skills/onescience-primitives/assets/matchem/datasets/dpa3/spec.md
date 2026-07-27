## content_principle
DPA3 数据集原语描述 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/dpa3` 下的 CH_3787 碳氢体系。该集合面向 DPA3 或 Deep Potential 类模型微调，将多个 CH system 的轨迹帧、能量和力标签组织为训练/验证 split。

## data_schema
单个 system 目录采用 DeepMD 风格：

- `type.raw`：体系内每个原子的类型编号。
- `set.000/coord.npy`：坐标，shape 为 `[frames, atoms * 3]`。
- `set.000/box.npy`：晶胞，shape 为 `[frames, 9]`。
- `set.000/energy.npy`：总能量，shape 为 `[frames]`。
- `set.000/force.npy`：原子力，shape 为 `[frames, atoms * 3]`。

已探测样例：

```text
CH_3787/train_CH/sys_100/set.000/coord.npy  : (45, 300), float64
CH_3787/train_CH/sys_100/set.000/energy.npy : (45,), float64
CH_3787/train_CH/sys_100/set.000/force.npy  : (45, 300), float64
```

`300 = 100 * 3`，表示该 system 每帧 100 个原子。

## directory_layout
```text
/matchem/dpa3
└── CH_3787
    ├── train_CH
    │   ├── sys_100
    │   │   ├── type.raw
    │   │   └── set.000/{box.npy, coord.npy, energy.npy, force.npy}
    │   └── ...
    └── val_CH
        ├── sys_100
        └── ...
```

## storage_format
主格式为 DeepMD `raw/npy`。`sys_*` 目录是数据索引单位，`set.000` 是帧集合单位。数组 dtype 可能为 `float64`，训练前可按模型实现转换为 `float32`，但转换应发生在 datapipe 或 collate 层，不能覆盖原始数据。

## scale_spec
`train_CH` 和 `val_CH` 下均有大量 `sys_*` 子目录。任务规模应以 `sys_*` 数量和每个 system 中 `energy.npy` 的帧数共同统计；只计算目录数会低估或高估真实样本数。

## coverage_spec
覆盖 CH 碳氢体系的多结构、多帧势能面数据，适用于 DPA3 微调、碳氢分子/材料势能拟合、能量-力联合学习和验证集误差跟踪。

## label_spec
标签为结构级总能量和原子级力。若接入 DPA3 训练配置，还需要明确元素类型映射、能量单位、距离截断和邻接构建方式。当前目录未显示 stress/virial 字段，不能默认启用应力损失。

## split_strategy
使用目录提供的 `train_CH` 和 `val_CH` 作为权威 split。模型调参、早停和每 N step 评测应只读取 `val_CH`；不要从 `train_CH` 中随机抽取验证样本再与 `val_CH` 混用。

## constraints
- `coord.npy` 和 `force.npy` 必须 reshape 为 `[frames, atoms, 3]` 后再构图。
- 缺少 `type_map.raw` 时需要从任务配置或同源统计文件获得元素映射，不能只凭 type 编号推断元素。
- 每个 system 可能原子数不同，batch 需要支持变长原子结构拼接。
- 若训练代码需要固定 PBC 语义，应从 `box.npy` 和任务场景显式设置。
