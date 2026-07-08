# pipeline_architecture

```text
TJWeather 数据根目录
  params.dataset.data_dir/
    metadata.json
      years: [year, ...]
      variables: [var, ...]
    data/<year>/*.nc
      每个 .nc 文件对应一个时间步
      fields: (ChannelLike, LatitudeLike, LongitudeLike)
      可识别维度名:
        channel | variable | variables
        latitude | lat
        longitude | lon
    stats/
      global_means.npy
      global_stds.npy

参数入口
  TJDatapipe(params, distributed, output_steps, input_steps, normalize)
    -> params.dataset
    -> params.dataloader

Dataset 初始化
  metadata.json
    -> years
    -> variables
    -> 校验 params.dataset.channels 是否存在
  stats/global_means.npy, stats/global_stds.npy
    -> channel_indices = variables.index(channel)
    -> mu = mu[:, channel_indices, :, :]
    -> sd = std[:, channel_indices, :, :]
  mode
    -> split_attr = train_years | val_years | test_years
    -> 必须得到显式年份列表
    -> selected_years
  selected_years
    -> data/<year>/*.nc
    -> sample_counts[year] = len(files) - input_steps - output_steps + 1
    -> year_offsets
    -> total_samples
  img_size
    -> latlon_grid(bounds=((90, -90), (0, 360)), shape=img_size[-2:])
    -> latlon_torch
  样例 .nc
    -> fields 变量存在性校验
    -> 推断 channel/lat/lon 维度名
    -> 若 channel 维有坐标，则用文件坐标重新校验变量顺序
    -> img_shape 按 patch_size 对齐

运行时取样
  idx
    -> bisect(year_offsets) 定位 year_idx
    -> step_idx = idx - year_offsets[year_idx]
    -> year = selected_years[year_idx]
  file_indices = step_idx : step_idx + input_steps + output_steps
    -> 逐文件 xr.open_dataset
    -> fields.transpose(channel_dim, lat_dim, lon_dim)
    -> isel(channel_indices)
    -> data: (input_steps + output_steps, Channels, Height, Width)
    -> 裁剪到 img_shape
    -> normalize=True 时执行 (x - mu) / sd
    -> 生成 cos_zenith
    -> return invar.squeeze(0), outvar.squeeze(0), cos_zenith, step_idx, time_index

Dataloader 装配
  train_dataloader()
    -> _build_dataloader("train")
    -> distributed=True: DistributedSampler(shuffle=True)
    -> distributed=False: shuffle=True
  val_dataloader()
    -> _build_dataloader("val")
    -> distributed=True: DistributedSampler(shuffle=False)
    -> distributed=False: shuffle=False
  test_dataloader()
    -> batch_size=1
    -> shuffle=False
    -> 不返回 sampler
```

# data_loading

- 主数据采用 NetCDF `.nc` 文件，源码实际读取路径为 `params.dataset.data_dir/data/<year>/*.nc`。
- 每个 `.nc` 文件对应一个时间步，文件排序后作为时间序列使用。
- 数据根目录必须包含 `metadata.json`，其中至少包含：
  - `years`: 可用年份列表。
  - `variables`: 全量变量名列表。
- 每个 NetCDF 文件必须包含变量 `fields`。
- `fields` 的维度名具有一定兼容性：
  - 通道维优先识别 `channel`、`variable`、`variables`，否则使用第一个维度。
  - 纬度维优先识别 `latitude`、`lat`，否则使用倒数第二个维度。
  - 经度维优先识别 `longitude`、`lon`，否则使用最后一个维度。
- 如果 `fields` 的通道维带坐标，源码会从文件坐标中读取变量名并重新建立 `channel_indices`。
- 统计量从 `params.dataset.stats_dir/global_means.npy` 与 `global_stds.npy` 读取，并按 `channel_indices` 切片。

# sampling_strategy

- 数据集划分必须通过显式年份列表完成：
  - `params.dataset.train_years`
  - `params.dataset.val_years`
  - `params.dataset.test_years`
- 源码会在找不到对应显式年份字段时尝试读取历史字段 `train_ratio`、`val_ratio`、`test_ratio`，但仍要求其值是 list/tuple/set；比例数字不会被接受。
- 每个年份内部按排序后的 `.nc` 文件做连续滑动窗口采样：
  - 窗口长度为 `input_steps + output_steps`。
  - 年份有效样本数为 `len(files) - input_steps - output_steps + 1`。
  - 每个年份样本数可以不同；源码使用 `year_offsets` 与 `bisect` 支持跨年份变长索引。
- 全局索引映射：
  - `year_idx = bisect_right(year_offsets, idx) - 1`
  - `step_idx = idx - year_offsets[year_idx]`
  - `year = selected_years[year_idx]`
- DataLoader 策略：
  - 训练模式：非分布式 `shuffle=True`，分布式使用 `DistributedSampler(shuffle=True)`。
  - 验证模式：不打乱，分布式使用 `DistributedSampler(shuffle=False)`。
  - 测试模式：`batch_size=1`，`shuffle=False`，不创建分布式 sampler。

# data_transform

