# ERA5 数据集元数据

## 概述

ERA5 (European Centre for Medium-Range Weather Forecasts Reanalysis, 5th generation) 是欧洲中期天气预报中心（ECMWF）发布的第五代全球大气再分析数据集。

### 基本信息

| 项目 | 说明 |
|------|------|
| **数据集名称** | ERA5 |
| **数据提供方** | European Centre for Medium-Range Weather Forecasts (ECMWF) |
| **版本** | 5th generation (ERA5) |
| **时间范围** | 1959年至今（实时更新） |
| **时间分辨率** | 1小时（原始数据），可选3小时、6小时等 |
| **空间分辨率** | 0.25° × 0.25°（约31km × 31km） |
| **空间范围** | 全球（纬度：90°S - 90°N，经度：0° - 360°） |
| **数据格式** | NetCDF、GRIB2 |
| **数据大小** | 约200TB（完整数据集） |

## 气象变量列表

### 地表变量

| 变量名 | 全称 | 单位 | 描述 | 维度 |
|--------|------|------|------|------|
| `t2m` | 2米温度 | K | 距地面2米处的空气温度 | [time, lat, lon] |
| `msl` | 海平面气压 | Pa | 海平面气压 | [time, lat, lon] |
| `u10` | 10米u风分量 | m/s | 距地面10米处的东向风速 | [time, lat, lon] |
| `v10` | 10米v风分量 | m/s | 距地面10米处的北向风速 | [time, lat, lon] |
| `d2m` | 2米露点温度 | K | 距地面2米处的露点温度 | [time, lat, lon] |
| `sst` | 海面温度 | K | 海面温度 | [time, lat, lon] |
| `skt` | 皮肤温度 | K | 地表皮肤温度 | [time, lat, lon] |
| `lai_hv` | 高植被覆盖率 | - | 高植被覆盖率 | [time, lat, lon] |
| `lai_lv` | 低植被覆盖率 | - | 低植被覆盖率 | [time, lat, lon] |
| `src` | 土壤湿度（表层） | m of water | 表层土壤湿度 | [time, lat, lon] |
| `swv` | 短波辐射（地表） | W/m² | 短波辐射通量 | [time, lat, lon] |
| `lwh` | 长波辐射（地表） | W/m² | 长波辐射通量 | [time, lat, lon] |

### 大气变量（多个气压层）

#### 850 hPa 层（约1.5 km高度）

| 变量名 | 全称 | 单位 | 描述 | 维度 |
|--------|------|------|------|------|
| `t850` | 850 hPa温度 | K | 850 hPa层温度 | [time, lat, lon] |
| `u850` | 850 hPa u风 | m/s | 850 hPa层东向风速 | [time, lat, lon] |
| `v850` | 850 hPa v风 | m/s | 850 hPa层北向风速 | [time, lat, lon] |
| `q850` | 850 hPa比湿 | kg/kg | 850 hPa层比湿 | [time, lat, lon] |
| `w850` | 850 hPa垂直速度 | Pa/s | 850 hPa层垂直速度 | [time, lat, lon] |

#### 700 hPa 层（约3 km高度）

| 变量名 | 全称 | 单位 | 描述 | 维度 |
|--------|------|------|------|------|
| `t700` | 700 hPa温度 | K | 700 hPa层温度 | [time, lat, lon] |
| `u700` | 700 hPa u风 | m/s | 700 hPa层东向风速 | [time, lat, lon] |
| `v700` | 700 hPa v风 | m/s | 700 hPa层北向风速 | [time, lat, lon] |
| `q700` | 700 hPa比湿 | kg/kg | 700 hPa层比湿 | [time, lat, lon] |
| `w700` | 700 hPa垂直速度 | Pa/s | 700 hPa层垂直速度 | [time, lat, lon] |

#### 500 hPa 层（约5.5 km高度）

| 变量名 | 全称 | 单位 | 描述 | 维度 |
|--------|------|------|------|------|
| `z500` | 500 hPa位势高度 | m²/s² | 500 hPa层位势高度 | [time, lat, lon] |
| `t500` | 500 hPa温度 | K | 500 hPa层温度 | [time, lat, lon] |
| `u500` | 500 hPa u风 | m/s | 500 hPa层东向风速 | [time, lat, lon] |
| `v500` | 500 hPa v风 | m/s | 500 hPa层北向风速 | [time, lat, lon] |
| `q500` | 500 hPa比湿 | kg/kg | 500 hPa层比湿 | [time, lat, lon] |
| `w500` | 500 hPa垂直速度 | Pa/s | 500 hPa层垂直速度 | [time, lat, lon] |

#### 250 hPa 层（约10 km高度）

