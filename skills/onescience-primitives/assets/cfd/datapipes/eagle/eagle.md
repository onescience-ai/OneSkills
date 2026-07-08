# Datapipe: EagleDatapipe

## 基本信息

- Datapipe 名称：`EagleDatapipe`
- 数据类型：`cfd`
- 主要任务：`variable-size mesh temporal-window flow prediction`
- 数据组织方式：`split_text_files_with_npz_trajectories_and_triangle_meshes`

## pipeline_responsibility

负责把 Eagle CFD 时序仿真目录组织为变长网格窗口样本，并在 batch 阶段对节点、边和 cluster 维度做 padding。

## 管道架构

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

## 数据加载

- 从 `source.splits_dir` 读取 `train.txt`、`valid.txt`、`test.txt`。
- 每个条目指向 `source.data_dir` 下的仿真目录。
- 仿真目录读取 `sim.npz` 和 `triangles.npy`。
- 当 `data.n_cluster > 1` 时，从 `source.cluster_dir` 读取聚类标签。

## 采样策略

- train 使用 `window_length_train`，通常随机抽取时间窗。
- valid 使用 `window_length_val`，test 使用 `window_length_test`，通常从固定起点取窗。
- `n_cluster` 仅支持源码允许的离散值。
- 一个样本是一段轨迹窗口，不直接拆成输入/标签。

## 数据转换

- 三角面通过 `_faces_to_edges` 转为去重无向边再扩展为双向边。
- `VX/VY` 组合为速度，`PS/PG` 组合为压力。
- `node_type` 可选转 one-hot。
- 可选使用硬编码统计量归一化速度和压力。
- 自定义 `collate` 过滤空样本，并对 batch 内最大节点数、边数、cluster 数补齐。

## 输入规格

- `<splits_dir>/train.txt`、`valid.txt`、`test.txt`。
- `<data_dir>/<case>/sim.npz`。
- `<data_dir>/<case>/triangles.npy`。
- 可选 `<cluster_dir>/<case>/constrained_kmeans_<n_cluster>.npy`。
- `sim.npz` 需包含 `pointcloud/VX/VY/PS/PG/mask`。

## 输出规格

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

## 约束条件

- split 文件名必须是 `valid.txt`，不是 `val.txt`。
- `n_cluster` 只能取源码允许值。
- 归一化统计量是硬编码常数，不从数据目录学习。
- `__getitem__` 异常时返回 `{}`，collate 会过滤；坏样本过多可能导致空 batch。
- datapipe 不决定输入步和预测步切分，这通常由模型或训练脚本完成。

## 启动方式

Python API 启动示例：

```python
from omegaconf import OmegaConf
from onescience.datapipes.cfd import EagleDatapipe

cfg = OmegaConf.load("conf/eagle.yaml")
datapipe = EagleDatapipe(cfg.datapipe, distributed=False)
train_loader, train_sampler = datapipe.train_dataloader()
val_loader, val_sampler = datapipe.val_dataloader()
test_loader, test_sampler = datapipe.test_dataloader(batch_size=1)
```

CLI 示例：

```sh
python train.py --config-name eagle datapipe.source.data_dir=/data/eagle datapipe.source.splits_dir=/data/eagle/splits datapipe.source.cluster_dir=/data/eagle/clusters datapipe.data.window_length_train=20 datapipe.data.window_length_val=20 datapipe.data.window_length_test=20 datapipe.data.n_cluster=10 datapipe.dataloader.batch_size=4
```

## 输入规格

- split 文件每行应是相对仿真目录。
- 每个仿真目录包含 `sim.npz` 和 `triangles.npy`。
- 若启用 cluster，需准备对应 `constrained_kmeans_<n_cluster>.npy`。
- `n_cluster`、`type_as_onehot`、`with_cells`、`normalized` 需要与训练脚本期望一致。

## 运行接口

- `EagleDataset(config, mode)`: 构造指定 split 的窗口样本。
- `normalize(velocity, pressure)`: 使用内置统计量归一化。
- `denormalize(velocity, pressure)`: 反归一化。
- `EagleDatapipe(params, distributed)`: 构造 loader。
- `train_dataloader()`、`val_dataloader()`、`test_dataloader(batch_size=None)`: 返回 loader 和 sampler。

## 主要函数

- `__getitem__`
- `normalize`
- `denormalize`
- `train_dataloader`
- `val_dataloader`
- `test_dataloader`

## 执行资源

- 需要读取 npz、npy 轨迹文件。
- padding 后 batch 尺寸由 batch 内最大节点数和边数决定。
- cluster 读取会增加 I/O。
- 分布式时可使用 `DistributedSampler`。

## 操作限制

- 输出为普通字典 batch，不是 PyG 或 DGL 图对象。
- 空样本会被过滤，数据质量差时需监控 batch 是否为空。
- 时间输入/目标切分需由下游模型完成。
- 不适合固定规则网格 benchmark 的直接训练协议。

## 规划决策

### 描述

该原语用于网格时序预测任务，将不同规模仿真轨迹窗口整理成可 batch 的 padded 字典。

### 使用时机

- 数据由 split 文本和仿真目录组成。
- 每个样本有不等节点数、边数或 cluster 数。
- 训练需要时间窗口而不是单帧样本。
- 模型使用 mesh edges、mask 或 cluster pooling。

### 输入

- 数据根目录、split 目录和可选 cluster 目录。
- train/valid/test 窗口长度。
- cluster 数、是否 one-hot 节点类型、是否保留 cells。
- batch size 和 num_workers。

### 输出

- train/val/test DataLoader。
- padding 后的速度、压力、节点、边、mask 和 cluster batch。
- 可选归一化/反归一化能力。

### 执行步骤

1. 校验 split 文件名和路径。
2. 抽查 `sim.npz` 字段和 `triangles.npy` 形状。
3. 根据模型选择 `with_cells` 和 `n_cluster`。
4. 设置窗口长度，确认训练脚本如何切分输入/目标。
5. 构造 datapipe 并监控空样本过滤情况。

### 约束

- `n_cluster` 不是任意整数。
- padding 会放大显存占用。
- 归一化统计量不可自动适配新数据分布。

### 下一阶段建议

若需要 DGL/PyG 图对象，增加图对象包装层；若数据已经是规则网格张量，用 CFDBench 或 DeepCFD；若是粒子轨迹，用 DeepMindLagrangian。

### 回退策略

- 空 batch 出现时先清理坏样本或降低 batch size。
- cluster 文件缺失时设置 `n_cluster=1` 或关闭 cluster 分支。
- padding 过大时按节点数分桶采样或降低 batch size。

## 源码锚点

- `{onescience_path}/onescience/src/onescience/datapipes/cfd/eagle.py`
- `{onescience_path}/onescience/src/onescience/datapipes/core/base_dataset.py`
