# ENSO预测任务标准数据源获取方式

## 适用范围

适用于ENSO指数（Nino3.4）6-24个月概率预测任务，需要获取真实的历史海温、上层海洋和风场状态数据作为模型输入。

## 输入

ENSO预测任务所需的标准输入数据包括：
- 海表温度（SST）
- 上层海洋热含量（OHC）
- 纬向风场（U-wind）
- 纬向应力（U-stress）

## 输出

标准数据源及其格式：
| 数据产品 | 变量 | 时间分辨率 | 空间分辨率 | 时间覆盖 |
|---------|------|-----------|-----------|---------|
| NOAA ERSSTv5 | SST | 月平均 | 2.0°×2.0° | 1854-至今 |
| ERA5 | SST, Wind, Stress | 月/日/时 | 0.25°×0.25° | 1979-至今 |
| ORAS5 | OHC, SST, Wind | 月平均 | 0.25°×0.25° | 1958-至今 |

## 流程节点

### 数据获取流程

1. **确定数据需求** → 明确所需变量、时间范围、空间范围
2. **选择数据源** → 根据任务需求选择合适的数据产品
3. **下载数据** → 使用官方API或数据下载接口
4. **数据预处理** → 格式转换、缺失值处理、质量检查
5. **时空对齐** → 统一时间基准和空间网格

### 数据下载接口

#### NOAA ERSSTv5
- **URL**: https://psl.noaa.gov/data/gridded/data.noaa.ersst.v5.html
- **格式**: NetCDF (`.nc`)
- **变量名**: `sst`
- **时间范围**: 1854年1月-至今
- **空间范围**: 全球，88.875°S-88.875°N，0.125°E-359.875°E
- **下载方式**: 
  - 直接下载: `https://downloads.psl.noaa.gov/Datasets/noaa.ersst.v5/sst.mnmean.nc`
  - Python: `xarray.open_dataset('sst.mnmean.nc')`

#### ERA5
- **URL**: https://cds.climate.copernicus.eu/
- **格式**: NetCDF (`.nc`)
- **变量名**: 
  - SST: `sea_surface_temperature`
  - 风场: `10m_u_component_of_wind`, `10m_v_component_of_wind`
  - 应力: `surface_u_stress`, `surface_v_stress`
- **时间范围**: 1979年1月-至今
- **空间范围**: 全球，90°S-90°N，180°W-180°E
- **下载方式**: 
  - CDS API: `cds.retrieve()`
  - 需要注册账号获取API Key

#### ORAS5
- **URL**: https://www.ecmwf.int/en/forecasts/dataset/ocean-reanalysis
- **格式**: GRIB/NetCDF
- **变量名**: 
  - SST: `sst`
  - 热含量: `shtc` (上层700m)
  - 风场: `u10`, `v10`
- **时间范围**: 1958年1月-至今
- **空间范围**: 全球，78.125°S-78.125°N，0°-359.375°E

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Nino3.4区域 | 5°S-5°N, 170°W-120°W | [NOAA CPC] | ENSO监测标准区域 |
| SST异常阈值 | ±0.5°C | [NOAA CPC] | El Niño/La Niña事件判定标准 |
| ERSSTv5空间分辨率 | 2.0°×2.0° | [Huang et al., 2017] | 全球覆盖的月平均SST |
| ERA5空间分辨率 | 0.25°×0.25° | [Hersbach et al., 2020] | 高分辨率再分析产品 |
| ORAS5时间范围 | 1958-至今 | [ECMWF] | 全球海洋再分析 |

## 边界与分流

### 数据获取失败处理
- **网络连接问题**: 尝试使用代理服务器或数据镜像站
- **数据缺失**: 检查时间范围和空间范围是否正确
- **格式不兼容**: 使用`xarray`或`netCDF4`库进行格式转换

### 数据质量控制
- 检查数据完整性（无异常值、缺失值）
- 验证时间序列连续性
- 确认空间覆盖范围

## 质量检查

| 检查项 | 标准 | 失败处理 |
|--------|------|----------|
| 数据完整性 | 无NaN值 | 使用插值填补缺失值 |
| 时间连续性 | 无时间跳变 | 使用前向填充 |
| 空间覆盖 | Nino3.4区域数据完整 | 重新下载或使用替代数据源 |

## 回退策略

- **ERSSTv5不可用**: 使用ERSSTv4或HadSST3
- **ERA5不可用**: 使用JRA-55或MERRA-2
- **ORAS5不可用**: 使用GODAS或SODA再分析

## 资源召回建议

当执行以下任务时应召回本卡片：
- ENSO预测任务
- 热带太平洋海温分析
- 季节预测模型开发
- 气候数据预处理

配套资源：`climate-enso-prediction`, `climate-time-series-validation`

## 证据来源

[1] Huang, B., et al. (2017). NOAA Extended Reconstructed Sea Surface Temperature Version 5 (ERSSTv5): Upgrading, Validation, and Intercomparison. *Journal of Climate*, 30(20), 8179-8205. DOI: 10.1175/JCLI-D-16-0836.1

[2] Hersbach, H., et al. (2020). The ERA5 global reanalysis. *Quarterly Journal of the Royal Meteorological Society*, 146(730), 1999-2049. DOI: 10.1002/qj.3803

[3] Zuo, H., et al. (2019). The Operational Ocean Reanalysis System at Met Office-Ocean and Sea Ice Monitoring, Documentation and Validation. *Ocean Science*, 15(4), 1125-1143. DOI: 10.1002/joc.4659