| 变量名 | 全称 | 单位 | 描述 | 维度 |
|--------|------|------|------|------|
| `t250` | 250 hPa温度 | K | 250 hPa层温度 | [time, lat, lon] |
| `u250` | 250 hPa u风 | m/s | 250 hPa层东向风速 | [time, lat, lon] |
| `v250` | 250 hPa v风 | m/s | 250 hPa层北向风速 | [time, lat, lon] |
| `q250` | 250 hPa比湿 | kg/kg | 250 hPa层比湿 | [time, lat, lon] |

#### 1000 hPa 层（地面附近）

| 变量名 | 全称 | 单位 | 描述 | 维度 |
|--------|------|------|------|------|
| `t1000` | 1000 hPa温度 | K | 1000 hPa层温度 | [time, lat, lon] |
| `u1000` | 1000 hPa u风 | m/s | 1000 hPa层东向风速 | [time, lat, lon] |
| `v1000` | 1000 hPa v风 | m/s | 1000 hPa层北向风速 | [time, lat, lon] |
| `q1000` | 1000 hPa比湿 | kg/kg | 1000 hPa层比湿 | [time, lat, lon] |

### 总变量列表（常用）

以下变量常用于气象预测模型：

```python
# 地表变量
surface_vars = [
    "t2m",      # 2米温度
    "msl",      # 海平面气压
    "u10",      # 10米u风
    "v10",      # 10米v风
    "d2m",      # 2米露点温度
    "sst",      # 海面温度
    "skt",      # 皮肤温度
]

# 850 hPa层变量
lower_troposphere_vars = [
    "t850",     # 850 hPa温度
    "u850",     # 850 hPa u风
    "v850",     # 850 hPa v风
    "q850",     # 850 hPa比湿
]

# 500 hPa层变量
mid_troposphere_vars = [
    "z500",     # 500 hPa位势高度
    "t500",     # 500 hPa温度
    "u500",     # 500 hPa u风
    "v500",     # 500 hPa v风
]

# 完整变量列表（GraphCast常用）
graphcast_vars = [
    "t2m",      # 2米温度
    "msl",      # 海平面气压
    "u10",      # 10米u风
    "v10",      # 10米v风
    "t850",     # 850 hPa温度
    "u850",     # 850 hPa u风
    "v850",     # 850 hPa v风
    "z500",     # 500 hPa位势高度
    "q850",     # 850 hPa比湿
    "t500",     # 500 hPa温度
]
```

## 数据维度信息

### 空间维度

| 维度 | 大小 | 范围 | 说明 |
|------|------|------|------|
| `lat` | 721 | -90° to 90° | 纬度，步长0.25° |
| `lon` | 1440 | 0° to 360° | 经度，步长0.25° |
| `height` | 1 | - | 地表（部分变量） |
| `level` | 137 | - | 气压层（部分变量） |

### 时间维度

| 参数 | 值 | 说明 |
|------|-----|------|
| **时间分辨率** | 1小时 | 原始数据 |
| **时间范围** | 1959-01-01至今 | 持续更新 |
| **总时间点** | >500,000 | 超过60年数据 |

### 数据格式

#### NetCDF格式

```python
import xarray as xr

# 加载数据
dataset = xr.open_dataset("era5.nc")

# 查看变量
print(dataset.data_vars.keys())

# 查看维度
print(dataset.dims)

# 查看坐标
print(dataset.coords.keys())
```

#### GRIB2格式

```python
import cfgrib

# 加载GRIB2数据
dataset = cfgrib.open_dataset("era5.grib2")

# 查看变量
print(dataset.data_vars.keys())
```

## 数据统计信息

### 统计参数

ERA5数据通常提供以下统计参数用于归一化：

| 统计参数 | 文件名 | 形状 | 说明 |
|---------|--------|------|------|
| **均值** | `global_means.npy` | [1, C, 1, 1] | 全球平均值 |
| **标准差** | `global_stds.npy` | [1, C, 1, 1] | 全球标准差 |
| **最小值** | `global_mins.npy` | [1, C, 1, 1] | 全球最小值 |
| **最大值** | `global_maxs.npy` | [1, C, 1, 1] | 全球最大值 |

### 典型统计值（示例）

```python
# 地表变量典型统计值
surface_stats = {
    "t2m": {"mean": 288.0, "std": 15.0, "min": 220.0, "max": 330.0},
    "msl": {"mean": 101325.0, "std": 1000.0, "min": 87000.0, "max": 105000.0},
    "u10": {"mean": 3.0, "std": 5.0, "min": -50.0, "max": 50.0},
    "v10": {"mean": 1.0, "std": 4.0, "min": -40.0, "max": 40.0},
}

# 850 hPa变量典型统计值
lower_troposphere_stats = {
    "t850": {"mean": 275.0, "std": 12.0, "min": 220.0, "max": 310.0},
    "u850": {"mean": 5.0, "std": 8.0, "min": -60.0, "max": 60.0},
    "v850": {"mean": 2.0, "std": 6.0, "min": -50.0, "max": 50.0},
    "q850": {"mean": 0.01, "std": 0.005, "min": 0.0, "max": 0.03},
}

# 500 hPa变量典型统计值
mid_troposphere_stats = {
    "z500": {"mean": 55000.0, "std": 5000.0, "min": 45000.0, "max": 65000.0},
    "t500": {"mean": 255.0, "std": 10.0, "min": 200.0, "max": 300.0},
    "u500": {"mean": 10.0, "std": 12.0, "min": -80.0, "max": 80.0},
    "v500": {"mean": 2.0, "std": 8.0, "min": -60.0, "max": 60.0},
}
```

