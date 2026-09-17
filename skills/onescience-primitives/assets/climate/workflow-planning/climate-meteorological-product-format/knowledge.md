# 气象产品格式规范知识卡片

## 适用范围

### 触发条件
- 任务需要生成气象预报产品
- 需要遵循NetCDF/CF标准格式
- 需要添加完整的元数据信息

### 适用场景
- 气象预报产品生成
- 科学数据发布和共享
- 模型输出标准化

### 不适用场景
- 业务预报系统（使用专用格式）
- 实时数据传输（使用轻量格式）

## 输入

### 数据内容
| 数据类型 | 说明 | 示例 |
|---------|------|------|
| 预报场 | 模型预报结果 | 降水率、温度、风速 |
| 概率产品 | 集合预报统计量 | 分位数、概率 |
| 不确定性 | 预报不确定性 | 集合离散度、置信区间 |
| 元数据 | 数据描述信息 | 时间、空间、变量信息 |

### 标准规范
| 规范 | 说明 | 适用范围 |
|------|------|---------|
| CF-1.8 | 气候和预报元数据规范 | NetCDF文件 |
| ACDD | 社区数据发现规范 | 数据共享 |
| WMO标准 | 世界气象组织标准 | 国际交换 |

## 输出

### NetCDF-4文件结构
```
dimensions:
  time = UNLIMITED ;
  latitude = 512 ;
  longitude = 512 ;
  ensemble = 50 ;

variables:
  float precipitation_rate(time, latitude, longitude) ;
    precipitation_rate:units = "mm h-1" ;
    precipitation_rate:long_name = "Precipitation Rate" ;
    precipitation_rate:standard_name = "rainfall_rate" ;
    precipitation_rate:_FillValue = -9999.f ;
    precipitation_rate:missing_value = -9999.f ;
  
  float latitude(latitude) ;
    latitude:units = "degrees_north" ;
    latitude:long_name = "Latitude" ;
    latitude:standard_name = "latitude" ;
  
  float longitude(longitude) ;
    longitude:units = "degrees_east" ;
    longitude:long_name = "Longitude" ;
    longitude:standard_name = "longitude" ;
  
  double time(time) ;
    time:units = "hours since 1970-01-01T00:00:00Z" ;
    time:long_name = "Time" ;
    time:standard_name = "time" ;
    time:calendar = "standard" ;
  
  float ensemble(ensemble) ;
    ensemble:long_name = "Ensemble Member" ;
    ensemble:axis = "ensemble" ;
```

### 元数据要求
| 元数据字段 | 说明 | 示例 |
|-----------|------|------|
| title | 产品标题 | "Radar-driven 0-3h Extreme Precipitation Ensemble Nowcast" |
| institution | 机构名称 | "China Meteorological Administration" |
| source | 数据来源 | "NowcastNet Model" |
| history | 处理历史 | "Generated on 2026-09-15" |
| references | 参考文献 | "DOI: 10.1038/s41586-023-06184-9" |
| Conventions | 标准规范 | "CF-1.8" |
| contact | 联系方式 | "xxx@example.com" |

### 产品文件命名
| 格式 | 说明 | 示例 |
|------|------|------|
| <类型>_<变量>_<时间>_<版本>.nc | 标准命名 | "nowcast_precip_rate_20260915_v1.0.nc" |

## 流程节点

### 产品生成标准流程
```
模型输出 → 变量重命名 → 单位标准化 → 元数据添加 → CF合规检查 → 文件输出 → 质量验证
```

### 每步操作
| 步骤 | 操作 | 工具 | 参数 | 质量门禁 |
|------|------|------|------|---------|
| 1. 数据加载 | 读取模型输出 | xarray | - | 数据可读 |
| 2. 变量重命名 | 符合CF标准名 | xarray.rename | - | 变量名规范 |
| 3. 单位标准化 | 统一单位 | xarray | - | 单位正确 |
| 4. 元数据添加 | 添加global attrs | xattrs | - | 元数据完整 |
| 5. CF检查 | 验证CF合规性 | cfcheck | - | 无错误 |
| 6. 文件输出 | 写入NetCDF-4 | xarray.to_netcdf | format='NETCDF4' | 文件可读 |
| 7. 质量验证 | 检查文件完整性 | netCDF4 | - | 内容正确 |

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 文件格式 | NetCDF-4 | CF-1.8标准 | 压缩存储 |
| 压缩类型 | deflate | 最佳实践 | level=4 |
| 填充值 | -9999 | CF约定 | 缺失值标记 |
| 时间单位 | hours since 1970-01-01 | CF约定 | 标准时间 |
| 空间分辨率 | 0.01°~0.1° | 任务需求 | 高分辨率 |

## 边界与分流

### 异常处理
| 异常情况 | 处理策略 | 降级方案 |
|---------|---------|---------|
| CF检查失败 | 修复不合规字段 | 降级为非CF格式 |
| 元数据缺失 | 添加默认值 | 标注不完整 |
| 文件过大 | 分块存储 | 使用分片 |

### 分支条件
- 若包含集合成员：添加ensemble维度
- 若包含不确定性：添加uncertainty变量
- 若多时次：使用UNLIMITED time维度

## 质量检查

### 验证点
1. 文件可读：标准库可打开
2. CF合规：通过cfcheck检查
3. 元数据完整：必填字段齐全
4. 变量正确：名称、单位、维度匹配

### 阈值
| 指标 | 阈值 | 失败处理 |
|------|------|---------|
| CF检查通过率 | 100% | 修复不合规项 |
| 元数据完整度 | 100% | 补充缺失项 |
| 文件可读率 | 100% | 重新生成 |

## 回退策略

1. **NetCDF不可用**: 使用HDF5或GRIB格式
2. **CF检查失败**: 降级为非标准格式并标注
3. **文件过大**: 分块存储或降低精度

## 资源召回建议

### 何时召回本卡片
- 任务需要生成标准气象产品
- 需要遵循NetCDF/CF规范
- 需要进行数据共享和发布

### 配套资源
- `climate-radar-data-acquisition`: 数据获取知识
- `climate-forecast-verification`: 验证知识

## 证据来源

[1] MetPy: A Meteorological Python Library for Data Analysis and Visualization, Bulletin of the American Meteorological Society, 2022, DOI: 10.1175/BAMS-D-21-0218.1
[2] WFDE5: bias-adjusted ERA5 reanalysis data for impact studies, Earth System Science Data, 2020, DOI: 10.5194/essd-12-2921-2020

**证据说明**: 本卡片内容基于论文摘要和专业知识整理。NetCDF/CF规范来自国际标准，产品格式基于气象数据共享通用实践。使用时建议参考CF标准文档获取详细规范。