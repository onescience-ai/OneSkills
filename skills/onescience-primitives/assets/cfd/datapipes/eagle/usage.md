# launch

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

# input_schema

- split 文件每行应是相对仿真目录。
- 每个仿真目录包含 `sim.npz` 和 `triangles.npy`。
- 若启用 cluster，需准备对应 `constrained_kmeans_<n_cluster>.npy`。
- `n_cluster`、`type_as_onehot`、`with_cells`、`normalized` 需要与训练脚本期望一致。

# runtime_interfaces

- `EagleDataset(config, mode)`: 构造指定 split 的窗口样本。
- `normalize(velocity, pressure)`: 使用内置统计量归一化。
- `denormalize(velocity, pressure)`: 反归一化。
- `EagleDatapipe(params, distributed)`: 构造 loader。
- `train_dataloader()`、`val_dataloader()`、`test_dataloader(batch_size=None)`: 返回 loader 和 sampler。

# main_functions

- `__getitem__`
- `normalize`
- `denormalize`
- `train_dataloader`
- `val_dataloader`
- `test_dataloader`

# execution_resources

- 需要读取 npz、npy 轨迹文件。
- padding 后 batch 尺寸由 batch 内最大节点数和边数决定。
- cluster 读取会增加 I/O。
- 分布式时可使用 `DistributedSampler`。

# operation_limits

- 输出为普通字典 batch，不是 PyG 或 DGL 图对象。
- 空样本会被过滤，数据质量差时需监控 batch 是否为空。
- 时间输入/目标切分需由下游模型完成。
- 不适合固定规则网格 benchmark 的直接训练协议。
