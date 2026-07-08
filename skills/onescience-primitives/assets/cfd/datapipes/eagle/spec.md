# pipeline_responsibility

负责把 Eagle CFD 时序仿真目录组织为变长网格窗口样本，并在 batch 阶段对节点、边和 cluster 维度做 padding。

# pipeline_architecture

```text
splits_dir
  train.txt / valid.txt / test.txt
    -> 相对仿真目录列表

单个仿真目录
  sim.npz
    -> pointcloud / VX / VY / PS / PG / mask
  triangles.npy
    -> faces
  optional cluster
    -> constrained_kmeans_<n_cluster>.npy

样本窗口
  读取轨迹
  -> faces_to_edges
  -> velocity = [VX, VY]
  -> pressure = [PS, PG]
  -> node_type / mask
  -> 可选归一化
  -> collate padding
```

# data_loading

- 从 `source.splits_dir` 读取 `train.txt`、`valid.txt`、`test.txt`。
- 每个条目指向 `source.data_dir` 下的仿真目录。
- 仿真目录读取 `sim.npz` 和 `triangles.npy`。
- 当 `data.n_cluster > 1` 时，从 `source.cluster_dir` 读取聚类标签。

# sampling_strategy

- train 使用 `window_length_train`，通常随机抽取时间窗。
- valid 使用 `window_length_val`，test 使用 `window_length_test`，通常从固定起点取窗。
- `n_cluster` 仅支持源码允许的离散值。
- 一个样本是一段轨迹窗口，不直接拆成输入/标签。

# data_transform

- 三角面通过 `_faces_to_edges` 转为去重无向边再扩展为双向边。
- `VX/VY` 组合为速度，`PS/PG` 组合为压力。
- `node_type` 可选转 one-hot。
- 可选使用硬编码统计量归一化速度和压力。
- 自定义 `collate` 过滤空样本，并对 batch 内最大节点数、边数、cluster 数补齐。

# input_schema

- `<splits_dir>/train.txt`、`valid.txt`、`test.txt`。
- `<data_dir>/<case>/sim.npz`。
- `<data_dir>/<case>/triangles.npy`。
- 可选 `<cluster_dir>/<case>/constrained_kmeans_<n_cluster>.npy`。
- `sim.npz` 需包含 `pointcloud/VX/VY/PS/PG/mask`。

# output_schema

- 样本字段包括：
  - `mesh_pos`
  - `edges`
  - `velocity`
  - `pressure`
  - `node_type`
  - `mask`
  - 可选 `cells`
  - 可选 `cluster`
  - `cluster_mask`
- batch 阶段这些字段按最大尺寸 padding。

# constraints

- split 文件名必须是 `valid.txt`，不是 `val.txt`。
- `n_cluster` 只能取源码允许值。
- 归一化统计量是硬编码常数，不从数据目录学习。
- `__getitem__` 异常时返回 `{}`，collate 会过滤；坏样本过多可能导致空 batch。
- datapipe 不决定输入步和预测步切分，这通常由模型或训练脚本完成。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/cfd/eagle.py`
- `{onescience_path}/onescience/src/onescience/datapipes/core/base_dataset.py`
