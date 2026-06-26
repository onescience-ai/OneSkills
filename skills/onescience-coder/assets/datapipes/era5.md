# Datapipe: ERA5Datapipe

## 基本信息

- Datapipe 名称：`ERA5Datapipe`
- 数据类型：`climate`
- 主要任务：`weather forecasting on regular grids`
- 数据组织方式：`yearly_hdf5_files`

## 管道职责

`ERA5Datapipe` 负责从 OneScience 数据卡中读取已配置的 ERA5 气象数据，并切成连续时间窗样本，组织为适合天气预测模型训练或推理的 `DataLoader`。

## 管道架构

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

## 数据加载

- 原始数据使用按年份组织的 HDF5 文件，源码实际搜索路径为 `dataset_dir/data/*.h5`，并按 `<year>.h5` 文件名解析可用年份。
- 每个 HDF5 文件必须包含 `fields` 数据集，形状为 `[TimeSteps, Channels, Height, Width]`。
- `fields.attrs["variables"]` 提供通道变量名，支持 bytes 或字符串；`fields.attrs["time_step"]` 提供小时级时间步长。
- 归一化统计量读取规则：
  - 优先使用同一 HDF5 文件中的 `global_means` 与 `global_stds`。
  - 若 HDF5 内没有统计量，则读取 `dataset_dir/stats/global_means.npy` 与 `dataset_dir/stats/global_stds.npy`。
- 参考数据卡约定的主数据路径为 `{ONESCIENCE_DATASETS_DIR}/ERA5/newh5/data_merged/<year>.h5`，统计量路径为 `{ONESCIENCE_DATASETS_DIR}/ERA5/newh5/stats/global_means.npy` 与 `global_stds.npy`；当前源码路径约定需要调用侧将 `dataset_dir` 对齐为含 `data/` 与 `stats/` 子目录的根目录。

## 采样策略

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

## 数据转换

- 变量筛选：根据 `used_variables` 在 `fields.attrs["variables"]` 中建立 `channel_indices`，只保留任务需要的通道。
- 时间窗切片：从 `fields` 读取 `input_steps + output_steps` 个连续时间步，前半段作为输入，后半段作为目标。
- 类型转换：将 HDF5/numpy 数据转换为 `torch.float32`。
- 标准化：当 `normalize=True` 时，对输入与输出执行 `(x - global_means) / global_stds`，统计量按所选通道同步切片。
- 经纬度网格：使用全球规则网格边界 `((90, -90), (0, 360))` 和 H/W 生成纬度、经度网格。
- 太阳天顶角：以 `datetime(year, 1, 1, tzinfo=pytz.utc)` 为起点，根据 `step_idx`、`input_steps`、`output_steps` 和 `time_step` 生成预测步时间戳，再调用 `cos_zenith_angle` 生成 `cos_zenith`。
- 时间索引：生成覆盖输入与输出窗口的 `YYYYMMDDHH` 字符串列表。
- 维度压缩：返回前对 `invar` 和 `outvar` 调用 `squeeze(0)`；当 `input_steps=1` 或 `output_steps=1` 时会去掉对应时间维。

## 输入规格

- `dataset_dir`: ERA5 数据根目录；源码期望其下存在 `data/<year>.h5` 和可选 `stats/`。
- `used_years`: 年份列表，例如 `[1979, 1980]`；每个年份必须有对应 HDF5 文件。
- `used_variables`: 变量名列表；所有变量必须存在于 `fields.attrs["variables"]`。
- `distributed`: 是否启用分布式 sampler。
- `input_steps`: 输入时间步数，默认 `1`。
- `output_steps`: 预测时间步数，默认 `1`。
- `normalize`: 是否使用全局均值和标准差做标准化，默认 `True`。
- `batch_size`: 训练/验证 DataLoader 批大小；测试模式会被覆盖为 `1`。
- `num_workers`: DataLoader 工作进程数。

## 输出规格

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

## 约束条件

