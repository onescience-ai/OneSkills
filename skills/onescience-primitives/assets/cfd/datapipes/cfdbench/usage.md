# launch

Python API 启动示例：

```python
from omegaconf import OmegaConf
from onescience.datapipes.cfd import CFDBenchDatapipe

cfg = OmegaConf.load("conf/cfdbench.yaml")
datapipe = CFDBenchDatapipe(cfg.datapipe, distributed=False)
train_loader, train_sampler = datapipe.train_dataloader()
val_loader, val_sampler = datapipe.val_dataloader()
test_loader = datapipe.test_dataloader()
```

CLI 示例：

```sh
python train.py --config-name cfdbench datapipe.source.data_dir=/data/CFDBench datapipe.source.data_name=cylinder_geo datapipe.data.task_type=auto datapipe.data.delta_time=0.1 datapipe.dataloader.batch_size=16 datapipe.dataloader.eval_batch_size=8
```

# input_schema

- 数据目录形如 `<data_dir>/<problem>/<subset>/case*/`。
- 每个 case 需要 `case.json`、`u.npy`、`v.npy`。
- `source.data_name` 必须能解析出受支持的 problem 和 subset。
- `split_ratios` 建议三段和为 1。

# runtime_interfaces

- `CFDBenchDataset(config, mode="train"|"val"|"test")`: 构造单个 split。
- `CFDBenchDatapipe(config, distributed=False)`: 构造 train/val/test。
- `train_dataloader()`: 返回训练 loader 和 sampler。
- `val_dataloader()`: 返回验证 loader 和 sampler。
- `test_dataloader()`: 返回测试 loader，batch size 固定为 1。

# main_functions

- `__getitem__`
- `train_dataloader`
- `val_dataloader`
- `test_dataloader`

# execution_resources

- 主要消耗 CPU 与内存读取 npy 时间序列。
- 规则网格张量 batch 可直接进入常规场模型训练。
- 分布式模式通过 sampler 支持训练/验证切分。

# operation_limits

- 自回归和静态模式不能共用同一训练脚本解包逻辑。
- 大量 case 或长时间序列会增加初始化和内存压力。
- 不提供图边、点云表面标记或三维几何特征。
- 若数据包含压力或更多变量，需要扩展读取和 collate 逻辑。