## 数据访问

### 通过 ECMWF Data Store 访问

```python
# 安装ecmwf-api-client
pip install ecmwf-api-client

# Python代码
from ecmwfapi import ECMWFDataServer

server = ECMWFDataServer()
server.retrieve({
    "stream": "oper",
    "levtype": "sfc",
    "param": "130.128/131.128/132.128/133.128",
    "levelist": "1000",
    "date": "19590101/to/20211231",
    "time": "00/06/12/18",
    "type": "an",
    "grid": "0.25/0.25",
    "target": "era5.nc"
})
```

### 通过 Copernicus Climate Data Store 访问

```python
# 安装cdsapi
pip install cdsapi

# Python代码
import cdsapi

c = cdsapi.Client()
c.retrieve(
    'reanalysis-era5-single-levels',
    {
        'product_type': 'reanalysis',
        'variable': ['2m_temperature', 'mean_sea_level_pressure', '10m_u_component_of_wind', '10m_v_component_of_wind'],
        'year': ['1959', '1960', '1961'],
        'month': ['01', '02', '03'],
        'day': ['01', '02', '03'],
        'time': ['00:00', '06:00', '12:00', '18:00'],
        'format': 'netcdf'
    },
    'era5_download.nc'
)
```

## 数据使用注意事项

### 1. 数据版权

- ERA5数据遵循CC BY 4.0许可协议
- 使用时需注明数据来源：ECMWF

### 2. 数据质量

- ERA5数据经过严格的质量控制
- 包含观测数据和模型分析的结合
- 适用于气象研究和业务预报

### 3. 数据更新

- ERA5数据持续更新
- 实时数据（近实时）：延迟约5天
- 最终数据（Final）：延迟约2个月

### 4. 数据版本

- **ERA5**: 第五代再分析数据（当前版本）
- **ERA5-LT**: 长时间再分析数据
- **ERA5-20C**: 20世纪再分析数据
- **ERA5-HE**: 高分辨率再分析数据

## 数据集文件结构

### 典型文件结构

```
era5_dataset/
├── data/                      # 原始数据
│   ├── 1959/                  # 按年份组织
│   │   ├── *.h5
│   │   └── metadata.json
│   ├── 1960/
│   └── ...
├── data_merged/              # 合并后的数据
│   ├── 1959.h5
│   ├── 1960.h5
│   └── ...
├── stats/                    # 统计信息
│   ├── global_means.npy
│   ├── global_stds.npy
│   ├── global_mins.npy
│   └── global_maxs.npy
├── metadata.json             # 元数据文件
└── README.md                 # 说明文档
```

### 元数据文件格式

```json
{
  "dataset": "ERA5",
  "version": "5th generation",
  "variables": [
    "t2m",
    "msl",
    "u10",
    "v10",
    "t850",
    "u850",
    "v850",
    "z500",
    "q850"
  ],
  "years": [1959, 1960, 1961, ..., 2021],
  "time_resolution": "1hour",
  "spatial_resolution": "0.25x0.25",
  "spatial_coverage": {
    "lat_range": [-90, 90],
    "lon_range": [0, 360]
  },
  "dimensions": {
    "lat": 721,
    "lon": 1440
  },
  "statistics": {
    "global_means": "stats/global_means.npy",
    "global_stds": "stats/global_stds.npy"
  }
}
```

## 参考文献

1. **ERA5论文**: Hersbach, H., et al. (2020). The ERA5 global reanalysis. Quarterly Journal of the Royal Meteorological Society, 146(730), 1999-2049.

2. **ECMWF Documentation**: https://confluence.ecmwf.int/display/CKB/ERA5

3. **Copernicus Climate Change Service**: https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels

## 相关链接

- [ECMWF ERA5官网](https://www.ecmwf.int/en/forecasts/datasets/era5)
- [Copernicus CDS](https://cds.climate.copernicus.eu/)
- [ERA5文档](https://confluence.ecmwf.int/display/CKB/ERA5)
- [ERA5数据下载](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels)

## 更新历史

- **2023-01-15**: 初始版本
- **2023-06-20**: 添加更多变量和统计信息
- **2024-01-10**: 更新数据访问方法
