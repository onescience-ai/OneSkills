# 气象数据可视化规范

本文档用于指导气象、气候、再分析、数值预报、站点观测和遥感网格数据的可视化生成。核心目标是让图形同时满足科学表达、气象行业习惯和代码可复用性。

## 适用数据与前置检查

- **网格场**：常见维度为 `time`、`level`、`lat`、`lon`，经纬度可为 1D 规则网格或 2D 曲线网格。
- **站点数据**：常见字段为站号、经度、纬度、时间、观测变量、质控标记。
- **垂直剖面**：可按经度-高度、纬度-高度、时间-高度或站点探空廓线展示。
- **时间约定**：标题和坐标轴必须注明 UTC、本地时或预报时效，例如 `2026-05-01 00 UTC`、`F024`。
- **单位核验**：绘图前确认单位，不要混用 K/degC、Pa/hPa、m/s/kt、kg/kg/g/kg。
- **缺测值**：绘图前将填充值、无效值、海陆掩膜转换为 `NaN` 或 masked array。
- **经度范围**：确认经度是 `0-360` 还是 `-180-180`，全球图建议添加 cyclic point 避免接缝。
- **纬度顺序**：若纬度从北到南递减，`contourf` 通常仍可绘制，但剖面和数组切片需显式确认方向。

## 常用图表类型

### 温度场可视化

- **等温线/填色图**：使用 `contour` / `contourf` 展示 2m 温度、850 hPa 温度、海表温度等空间分布。
- **温度异常图**：使用以 0 为中心的双极色标，适合距平、偏差和模式误差。
- **时间序列**：用 `plot` 展示站点或区域平均温度随时间变化，并注明时区、日界线和统计口径。
- **垂直剖面**：高度/气压层-纬度或经度截面，展示层结、逆温和锋区结构。

### 风场可视化

- **风矢量图**：`quiver` 用箭头表达风向和风速，需降采样避免拥挤。
- **风羽图**：`barbs` 是气象业务中更标准的表达，通常使用 knots。
- **流线图**：`streamplot` 适合规则平面网格上的流动轨迹，不适合直接用于复杂地图投影后的坐标。
- **风速填色叠加风向**：以风速大小为填色层，叠加 `quiver` 或 `barbs` 表示方向。
- **风玫瑰图**：适合站点风向频率统计，使用极坐标或 `windrose` 库。

### 气压与位势高度可视化

- **海平面气压等压线**：常用 `contour`，业务图常见间隔为 4 hPa。
- **位势高度等值线**：500 hPa 常见间隔为 60 gpm 或 6 dagpm，850/700/200 hPa 需按场值范围调整。
- **厚度场**：如 1000-500 hPa 厚度，可用等值线或填色辅助判断冷暖空气。
- **异常/距平场**：气压、位势高度距平使用双极色标；绝对场优先用等值线或感知均匀顺序色标。

### 湿度与水汽可视化

- **相对湿度填色**：范围通常为 0-100%，建议固定色标范围，便于多时次比较。
- **比湿/混合比剖面**：展示水汽垂直分布，单位常用 g/kg。
- **可降水量**：通常用空间填色图或区域平均时间序列，不宜称为柱状图的固定形式。
- **水汽通量/水汽通量散度**：可使用填色叠加矢量，散度类变量应使用双极色标。

### 降水可视化

- **累计降水柱状图**：适合站点或区域平均的逐时/逐日降水量。
- **累计降水曲线**：展示过程累积量和事件演变。
- **空间降水分布**：使用 `pcolormesh` / `contourf`，色阶应按业务阈值或非线性分级设计。
- **降水率/雷达回波**：降水率、反射率等非负变量使用顺序色标，避免双极色标。
- **频率分布**：用直方图或概率密度展示降水强度分布，需说明样本时间尺度。

### 云、辐射与卫星遥感

- **云量/云顶温度**：云量使用 0-100% 顺序色标，云顶亮温可按温度场处理。
- **反照率/短波辐射**：非负变量使用顺序色标，注明 W/m^2 或百分比。
- **红外/水汽通道亮温**：注意反色习惯，冷云顶常用更亮或更冷的色阶表达。

### 海表与海洋变量

- **海表温度（SST）**：绝对 SST 可用热力顺序色标，SST 异常用双极色标。
- **海冰覆盖**：二值或连续场填色，建议固定 `0-100%` 或 `0-1` 范围。
- **海面高度异常**：正负异常使用以 0 为中心的双极色标。

### 垂直运动

- **压力速度 omega**：单位常为 Pa/s，气象中正值通常表示下沉、负值表示上升。
- **几何垂直速度 w**：单位常为 m/s，正值通常表示上升。
- **垂直剖面流线**：叠加水平风分量与垂直速度时，需缩放垂直速度以避免视觉失真。