- `used_years` 中每个年份必须存在于数据目录中，否则初始化时抛出 `ValueError`。
- `used_variables` 中每个变量必须存在于 HDF5 元数据 `fields.attrs["variables"]` 中，否则初始化时抛出 `ValueError`。
- `fields` 必须是四维 `[TimeSteps, Channels, Height, Width]`；代码不处理缺失维度、非规则网格或非 HDF5 格式。
- `T` 必须满足 `T >= input_steps + output_steps`，否则 `samples_per_year` 会小于等于 0，采样不可用。
- 标准化统计量必须覆盖全部变量通道，并能按 `[:, channel_indices, :, :]` 切片。
- 当前实现即使 `normalize=False` 也会初始化统计量文件；统计量缺失时仍可能在初始化阶段失败。
- `time_index` 与 `cos_zenith` 假设每个年份从 UTC 的 1 月 1 日 00 时开始，并按固定 `time_step` 均匀采样。
- 参考数据卡的 `data_merged/<year>.h5` 路径与源码 `data/<year>.h5` 约定不完全一致，落地时必须统一目录结构或做适配。

## 启动方式

ERA5Datapipe 主要通过 Python API 启动；源码未提供独立 CLI。下面示例给出完整参数，并假设数据根目录已经整理为包含 `data/` 与 `stats/` 子目录的结构。

```sh
python -c "from onescience.datapipes.climate.era5 import ERA5Datapipe; dp = ERA5Datapipe(dataset_dir=r'%ONESCIENCE_DATASETS_DIR%/ERA5/newh5', used_years=[1979, 1980], used_variables=['u10', 'v10', 't2m'], distributed=False, input_steps=1, output_steps=1, normalize=True, batch_size=4, num_workers=4); loader, sampler = dp.get_dataloader(mode='train'); batch = next(iter(loader)); print(type(batch), len(batch))"
```

典型训练脚本中可按阶段分别构造 datapipe：

```python
from onescience.datapipes.climate.era5 import ERA5Datapipe

train_pipe = ERA5Datapipe(
    dataset_dir="/path/to/ERA5/newh5",
    used_years=[1979, 1980, 1981],
    used_variables=["u10", "v10", "t2m"],
    distributed=False,
    input_steps=1,
    output_steps=1,
    normalize=True,
    batch_size=8,
    num_workers=4,
)

train_loader, train_sampler = train_pipe.get_dataloader(mode="train")
```

## 运行接口

- `ERA5Datapipe(...)`
  - 保存数据路径、年份、变量、分布式开关、窗口长度、归一化开关和 DataLoader 参数。
- `get_dataloader(mode)`
  - 构造 `ERA5Dataset`。
  - 根据 `mode` 和 `distributed` 选择 shuffle 或 `DistributedSampler`。
  - 返回 `(DataLoader, sampler)`。
- `ERA5Dataset(...)`
  - 执行年份文件发现、变量校验、样本数量计算、统计量读取和经纬度网格初始化。
- `ERA5Dataset.__getitem__(idx)`
  - 将全局样本索引映射到年份与年份内时间步，读取连续窗口并返回模型可消费的 batch 元素。

## 主要函数

- `get_dataloader`

## 执行资源

- 计算资源：
  - 数据读取和预处理主要运行在 CPU。
  - `DataLoader(pin_memory=True)` 适合后续将 batch 搬运到 GPU/DCU 训练流程。
- 存储资源：
  - 需要本地或共享文件系统提供按年份 HDF5 文件。
  - 多 worker 读取会并发打开 HDF5 文件，底层文件系统需要能承受相应 I/O。
- Python 依赖：
  - `h5py`
  - `numpy`
  - `pytz`
  - `torch`
  - OneScience climate utils 中的 `latlon_grid` 与 `cos_zenith_angle`
- 分布式运行：
  - `distributed=True` 时仅创建 `DistributedSampler`，调用方仍需在训练入口完成进程组初始化，并在每个 epoch 按常规方式设置 sampler epoch。

## 操作限制

