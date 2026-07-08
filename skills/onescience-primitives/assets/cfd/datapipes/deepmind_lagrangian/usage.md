# launch

Python API 启动示例：

```python
from omegaconf import OmegaConf
from onescience.datapipes.cfd import DeepMindLagrangianDatapipe

cfg = OmegaConf.load("conf/lagrangian.yaml")
datapipe = DeepMindLagrangianDatapipe(cfg, distributed=False)
train_loader = datapipe.train_dataloader()
val_loader = datapipe.val_dataloader()
test_loader = datapipe.test_dataloader()
```

CLI 示例：

```sh
python train.py --config-name lagrangian datapipe.source.data_dir=/data/lagrangian data.num_history=5 data.noise_std=0.0003 data.train.split=train data.valid.split=valid data.test.split=test datapipe.dataloader.train.batch_size=2
```

# input_schema

- 数据根目录包含 `metadata.json` 和 split 对应 TFRecord。
- `metadata.json` 需要包含速度/加速度均值方差、时间步长、边界、维度和默认连接半径。
- `particle_type` 和 `position` 必须符合源码解析逻辑。

# runtime_interfaces

- `DeepMindLagrangianDataset(config, mode)`: 构造一个 split 的动态图样本。
- `DeepMindLagrangianDatapipe(cfg, distributed=False)`: 构造 train/valid/test loader。
- `train_dataloader()`: 返回训练 GraphDataLoader。
- `val_dataloader()`: 返回验证 GraphDataLoader。
- `test_dataloader()`: 返回测试 GraphDataLoader。

# main_functions

- `__getitem__`
- `denormalize_velocity`
- `denormalize_acceleration`
- `unpack_targets`
- `unpack_inputs`
- `time_integrator`
- `train_dataloader`
- `val_dataloader`
- `test_dataloader`

# execution_resources

- 需要 TensorFlow 读取 TFRecord。
- 需要 DGL 存储和 batch 图。
- 半径图构建使用全对全距离，粒子数大时 CPU/GPU 与内存压力明显。
- 分布式通过 `GraphDataLoader(..., use_ddp=...)` 控制。

# operation_limits

- 不支持欧拉规则网格输入。
- 粒子数过大时动态构图可能成为瓶颈。
- `valid` 文件名和配置名需要一致。
- rollout 中若位置更新后邻接改变，应复用 `graph_update` 更新边。