- 变量筛选：根据 `params.dataset.channels` 在 metadata 或文件坐标变量名中建立 `channel_indices`，只读取所需变量。
- 维度规整：每个文件读取后执行 `fields.transpose(channel_dim, lat_dim, lon_dim)`，统一为 `(Channels, Height, Width)`。
- 时间窗口堆叠：连续读取 `input_steps + output_steps` 个 `.nc` 文件，并沿时间维堆叠为 `(Steps, Channels, Height, Width)`。
- 输入/目标切分：
  - `invar = data[:input_steps]`
  - `outvar = data[input_steps:]`
- patch 对齐裁剪：
  - 从样例文件推断原始 `Height/Width`。
  - `img_shape = [s - s % patch_size[i] for i, s in enumerate(shape[-2:])]`。
  - 样本裁剪为 `[:, :, :h, :w]`。
- 标准化：当 `normalize=True` 时执行 `(x - mu) / sd`；源码不做 NaN 填补或异常值清洗。
- 经纬度网格：使用 `params.dataset.img_size[-2:]` 与全局边界 `((90, -90), (0, 360))` 生成纬度、经度网格。
- 太阳天顶角：以 `datetime(year, 1, 1, tzinfo=pytz.utc)` 为起点，根据 `step_idx`、`output_steps` 和 `params.dataset.time_res` 构造预测时间戳，并调用 `cos_zenith_angle`。
- 时间索引：返回每个窗口文件名去掉扩展名后的字符串列表。
- 返回前压缩：对 `invar` 与 `outvar` 调用 `squeeze(0)`；单步输入或输出会移除时间维。

# input_schema

Python 参数结构：

```text
params.dataset:
  data_dir: TJWeather 数据根目录
  stats_dir: 统计量目录
  channels: 需要使用的变量名列表
  train_years: 训练年份列表
  val_years: 验证年份列表
  test_years: 测试年份列表
  time_res: 时间分辨率，单位小时
  img_size: 用于生成经纬度网格的空间尺寸，至少末两维为 Height/Width

params.dataloader:
  batch_size: 训练/验证批大小
  num_workers: DataLoader worker 数
  pin_memory: 可选，默认 True

TJDatapipe:
  distributed: 是否启用分布式采样
  input_steps: 输入时间步数，默认 1
  output_steps: 输出时间步数，默认 1
  normalize: 是否 z-score 标准化，默认 True
```

目录与文件结构：

```text
data_dir/
  metadata.json
  data/
    <year>/
      <timestamp>.nc
      ...
  stats/
    global_means.npy
    global_stds.npy
```

NetCDF 单文件结构：

```text
<timestamp>.nc
  fields:
    dims: channel/variable/variables, latitude/lat, longitude/lon
    shape: [Channels, Height, Width]
```

# output_schema

单样本返回五元组：

```text
invar:
  含义: 输入气象场
  input_steps=1:  (Channels, Height, Width)
  input_steps>1:  (input_steps, Channels, Height, Width)
  dtype: 由 NetCDF 数据转换为 torch.Tensor 后保留，通常为浮点张量

outvar:
  含义: 目标气象场
  output_steps=1: (Channels, Height, Width)
  output_steps>1: (output_steps, Channels, Height, Width)
  dtype: 由 NetCDF 数据转换为 torch.Tensor 后保留，通常为浮点张量

cos_zenith:
  含义: 预测时间步对应的太阳天顶角余弦特征
  shape: 通常与 (output_steps, Height, Width) 对齐
  dtype: torch.float32

step_idx:
  含义: 当前样本在所属年份内的起始文件索引
  type: int

time_index:
  含义: 输入与输出窗口对应的文件名时间索引
  length: input_steps + output_steps
  type: List[str]
```

Dataloader 返回：

```text
train_dataloader():
  (data_loader, sampler)

val_dataloader():
  (data_loader, sampler)

test_dataloader():
  data_loader
```

# constraints

- `metadata.json` 必须存在，并包含 `years` 与 `variables`。
- `params.dataset.channels` 中每个变量必须存在于 `metadata.json["variables"]`；若文件通道维坐标存在，还必须存在于文件坐标变量名中。
- 对应 mode 的年份列表必须显式配置且非空；比例数值不会被解释为划分比例。
- 所选年份必须全部存在于 `metadata.json["years"]`。
- 每个所选年份目录必须存在 `.nc` 文件，且文件数必须大于等于 `input_steps + output_steps`。
- 每个 `.nc` 文件必须包含变量 `fields`。
- 统计量 `.npy` 必须存在，并且能按 `[:, channel_indices, :, :]` 切片并广播到样本张量。
- 源码不做 NaN 填补、单位换算、质量控制或时间轴重采样。
- 文件名排序即时间顺序；如果文件命名不能正确排序，窗口采样会错位。
- `cos_zenith` 时间戳假设每年从 UTC 1 月 1 日 00 时开始，并按固定 `time_res` 均匀推进。
- `latlon_torch` 使用 `params.dataset.img_size[-2:]` 生成，样本实际裁剪尺寸来自文件和 patch_size；两者应保持一致，避免空间特征与样本尺寸不匹配。
- `squeeze(0)` 会在单步输入或输出时移除时间维，下游模型需显式适配。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/climate/tjweather.py`
- `{onescience_path}/onescience/src/onescience/datapipes/climate/utils/zenith_angle.py`
- `{onescience_path}/onescience/src/onescience/datapipes/climate/utils/invariant.py`
- `{onescience_path}/onescience/src/onescience/datapipes/core.py`
