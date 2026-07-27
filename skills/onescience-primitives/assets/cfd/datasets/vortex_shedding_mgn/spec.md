## content_principle
Vortex Shedding MGN 数据集原语描述 `/public/share/sugonhpcapp01/onestore/onedatasets/vortex_shedding_mgn` 下的 DeepMind CylinderFlow 圆柱绕流图数据，用于 MeshGraphNet rollout。

## data_schema
`cylinder_flow` 下包含 `meta.json`、`train.tfrecord`、`valid.tfrecord`、`test.tfrecord` 和 `stats/{edge_stats.json,node_stats.json}`。meta 已探测含 `simulator=comsol`、`dt=0.01`、`trajectory_length=600`、`features` 和 `field_names`。

## directory_layout
```text
/vortex_shedding_mgn
└── cylinder_flow
    ├── meta.json
    ├── train.tfrecord
    ├── valid.tfrecord
    ├── test.tfrecord
    └── stats/{edge_stats.json,node_stats.json}
```

## storage_format
轨迹为 TFRecord，元数据和统计量为 JSON。OneScience `deepmind_cylinderflow` datapipe 用 TensorFlow 解析并构造 DGL 图。

## scale_spec
单条轨迹长度 600，时间步长 0.01。轨迹数、节点数和单元数需由 TFRecord 解析统计。

## coverage_spec
覆盖二维圆柱绕流/涡街时序，适合 MeshGraphNet 单步预测、多步 rollout 和物理图建模。

## label_spec
节点输入通常为当前速度和节点类型 one-hot；标签为下一时刻速度/压力相关量。验证/测试还返回 cells 和 rollout mask。

## split_strategy
使用官方 `train/valid/test.tfrecord`。非训练 split 需要可读取训练统计量。

## constraints
依赖 TensorFlow 与 DGL；train 和 val/test 返回协议不同；统计量文件必须与数据版本一致。
