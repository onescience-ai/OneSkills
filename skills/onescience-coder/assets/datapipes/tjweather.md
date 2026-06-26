# Datapipe: TJWeatherDatapipe

## 基本信息

- Datapipe 名称：`TJWeatherDatapipe`
- 数据类型：`climate`
- 主要任务：`将按年份目录存储的逐时间步 NetCDF 文件，组织成多步输入 / 多步输出的气象预报训练样本`
- 数据组织方式：`yearly_timestep_netcdf_files`

## 管道职责

将按年份目录存储的逐时间步 NetCDF 文件，组织成多步输入 / 多步输出的气象预报训练样本。

- 数据目录结构：`<data_dir>/data/<year>/*.nc`，每个 `.nc` 文件对应一个时间步
- 负责变量筛选、归一化（z-score）、空间裁剪（patch 对齐）、cos 太阳天顶角生成
- 同时负责 `Dataset`（`TJDataset`）与 `DataLoader`（`TJDatapipe`）

## 管道架构

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

## 数据加载

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

## 采样策略

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

## 数据转换

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

## 输入规格

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

## 输出规格

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

## 约束条件

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

## 启动方式

TJDatapipe 主要通过 Python API 或训练 pipeline 配置启动；源码未提供独立 CLI。下面示例给出完整参数形态，并假设数据目录已经包含 `metadata.json`、`data/<year>/*.nc` 和 `stats/*.npy`。

```sh
python -c "from types import SimpleNamespace; from onescience.datapipes.climate.tjweather import TJDatapipe; dataset = SimpleNamespace(data_dir=r'%ONESCIENCE_DATASETS_DIR%/TJWeather/TJ1-GB', stats_dir=r'%ONESCIENCE_DATASETS_DIR%/TJWeather/TJ1-GB/stats', channels=['t2mz', 'UGRD10m', 'VGRD10m'], train_years=[2023], val_years=[2024], test_years=[2025], time_res=1, img_size=[1, 1, 1800, 3600]); dataloader = SimpleNamespace(batch_size=2, num_workers=4, pin_memory=True); params = SimpleNamespace(dataset=dataset, dataloader=dataloader); dp = TJDatapipe(params=params, distributed=False, output_steps=1, input_steps=1, normalize=True); loader, sampler = dp.train_dataloader(); batch = next(iter(loader)); print(type(batch), len(batch))"
```

典型训练脚本中可直接使用阶段接口：

```python
from types import SimpleNamespace
from onescience.datapipes.climate.tjweather import TJDatapipe

dataset = SimpleNamespace(
    data_dir="/path/to/TJWeather/TJ1-GB",
    stats_dir="/path/to/TJWeather/TJ1-GB/stats",
    channels=["t2mz", "UGRD10m", "VGRD10m"],
    train_years=[2023],
    val_years=[2024],
    test_years=[2025],
    time_res=1,
    img_size=[1, 1, 1800, 3600],
)
dataloader = SimpleNamespace(batch_size=2, num_workers=4, pin_memory=True)
params = SimpleNamespace(dataset=dataset, dataloader=dataloader)

pipe = TJDatapipe(
    params=params,
    distributed=False,
    output_steps=1,
    input_steps=1,
    normalize=True,
)

train_loader, train_sampler = pipe.train_dataloader()
val_loader, val_sampler = pipe.val_dataloader()
test_loader = pipe.test_dataloader()
```

## 运行接口

- `TJDatapipe(params, distributed, output_steps=1, input_steps=1, normalize=True)`
  - 保存数据配置、dataloader 配置、分布式开关、输入/输出窗口长度和标准化开关。
- `train_dataloader()`
  - 构造训练模式 `TJDataset`，返回 `(DataLoader, sampler)`。
- `val_dataloader()`
  - 构造验证模式 `TJDataset`，返回 `(DataLoader, sampler)`。
- `test_dataloader()`
  - 构造测试模式 `TJDataset`，返回 `DataLoader`，batch size 固定为 `1`。
- `TJDataset(...)`
  - 读取 metadata、统计量、年份 split、文件列表、经纬度网格和样本空间 shape。
- `TJDataset.__getitem__(idx)`
  - 将全局样本索引映射到年份和年份内偏移，逐文件读取连续时间窗口并返回五元组样本。

## 主要函数

- `train_dataloader`
- `val_dataloader`
- `test_dataloader`

## 执行资源

- 计算资源：
  - 数据读取、变量筛选、裁剪、标准化和太阳天顶角生成主要在 CPU 上完成。
  - `pin_memory=True` 便于后续训练流程将 batch 迁移到 GPU/DCU 等加速设备。
- 存储与 I/O：
  - 每个样本会逐时间步打开多个 `.nc` 文件。
  - 高 `num_workers` 和大 batch 会显著增加 NetCDF 文件并发读取压力。
  - 建议在共享文件系统上先做小样本吞吐测试，再扩大 worker 数。
