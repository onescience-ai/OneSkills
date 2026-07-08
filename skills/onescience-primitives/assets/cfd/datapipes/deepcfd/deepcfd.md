# Datapipe: DeepcfdDatapipe

## 基本信息

- Datapipe 名称：`DeepcfdDatapipe`
- 数据类型：`cfd`
- 主要任务：`steady regular-grid flow-field regression`
- 数据组织方式：`paired_pickle_arrays_loaded_in_memory`

## pipeline_responsibility

负责把 DeepCFD 的成对 pickle 输入/输出数组读入内存，随机划分训练与测试样本，并输出普通字典 batch 以及通道级 loss 权重。

## 管道架构

```text
数据目录
  dataX.pkl
    -> 输入规则网格张量
  dataY.pkl
    -> 输出规则网格张量

初始化
  pickle 全量加载
  -> seed 打乱索引
  -> split_ratio 划分 train / test
  -> 统计 y 通道权重

样本
  {"x": input_tensor, "y": target_tensor}
```

## 数据加载

- 从 `source.data_dir/source.data_x_name` 读取输入 pickle。
- 从 `source.data_dir/source.data_y_name` 读取输出 pickle。
- pickle 内容被转换为张量并保存在 dataset 内存中。

## 采样策略

- 用 `data.seed` 打乱样本索引。
- `data.split_ratio` 之前的样本作为 train。
- 剩余样本作为 test；源码中 `mode="val"` 也落在同一剩余段。

## 数据转换

- 不执行复杂几何变换或图构建。
- `__getitem__` 返回 `{"x": tensor, "y": tensor}`。
- 根据完整目标张量统计 3 个输出通道的 RMS 风格权重，供加权损失使用。

## 输入规格

- `<data_dir>/<data_x_name>`: pickle 格式输入数组。
- `<data_dir>/<data_y_name>`: pickle 格式目标数组。
- `dataX` 与 `dataY` 样本数必须一致。
- 常见形状：`x -> [ChannelsIn, Height, Width]`，`y -> [ChannelsOut, Height, Width]`。

## 输出规格

- `sample["x"]`: 输入规则网格张量。
- `sample["y"]`: 目标规则网格张量。
- `get_loss_weights()` 返回训练集目标通道权重。

## 约束条件

- 数据会一次性加载到内存。
- 当前 loss 权重实现默认输出通道数为 3。
- 没有真正独立的 val split。
- 不输出坐标、mask、图边或 case 参数。

## 启动方式

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

## 输入规格

- 准备同一样本顺序的 `dataX.pkl` 和 `dataY.pkl`。
- 输入和输出数组第一维应为样本维。
- 输出通道若不是 3，需要同步修改 loss 权重逻辑或训练脚本。

## 运行接口

- `DeepCFDDataset(config, mode)`: 构造 train/test/val 样本段。
- `DeepCFDDatapipe(config, distributed=False)`: 构造训练和测试 dataloader。
- `get_loss_weights()`: 返回训练目标通道权重。
- `train_dataloader()`: 返回训练 loader 和 sampler。
- `test_dataloader()`: 返回测试 loader 和 sampler。

## 主要函数

- `__getitem__`
- `get_loss_weights`
- `train_dataloader`
- `test_dataloader`

## 执行资源

- 需要足够内存容纳完整 pickle 输入和输出。
- 运行期数据转换轻量，主要成本在模型训练。
- 分布式时可使用 `DistributedSampler`。

## 操作限制

- 没有单独 `val_dataloader`。
- pickle 文件过大时初始化可能慢或内存不足。
- 不适用于非规则网格、变长点云或图样本。
- `mode="val"` 与 `mode="test"` 使用同一剩余划分，不能作为独立评估集。

## 规划决策

### 描述

该原语用于规划简单规则网格稳态 CFD 回归数据流，将成对输入/输出数组直接变成字典 batch。

### 使用时机

- 数据已经预处理为 `X -> Y` 成对规则网格张量。
- 模型是图像式或卷积式场回归模型。
- 不需要图结构、坐标网格、case 参数或时间序列逻辑。
- 需要复用 DeepCFD 示例训练流程。

### 输入

- 输入 pickle 文件名和目标 pickle 文件名。
- train/test 划分比例和随机种子。
- batch size、num_workers。
- 是否使用输出通道权重。

### 输出

- train/test dataloader。
- `{"x", "y"}` 样本 batch。
- 训练集通道权重。

### 执行步骤

1. 确认 `dataX` 与 `dataY` 样本数一致。
2. 估算 pickle 全量加载内存。
3. 设置 split ratio 和随机种子。
4. 构造 datapipe 并读取 loss weights。
5. 将 batch 协议接入 DeepCFD 模型训练。

### 约束

- 输出通道默认 3。
- 没有独立验证集。
- 数据必须能完整加载到内存。

### 下一阶段建议

若需要时间序列或物理参数，转向 CFDBench；若需要 HDF5 operator learning，转向 PDENNEval；若需要几何图结构，转向 AirfRANS 或 ShapeNetCar。

### 回退策略

- 内存不足时先离线切分 pickle 或改写 dataset 为懒加载。
- 需要验证集时在外部重新划分数据文件或扩展 datapipe。
- 通道数不同则禁用或重写 `get_loss_weights`。

## 源码锚点

- `{onescience_path}/onescience/src/onescience/datapipes/cfd/deepcfd.py`
- `{onescience_path}/onescience/examples/cfd/DeepCFD/train.py`
- `{onescience_path}/onescience/examples/cfd/DeepCFD/conf/deepcfd.yaml`
