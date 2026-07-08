# pipeline_architecture

```text
CMEMS 年份 HDF5 数据根目录
  dataset_dir/
    metadata.json                     可选；可提供 variables
    data/<year>.h5                    每个年份一个 HDF5 文件
      fields: (TimeSteps, AllChannels, Height, Width)
      fields.attrs["variables"]       首选变量名来源
      fields.attrs["time_step"]       小时级时间步长
    stats/global_means.npy
    stats/global_stds.npy

初始化样本索引
  used_years
    -> 扫描 dataset_dir/data/*.h5
    -> 从 <year>.h5 文件名解析 available_years
    -> 校验每个 used_year 是否存在
    -> file_map: year -> dataset_dir/data/<year>.h5
  used_variables
    -> 优先从 fields.attrs["variables"] 读取变量名
    -> 若 HDF5 属性缺失，则从 metadata.json 的 variables 读取
    -> 校验变量存在性
    -> channel_indices
  fields shape
    -> T, C, H, W
    -> samples_per_year = T - input_steps - output_steps + 1
    -> total_samples = len(used_years) * samples_per_year

统计量与空间辅助特征
  stats/global_means.npy
    -> mu[:, channel_indices, :, :]
  stats/global_stds.npy
    -> sd[:, channel_indices, :, :]
  latlon_grid(bounds=((90, -90), (0, 360)), shape=(H, W))
    -> latlon_torch: (2, Height, Width)

运行时取样
  idx
    -> year_idx = idx // samples_per_year
    -> step_idx = idx % samples_per_year
    -> year = used_years[year_idx]
  HDF5 fields[step_idx : step_idx + input_steps + output_steps]
    -> 按 channel_indices 筛选变量通道
    -> data:   (input_steps + output_steps, Channels, Height, Width)
    -> invar:  (input_steps, Channels, Height, Width)
    -> outvar: (output_steps, Channels, Height, Width)
    -> NaN 使用对应通道均值替换
    -> normalize=True 时执行 (x - mu) / sd
    -> 基于预测时间戳和 latlon_torch 生成 cos_zenith
    -> return invar.squeeze(0), outvar.squeeze(0), cos_zenith, step_idx, time_index

DataLoader 装配
  CMEMSDatapipe.get_dataloader(mode)
    train:
      distributed=True  -> DistributedSampler(shuffle=True)
      distributed=False -> DataLoader(shuffle=True)
    val/其他非 train:
      shuffle=False
      distributed=True -> DistributedSampler(shuffle=False)
    test:
      batch_size 固定为 1
```

# data_loading

- 数据根目录由 `dataset_dir` 指定，源码实际搜索路径为 `dataset_dir/data/*.h5`。
- 每个年份文件名必须可解析为整数年份，例如 `1993.h5`；`used_years` 中的每个年份必须有对应文件。
- 每个 HDF5 文件必须包含 `fields` 数据集，且 `fields` 必须为四维数组 `[TimeSteps, Channels, Height, Width]`。
- 变量名来源优先级：
  - 首选 `fields.attrs["variables"]`，支持 bytes 或字符串形式。
  - 若 HDF5 属性缺失，则回退到 `dataset_dir/metadata.json` 中的 `variables` 字段。
- 时间步长必须由 `fields.attrs["time_step"]` 提供，单位按小时解释。
- 归一化统计量固定从 `dataset_dir/stats/global_means.npy` 与 `dataset_dir/stats/global_stds.npy` 读取。

# sampling_strategy

- 数据集划分不在源码内部自动完成；调用方通过为训练、验证、测试分别传入不同的 `used_years` 来控制阶段划分。
- 单个年份内使用连续滑动窗口采样：
  - 窗口总长度为 `input_steps + output_steps`。
  - 有效起点数为 `T - input_steps - output_steps + 1`。
  - 总样本数为 `len(used_years) * samples_per_year`。
- 全局样本索引映射：
  - `year_idx = idx // samples_per_year`
  - `step_idx = idx % samples_per_year`
  - `year = used_years[year_idx]`
- `mode == "train"` 时启用训练采样策略：
  - 非分布式：`DataLoader(shuffle=True)`。
  - 分布式：`DistributedSampler(shuffle=True)`。
- 非训练模式不打乱；`mode == "test"` 时 batch size 强制为 `1`。

# data_transform