### 多变量组合

- **温度 + 风场**：温度或温度平流填色为基础层，风矢量/风羽为覆盖层。
- **气压 + 风场**：海平面气压等压线叠加 10m 风，有助于识别低压、高压和锋面附近流场。
- **位势高度 + 温度 + 风场**：常用于高空天气图，位势高度等值线 + 温度填色 + 风羽。
- **降水 + MSLP/风场**：降水填色叠加等压线和低层风，适合天气过程诊断。

### 多时刻对比

- **多面板分时图**：2x2 或 1xN 布局，每个面板展示同一变量的不同时刻。
- **预报时效对比**：标题需标注起报时间和预报时效，例如 `Init 2026-05-01 00 UTC, F024`。
- **动画帧序列**：多个 PNG 帧组成 GIF/MP4，固定色标范围和地图范围。
- **Hovmoller 图**：经度-时间或纬度-时间截面展示波动、MJO、锋面或降水带传播。

## 配色方案

- **温度绝对场**：`coolwarm`、`RdYlBu_r` 或领域自定义温度色标；多时次比较时固定 `vmin/vmax`。
- **温度/高度/气压异常**：`RdBu_r`、`coolwarm`，并使用 `TwoSlopeNorm(vcenter=0)`。
- **降水/降水率**：`Blues`、`YlGnBu`、`turbo` 或业务分级色标；非负变量不要使用双极色标。
- **风速**：`YlOrRd`、`magma`、`viridis`，固定起点 0。
- **气压/位势高度绝对场**：优先等值线；如需填色，使用 `viridis`、`cividis` 等顺序色标。
- **相对湿度**：`Greens`、`BrBG` 或 `YlGnBu`，范围通常固定为 `0-100`。
- **垂直速度**：omega 使用 `RdBu_r` 时建议蓝色表示上升（负 omega）、红色表示下沉（正 omega）；w 可按相反物理含义调整标注。
- **海洋异常变量**：`RdBu_r`，以 0 为中心。
- **方差/标准差/不确定性**：`YlOrRd`、`magma` 或 `hot`，表达非负强度。

## 单位与标签规范

- **温度**：K 或 degC；若转换，使用 `degC = K - 273.15`。
- **风速**：m/s、km/h 或 kt；风羽图常用 kt，`1 m/s = 1.94384 kt`。
- **气压**：Pa 或 hPa；海平面气压常用 hPa，`hPa = Pa / 100`。
- **位势高度**：gpm 或 dagpm；500 hPa 层业务图常用 gpm 或 dagpm。
- **降水**：mm（累计量）、mm/h（降水率）。
- **相对湿度**：%（0-100）；比湿 kg/kg 或 g/kg。
- **垂直速度**：omega 为 Pa/s，w 为 m/s，必须说明正负方向含义。
- **坐标轴**：经度、纬度、压力层、高度、时间均需含单位或坐标基准。
- **压力层标注**：使用空格分隔数值和单位，如 `500 hPa`、`850 hPa`。
- **标题**：包含变量、层次/高度、区域、时刻或时效。

## 常用 Python 库

- `matplotlib`：基础绘图、色标、布局控制。
- `cartopy`：地图投影和地理要素，常用 `PlateCarree`、`LambertConformal`、`Orthographic`。
- `xarray`：多维气象数据处理，适合 NetCDF/GRIB 解码后的数据。
- `metpy`：单位处理、气象诊断计算、风羽和 Skew-T 等专业工具。
- `numpy`：数组计算和缺测值处理。
- `cmocean` / `cmaps`：海洋和气象色标。
- `cfgrib` / `netCDF4` / `h5netcdf`：常见气象数据读取后端。
- `imageio` / `Pillow`：动画帧合成。

## 代码模板

以下模板假设：

- `lon`、`lat` 为一维经纬度数组，`field`、`u`、`v` 为形状 `(lat, lon)` 的二维数组。
- 若使用 xarray，可传入 `da["lon"].values`、`da["lat"].values`、`da.values`。
- 地图投影中的数据坐标系通常是 `ccrs.PlateCarree()`，显示投影可按区域替换。

### 1. 空间场填色 + 等值线叠加（规则经纬网格）

