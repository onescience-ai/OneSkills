# ERA5 数据处理配置

## 基本配置

```yaml
# 数据路径配置
data:
  path: "/data/era5"  # ERA5数据根目录
  format: "NetCDF"    # 数据格式：NetCDF, HDF5, Zarr
  
# 变量配置
variables:
  # 地表变量
  surface:
    - "t2m"    # 2米温度
    - "msl"    # 海平面气压
    - "u10"    # 10米u风
    - "v10"    # 10米v风
    - "d2m"    # 2米露点温度
  
  # 850 hPa层变量
  lower_troposphere:
    - "t850"   # 850 hPa温度
    - "u850"   # 850 hPa u风
    - "v850"   # 850 hPa v风
    - "q850"   # 850 hPa比湿
  
  # 500 hPa层变量
  mid_troposphere:
    - "z500"   # 500 hPa位势高度
    - "t500"   # 500 hPa温度
    - "u500"   # 500 hPa u风
    - "v500"   # 500 hPa v风

# 时间配置
time:
  start: "1959-01-01"
  end: "2021-12-31"
  step: "1hour"
  
# 空间配置
spatial:
  lat_range: [-90, 90]
  lon_range: [0, 360]
  lat_resolution: 0.25
  lon_resolution: 0.25

# 统计配置
statistics:
  mean_file: "stats/global_means.npy"
  std_file: "stats/global_stds.npy"
  min_file: "stats/global_mins.npy"
  max_file: "stats/global_maxs.npy"
```

## 数据处理流程配置

```yaml
# 数据处理流程
processing:
  # 数据接入
  ingestion:
    enabled: true
    format: "NetCDF"
    variables: ["t2m", "msl", "u10", "v10", "t850", "u850", "v850", "z500", "q850"]
  
  # 数据清洗
  cleaning:
    enabled: true
    fill_value: 0
    detect_outliers: true
    outlier_method: "3sigma"  # 3-sigma原则
  
  # 数据对齐
  alignment:
    enabled: true
    spatial_alignment: true
    temporal_alignment: true
    target_lat: null  # null表示自动计算
    target_lon: null  # null表示自动计算
  
  # 数据重采样
  resampling:
    enabled: true
    spatial_resampling: false
    temporal_resampling: true
    target_temporal_resolution: "6hour"
  
  # 数据标准化
  normalization:
    enabled: true
    method: "zscore"  # z-score标准化
    fit: true
    statistics_file: "stats/era5_statistics.npz"
```

## 训练数据集配置

```yaml
# 训练数据集配置
dataset:
  # 数据集基本信息
  name: "era5"
  domain: "earth"
  task: "forecasting"
  
  # 数据源
  source:
    type: "NetCDF"
    path: "/data/era5"
    split: "train"  # train, val, test
    
  # 数据配置
  data:
    variables: ["t2m", "msl", "u10", "v10", "t850", "u850", "v850", "z500", "q850"]
    features: ["lat", "lon"]
    num_samples: -1  # -1表示全部
    sample_rate: 1.0  # 采样率
    
  # 时间序列配置
  time_series:
    input_steps: 2    # 输入时间步数
    target_steps: 1   # 目标时间步数
    time_step: "6hour" # 时间步长
    
  # 数据增强
  augmentation:
    enabled: true
    random_rotation: true
    random_flip: true
    
  # 性能配置
  performance:
    cache: false
    cache_dir: null
    preload: false
    lazy_load: true
    num_workers: 4
    pin_memory: true
```

## 数据加载配置

```yaml
# 数据加载配置
dataloader:
  batch_size: 4
  shuffle: true
  num_workers: 4
  pin_memory: true
  drop_last: true
  prefetch_factor: 2
  persistent_workers: false
```

## 完整配置示例

```yaml
# 完整的ERA5数据处理配置
config:
  # 数据路径
  data_path: "/data/era5"
  data_format: "NetCDF"
  
  # 变量列表
  variables:
    - "t2m"
    - "msl"
    - "u10"
    - "v10"
    - "t850"
    - "u850"
    - "v850"
    - "z500"
    - "q850"
    
  # 时间配置
  time:
    start: "1959-01-01"
    end: "2021-12-31"
    step: "1hour"
    
  # 空间配置
  spatial:
    lat_range: [-90, 90]
    lon_range: [0, 360]
    lat_resolution: 0.25
    lon_resolution: 0.25
    
  # 数据处理
  processing:
    cleaning:
      fill_value: 0
      detect_outliers: true
      
    alignment:
      spatial_alignment: true
      temporal_alignment: true
      
    resampling:
      temporal_resampling: true
      target_resolution: "6hour"
      
    normalization:
      enabled: true
      method: "zscore"
      
  # 数据集配置
  dataset:
    name: "era5"
    domain: "earth"
    task: "forecasting"
    input_steps: 2
    target_steps: 1
    augmentation: true
    
  # DataLoader配置
  dataloader:
    batch_size: 4
    num_workers: 4
    pin_memory: true
```

## Python代码示例

### 1. 数据加载