- Python 依赖：
  - `numpy`
  - `pytz`
  - `torch`
  - `xarray`
  - OneScience datapipes 基类与 climate utils
- 分布式运行：
  - `distributed=True` 时训练/验证会创建 `DistributedSampler`。
  - 调用方需要在训练入口完成分布式进程组初始化，并按 epoch 设置 sampler 状态。

## 操作限制

- 仅直接支持已经转换为 `data/<year>/*.nc` 的 TJWeather 风格逐时间步 NetCDF 数据。
- 不直接支持单个 NetCDF 内含完整长时间轴且未拆分为逐文件时间步的布局，除非先做转换或 adapter。
- `train_years`、`val_years`、`test_years` 必须显式给出，不能依赖比例自动划分。
- 文件名排序被视为时间顺序；命名不规范会导致窗口顺序错误。
- 当前实现不做缺失值填补、异常值清洗、单位换算、空间插值或时间重采样。
- `normalize=False` 不会跳过统计量读取；统计量缺失仍会在初始化阶段失败。
- 测试接口不返回 sampler；若测试阶段也需要分布式切分，需要外层自行封装。
- 单步输入或输出会因 `squeeze(0)` 移除时间维，下游模型若要求固定时间维需要补维。

## 规划决策

### 描述

TJDatapipe 的规划决策重点是判断一套中科天机气象数据是否已经满足 OneScience 当前 TJWeather 逐时间步 NetCDF 协议，并决定应直接复用、做路径/元数据适配，还是先新增转换流程。它适合把已经按年份和时间步整理好的 `.nc` 文件切分为多步输入和多步输出窗口，并输出给气象预报模型训练、验证、测试或推理流程；它不承担原始数据清洗、变量单位统一、时间重采样、空间重网格、自动年份划分和质量控制。

### 使用时机

- 任务目标是 TJWeather 或 TJWeather 风格的规则经纬度气象预报。
- 数据已经按 `data/<year>/*.nc` 组织，每个 `.nc` 文件对应一个时间步。
- 每个 NetCDF 文件中存在 `fields` 变量，且可以被规整为 `(Channels, Height, Width)`。
- 已有 `metadata.json` 描述可用年份和变量列表。
- 已有 `global_means.npy` 与 `global_stds.npy` 统计量。
- 需要用 `input_steps` 和 `output_steps` 构造连续时间窗口。
- 需要按显式年份列表组织 train/val/test 阶段。
- 下游模型接受返回的五元组结构，或可以通过轻量 adapter 适配。

不建议直接使用的场景：

- 数据仍是 GRIB、Zarr、单体长时间轴 NetCDF 或其他未拆分格式。
- 文件目录不是 `data/<year>/*.nc`，且暂时不能调整路径或添加 adapter。
- 变量名、通道坐标或统计量通道顺序无法与 `params.dataset.channels` 对齐。
- 任务需要复杂缺失值填补、质量控制、空间插值、单位换算或时间轴重采样。
- 下游模型不接受单步样本的 squeezed shape。

### 输入

- 数据目录决策输入：
  - `data_dir`
  - `stats_dir`
  - `metadata.json` 是否存在
  - `data/<year>/*.nc` 是否存在
- 数据内容决策输入：
  - `metadata.json["years"]`
  - `metadata.json["variables"]`
  - `.nc` 文件中的 `fields` 变量
  - `fields` 的通道、纬度、经度维度名
  - 通道维坐标是否给出变量名
  - `global_means/global_stds` shape
- 任务配置决策输入：
  - `channels`
  - `train_years`
  - `val_years`
  - `test_years`
  - `input_steps`
  - `output_steps`
  - `time_res`
  - `img_size`
  - `normalize`
  - `batch_size`
  - `num_workers`
  - `distributed`
- 下游约束决策输入：
  - 模型期望变量顺序
  - 模型是否依赖 `cos_zenith`
  - 模型是否要求单步样本保留时间维
  - 训练入口是否已经初始化分布式环境
  - 文件系统是否能承受并发 NetCDF 读取

### 输出

规划阶段应输出以下结构化决策：

```text
datapipe_choice:
  name: TJDatapipe
  action: reuse | adapt_path | adapt_metadata | build_converter | reject

data_contract:
  data_dir: <resolved path>
  stats_dir: <resolved path>
  file_layout: data/<year>/*.nc
  fields_variable: fields
  variables: <selected channels>
  input_steps: <int>
  output_steps: <int>
  time_res: <hours>

split_plan:
  train_years: [...]
  val_years: [...]
  test_years: [...]

runtime_plan:
  interface: train_dataloader | val_dataloader | test_dataloader
  distributed: true | false
  batch_size: <int>
  num_workers: <int>
  normalize: true | false

risk_flags:
  - path_layout_mismatch
  - missing_metadata
  - missing_years
  - missing_variables
  - channel_order_mismatch
  - missing_stats
  - unsorted_time_files
  - inconsistent_img_size
  - squeezed_time_dimension
  - netcdf_io_bottleneck
```