```python
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


def plot_contour_map(lon, lat, field, title, output_path):
    data_crs = ccrs.PlateCarree()
    map_crs = ccrs.PlateCarree(central_longitude=180)

    fig, ax = plt.subplots(figsize=(12, 6), subplot_kw={"projection": map_crs})
    vmin = np.nanmin(field)
    vmax = np.nanmax(field)
    if np.isclose(vmin, vmax):
        vmin -= 0.5
        vmax += 0.5
    levels = np.linspace(vmin, vmax, 21)

    cf = ax.contourf(
        lon,
        lat,
        field,
        levels=levels,
        cmap="coolwarm",
        extend="both",
        transform=data_crs,
    )
    cl = ax.contour(
        lon,
        lat,
        field,
        levels=levels[::4],
        colors="black",
        linewidths=0.5,
        transform=data_crs,
    )
    ax.clabel(cl, fmt="%.0f", fontsize=7)

    ax.coastlines(resolution="110m", linewidth=0.6)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3)
    ax.add_feature(cfeature.LAND, facecolor="0.92", alpha=0.4)
    gl = ax.gridlines(draw_labels=True, linewidth=0.3, alpha=0.5)
    gl.top_labels = False
    gl.right_labels = False

    cbar = fig.colorbar(cf, ax=ax, orientation="horizontal", pad=0.06, shrink=0.82)
    cbar.set_label("Temperature (K)")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
```

### 2. 风速填色 + 风矢量/风羽

```python
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


def plot_wind_map(lon, lat, u, v, output_path, use_barbs=False):
    data_crs = ccrs.PlateCarree()
    fig, ax = plt.subplots(figsize=(12, 6), subplot_kw={"projection": data_crs})

    wind_speed = np.hypot(u, v)
    vmax = np.nanpercentile(wind_speed, 98)
    if not np.isfinite(vmax) or vmax <= 0:
        vmax = 1.0
    levels = np.linspace(0, vmax, 16)
    cf = ax.contourf(
        lon,
        lat,
        wind_speed,
        levels=levels,
        cmap="YlOrRd",
        extend="max",
        transform=data_crs,
    )

    step_y = max(1, len(lat) // 25)
    step_x = max(1, len(lon) // 40)
    skip = (slice(None, None, step_y), slice(None, None, step_x))

    if use_barbs:
        ms_to_kt = 1.94384
        ax.barbs(
            lon[skip[1]],
            lat[skip[0]],
            u[skip] * ms_to_kt,
            v[skip] * ms_to_kt,
            length=5,
            linewidth=0.5,
            transform=data_crs,
        )
    else:
        q = ax.quiver(
            lon[skip[1]],
            lat[skip[0]],
            u[skip],
            v[skip],
            transform=data_crs,
            scale=350,
            width=0.002,
        )
        ax.quiverkey(q, 0.88, -0.08, 10, "10 m/s", labelpos="E")

    ax.coastlines(resolution="110m", linewidth=0.6)
    ax.set_title("Wind speed and direction")
    cbar = fig.colorbar(cf, ax=ax, orientation="horizontal", pad=0.06, shrink=0.82)
    cbar.set_label("Wind speed (m/s)")
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
```

### 3. 站点/非规则散点数据

```python
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


def plot_station_scatter(lon, lat, values, output_path):
    data_crs = ccrs.PlateCarree()
    fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={"projection": data_crs})

    sc = ax.scatter(
        lon,
        lat,
        c=values,
        cmap="coolwarm",
        s=32,
        alpha=0.85,
        edgecolors="black",
        linewidths=0.3,
        transform=data_crs,
    )
    ax.coastlines(resolution="110m", linewidth=0.6)
    ax.set_extent([min(lon) - 2, max(lon) + 2, min(lat) - 2, max(lat) + 2], crs=data_crs)
    ax.set_title("Station observations")
    cbar = fig.colorbar(sc, ax=ax, orientation="horizontal", pad=0.06, shrink=0.82)
    cbar.set_label("Variable")
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
```

### 4. 时间序列（区域平均或站点温度）

```python
import matplotlib.pyplot as plt


def plot_temperature_series(times, mean_temp, min_temp, max_temp, output_path):
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(times, mean_temp, marker="o", color="#c0392b", linewidth=2.2, label="Mean")
    ax.fill_between(times, min_temp, max_temp, alpha=0.22, color="#e74c3c", label="Min-Max")
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("2m temperature (degC)")
    ax.grid(True, alpha=0.3)
    ax.legend(frameon=False)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
```

### 5. 多面板分时对比

```python
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


def plot_multi_panel(lon, lat, fields, time_labels, output_path):
    data_crs = ccrs.PlateCarree()
    fig, axes = plt.subplots(
        2,
        2,
        figsize=(13, 8),
        subplot_kw={"projection": data_crs},
        constrained_layout=True,
    )
    vmin = np.nanmin(fields)
    vmax = np.nanmax(fields)
    if np.isclose(vmin, vmax):
        vmin -= 0.5
        vmax += 0.5
    levels = np.linspace(vmin, vmax, 21)
    mappable = None

    for ax, field, label in zip(axes.ravel(), fields[:4], time_labels[:4]):
        mappable = ax.contourf(
            lon,
            lat,
            field,
            levels=levels,
            cmap="coolwarm",
            extend="both",
            transform=data_crs,
        )
        ax.coastlines(resolution="110m", linewidth=0.5)
        ax.set_title(label)

    cbar = fig.colorbar(mappable, ax=axes.ravel().tolist(), orientation="horizontal", pad=0.05)
    cbar.set_label("Temperature (K)")
    fig.suptitle("Temperature evolution")
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
```

