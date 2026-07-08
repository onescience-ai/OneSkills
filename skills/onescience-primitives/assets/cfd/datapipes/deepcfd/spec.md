# pipeline_responsibility

负责把 DeepCFD 的成对 pickle 输入/输出数组读入内存，随机划分训练与测试样本，并输出普通字典 batch 以及通道级 loss 权重。

# pipeline_architecture

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

# data_loading

- 从 `source.data_dir/source.data_x_name` 读取输入 pickle。
- 从 `source.data_dir/source.data_y_name` 读取输出 pickle。
- pickle 内容被转换为张量并保存在 dataset 内存中。

# sampling_strategy

- 用 `data.seed` 打乱样本索引。
- `data.split_ratio` 之前的样本作为 train。
- 剩余样本作为 test；源码中 `mode="val"` 也落在同一剩余段。

# data_transform

- 不执行复杂几何变换或图构建。
- `__getitem__` 返回 `{"x": tensor, "y": tensor}`。
- 根据完整目标张量统计 3 个输出通道的 RMS 风格权重，供加权损失使用。

# input_schema

- `<data_dir>/<data_x_name>`: pickle 格式输入数组。
- `<data_dir>/<data_y_name>`: pickle 格式目标数组。
- `dataX` 与 `dataY` 样本数必须一致。
- 常见形状：`x -> [ChannelsIn, Height, Width]`，`y -> [ChannelsOut, Height, Width]`。

# output_schema

- `sample["x"]`: 输入规则网格张量。
- `sample["y"]`: 目标规则网格张量。
- `get_loss_weights()` 返回训练集目标通道权重。

# constraints

- 数据会一次性加载到内存。
- 当前 loss 权重实现默认输出通道数为 3。
- 没有真正独立的 val split。
- 不输出坐标、mask、图边或 case 参数。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/cfd/deepcfd.py`
- `{onescience_path}/onescience/examples/cfd/DeepCFD/train.py`
- `{onescience_path}/onescience/examples/cfd/DeepCFD/conf/deepcfd.yaml`
