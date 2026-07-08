# launch

Python API 启动示例：

```python
from omegaconf import OmegaConf
from onescience.datapipes.cfd import BENODatapipe

cfg = OmegaConf.load("conf/beno.yaml")
datapipe = BENODatapipe(cfg.datapipe, distributed=False)
train_loader, train_sampler = datapipe.train_dataloader()
test_loader, test_sampler = datapipe.test_dataloader()
```

CLI 示例：

```sh
python train.py --config-name beno datapipe.source.data_dir=/data/BENO datapipe.source.file_prefix=example datapipe.source.cache_dir=/data/BENO/cache datapipe.data.ntrain=1000 datapipe.data.ntest=200 datapipe.dataloader.batch_size=8
```

# input_schema

- 数据目录需包含 `RHS_<prefix>_all.npy`、`SOL_<prefix>_all.npy`、`BC_<prefix>_all.npy`。
- `cache_dir` 建议独立于原始数据目录，便于清理和复用。
- 配置 `resolution`、`ns` 与原始数组空间分辨率保持一致。

# runtime_interfaces

- `BENODataset(config, mode="train"|"test")`: 读取或生成异构图样本。
- `BENODatapipe(config, distributed=False)`: 同时构造训练和测试数据集。
- `train_dataloader()`: 返回训练 `GeoDataLoader` 和 sampler。
- `test_dataloader()`: 返回测试 `GeoDataLoader` 和 sampler。

# main_functions

- `__getitem__`
- `train_dataloader`
- `test_dataloader`

# execution_resources

- 首次运行需要较多 CPU 时间完成平滑、梯度、距离和图边构造。
- 缓存写入需要本地磁盘空间。
- batch 后是图结构数据，节点数和边数会影响内存占用。

# operation_limits

- 没有 `val_dataloader`。
- 不适合边界点数不是 128 且未修改源码的数据。
- 不适合目标列不是 `SOL[..., 0]` 的多变量监督任务。
- 缓存与 `file_prefix/mode/count` 绑定，配置变化后需确认缓存是否过期。
