# launch

Python API 启动示例：

```python
from omegaconf import OmegaConf
from onescience.datapipes.cfd import AirfRANSDatapipe

cfg = OmegaConf.load("conf/airfrans.yaml")
datapipe = AirfRANSDatapipe(cfg.datapipe, distributed=False)
train_loader, train_sampler = datapipe.train_dataloader()
val_loader, val_sampler = datapipe.val_dataloader()
test_loader = datapipe.test_dataloader()
```

CLI 示例：

```sh
python train.py --config-name airfrans datapipe.source.data_dir=/data/AirfRANS datapipe.source.stats_dir=/data/AirfRANS/stats datapipe.data.splits.train_name=full_train datapipe.data.splits.test_name=full_test datapipe.dataloader.batch_size=4
```

# input_schema

- 准备包含 `manifest.json` 的 AirfRANS 根目录。
- 每个 manifest 样本名必须对应同名子目录，子目录内包含 internal vtu 和 aerofoil vtp。
- 配置 `source.stats_dir` 为可写目录，训练阶段首次运行会生成归一化统计量。
- 确认样本名能解析出 `Uinf` 和攻角。

# runtime_interfaces

- `AirfRANSDataset(config, mode, coef_norm=None)`: 构造指定 split 的样本集。
- `AirfRANSDatapipe(params, distributed)`: 构造 train/val/test 数据管道。
- `train_dataloader()`: 返回训练 loader 和可选 sampler。
- `val_dataloader()`: 返回验证 loader 和可选 sampler。
- `test_dataloader()`: 返回测试 loader。

# main_functions

- `__getitem__`
- `train_dataloader`
- `val_dataloader`
- `test_dataloader`

# execution_resources

- 需要 CPU 读取 VTK、执行几何采样和归一化统计。
- 构图使用点间半径邻域，点数较大时内存和 CPU/GPU 邻接构造开销会上升。
- 依赖 VTK 读取能力、数值数组处理能力和图样本 batch 能力。
- 分布式训练可通过 datapipe 的 `distributed=True` 启用 sampler。

# operation_limits

- 不支持没有 `manifest.json` 的散文件数据。
- 不支持字段名偏离 AirfRANS 约定的 VTK 文件。
- 测试阶段不做点级 subsampling，超大网格可能造成显存或内存压力。
- 训练/验证/测试的统计量必须一致，不能分别独立归一化。