- 仅支持按年份 HDF5 文件组织的规则经纬度 ERA5 数据，不直接支持 NetCDF、Zarr、GRIB 或非结构网格。
- 路径结构必须与源码期望一致；若只有数据卡中的 `data_merged/` 目录，需要在调用前调整 `dataset_dir`、目录名或建立适配层。
- `used_years` 与 `used_variables` 校验严格，年份文件缺失或变量名不匹配会直接失败。
- 当前 datapipe 不做缺失值填补、异常值清洗、时间轴重采样或变量单位转换。
- `normalize=False` 不代表可以省略统计量文件，因为初始化流程仍会尝试读取统计量。
- 当 `input_steps=1` 或 `output_steps=1` 时，返回张量会被 `squeeze(0)` 去掉时间维；下游模型或 collate 后处理需要显式处理这一点。
- 测试模式固定 `batch_size=1`，不适合直接用于大 batch 离线推理吞吐测试，除非外层另行封装。

## 规划决策

### 描述

ERA5Datapipe 的规划决策重点是判断一套气象数据是否已经满足 OneScience ERA5 年份 HDF5 协议，并决定应直接复用、做路径/元数据适配，还是新增更上层的数据转换流程。它适合把已整理好的 ERA5 全球规则网格数据切分为连续时间窗，输出给天气预测模型训练、验证、测试或推理流程；不承担原始 GRIB/NetCDF 清洗、变量单位统一、时间轴重采样和数据集划分策略生成。

### 使用时机

- 任务目标是全球或区域规则网格天气预报，且数据已经整理为按年份存储的 HDF5。
- 需要从 ERA5 数据中按 `used_variables` 筛选变量通道。
- 需要用 `input_steps` 与 `output_steps` 构造连续时间窗样本。
- 需要标准化输入/目标，并为预测步生成太阳天顶角特征。
- 训练、验证、测试的年份集合已经由配置或上游规划确定，可以通过 `used_years` 显式传入。

不建议直接使用的场景：

- 数据仍是 GRIB、NetCDF、Zarr 或其他未转 HDF5 的格式。
- 任务需要复杂质量控制、缺失值填补、时间重采样或单位换算。
- 下游模型要求固定保留时间维，但当前 `squeeze(0)` 行为会改变单步样本形状。
- 数据目录只能提供 `data_merged/`，而调用环境无法调整为源码期望的 `data/`。

### 输入

- 数据目录决策输入：
  - `dataset_dir`
  - 年份 HDF5 文件是否位于 `dataset_dir/data/<year>.h5`
  - 统计量是否位于 HDF5 内部，或位于 `dataset_dir/stats/`
- 数据内容决策输入：
  - `fields` shape
  - `fields.attrs["variables"]`
  - `fields.attrs["time_step"]`
  - `global_means/global_stds` shape
- 任务配置决策输入：
  - train/val/test 对应的 `used_years`
  - `used_variables`
  - `input_steps`
  - `output_steps`
  - `normalize`
  - `batch_size`
  - `distributed`
- 下游约束决策输入：
  - 模型期望的变量通道数
  - 模型是否接受单步样本的 squeezed shape
  - 训练脚本是否已初始化分布式环境

### 输出

规划阶段应输出以下结构化决策：

```text
datapipe_choice:
  name: ERA5Datapipe
  action: reuse | adapt_path | adapt_metadata | build_converter | reject

data_contract:
  dataset_dir: <resolved path>
  year_files: dataset_dir/data/<year>.h5
  stats_source: embedded_h5 | stats_npy
  variables: <selected variables>
  input_steps: <int>
  output_steps: <int>

split_plan:
  train_years: [...]
  val_years: [...]
  test_years: [...]

runtime_plan:
  mode: train | val | test
  distributed: true | false
  batch_size: <int>
  num_workers: <int>

risk_flags:
  - path_layout_mismatch
  - missing_variables
  - missing_stats
  - time_axis_assumption
  - squeezed_time_dimension
```

### 执行步骤