### 6. 垂直剖面（压力坐标）

```python
import matplotlib.pyplot as plt


def plot_pressure_section(x_coord, pressure_hpa, field, output_path):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    cf = ax.contourf(x_coord, pressure_hpa, field, levels=21, cmap="RdYlBu_r", extend="both")
    cl = ax.contour(x_coord, pressure_hpa, field, colors="black", linewidths=0.4, levels=cf.levels[::4])
    ax.clabel(cl, fmt="%.0f", fontsize=7)
    ax.invert_yaxis()
    ax.set_yscale("log")
    ax.set_ylabel("Pressure (hPa)")
    ax.set_xlabel("Latitude or longitude")
    ax.set_title("Vertical cross section")
    cbar = fig.colorbar(cf, ax=ax, pad=0.02)
    cbar.set_label("Variable")
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
```

### 7. Hovmoller 图

```python
import matplotlib.pyplot as plt


def plot_hovmoller(x_coord, times, field_time_x, output_path):
    fig, ax = plt.subplots(figsize=(11, 5))
    cf = ax.contourf(x_coord, times, field_time_x, levels=21, cmap="RdBu_r", extend="both")
    ax.set_xlabel("Longitude or latitude")
    ax.set_ylabel("Time (UTC)")
    ax.set_title("Hovmoller diagram")
    cbar = fig.colorbar(cf, ax=ax, pad=0.02)
    cbar.set_label("Anomaly")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
```

### 8. 无 cartopy 时的降级方案

当 `cartopy` 不可用时，只绘制经纬度坐标，不添加海岸线；标题或说明中应标注这是降级地图。

```python
import matplotlib.pyplot as plt


def plot_without_cartopy(lon, lat, values, output_path):
    fig, ax = plt.subplots(figsize=(10, 5))
    sc = ax.scatter(lon, lat, c=values, cmap="coolwarm", s=20, alpha=0.85)
    ax.set_xlabel("Longitude (degrees_east)")
    ax.set_ylabel("Latitude (degrees_north)")
    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    ax.axhline(0, color="gray", alpha=0.35, linewidth=0.6)
    ax.axvline(0, color="gray", alpha=0.35, linewidth=0.6)
    ax.grid(True, alpha=0.25)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("Geographic scatter plot without map projection")
    cbar = fig.colorbar(sc, ax=ax, pad=0.02)
    cbar.set_label("Variable")
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
```

## 图表质量标准

### 必须检查项

| 检查项 | 要求 |
|--------|------|
| 变量与单位 | 标题、坐标轴、色标至少一处明确变量名和单位 |
| 时间信息 | 标明 UTC/本地时、预报起报时刻、预报时效或统计时段 |
| 色标范围 | 多面板和动画必须固定范围；异常场以 0 为中心 |
| 色标类型 | 非负变量用顺序色标，异常/散度/垂直速度等正负变量用双极色标 |
| 地图投影 | 地理空间图应声明数据 CRS 和显示投影 |
| 地图要素 | 全球/区域地图至少包含海岸线，必要时添加国界、省界、海陆掩膜 |
| 网格密度 | 风矢量、站点标签和等值线标签不得遮挡主要信号 |
| 分辨率 | PNG 建议 200-300 dpi；论文或报告编辑优先导出 SVG/PDF |
| 可比性 | 同一变量跨时次、跨模型、跨试验对比时使用相同色阶和范围 |

### 地图要素检查

| 检查项 | 要求 |
|--------|------|
| `coastlines` | 全球图必须；区域图建议保留 |
| `gridlines` | 经纬度标签清晰，不与标题和色标重叠 |
| `set_extent` | 区域图应设置范围，避免默认全球视角 |
| `transform` | `contourf`、`scatter`、`quiver` 等必须传入数据坐标系 |
| cyclic point | 全球填色图跨 0/360 或 -180/180 接缝时建议添加 |

### 禁止项

- 不要对降水、风速、云量、湿度等非负变量使用双极色标。
- 不要省略色标单位，尤其是 K/degC、Pa/hPa、m/s/kt。
- 不要在高密度风场上使用未降采样的矢量箭头。
- 不要让多面板图各自自动缩放色标范围后再直接比较强弱。
- 不要把 omega 的正负方向与 w 的正负方向混为一谈。
- 不要在地图投影图上省略 `transform`，否则不同投影下位置可能错误。
