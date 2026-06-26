# Datapipe: CMEMSDatapipe

## 基本信息

- Datapipe 名称：`CMEMSDatapipe`
- 数据类型：`climate`
- 主要任务：`ocean forecasting on regular grids`
- 数据组织方式：`yearly_hdf5_files`

## 管道职责

`CMEMSDatapipe` 负责把按年份目录、按时刻存储的 CMEMS 海洋场数据切成连续时间窗样本,并组织成适合模型训练或推理的 `DataLoader`。

补充说明：

- 原始数据以"按年份分目录、目录下按时刻存 HDF5 文件"的方式组织
- datapipe 负责年份划分、变量筛选、时间窗切片、NaN 处理、归一化、太阳天顶角构造和 `DataLoader` 组装
- train / val / test 划分在 datapipe 内部通过配置完成

## 管道架构

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

## 数据加载

- 数据根目录由 `dataset_dir` 指定，源码实际搜索路径为 `dataset_dir/data/*.h5`。
- 每个年份文件名必须可解析为整数年份，例如 `1993.h5`；`used_years` 中的每个年份必须有对应文件。
- 每个 HDF5 文件必须包含 `fields` 数据集，且 `fields` 必须为四维数组 `[TimeSteps, Channels, Height, Width]`。
- 变量名来源优先级：
  - 首选 `fields.attrs["variables"]`，支持 bytes 或字符串形式。
  - 若 HDF5 属性缺失，则回退到 `dataset_dir/metadata.json` 中的 `variables` 字段。
- 时间步长必须由 `fields.attrs["time_step"]` 提供，单位按小时解释。
- 归一化统计量固定从 `dataset_dir/stats/global_means.npy` 与 `dataset_dir/stats/global_stds.npy` 读取。

## 采样策略

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

## 数据转换

- 变量筛选：根据 `used_variables` 在全部变量名中建立 `channel_indices`，只保留任务所需通道。
- 时间窗口切片：从 `fields` 连续读取 `input_steps + output_steps` 帧，前半段作为输入，后半段作为目标。
- 类型转换：将 HDF5/numpy 数据转换为 `torch.float32` 张量。
- 缺失值处理：对 `invar` 与 `outvar` 中的 `NaN` 使用所选通道对应的全局均值 `mu` 替换。
- 标准化：当 `normalize=True` 时，对输入与目标执行 `(x - mu) / sd`。
- 经纬度网格：使用全局规则网格边界 `((90, -90), (0, 360))` 和当前 `H/W` 生成纬度、经度网格。
- 太阳天顶角：以 `datetime(year, 1, 1, tzinfo=pytz.utc)` 为年份起点，根据 `step_idx`、`input_steps`、`output_steps` 和 `time_step` 生成预测时间戳，再调用 `cos_zenith_angle` 生成 `cos_zenith`。
- 时间索引：生成覆盖输入与输出窗口的 `YYYYMMDDHH` 字符串列表。
- 返回前压缩：对 `invar` 与 `outvar` 调用 `squeeze(0)`；当对应时间步为 `1` 时会移除时间维。

## 输入规格

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

## 输出规格

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

## 约束条件

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

## 启动方式

CMEMSDatapipe 主要通过 Python API 启动；源码未提供独立 CLI。下面示例给出完整参数，并假设数据根目录已经整理为包含 `data/` 与 `stats/` 子目录的结构。

```sh
python -c "from onescience.datapipes.climate.cmems import CMEMSDatapipe; dp = CMEMSDatapipe(dataset_dir=r'%ONESCIENCE_DATASETS_DIR%/CMEMS/h5', used_years=[1993, 1994], used_variables=['thetao', 'so', 'uo', 'vo'], distributed=False, input_steps=1, output_steps=1, normalize=True, batch_size=4, num_workers=4); loader, sampler = dp.get_dataloader(mode='train'); batch = next(iter(loader)); print(type(batch), len(batch))"
```

典型训练脚本中可按阶段分别构造 datapipe：

