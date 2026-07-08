# launch

Python API 启动示例：

```python
from omegaconf import OmegaConf
from onescience.datapipes.cfd import DeepCFDDatapipe

cfg = OmegaConf.load("conf/deepcfd.yaml")
datapipe = DeepCFDDatapipe(cfg.datapipe, distributed=False)
loss_weights = datapipe.get_loss_weights()
train_loader, train_sampler = datapipe.train_dataloader()
test_loader, test_sampler = datapipe.test_dataloader()
```

CLI 示例：

```sh
python train.py --config-name deepcfd datapipe.source.data_dir=/data/DeepCFD datapipe.source.data_x_name=dataX.pkl datapipe.source.data_y_name=dataY.pkl datapipe.data.split_ratio=0.8 datapipe.dataloader.batch_size=16
```

# input_schema

- 准备同一样本顺序的 `dataX.pkl` 和 `dataY.pkl`。
- 输入和输出数组第一维应为样本维。
- 输出通道若不是 3，需要同步修改 loss 权重逻辑或训练脚本。

# runtime_interfaces

- `DeepCFDDataset(config, mode)`: 构造 train/test/val 样本段。
- `DeepCFDDatapipe(config, distributed=False)`: 构造训练和测试 dataloader。
- `get_loss_weights()`: 返回训练目标通道权重。
- `train_dataloader()`: 返回训练 loader 和 sampler。
- `test_dataloader()`: 返回测试 loader 和 sampler。

# main_functions

- `__getitem__`
- `get_loss_weights`
- `train_dataloader`
- `test_dataloader`

# execution_resources

- 需要足够内存容纳完整 pickle 输入和输出。
- 运行期数据转换轻量，主要成本在模型训练。
- 分布式时可使用 `DistributedSampler`。

# operation_limits

- 没有单独 `val_dataloader`。
- pickle 文件过大时初始化可能慢或内存不足。
- 不适用于非规则网格、变长点云或图样本。
- `mode="val"` 与 `mode="test"` 使用同一剩余划分，不能作为独立评估集。
