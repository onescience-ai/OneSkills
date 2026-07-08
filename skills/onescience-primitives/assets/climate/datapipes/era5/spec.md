# pipeline_architecture

```text
ERA5 年份 HDF5 文件
  dataset_dir/data/<year>.h5
    fields: (TimeSteps, AllChannels, Height, Width)
    attrs["variables"]: 变量名列表
    attrs["time_step"]: 相邻帧小时间隔

样本索引初始化
  used_years
    -> 校验年份文件是否存在
    -> file_map: year -> HDF5 path
  used_variables
    -> 校验变量是否存在于 fields.attrs["variables"]
    -> channel_indices
  TimeSteps/input_steps/output_steps
    -> samples_per_year = T - input_steps - output_steps + 1
    -> total_samples = len(used_years) * samples_per_year

统计量与空间网格
  优先读取 HDF5 内 global_means/global_stds
    -> 若不存在，回退到 dataset_dir/stats/global_means.npy 与 global_stds.npy
  latlon_grid(bounds=((90, -90), (0, 360)), shape=(H, W))
    -> latlon_torch: (2, Height, Width)

运行时取样
  idx
    -> year_idx = idx // samples_per_year
    -> step_idx = idx % samples_per_year
    -> year = used_years[year_idx]
  HDF5 fields[step_idx : step_idx + input_steps + output_steps]
    -> 按 channel_indices 筛选变量
    -> data: (input_steps + output_steps, Channels, Height, Width)
    -> invar:  (input_steps, Channels, Height, Width)
    -> outvar: (output_steps, Channels, Height, Width)
    -> normalize 可选标准化
    -> cos_zenith_angle(timestamps, latlon)
    -> return invar.squeeze(0), outvar.squeeze(0), cos_zenith, step_idx, time_index

DataLoader 装配
  ERA5Datapipe.get_dataloader(mode)
    train:
      distributed=True  -> DistributedSampler(shuffle=True)
      distributed=False -> DataLoader(shuffle=True)
    val/test:
      shuffle=False
      test batch_size 固定为 1
```

# data_loading

- 原始数据使用按年份组织的 HDF5 文件，源码实际搜索路径为 `dataset_dir/data/*.h5`，并按 `<year>.h5` 文件名解析可用年份。
- 每个 HDF5 文件必须包含 `fields` 数据集，形状为 `[TimeSteps, Channels, Height, Width]`。
- `fields.attrs["variables"]` 提供通道变量名，支持 bytes 或字符串；`fields.attrs["time_step"]` 提供小时级时间步长。
- 归一化统计量读取规则：
  - 优先使用同一 HDF5 文件中的 `global_means` 与 `global_stds`。
  - 若 HDF5 内没有统计量，则读取 `dataset_dir/stats/global_means.npy` 与 `dataset_dir/stats/global_stds.npy`。
- 参考数据卡约定的主数据路径为 `{ONESCIENCE_DATASETS_DIR}/ERA5/newh5/data_merged/<year>.h5`，统计量路径为 `{ONESCIENCE_DATASETS_DIR}/ERA5/newh5/stats/global_means.npy` 与 `global_stds.npy`；当前源码路径约定需要调用侧将 `dataset_dir` 对齐为含 `data/` 与 `stats/` 子目录的根目录。

# sampling_strategy

- 数据集划分不在 datapipe 内部完成；调用方必须为训练、验证、测试分别传入对应的 `used_years`。
- 单个年份内使用连续滑动窗口采样：
  - 窗口长度为 `input_steps + output_steps`。
  - 有效起点数为 `T - input_steps - output_steps + 1`。
  - 全局样本数为 `len(used_years) * samples_per_year`。
- 样本索引规则：
  - `year_idx = idx // samples_per_year`
  - `step_idx = idx % samples_per_year`
  - `year = used_years[year_idx]`
- DataLoader 策略：
  - `mode == "train"` 时，非分布式使用随机打乱，分布式使用 `DistributedSampler(shuffle=True)`。
  - 非训练模式不打乱；分布式时使用 `DistributedSampler(shuffle=False)`。
  - `mode == "test"` 时 batch size 固定为 1。

# data_transform

