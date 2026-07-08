# pipeline_responsibility

负责把 DeepMind 粒子轨迹数据转换为动态半径图样本，处理 TFRecord bytes 解析、历史速度窗口、边界距离特征、粒子类型编码、随机游走噪声、归一化目标和时间积分辅助。

# pipeline_architecture

```text
数据目录
  metadata.json
    -> sequence_length / dt / bounds / dim
    -> vel_mean/std, acc_mean/std
    -> default_connectivity_radius
  <split>.tfrecord
    -> particle_type
    -> position sequence

样本窗口
  positions[t-history : t+1]
    -> position_t
    -> velocity_history
    -> boundary_features
    -> node_type_onehot
    -> radius graph
    -> edge features
    -> next_position / next_velocity / next_acceleration
```

# data_loading

- 从 `datapipe.source.data_dir/metadata.json` 读取统计量和物理元数据。
- 根据 `cfg.data.<split>.split` 读取对应 `<split>.tfrecord`。
- 使用 TensorFlow 解析序列化 bytes 字段，得到粒子类型和位置序列。
- 每个 split 可限制 `num_sequences` 和 `num_steps`。

# sampling_strategy

- 一个 item 对应一条轨迹上的一个历史窗口。
- `num_history` 决定输入历史速度帧数量。
- train/valid/test split 名称由配置指定，valid 使用 `mode="valid"`。
- 图边在每个样本中按当前位置和半径动态重建。

# data_transform

- 根据连续位置计算速度和加速度。
- 训练阶段对动态粒子注入随机游走噪声，运动学粒子通过 mask 排除。
- 计算边界距离/裁剪特征。
- 粒子类型转 one-hot。
- 使用 `torch.cdist` 半径邻接构图，并写入边相对位移与距离特征。
- 提供反归一化和时间积分辅助。

# input_schema

- `<data_dir>/metadata.json`。
- `<data_dir>/<split>.tfrecord`。
- 必需配置：`data.num_history`、`data.noise_std`、`data.num_node_types`。
- 每个 split 需配置 `split`、`num_sequences`、可选 `num_steps`。

# output_schema

- 返回 `DGLGraph`。
- `ndata["x"]`: `[position_t, velocity_history, boundary_features, node_type_onehot]` 拼接特征。
- `ndata["y"]`: `[next_position, next_velocity, next_acceleration]`。
- `ndata["pos"]`: 当前粒子位置。
- `ndata["mask"]`: 动态粒子或训练目标 mask。
- `ndata["t"]`: 时间索引。
- `edata["x"]`: 半径图边特征。

# constraints

- 依赖 TensorFlow compat v1 和 DGL。
- 半径图基于全对全距离，粒子数很大时成本高。
- metadata 中统计量和物理元数据必须完整。
- split 配置分布在 `cfg.data.*` 和 `cfg.datapipe.*`，生成配置时需保持一致。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/cfd/deepmind_lagrangian.py`
- `{onescience_path}/onescience/examples/cfd/Vortex_shedding_mgn/`
- `{onescience_path}/onescience/src/onescience/datapipes/core/base_dataset.py`
