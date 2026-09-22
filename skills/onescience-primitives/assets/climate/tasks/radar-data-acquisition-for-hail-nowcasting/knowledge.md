# 天气雷达数据获取与预处理（冰雹临近预报）

## 适用范围

冰雹临近预报（0-2小时时效）场景下，需要从真实天气雷达观测获取组合反射率（Composite Reflectivity）、体扫基数据或衍生产品作为输入。本卡覆盖国内外主流雷达数据源的访问方式、数据格式规范、质量检查方法与预处理流程。合成数据仅适用于算法流程验证，不可替代真实观测用于业务性能判定。

## 输入

- 预报目标区域与时段（空间范围、时间窗口）
- 雷达产品类型需求：组合反射率（CR）、等高面反射率（CAPPI）、最大反射率（MAXZ）等
- 时空分辨率要求：通常 1-6 分钟时间间隔、250m-1km 空间分辨率

## 输出

- 格式统一的雷达反射率网格数据（numpy HDF5 或 NetCDF）
- 数据质量元数据（覆盖率、缺失率、异常标记）
- 通过质量检查的可输入数据集

## 流程节点

1. 数据源选择与接入 → 2. 格式解析与坐标对齐 → 3. 质量检查 → 4. 预处理与标准化

每步含：操作、参数、工具、质量门禁

### 步骤1：数据源选择与接入

根据任务区域和时效要求选择合适数据源：

**中国区域（优先）**：
- **CINRAD（中国新一代天气雷达）**：全国约 240 部，覆盖 S 波段和 C 波段。基数据通过省级气象数据中心分发，组合反射率产品可从全国综合气象信息共享平台（CIMISS）获取。实时产品延迟约 5-10 分钟。[1][4]
- **CIMISS 数据接口**：http://data.cma.cn 提供标准 API，支持按站号、时间范围查询。需注册账号并获取 token。[4]

**北美区域**：
- **MRMS（Multi-Radar Multi-Sensor）**：NSSL 开发的多雷达多传感器融合系统，提供 1km 分辨率的组合反射率、MESH（最大预期冰雹尺寸）等衍生产品。数据通过 Iowa State University 的 MTNet 或 NOAA 高性能数据库获取。空间覆盖美国本土，时间分辨率 2 分钟。[2][5]
- **NEXRAD（Next-Generation Radar）**：美国 WSR-88D 网络，基数据通过 AWS S3 公开存储桶（s3://noaa-nexrad-level2）免费访问，格式为 Level-II 二进制或 Level-III 产品。[2]

**欧洲/全球**：
- **OPERA（欧洲雷达网络）**：通过 EUMETNET 获取，格式遵循 ODIM_H5 标准。
- **TAASRAD19 数据集**：意大利阿尔卑斯地区高分辨率雷达反射率数据集，包含 894,916 个时间步长，1km 分辨率，5分钟时间间隔。[1]

### 步骤2：格式解析与坐标对齐

| 数据源 | 主要格式 | 解析库 | 坐标系统 |
|--------|----------|--------|----------|
| CINRAD | Polar 格式（230km 体扫） | Py-ART, wradlib | 极坐标 → Lambert 投影 |
| MRMS | NetCDF4 / GRIB2 | xarray, cfgrib | 1km 等经纬度网格 |
| NEXRAD Level-II | 二进制（AR2） | Py-ART, ODIM | 极坐标 → Lambert |
| NEXRAD Level-III | NIDS 格式 | Py-ART | 网格化产品 |
| TAASRAD19 | HDF5 (ODIM) | h5py, xarray | ODIM 标准网格 |

**关键操作**：
- 体扫数据需完成 PPI（平面位置显示）到 CAPPI 或等经纬度网格的插值
- 不同雷达站数据需统一到相同投影和分辨率
- 时间对齐：不同雷达体扫起始时间不同，需插值到统一时间戳

### 步骤3：质量检查

