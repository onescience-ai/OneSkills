# launch

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

# input_schema

- 数据根目录：
  - `data_dir/metadata.json`
  - `data_dir/data/<year>/*.nc`
  - `stats_dir/global_means.npy`
  - `stats_dir/global_stds.npy`
- `metadata.json`：
  - `years`: 全部可用年份。
  - `variables`: 全量变量名，顺序需要与统计量通道顺序一致。
- NetCDF 文件：
  - 必须包含 `fields`。
  - 推荐使用 `channel`、`latitude`、`longitude` 维度名；源码也兼容 `variable/variables`、`lat`、`lon`。
  - 如果通道维有坐标，坐标值应为变量名。
- 配置字段：
  - `params.dataset.channels`: 任务所需变量列表。
  - `params.dataset.train_years/val_years/test_years`: 显式年份列表。
  - `params.dataset.time_res`: 小时级时间间隔。
  - `params.dataset.img_size`: 经纬度网格生成尺寸。
  - `params.dataloader.batch_size`: 训练/验证批大小。
  - `params.dataloader.num_workers`: 数据加载 worker 数。
  - `params.dataloader.pin_memory`: 可选，默认 `True`。

# runtime_interfaces

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

# main_functions

- `train_dataloader`
- `val_dataloader`
- `test_dataloader`

# execution_resources

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

# operation_limits

- 仅直接支持已经转换为 `data/<year>/*.nc` 的 TJWeather 风格逐时间步 NetCDF 数据。
- 不直接支持单个 NetCDF 内含完整长时间轴且未拆分为逐文件时间步的布局，除非先做转换或 adapter。
- `train_years`、`val_years`、`test_years` 必须显式给出，不能依赖比例自动划分。
- 文件名排序被视为时间顺序；命名不规范会导致窗口顺序错误。
- 当前实现不做缺失值填补、异常值清洗、单位换算、空间插值或时间重采样。
- `normalize=False` 不会跳过统计量读取；统计量缺失仍会在初始化阶段失败。
- 测试接口不返回 sampler；若测试阶段也需要分布式切分，需要外层自行封装。
- 单步输入或输出会因 `squeeze(0)` 移除时间维，下游模型若要求固定时间维需要补维。