```python
import xarray as xr
import numpy as np
from pathlib import Path

# 加载ERA5数据
data_path = Path("/data/era5")
dataset = xr.open_dataset(data_path / "era5.nc")

# 查看变量
print("Variables:", list(dataset.data_vars.keys()))

# 查看维度
print("Dimensions:", dataset.dims)

# 查看坐标
print("Coordinates:", list(dataset.coords.keys()))
```

### 2. 数据处理

```python
from onescience.datapipes.climate.era5 import ERA5Datapipe

# 创建ERA5数据管道
params = {
    "dataset": {
        "data_dir": "/data/era5",
        "stats_dir": "/data/era5/stats",
        "channels": ["t2m", "msl", "u10", "v10"],
        "time_res": 1,  # 小时
        "train_ratio": 0.8,
        "val_ratio": 0.1,
        "test_ratio": 0.1,
        "img_size": [721, 1440],
        "batch_size": 4,
        "num_workers": 4,
    },
    "dataloader": {
        "batch_size": 4,
        "num_workers": 4,
    }
}

datapipe = ERA5Datapipe(params, distributed=False)

# 获取数据加载器
train_loader, sampler = datapipe.train_dataloader()
val_loader, _ = datapipe.val_dataloader()
test_loader = datapipe.test_dataloader()
```

### 3. 数据可视化

```python
import matplotlib.pyplot as plt

# 选择变量
var = dataset["t2m"]

# 绘制时间序列
var.isel(lat=360, lon=720).plot()
plt.title("2m Temperature Time Series")
plt.show()

# 绘制空间分布
var.isel(time=0).plot()
plt.title("2m Temperature Spatial Distribution")
plt.show()
```

### 4. 数据统计

```python
# 计算统计信息
stats = {}
for var_name in dataset.data_vars.keys():
    var = dataset[var_name]
    stats[var_name] = {
        "mean": float(var.mean().values),
        "std": float(var.std().values),
        "min": float(var.min().values),
        "max": float(var.max().values),
    }

# 保存统计信息
np.savez("stats/era5_statistics.npz", **stats)
```

## 常用数据处理操作

### 1. 选择变量

```python
# 选择特定变量
selected_vars = dataset[["t2m", "msl", "u10", "v10"]]

# 选择变量范围
t2m = dataset["t2m"]
t2m_subset = t2m.sel(time=slice("2020-01-01", "2020-12-31"))
```

### 2. 数据重采样

```python
# 时间重采样（6小时均值）
dataset_6h = dataset.resample(time="6h").mean()

# 空间重采样（降采样）
dataset_coarse = dataset.coarsen(lat=4, lon=4).mean()
```

### 3. 数据标准化

```python
# Z-score标准化
mean = dataset.mean()
std = dataset.std()
dataset_norm = (dataset - mean) / std

# Min-Max标准化
min_val = dataset.min()
max_val = dataset.max()
dataset_norm = (dataset - min_val) / (max_val - min_val)
```

### 4. 数据切片

```python
# 时间切片
dataset_time = dataset.isel(time=slice(0, 1000))

# 空间切片
dataset_region = dataset.sel(lat=slice(30, 60), lon=slice(100, 140))

# 变量切片
dataset_vars = dataset.isel(channel=[0, 1, 2])
```

## 数据集划分

```python
# 按年份划分
years = sorted(dataset.time.dt.year.unique().values)
n_years = len(years)

train_years = years[:int(0.8*n_years)]
val_years = years[int(0.8*n_years):int(0.9*n_years)]
test_years = years[int(0.9*n_years):]

# 按时间比例划分
total_steps = len(dataset.time)
train_end = int(0.8 * total_steps)
val_end = int(0.9 * total_steps)

train_dataset = dataset.isel(time=slice(0, train_end))
val_dataset = dataset.isel(time=slice(train_end, val_end))
test_dataset = dataset.isel(time=slice(val_end, None))
```

## 错误处理

### 常见错误1：数据文件不存在

```python
data_path = Path("/data/era5")
if not data_path.exists():
    raise FileNotFoundError(f"Data path not found: {data_path}")
```

### 常见错误2：变量不存在

```python
required_vars = ["t2m", "msl", "u10", "v10"]
available_vars = list(dataset.data_vars.keys())

missing_vars = [var for var in required_vars if var not in available_vars]
if missing_vars:
    raise ValueError(f"Missing variables: {missing_vars}")
```

### 常见错误3：数据格式错误

```python
if not isinstance(dataset, xr.Dataset):
    raise TypeError("Dataset must be xarray.Dataset")
```

## 性能优化

### 1. 数据缓存

```python
# 启用数据缓存
dataset = dataset.chunk({"time": 100, "lat": 721, "lon": 1440})
```

### 2. 并行加载

```python
# 使用多线程加载
import dask
dask.config.set(scheduler='threads')

dataset = xr.open_dataset(data_path, chunks="auto")
```

### 3. 内存优化

```python
# 使用内存映射
dataset = xr.open_dataset(data_path, engine="h5netcdf", mask_and_scale=False)
```

## 参考资料

- [ERA5官方文档](https://confluence.ecmwf.int/display/CKB/ERA5)
- [xarray官方文档](https://xarray.pydata.org/)
- [NetCDF官方文档](https://www.unidata.ucar.edu/software/netcdf/)