1. 确认任务是否属于 ERA5 或 ERA5 风格的规则经纬度天气预测数据读取。
2. 检查数据是否已转为按年份 HDF5，并确认每个目标年份存在对应文件。
3. 对齐路径结构：
   - 若已有 `dataset_dir/data/<year>.h5`，可直接复用。
   - 若只有数据卡中的 `data_merged/<year>.h5`，先规划目录调整、软链接或轻量 adapter。
4. 打开一个样例 HDF5 文件，检查 `fields` 维度、变量属性和 `time_step`。
5. 比对 `used_variables` 与 HDF5 变量名，必要时生成变量映射或要求上游修复数据元数据。
6. 检查统计量来源；若没有 HDF5 内嵌统计量，则确认 `stats/global_means.npy` 和 `global_stds.npy` 可用。
7. 根据任务阶段配置 `used_years`，不要指望 datapipe 内部自动划分 train/val/test。
8. 根据下游模型输入协议评估 `input_steps/output_steps` 与 squeezed shape 是否需要外层 collate/adapter。
9. 构造 `ERA5Datapipe`，调用 `get_dataloader(mode)`，在小样本上验证 batch 五元组的 shape、dtype 和时间索引。
10. 再接入训练或推理主流程。

### 约束

- 不要在没有检查 `fields.attrs["variables"]` 的情况下猜测通道顺序。
- 不要把 train/val/test 划分逻辑塞进 datapipe；应由外部配置明确传入 `used_years`。
- 不要把路径不一致问题交给模型层处理；应在数据目录、数据卡或 datapipe adapter 层解决。
- 若下游模型要求多步时间维始终存在，需要在外层封装或修改 datapipe 返回协议，避免单步 `squeeze(0)` 引发隐式 shape 漂移。
- 若启用分布式采样，训练入口必须已完成分布式初始化；datapipe 只负责 sampler 构造。
- `cos_zenith` 的时间假设来自年份起点和固定 `time_step`，若数据文件内部存在非均匀时间轴或非 UTC 时间定义，必须先修正数据或替换时间特征生成逻辑。

### 下一阶段建议

- 若目标是训练天气模型，下一阶段应生成变量列表、年份划分、模型输入通道映射、loss/metric 配置和训练脚本中的 dataloader 初始化代码。
- 若目标是新增 ERA5 派生数据，下一阶段应先写数据转换/校验脚本，把原始数据整理成 `fields + variables + time_step + stats` 协议。
- 若目标是模型适配，下一阶段应验证 batch 中 `invar/outvar/cos_zenith` 的 shape 是否与模型 forward 和训练 loop 匹配，再决定是否加 adapter。
- 若目标是大规模训练，下一阶段应做 I/O 吞吐测试，调整 `num_workers`、batch size、缓存策略和分布式 sampler 设置。

### 回退策略

- 年份文件缺失：重新解析 `used_years`，检查数据目录；若数据在 `data_merged/`，创建路径适配或修改配置中的 `dataset_dir`。
- 变量缺失：从 HDF5 `variables` 属性生成可用变量清单，修正 `used_variables` 或重建数据元数据。
- 统计量缺失：优先检查 HDF5 是否可内嵌 `global_means/global_stds`；否则生成 `stats/global_means.npy` 与 `global_stds.npy`。
- shape 不符合下游模型：在 datapipe 外层添加 adapter，统一补回时间维或重排维度。
- 时间特征不可信：暂时禁用依赖 `cos_zenith` 的模型分支，或用真实时间轴重写时间戳生成逻辑。
- HDF5 并发读取不稳定：降低 `num_workers`，切换本地缓存，或在训练前做数据分片与 I/O 压测。

## 源码锚点

- `{onescience_path}/onescience/src/onescience/datapipes/climate/era5.py`
- `{onescience_path}/onescience/src/onescience/datapipes/climate/utils/invariant.py`
- `{onescience_path}/onescience/src/onescience/datapipes/climate/utils/zenith_angle.py`