```python
from onescience.datapipes.climate.cmems import CMEMSDatapipe

train_pipe = CMEMSDatapipe(
    dataset_dir="/path/to/CMEMS/h5",
    used_years=[1993, 1994, 1995],
    used_variables=["thetao", "so", "uo", "vo"],
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

- `CMEMSDatapipe(...)`
  - 保存数据根目录、年份列表、变量列表、分布式开关、窗口长度、归一化开关和 DataLoader 参数。
- `get_dataloader(mode)`
  - 构造 `CMEMSDataset`。
  - 根据 `mode` 与 `distributed` 选择 shuffle 或分布式 sampler。
  - 返回 `(dataloader, sampler)`。
- `CMEMSDataset(...)`
  - 执行年份文件发现、变量校验、样本数量计算、统计量读取和经纬度网格初始化。
- `CMEMSDataset.__getitem__(idx)`
  - 将全局样本索引映射到年份与年份内起始时间步，读取连续窗口，并返回模型可消费的五元组样本。

## 主要函数

- `get_dataloader`

## 执行资源

- 计算资源：
  - 数据读取、索引、NaN 替换、标准化和时间特征构造主要运行在 CPU。
  - `pin_memory=True` 便于后续训练流程将 batch 迁移到加速设备。
- 存储资源：
  - 需要本地或共享文件系统提供按年份组织的 HDF5 文件。
  - 多 worker 会并发打开 HDF5 文件，底层文件系统需要具备足够 I/O 能力。
- Python 依赖：
  - `h5py`
  - `numpy`
  - `pytz`
  - `torch`
  - OneScience climate utils 中的 `latlon_grid` 与 `cos_zenith_angle`
- 分布式运行：
  - `distributed=True` 仅创建 `DistributedSampler`；调用方仍需在训练入口完成分布式进程组初始化，并按训练惯例设置 sampler epoch。

## 操作限制

- 仅直接支持按年份 HDF5 文件组织的规则经纬度 CMEMS 海洋数据；不直接读取 NetCDF、Zarr、GRIB 或非结构网格。
- 路径结构必须与源码期望一致；若原始数据仍是按时间戳文件或按年份目录组织，需要先转换或建立适配层。
- `used_years` 与 `used_variables` 校验严格，年份文件缺失或变量名不匹配会直接失败。
- 当前 datapipe 不执行复杂质量控制、异常值清洗、单位换算、时间轴重采样或空间重网格。
- `normalize=False` 不代表可以省略统计量文件；初始化流程仍会读取统计量，NaN 填补也依赖全局均值。
- 单步输入或输出会因 `squeeze(0)` 移除时间维，下游模型若要求固定时间维，需要外层 adapter 补回。
- 测试模式固定 `batch_size=1`，如需大 batch 离线推理吞吐测试，应在外层封装或调整调用方式。

## 规划决策

### 描述

CMEMSDatapipe 的规划决策重点是判断一套海洋预报数据是否已经满足当前 OneScience CMEMS 年份 HDF5 协议，并决定应直接复用、做路径/元数据适配，还是先新增数据转换流程。它适合把已整理好的 CMEMS 规则经纬度海洋场切分为连续时间窗口，输出给海洋预测模型的训练、验证、测试或推理流程；它不承担原始 NetCDF/Zarr 清洗、质量控制、单位统一、空间重网格和数据集划分策略生成。

### 使用时机

- 任务目标是 CMEMS 或 CMEMS 风格的全球/区域海洋场预测。
- 数据已经整理为按年份存储的 HDF5，且每个文件包含 `fields` 四维数组。
- 需要按 `used_variables` 筛选海洋变量通道。
- 需要用 `input_steps` 与 `output_steps` 构造连续时间窗口样本。
- 需要用全局统计量做 NaN 均值填补和可选标准化。
- 需要为预测时间步生成太阳天顶角余弦特征。
- 训练、验证、测试的年份集合已经由上游配置或规划逻辑确定，可通过 `used_years` 显式传入。

不建议直接使用的场景：

- 数据仍是 NetCDF、Zarr、GRIB、逐时刻散文件或其他未转换为当前 HDF5 协议的格式。
- 任务需要复杂质量控制、缺失值插值、异常值剔除、单位换算、时间重采样或空间重网格。
- 下游模型要求单步样本也必须保留时间维，但当前返回协议会对单步时间维执行压缩。
- 数据目录缺少 `stats/` 统计量，且无法在接入前补齐。

### 输入

- 数据目录决策输入：
  - `dataset_dir`
  - 年份 HDF5 文件是否位于 `dataset_dir/data/<year>.h5`
  - 统计量是否位于 `dataset_dir/stats/global_means.npy` 与 `global_stds.npy`
  - 是否存在可选 `metadata.json`
- 数据内容决策输入：
  - `fields` shape
  - `fields.attrs["variables"]` 或 `metadata.json["variables"]`
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
  - 模型期望的变量通道数和顺序
  - 模型是否接受单步样本的 squeezed shape
  - 训练入口是否已经初始化分布式环境
  - 训练或推理阶段是否依赖 `cos_zenith`

### 输出

规划阶段应输出以下结构化决策：

```text
datapipe_choice:
  name: CMEMSDatapipe
  action: reuse | adapt_path | adapt_metadata | build_converter | reject

