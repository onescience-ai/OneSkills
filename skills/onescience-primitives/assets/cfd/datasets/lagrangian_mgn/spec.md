## content_principle
Lagrangian MGN 数据集原语描述 `/public/share/sugonhpcapp01/onestore/onedatasets/Lagrangian_MGN` 下的 DeepMind Water 粒子轨迹数据。该集合面向拉格朗日粒子动力学预测。

## data_schema
`data/Water` 下包含 `metadata.json` 和 `train.tfrecord`、`valid.tfrecord`、`test.tfrecord`。metadata 已探测包含 `bounds`、`sequence_length=1000`、`default_connectivity_radius=0.015`、`dim=2`、`dt=0.0025`、`vel_mean/std`、`acc_mean/std`。

## directory_layout
```text
/Lagrangian_MGN
└── data/Water
    ├── metadata.json
    ├── train.tfrecord
    ├── valid.tfrecord
    └── test.tfrecord
```

## storage_format
轨迹为 TFRecord，元数据为 JSON。OneScience `deepmind_lagrangian` datapipe 使用 TensorFlow 解析粒子类型和位置序列，并构建 DGL 半径图。

## scale_spec
单条序列长度 1000，二维粒子坐标，时间步长 0.0025。粒子数、序列数和 split 样本数需从 TFRecord 解析统计。

## coverage_spec
覆盖二维水体拉格朗日粒子运动，适用于 MeshGraphNet、粒子动力学、历史速度窗口和边界距离特征建模。

## label_spec
标签为下一位置、下一速度和下一加速度；训练阶段通常对动态粒子加噪并用 mask 排除运动学粒子。

## split_strategy
使用 `train/valid/test.tfrecord` 的官方 split。每个样本由轨迹和时间窗口组成，不应跨 split 重新抽样。

## constraints
依赖 TensorFlow 和 DGL；半径图全对全距离成本高；metadata 的统计量、bounds、dt、connectivity radius 必须完整。
