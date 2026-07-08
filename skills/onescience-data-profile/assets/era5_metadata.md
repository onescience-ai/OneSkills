# ERA5 数据集元信息说明

## 存储路径

ERA5 数据集位于环境变量 `$ONESCIENCE_DATASETS_DIR` 指定的路径下。

## 目录结构

```text
$ONESCIENCE_DATASETS_DIR/ERA5
├── data
│   ├── 1979.h5
│   ├── 1980.h5
│   ├── ...
│   └── 2025.h5
├── static
│   ├── geopotential.nc
│   ├── land_mask.npy
│   ├── land_sea_mask.nc
│   ├── soil_type.npy
│   └── topography.npy
└── stats
    ├── global_means.npy
    ├── global_stds.npy
    ├── global_diffs_stddev_by_level.npy
    ├── global_min_by_level.npy
    └── <variable>_<stat>.npy
```

## 数据总体信息

- 时间覆盖：1979 - 2025
- 文件组织：每年一个 HDF5 文件，命名格式为 `YYYY.h5`
- 时间分辨率：6 小时
- 每年时间步数：1460，即 365 天 x 4 个时次
- 每日时次：00、06、12、18 UTC
- 空间网格：721 x 1440
- 空间分辨率：全球 0.25° 网格
- 数据类型：`float32`
- 主数据维度：`fields: [T, C, H, W] = (1460, 243, 721, 1440)`

维度含义：

- `T`: 年内时间步索引，范围为 0 - 1459
- `C`: 变量通道数，当前为 243
- `H`: 纬度网格数，当前为 721
- `W`: 经度网格数，当前为 1440

## data/ 时序数据

### 文件命名

当前版本按年聚合存储：

```text
data/1979.h5
data/1980.h5
...
data/2025.h5
```

每个文件包含该年份的 1460 个 6 小时时间步。闰年仍按 365 天、1460 个时间步处理。

### 文件内部结构

每个 `YYYY.h5` 文件包含以下数据集：

```text
fields       : [T, C, H, W] = (1460, 243, 721, 1440), dtype=float32
global_means : [1, C, 1, 1] = (1, 243, 1, 1), dtype=float32
global_stds  : [1, C, 1, 1] = (1, 243, 1, 1), dtype=float32
```

`fields` 数据集属性：

```text
variables : 长度为 243 的变量名列表，顺序与 fields 的 C 维严格对应
time_step : 6
```

读取变量时必须先从 `fields.attrs["variables"]` 中查找变量名对应的通道索引，再从 `fields[:, index, :, :]` 或 `fields[t, index, :, :]` 中提取数据。

示例：

```python
import h5py

with h5py.File("data/1979.h5", "r") as f:
    fields = f["fields"]
    variables = [
        v.decode() if isinstance(v, bytes) else str(v)
        for v in fields.attrs["variables"]
    ]
    idx = variables.index("2m_temperature")
    first_time_step = fields[0, idx, :, :]
```

## 变量命名规则

- 带压力层后缀的变量表示该压力层上的气象变量，压力层单位为 hPa，例如 `temperature_850`、`geopotential_500`。
- 不带数字后缀的变量表示地表变量或诊断变量，例如 `2m_temperature`、`surface_pressure`、`total_precipitation`。
- 当前 243 个通道由原有 99 个变量和新增压力层变量组成。
- 通道顺序以 `fields.attrs["variables"]` 为准；以下列表记录当前文件中的变量顺序。

## 完整变量列表

