# launch

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

# input_schema

- 目录准备：
  - `dataset_dir/data/<year>.h5`
  - `dataset_dir/stats/global_means.npy`
  - `dataset_dir/stats/global_stds.npy`
  - `dataset_dir/metadata.json` 可选；当 HDF5 `fields` 缺少变量属性时用于提供 `variables`。
- HDF5 文件要求：
  - `fields`: 四维数组 `[TimeSteps, Channels, Height, Width]`。
  - `fields.attrs["variables"]`: 与通道顺序一致的变量名列表，推荐直接写入 HDF5。
  - `fields.attrs["time_step"]`: 小时级时间步长。
- 配置要求：
  - `used_years` 负责数据阶段划分，源码不内置 train/val/test 年份切分策略。
  - `used_variables` 负责通道筛选，名称必须与 HDF5 属性或 metadata 中的变量名完全一致。
  - `input_steps` 与 `output_steps` 决定每个样本的连续时间窗口长度。

# runtime_interfaces

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

# main_functions

- `get_dataloader`

# execution_resources

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

# operation_limits

- 仅直接支持按年份 HDF5 文件组织的规则经纬度 CMEMS 海洋数据；不直接读取 NetCDF、Zarr、GRIB 或非结构网格。
- 路径结构必须与源码期望一致；若原始数据仍是按时间戳文件或按年份目录组织，需要先转换或建立适配层。
- `used_years` 与 `used_variables` 校验严格，年份文件缺失或变量名不匹配会直接失败。
- 当前 datapipe 不执行复杂质量控制、异常值清洗、单位换算、时间轴重采样或空间重网格。
- `normalize=False` 不代表可以省略统计量文件；初始化流程仍会读取统计量，NaN 填补也依赖全局均值。
- 单步输入或输出会因 `squeeze(0)` 移除时间维，下游模型若要求固定时间维，需要外层 adapter 补回。
- 测试模式固定 `batch_size=1`，如需大 batch 离线推理吞吐测试，应在外层封装或调整调用方式。
