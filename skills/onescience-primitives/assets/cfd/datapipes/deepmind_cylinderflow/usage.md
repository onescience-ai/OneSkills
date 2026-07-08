# launch

Python API 启动示例：

```python
from omegaconf import OmegaConf
from onescience.datapipes.cfd import DeepMind_CylinderFlowDatapipe

cfg = OmegaConf.load("conf/mgn_cylinderflow.yaml")
datapipe = DeepMind_CylinderFlowDatapipe(cfg.datapipe, distributed=False)
train_loader, train_sampler = datapipe.train_dataloader()
val_loader, val_sampler = datapipe.val_dataloader()
test_loader = datapipe.test_dataloader()
```

CLI 示例：

```sh
python train.py --config-name mgn_cylinderflow datapipe.source.data_dir=/data/cylinder_flow datapipe.source.stats_dir=/data/cylinder_flow/stats datapipe.data.train_samples=1000 datapipe.data.train_steps=600 datapipe.data.val_samples=100 datapipe.data.val_steps=600 datapipe.dataloader.batch_size=2
```

# input_schema

- 数据目录必须包含 `meta.json` 和三个 split 的 TFRecord。
- `stats_dir` 应可写；训练阶段会生成统计量。
- 配置每个 split 的样本数和时间步数，避免超过 TFRecord 实际长度。

# runtime_interfaces

- `DeepMind_CylinderFlowDataset(config, mode)`: 解析指定 split 为图样本。
- `DeepMind_CylinderFlowDatapipe(params, distributed)`: 构造三个 split 的 GraphDataLoader。
- `train_dataloader()`: 返回训练 GraphDataLoader 和 sampler。
- `val_dataloader()`: 返回验证 GraphDataLoader 和 sampler。
- `test_dataloader()`: 返回测试 GraphDataLoader。

# main_functions

- `__getitem__`
- `train_dataloader`
- `val_dataloader`
- `test_dataloader`

# execution_resources

- 需要 TensorFlow TFRecord 读取环境。
- 需要 DGL 图运行环境。
- 图 batch 内存与节点数、边数和轨迹展开长度相关。
- 训练噪声和统计量计算主要消耗 CPU/GPU 张量计算资源。

# operation_limits

- 不支持普通 npy、h5、VTK 输入。
- val/test batch 不是单纯 graph，调用侧需要解包 `cells` 和 `mask`。
- 统计量缺失会影响非训练 split 初始化。
- 节点类型、速度和压力字段变化时需要同步改模型配置。