- 变量筛选：根据 `used_variables` 在 `fields.attrs["variables"]` 中建立 `channel_indices`，只保留任务需要的通道。
- 时间窗切片：从 `fields` 读取 `input_steps + output_steps` 个连续时间步，前半段作为输入，后半段作为目标。
- 类型转换：将 HDF5/numpy 数据转换为 `torch.float32`。
- 标准化：当 `normalize=True` 时，对输入与输出执行 `(x - global_means) / global_stds`，统计量按所选通道同步切片。
- 经纬度网格：使用全球规则网格边界 `((90, -90), (0, 360))` 和 H/W 生成纬度、经度网格。
- 太阳天顶角：以 `datetime(year, 1, 1, tzinfo=pytz.utc)` 为起点，根据 `step_idx`、`input_steps`、`output_steps` 和 `time_step` 生成预测步时间戳，再调用 `cos_zenith_angle` 生成 `cos_zenith`。
- 时间索引：生成覆盖输入与输出窗口的 `YYYYMMDDHH` 字符串列表。
- 维度压缩：返回前对 `invar` 和 `outvar` 调用 `squeeze(0)`；当 `input_steps=1` 或 `output_steps=1` 时会去掉对应时间维。

# input_schema

- `dataset_dir`: ERA5 数据根目录；源码期望其下存在 `data/<year>.h5` 和可选 `stats/`。
- `used_years`: 年份列表，例如 `[1979, 1980]`；每个年份必须有对应 HDF5 文件。
- `used_variables`: 变量名列表；所有变量必须存在于 `fields.attrs["variables"]`。
- `distributed`: 是否启用分布式 sampler。
- `input_steps`: 输入时间步数，默认 `1`。
- `output_steps`: 预测时间步数，默认 `1`。
- `normalize`: 是否使用全局均值和标准差做标准化，默认 `True`。
- `batch_size`: 训练/验证 DataLoader 批大小；测试模式会被覆盖为 `1`。
- `num_workers`: DataLoader 工作进程数。

# output_schema

单样本返回五元组：

```text
invar:
  normalize=True 时为标准化后的输入气象场
  input_steps=1:  (Channels, Height, Width)
  input_steps>1:  (input_steps, Channels, Height, Width)
  dtype: torch.float32

outvar:
  normalize=True 时为标准化后的目标气象场
  output_steps=1: (Channels, Height, Width)
  output_steps>1: (output_steps, Channels, Height, Width)
  dtype: torch.float32

cos_zenith:
  预测时间步对应的太阳天顶角余弦
  shape 依赖 cos_zenith_angle 实现，通常与 (output_steps, Height, Width) 对齐
  dtype: torch.float32

step_idx:
  当前样本在年份内的起始时间步索引
  type: int

time_index:
  输入与输出窗口的时间字符串列表
  length: input_steps + output_steps
  format: YYYYMMDDHH
```

`get_dataloader(mode)` 返回：

```text
(dataloader, sampler)
  dataloader: torch.utils.data.DataLoader
  sampler: DistributedSampler 或 None
```

# constraints

- `used_years` 中每个年份必须存在于数据目录中，否则初始化时抛出 `ValueError`。
- `used_variables` 中每个变量必须存在于 HDF5 元数据 `fields.attrs["variables"]` 中，否则初始化时抛出 `ValueError`。
- `fields` 必须是四维 `[TimeSteps, Channels, Height, Width]`；代码不处理缺失维度、非规则网格或非 HDF5 格式。
- `T` 必须满足 `T >= input_steps + output_steps`，否则 `samples_per_year` 会小于等于 0，采样不可用。
- 标准化统计量必须覆盖全部变量通道，并能按 `[:, channel_indices, :, :]` 切片。
- 当前实现即使 `normalize=False` 也会初始化统计量文件；统计量缺失时仍可能在初始化阶段失败。
- `time_index` 与 `cos_zenith` 假设每个年份从 UTC 的 1 月 1 日 00 时开始，并按固定 `time_step` 均匀采样。
- 参考数据卡的 `data_merged/<year>.h5` 路径与源码 `data/<year>.h5` 约定不完全一致，落地时必须统一目录结构或做适配。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/climate/era5.py`
- `{onescience_path}/onescience/src/onescience/datapipes/climate/utils/invariant.py`
- `{onescience_path}/onescience/src/onescience/datapipes/climate/utils/zenith_angle.py`