- 变量筛选：根据 `used_variables` 在全部变量名中建立 `channel_indices`，只保留任务所需通道。
- 时间窗口切片：从 `fields` 连续读取 `input_steps + output_steps` 帧，前半段作为输入，后半段作为目标。
- 类型转换：将 HDF5/numpy 数据转换为 `torch.float32` 张量。
- 缺失值处理：对 `invar` 与 `outvar` 中的 `NaN` 使用所选通道对应的全局均值 `mu` 替换。
- 标准化：当 `normalize=True` 时，对输入与目标执行 `(x - mu) / sd`。
- 经纬度网格：使用全局规则网格边界 `((90, -90), (0, 360))` 和当前 `H/W` 生成纬度、经度网格。
- 太阳天顶角：以 `datetime(year, 1, 1, tzinfo=pytz.utc)` 为年份起点，根据 `step_idx`、`input_steps`、`output_steps` 和 `time_step` 生成预测时间戳，再调用 `cos_zenith_angle` 生成 `cos_zenith`。
- 时间索引：生成覆盖输入与输出窗口的 `YYYYMMDDHH` 字符串列表。
- 返回前压缩：对 `invar` 与 `outvar` 调用 `squeeze(0)`；当对应时间步为 `1` 时会移除时间维。

# input_schema

- `dataset_dir`: CMEMS 数据根目录；其下需要包含 `data/`、`stats/`，可选包含 `metadata.json`。
- `used_years`: 年份列表，例如 `[1993, 1994]`；每个年份必须对应 `data/<year>.h5`。
- `used_variables`: 变量名列表；每个名称必须存在于 `fields.attrs["variables"]` 或 `metadata.json["variables"]`。
- `distributed`: 是否启用分布式采样器，默认 `False`。
- `input_steps`: 输入时间步数，默认 `1`。
- `output_steps`: 预测时间步数，默认 `1`。
- `normalize`: 是否使用全局均值和标准差执行标准化，默认 `True`。
- `batch_size`: 训练/验证等非 test 模式的 DataLoader 批大小，默认 `1`。
- `num_workers`: DataLoader 工作进程数，默认 `4`。

HDF5 文件结构：

```text
data/<year>.h5
  fields:
    shape: [TimeSteps, AllChannels, Height, Width]
    attrs:
      variables: [str | bytes, ...]
      time_step: int

stats/global_means.npy:
  shape: 可按 [:, channel_indices, :, :] 切片并广播到样本张量

stats/global_stds.npy:
  shape: 可按 [:, channel_indices, :, :] 切片并广播到样本张量
```

# output_schema

单样本返回五元组：

```text
invar:
  含义: 输入海洋场
  input_steps=1:  (Channels, Height, Width)
  input_steps>1:  (input_steps, Channels, Height, Width)
  dtype: torch.float32

outvar:
  含义: 目标海洋场
  output_steps=1: (Channels, Height, Width)
  output_steps>1: (output_steps, Channels, Height, Width)
  dtype: torch.float32

cos_zenith:
  含义: 预测时间步对应的太阳天顶角余弦特征
  shape: 通常与 (output_steps, Height, Width) 对齐，具体取决于 cos_zenith_angle 实现
  dtype: torch.float32

step_idx:
  含义: 当前样本在年份内的起始时间步索引
  type: int

time_index:
  含义: 输入与输出窗口的时间字符串列表
  length: input_steps + output_steps
  format: YYYYMMDDHH
```

`get_dataloader(mode)` 返回：

```text
(dataloader, sampler)
  dataloader: DataLoader 实例
  sampler: DistributedSampler 或 None
```

# constraints

- `dataset_dir/data` 下必须存在可解析年份的 `.h5` 文件，否则初始化失败。
- `used_years` 中所有年份都必须存在于已发现文件集合中。
- `fields` 必须存在且为四维 `[TimeSteps, Channels, Height, Width]`。
- 变量名必须能从 `fields.attrs["variables"]` 或 `metadata.json["variables"]` 获取；否则无法建立通道索引。
- `fields.attrs["time_step"]` 必须存在，否则无法生成时间索引与太阳天顶角时间戳。
- `T` 必须满足 `T >= input_steps + output_steps`，否则有效样本数会小于等于 0。
- 统计量文件在初始化阶段无条件读取；即使 `normalize=False`，缺少 `global_means.npy` 或 `global_stds.npy` 仍可能导致失败，因为 NaN 填补也依赖 `mu`。
- `global_means.npy` 与 `global_stds.npy` 必须能按 `[:, channel_indices, :, :]` 切片，并能与样本张量广播。
- 时间轴假设每个年份从 UTC 1 月 1 日 00 时开始，且按固定 `time_step` 均匀采样。
- `squeeze(0)` 会在单步输入或单步输出时移除时间维，下游模型或 collate 逻辑需显式处理该 shape 变化。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/climate/cmems.py`
- `{onescience_path}/onescience/src/onescience/datapipes/climate/utils/invariant.py`
- `{onescience_path}/onescience/src/onescience/datapipes/climate/utils/zenith_angle.py`
