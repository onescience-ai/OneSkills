# launch

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

# input_schema

- 目录准备：
  - 源码期望：`dataset_dir/data/<year>.h5`
  - 源码回退统计量：`dataset_dir/stats/global_means.npy` 与 `dataset_dir/stats/global_stds.npy`
  - 数据卡主路径：`{ONESCIENCE_DATASETS_DIR}/ERA5/newh5/data_merged/<year>.h5`
- HDF5 文件要求：
  - `fields`: 四维数组 `[TimeSteps, Channels, Height, Width]`
  - `fields.attrs["variables"]`: 与通道顺序一致的变量名列表
  - `fields.attrs["time_step"]`: 小时级时间步长
  - 可选 `global_means` 与 `global_stds`: 形状应可按 `[1, Channels, 1, 1]` 语义广播
- 配置要求：
  - `used_years` 负责数据阶段划分，datapipe 不内置 train/val/test 年份策略。
  - `used_variables` 负责通道筛选，名称必须与 HDF5 属性完全一致。
  - `input_steps` 与 `output_steps` 决定每个样本的连续时间窗口长度。

# runtime_interfaces

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

# main_functions

- `get_dataloader`

# execution_resources

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

# operation_limits

- 仅支持按年份 HDF5 文件组织的规则经纬度 ERA5 数据，不直接支持 NetCDF、Zarr、GRIB 或非结构网格。
- 路径结构必须与源码期望一致；若只有数据卡中的 `data_merged/` 目录，需要在调用前调整 `dataset_dir`、目录名或建立适配层。
- `used_years` 与 `used_variables` 校验严格，年份文件缺失或变量名不匹配会直接失败。
- 当前 datapipe 不做缺失值填补、异常值清洗、时间轴重采样或变量单位转换。
- `normalize=False` 不代表可以省略统计量文件，因为初始化流程仍会尝试读取统计量。
- 当 `input_steps=1` 或 `output_steps=1` 时，返回张量会被 `squeeze(0)` 去掉时间维；下游模型或 collate 后处理需要显式处理这一点。
- 测试模式固定 `batch_size=1`，不适合直接用于大 batch 离线推理吞吐测试，除非外层另行封装。