### 执行步骤

1. 确认任务是否属于 TJWeather 或 TJWeather 风格的规则经纬度气象预测。
2. 检查数据是否已经整理为 `data/<year>/*.nc`；若不是，先规划转换或路径 adapter。
3. 读取 `metadata.json`，确认 `years` 与 `variables` 存在。
4. 校验 `train_years`、`val_years`、`test_years` 是显式非空年份列表，并且都在 `metadata.json["years"]` 中。
5. 比对 `channels` 与 `metadata.json["variables"]`，确认任务变量都存在。
6. 打开一个样例 `.nc` 文件，确认存在 `fields` 变量。
7. 推断或确认 `fields` 的 channel/lat/lon 维度；如果通道维带坐标，继续校验变量坐标与 `channels` 匹配。
8. 检查每个目标年份目录的 `.nc` 文件数量是否满足 `input_steps + output_steps`。
9. 检查文件名排序是否等价于时间顺序；必要时在转换阶段重命名或生成排序清单。
10. 检查 `global_means.npy` 和 `global_stds.npy` 是否存在，shape 是否可按 `channel_indices` 切片并广播。
11. 核对 `img_size[-2:]` 与样本裁剪后空间尺寸是否一致，避免 `cos_zenith` 与样本空间维不匹配。
12. 根据下游模型协议评估 `squeeze(0)` 行为是否需要外层补维 adapter。
13. 构造 `TJDatapipe` 并调用目标阶段 dataloader，在小样本上验证返回五元组的 shape、dtype 和时间索引。
14. 再接入训练、验证、测试或推理主流程。

### 约束

- 不要使用比例数字期望 datapipe 自动划分年份；源码要求显式年份集合。
- 不要在未检查 metadata 和文件通道坐标的情况下假设变量顺序。
- 不要让模型层承担路径布局、变量命名或统计量缺失问题；这些应在数据准备或 adapter 层解决。
- 不要假设 `normalize=False` 可以省略统计量文件；源码初始化仍读取统计量。
- 若 `img_size` 与文件实际空间尺寸不同，必须确认裁剪后尺寸与 `cos_zenith` 尺寸一致。
- 若启用分布式采样，训练入口必须先初始化分布式环境；datapipe 只构造 sampler。
- 若下游模型要求固定时间维，必须处理 `squeeze(0)` 引发的单步维度变化。
- 若文件系统无法支撑高并发 NetCDF 读取，应限制 `num_workers` 或先转换为更适合训练的存储格式。

### 下一阶段建议

- 若目标是训练 TJWeather 气象模型，下一阶段应生成 channels、年份划分、模型输入通道映射、loss/metric 配置和 dataloader 初始化代码。
- 若目标是接入新的 TJWeather 子数据集，下一阶段应先编写转换和校验脚本，统一生成 `metadata.json`、`data/<year>/*.nc` 和 `stats/*.npy`。
- 若目标是模型适配，下一阶段应验证 `invar/outvar/cos_zenith` 的 shape 是否与 forward 和训练 loop 匹配，再决定是否补维、裁剪或重排维度。
- 若目标是大规模训练，下一阶段应做 NetCDF I/O 压测，评估 `num_workers`、batch size、本地缓存和数据格式转换策略。

### 回退策略

- `metadata.json` 缺失：从数据清单生成年份和变量列表，写回标准 metadata 后再加载。
- 年份目录或 `.nc` 文件缺失：修正 `train_years/val_years/test_years`，检查数据根目录，或建立路径适配。
- 变量缺失：从 `fields` 通道坐标提取可用变量清单，修正 `channels` 或重建数据变量元数据。
- 统计量缺失：按全量变量顺序重新计算 `global_means.npy` 与 `global_stds.npy`。
- 文件排序不可信：在转换阶段重命名为可排序时间戳，或修改外层 adapter 提供稳定排序。
- 空间尺寸不匹配：调整 `img_size`、`patch_size` 或外层裁剪逻辑，使样本和 `cos_zenith` 对齐。
- shape 不符合下游模型：在 datapipe 外层添加 adapter，补回时间维或重排维度。
- NetCDF 读取过慢：降低 `num_workers`，复制到本地高速盘，或离线转换为分片 HDF5/Zarr 等训练友好格式。

## 源码锚点

- `{onescience_path}/onescience/src/onescience/datapipes/climate/tjweather.py`
- `{onescience_path}/onescience/src/onescience/datapipes/climate/utils/zenith_angle.py`
- `{onescience_path}/onescience/src/onescience/datapipes/climate/utils/invariant.py`
- `{onescience_path}/onescience/src/onescience/datapipes/core.py`