```text
10m_u_component_of_wind, 10m_v_component_of_wind, 2m_temperature,
geopotential_100, geopotential_1000, geopotential_150,
geopotential_200, geopotential_250, geopotential_300,
geopotential_400, geopotential_50, geopotential_500,
geopotential_600, geopotential_700, geopotential_850,
geopotential_925, mean_sea_level_pressure, relative_humidity_500,
relative_humidity_850, specific_humidity_100, specific_humidity_1000,
specific_humidity_150, specific_humidity_200, specific_humidity_250,
specific_humidity_300, specific_humidity_400, specific_humidity_50,
specific_humidity_500, specific_humidity_600, specific_humidity_700,
specific_humidity_850, specific_humidity_925, surface_pressure,
temperature_100, temperature_1000, temperature_150, temperature_200,
temperature_250, temperature_300, temperature_400, temperature_50,
temperature_500, temperature_600, temperature_700, temperature_850,
temperature_925, total_column_water_vapour, total_precipitation,
u_component_of_wind_100, u_component_of_wind_1000,
u_component_of_wind_150, u_component_of_wind_200,
u_component_of_wind_250, u_component_of_wind_300,
u_component_of_wind_400, u_component_of_wind_50,
u_component_of_wind_500, u_component_of_wind_600,
u_component_of_wind_700, u_component_of_wind_850,
u_component_of_wind_925, v_component_of_wind_100,
v_component_of_wind_1000, v_component_of_wind_150,
v_component_of_wind_200, v_component_of_wind_250,
v_component_of_wind_300, v_component_of_wind_400,
v_component_of_wind_50, v_component_of_wind_500,
v_component_of_wind_600, v_component_of_wind_700,
v_component_of_wind_850, v_component_of_wind_925,
relative_humidity_50, relative_humidity_200, relative_humidity_100,
relative_humidity_150, relative_humidity_250, relative_humidity_300,
relative_humidity_400, relative_humidity_600, relative_humidity_700,
relative_humidity_925, relative_humidity_1000, sea_surface_temperature,
vertical_velocity_50, vertical_velocity_100, vertical_velocity_150,
vertical_velocity_200, vertical_velocity_250, vertical_velocity_300,
vertical_velocity_400, vertical_velocity_500, vertical_velocity_600,
vertical_velocity_700, vertical_velocity_850, vertical_velocity_925,
vertical_velocity_1000,
geopotential_1, geopotential_2, geopotential_3, geopotential_5,
geopotential_7, geopotential_10, geopotential_20, geopotential_30,
geopotential_70, geopotential_125, geopotential_175, geopotential_225,
geopotential_350, geopotential_450, geopotential_550, geopotential_650,
geopotential_750, geopotential_775, geopotential_800, geopotential_825,
geopotential_875, geopotential_900, geopotential_950, geopotential_975,
relative_humidity_1, relative_humidity_2, relative_humidity_3,
relative_humidity_5, relative_humidity_7, relative_humidity_10,
relative_humidity_20, relative_humidity_30, relative_humidity_70,
relative_humidity_125, relative_humidity_175, relative_humidity_225,
relative_humidity_350, relative_humidity_450, relative_humidity_550,
relative_humidity_650, relative_humidity_750, relative_humidity_775,
relative_humidity_800, relative_humidity_825, relative_humidity_875,
relative_humidity_900, relative_humidity_950, relative_humidity_975,
specific_humidity_1, specific_humidity_2, specific_humidity_3,
specific_humidity_5, specific_humidity_7, specific_humidity_10,
specific_humidity_20, specific_humidity_30, specific_humidity_70,
specific_humidity_125, specific_humidity_175, specific_humidity_225,
specific_humidity_350, specific_humidity_450, specific_humidity_550,
specific_humidity_650, specific_humidity_750, specific_humidity_775,
specific_humidity_800, specific_humidity_825, specific_humidity_875,
specific_humidity_900, specific_humidity_950, specific_humidity_975,
temperature_1, temperature_2, temperature_3, temperature_5,
temperature_7, temperature_10, temperature_20, temperature_30,
temperature_70, temperature_125, temperature_175, temperature_225,
temperature_350, temperature_450, temperature_550, temperature_650,
temperature_750, temperature_775, temperature_800, temperature_825,
temperature_875, temperature_900, temperature_950, temperature_975,
u_component_of_wind_1, u_component_of_wind_2, u_component_of_wind_3,
u_component_of_wind_5, u_component_of_wind_7, u_component_of_wind_10,
u_component_of_wind_20, u_component_of_wind_30, u_component_of_wind_70,
u_component_of_wind_125, u_component_of_wind_175,
u_component_of_wind_225, u_component_of_wind_350,
u_component_of_wind_450, u_component_of_wind_550,
u_component_of_wind_650, u_component_of_wind_750,
u_component_of_wind_775, u_component_of_wind_800,
u_component_of_wind_825, u_component_of_wind_875,
u_component_of_wind_900, u_component_of_wind_950,
u_component_of_wind_975, v_component_of_wind_1,
v_component_of_wind_2, v_component_of_wind_3, v_component_of_wind_5,
v_component_of_wind_7, v_component_of_wind_10, v_component_of_wind_20,
v_component_of_wind_30, v_component_of_wind_70, v_component_of_wind_125,
v_component_of_wind_175, v_component_of_wind_225,
v_component_of_wind_350, v_component_of_wind_450,
v_component_of_wind_550, v_component_of_wind_650,
v_component_of_wind_750, v_component_of_wind_775,
v_component_of_wind_800, v_component_of_wind_825,
v_component_of_wind_875, v_component_of_wind_900,
v_component_of_wind_950, v_component_of_wind_975
```

## static/ 静态场

静态场文件包括：

- `geopotential.nc`: NetCDF 格式
- `land_mask.npy`: NumPy 格式，维度为 `(721, 1440)`
- `land_sea_mask.nc`: NetCDF 格式
- `soil_type.npy`: NumPy 格式，维度为 `(721, 1440)`
- `topography.npy`: NumPy 格式，维度为 `(721, 1440)`

这些静态场不随时间变化，空间网格与 `fields` 的 `H, W` 维一致。

## stats/ 统计信息

每个年度 HDF5 文件内部包含与 243 个通道对应的统计数据：

- `global_means`: 维度为 `[1, 243, 1, 1]`
- `global_stds`: 维度为 `[1, 243, 1, 1]`

外部 `stats/` 目录中还保留了全局统计和逐变量统计文件，例如：

- `global_means.npy`
- `global_stds.npy`
- `global_diffs_stddev_by_level.npy`
- `global_min_by_level.npy`
- `<variable>_means.npy`
- `<variable>_stds.npy`
- `<variable>_diffs_stddev_by_level.npy`
- `<variable>_min_by_level.npy`

> 注意：当前外部 `stats/global_*.npy` 文件维度为 `[1, 99, 1, 1]`，对应原有 99 个变量通道；对 243 通道数据做标准化时，应优先使用年度 HDF5 文件内部的 `global_means` 和 `global_stds`，或确认外部统计文件已重新生成到 243 通道版本。

## 取数注意事项

- 变量通道顺序必须从 `fields.attrs["variables"]` 读取。
- 时间索引按 6 小时递增：`t=0` 对应该年 1 月 1 日 00:00 UTC，`t=1` 对应 06:00 UTC，`t=2` 对应 12:00 UTC，`t=3` 对应 18:00 UTC。
- 单个年度文件体量较大，读取时建议按时间步和变量切片读�取，避免一次性加载完整 `fields`。