# AVHRR与MODIS卫星NDVI数据获取

## 适用范围
执行AVHRR-MODIS连续NDVI历史序列融合重建任务前，需要获取真实的卫星NDVI数据。本卡指导如何从权威分发平台检索、下载AVHRR和MODIS NDVI产品，识别数据格式，确认时空覆盖范围，理解版本信息和质量标志。

## 输入
- 目标区域的空间范围（经纬度边界）
- 目标时间范围（起止年份）
- 所需NDVI产品类型（如GIMMS3g、MOD13A2、MOD13C1等）

## 输出
- 符合任务要求的AVHRR和MODIS NDVI数据文件（NetCDF4/HDF5格式）
- 数据质量标志文件
- 数据元数据文档

## 流程节点
1. 确定数据产品需求 → 2. 选择数据分发平台 → 3. 注册与认证 → 4. 检索与筛选 → 5. 下载与格式转换 → 6. 质量标志解读

### 步骤1：确定数据产品需求
- **操作**：根据任务需求确定AVHRR和MODIS NDVI产品类型
- **参数**：空间分辨率（AVHRR: ~8km, MODIS: 250m-1km）、时间分辨率（日/8天/16天/月）
- **工具**：产品规格文档
- **质量门禁**：产品类型与任务需求匹配

### 步骤2：选择数据分发平台
- **AVHRR数据**：
  - NASA LAADS DAAC (https://ladsweb.modaps.eosdis.nasa.gov/)
  - USGS EarthExplorer (https://earthexplorer.usgs.gov/)
  - NOAA CLASS (https://www.avl.class.noaa.gov/)
- **MODIS数据**：
  - NASA LAADS DAAC
  - USGS EarthExplorer
  - NASA Earthdata (https://earthdata.nasa.gov/)
- **质量门禁**：平台支持所需数据产品

### 步骤3：注册与认证
- **操作**：在数据分发平台注册账户并完成认证
- **工具**：平台注册系统
- **质量门禁**：账户激活并获得下载权限

### 步骤4：检索与筛选
- **操作**：使用空间范围、时间范围、云覆盖等条件检索数据
- **参数**：经纬度边界、日期范围、最大云覆盖百分比
- **工具**：平台检索接口
- **质量门禁**：检索结果满足时空覆盖要求

### 步骤5：下载与格式转换
- **操作**：下载数据文件并转换为统一格式
- **参数**：目标格式（NetCDF4/HDF5）
- **工具**：HDFView、GDAL、xarray
- **质量门禁**：文件完整且可读取

### 步骤6：质量标志解读
- **操作**：解读数据质量标志，识别可靠像元
- **参数**：质量标志位定义
- **工具**：产品文档
- **质量门禁**：质量标志正确应用

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| AVHRR时间覆盖 | 1981-至今 | [1] | GIMMS3g产品从1981年开始 |
| MODIS时间覆盖 | 2000-至今 | [1] | Terra MODIS从2000年开始 |
| AVHRR空间分辨率 | ~8km | [1] | GIMMS3g产品分辨率 |
| MODIS空间分辨率 | 250m-1km | [1] | 根据产品类型不同 |

### 校准数值
以下数值来自蒙古高原NDVI产品比较研究[1]，供量级校准；其他区域需以自身证据重新锚定：
| 产品 | 空间分辨率 | 时间分辨率 | 时间范围 |
|------|------------|------------|----------|
| AVHRR GIMMS3g | 8km | 15天 | 1981-2015 |
| Terra MODIS | 250m-1km | 日/8天/16天 | 2000-至今 |
| SPOT-VGT | 1km | 10天 | 1998-2014 |

## 边界与分流
- 若目标时间早于2000年，只能使用AVHRR数据
- 若需要高空间分辨率，优先选择MODIS产品
- 若数据分发平台不可用，可尝试替代平台或联系数据提供方

## 质量检查
- 检查数据文件是否完整（无缺失值）
- 验证时空范围是否符合要求
- 确认质量标志是否正确应用

## 回退策略
- 若首选平台不可用，使用替代平台
- 若数据格式不兼容，使用格式转换工具

## 资源召回建议
- 当任务涉及AVHRR或MODIS数据获取时召回本卡
- 配套召回NDVI融合算法卡和NDVI异常值处理卡

## 证据来源
[1] Intercomparison of AVHRR GIMMS3g, Terra MODIS, and SPOT-VGT NDVI Products over the Mongolian Plateau, Remote Sensing, 2019, DOI: 10.3390/rs11172030
[2] Extending NDVI time series in Mongolia using spatial correlation analysis between AVHRR-GIMMS and MODIS TERRA data, Mongolian Journal of Geography and Geoecology, 2025, DOI: 10.5564/mjgg.v62i46.4133
[3] Bayesian MODIS NDVI back-prediction by intersensor calibration with AVHRR, Remote Sensing of Environment, 2016, DOI: 10.1016/j.rse.2016.09.002