- **覆盖率检查**：目标区域内有效反射率像元占比 ≥ 80%
- **异常值检查**：反射率值应落在合理范围（通常 -32 至 75 dBZ），超出范围标记为无效
- **孤立像元检查**：孤立有效像元（<5 个相邻像元）需标记或滤除
- **时序一致性**：相邻时间步反射率变化不应超过物理合理阈值（如 30 dBZ/5min）

### 步骤4：预处理与标准化

- 缺失值填充：使用前一时刻或邻近格点插值
- 反射率归一化：dBZ → 线性反射率因子 Z（mm⁶/m³）或直接归一化到 [0,1]
- 尺寸裁剪：裁剪到模型输入尺寸（如 256×256 或 512×512）

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| CINRAD 体扫周期 | 6 min (VCP11) / 4 min (VCP21) | [4] | VCP 模式决定时间分辨率 |
| MRMS 空间分辨率 | 1 km | [2][5] | 美国本土统一网格 |
| MRMS 时间分辨率 | 2 min | [2] | 多雷达融合后的时间分辨率 |
| NEXRAD Level-II 免费访问 | AWS S3: noaa-nexrad-level2 | [2] | 无需认证，直接读取 |
| 反射率有效范围 | -32 至 75 dBZ | [1][3] | 超出范围为无效或饱和 |
| TAASRAD19 数据量 | 894,916 时间步 × 1km | [1] | 约 1.5TB HDF5 |
| CINRAD QPE 偏差 | GPM-DPR 校正后 ≤ 1 dB | [4] | 反射率偏差影响降水估算 |

## 边界与分流

- **无实时数据**：若任务为算法流程演示且允许合成数据，可在 metadata.json 中标注 `source: synthetic`，但所有检验指标必须注明不具业务参考价值
- **数据源不可达**：优先降级到公开可获取的数据源（如 NEXRAD AWS S3），其次使用历史存档数据
- **多雷达拼图**：当单雷达覆盖不足时，需使用多雷达拼图产品（如 MRMS 组合反射率），注意不同雷达站间的标定一致性

## 质量检查

- 验证 data/ 目录下 radar_reflectivity_*.npy 文件的来源 metadata 是否为真实观测
- metadata.json 中 source 字段应记录实际数据源名称（如 "CINRAD/SA"、"MRMS/CONUS"）
- 覆盖率 < 80% 时应降级或标记数据质量警告

## 回退策略

- CINRAD 不可达 → 尝试 MRMS 或 NEXRAD 作为替代数据源
- 全部实时源不可达 → 使用 TAASRAD19 等历史数据集
- 历史数据集也不可用 → 仅在标注合成数据前提下使用模拟数据

## 资源召回建议

- 冰雹临近预报任务的数据输入阶段应召回本卡
- 配套召回 `diffusion-probability-model-for-nowcasting`（概率场生成）和 `nowcasting-verification-independence`（验证数据独立性）
- CINRAD 数据处理可进一步召回 CINRAD 专用处理工具卡

## 证据来源

[1] TAASRAD19, a high-resolution weather radar reflectivity dataset for precipitation, Scientific Data, 2020, DOI: 10.1038/s41597-020-00545-9
[2] An Hourly Climatology of Operational MRMS MESH-Diagnosed Severe and Significant Hail, Weather and Forecasting, 2021, DOI: 10.1175/WAF-D-20-0191.1
[3] Detection of hail signatures from single-polarization C-band radar reflectivity, Atmospheric Research, 2015, DOI: 10.1016/j.atmosres.2015.07.023
[4] Improving CINRAD Radar QPE Through GPM-DPR Reflectivity Bias Correction, Water Resources Research, 2023, DOI: 10.1029/2023WR035432
[5] Use of Deep Learning for Weather Radar Nowcasting, Journal of Atmospheric and Oceanic Technology, 2021, DOI: 10.1175/JTECH-D-20-0157.1