data_contract:
  dataset_dir: <resolved path>
  year_files: dataset_dir/data/<year>.h5
  stats_source: stats_npy
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
  - missing_year_files
  - missing_variables
  - missing_time_step
  - missing_stats
  - nonuniform_time_axis
  - squeezed_time_dimension
```

### 执行步骤

1. 确认任务是否属于 CMEMS 或 CMEMS 风格的规则经纬度海洋预测数据读取。
2. 检查数据是否已经转换为按年份 HDF5，并确认每个目标年份存在对应文件。
3. 对齐路径结构：
   - 若已有 `dataset_dir/data/<year>.h5`，可直接复用。
   - 若是按年份目录、逐时刻文件或其他命名方式，先规划转换脚本、软链接策略或轻量 adapter。
4. 打开一个样例 HDF5 文件，检查 `fields` 是否为 `[TimeSteps, Channels, Height, Width]`。
5. 检查变量名来源；优先使用 `fields.attrs["variables"]`，缺失时确认 `metadata.json["variables"]` 可用。
6. 比对 `used_variables` 与可用变量名，必要时生成变量映射或要求上游修复元数据。
7. 检查 `fields.attrs["time_step"]` 是否存在，并确认它能代表均匀小时级时间轴。
8. 检查 `stats/global_means.npy` 和 `stats/global_stds.npy` 是否存在，且 shape 能覆盖所选通道。
9. 根据任务阶段配置 `used_years`，不要期望 datapipe 内部自动拆分 train/val/test。
10. 根据下游模型输入协议评估 `input_steps/output_steps` 与 squeezed shape 是否需要外层 adapter。
11. 构造 `CMEMSDatapipe`，调用 `get_dataloader(mode)`，在小样本上验证 batch 五元组的 shape、dtype 和时间索引。
12. 再接入训练、验证、测试或推理主流程。

### 约束

- 不要在未检查变量元数据的情况下猜测通道顺序。
- 不要把 train/val/test 划分逻辑塞进 datapipe；应由外部配置明确传入 `used_years`。
- 不要让模型层处理数据路径不一致问题；路径适配应在数据目录、数据卡或 datapipe adapter 层完成。
- 不要假设 `normalize=False` 可以跳过统计量准备；源码初始化仍依赖统计量文件。
- 若下游要求多步时间维始终存在，需要在外层封装或调整 datapipe 返回协议，避免单步 `squeeze(0)` 引发隐式 shape 漂移。
- 若启用分布式采样，训练入口必须已经完成分布式初始化；datapipe 只负责 sampler 构造。
- `cos_zenith` 的时间假设来自年份 UTC 起点和固定 `time_step`；若数据有非均匀时间轴或非 UTC 定义，必须先修正数据或替换时间特征生成逻辑。

### 下一阶段建议

- 若目标是训练海洋预测模型，下一阶段应生成变量列表、年份划分、模型输入通道映射、loss/metric 配置和训练脚本中的 dataloader 初始化代码。
- 若目标是接入新的 CMEMS 派生数据，下一阶段应先编写数据转换与校验脚本，把原始数据整理成 `fields + variables + time_step + stats` 协议。
- 若目标是模型适配，下一阶段应验证 batch 中 `invar/outvar/cos_zenith` 的 shape 是否与模型 forward 和训练 loop 匹配，再决定是否增加 adapter。
- 若目标是大规模训练，下一阶段应做 I/O 吞吐测试，调节 `num_workers`、batch size、本地缓存策略和分布式 sampler 设置。

### 回退策略

- 年份文件缺失：重新解析 `used_years`，检查数据目录；若数据在其他目录结构中，创建路径适配或先执行转换。
- 变量缺失：从 HDF5 属性或 metadata 生成可用变量清单，修正 `used_variables` 或重建数据元数据。
- 时间步缺失：补写 `fields.attrs["time_step"]`，或在转换阶段显式生成均匀时间轴协议。
- 统计量缺失：重新计算并保存 `stats/global_means.npy` 与 `stats/global_stds.npy`；在补齐前不要直接进入训练。
- shape 不符合下游模型：在 datapipe 外层添加 adapter，统一补回时间维或重排维度。
- 太阳天顶角不可用或不可信：临时禁用依赖 `cos_zenith` 的模型分支，或用真实时间轴重写时间戳生成逻辑。
- HDF5 并发读取不稳定：降低 `num_workers`，切换本地缓存，或在训练前做数据分片与 I/O 压测。

## 源码锚点

- `{onescience_path}/onescience/src/onescience/datapipes/climate/cmems.py`
- `{onescience_path}/onescience/src/onescience/datapipes/climate/utils/invariant.py`
- `{onescience_path}/onescience/src/onescience/datapipes/climate/utils/zenith_angle.py`
