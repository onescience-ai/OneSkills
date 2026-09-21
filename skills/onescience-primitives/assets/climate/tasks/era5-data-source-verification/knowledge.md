# ERA5再分析数据源核验流程

## 适用范围
适用于气象科研任务中需要使用ERA5再分析数据作为输入数据的场景，包括但不限于天气锋面检测、气候分析、数值天气预报验证等任务。当任务要求"源观测资料（必填）"时，必须执行数据源核验流程。

## 输入
- 任务需求文档，明确所需数据变量（温度、湿度、风场、气压等）
- 目标区域和时段信息
- 数据分辨率要求（0.25°或0.1°）

## 输出
- 数据源核验报告，包含：
  - 数据来源和版本标识
  - 时空覆盖验证结果
  - 数据质量标志解读
  - 合成数据使用边界说明
- 可追溯的数据获取记录

## 流程节点
1. **数据来源确认** → 确认ERA5数据通过ECMWF CDS API获取
2. **版本标识核验** → 验证数据版本号（ERA5/ERA5-Land）
3. **时空覆盖验证** → 检查数据时空覆盖范围是否满足任务需求
4. **质量标志解读** → 解读数据质量标志和不确定性信息
5. **合成数据边界确认** → 确认合成数据使用边界和适用场景

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 数据源 | ECMWF CDS API | [1] | ERA5数据官方获取途径 |
| 空间分辨率 | 0.25°（再分析） | [2] | 全球规则经纬度网格 |
| 时间覆盖 | 1940至今 | [2] | 逐小时数据 |
| 变量单位 | 温度K、湿度kg/kg、气压Pa、风场m/s | [1] | ERA5标准单位 |
| 更新频率 | 每日更新 | [2] | 延迟约5天 |
| 不确定性估计 | 10成员集合 | [1] | 三小时间隔采样 |

## 边界与分流
- 当任务仅需方法开发和测试时，可使用合成数据，但必须在交付物中明确标注"合成数据，仅用于方法验证"
- 当任务要求科学有效性时，必须使用真实ERA5数据，不得使用合成数据替代
- 当数据获取失败时，应记录失败原因并降级为PARTIAL完成

## 质量检查
- 检查NetCDF文件的global_attributes是否包含Conventions、title、source等ERA5标准元数据字段
- 验证数据版本号是否正确标识
- 确认时空覆盖范围是否满足任务需求

## 回退策略
- 当无法获取真实ERA5数据时，标记相关交付项为PARTIAL并说明原因
- 当数据质量标志异常时，记录异常情况并评估对任务结果的影响

## 资源召回建议
- 当任务需要使用ERA5再分析数据时召回本卡片
- 配套使用气象多要素数据时空对齐标准流程卡片
- 配套使用气象产品质控规范卡片

## 补充证据（开源文档）
[D1] ERA5 hourly data on single levels from 1940 to present, Copernicus Climate Data Store, 2026-09-21, URL: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels（访问时间：2026-09-21）
[D2] ERA5 hourly data on pressure levels from 1940 to present, Copernicus Climate Data Store, 2026-09-21, URL: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-pressure-levels（访问时间：2026-09-21）

## 证据来源
[1] ERA5-Land: a state-of-the-art global reanalysis dataset for land applications, Muñoz-Sabater et al., Earth System Science Data, 2021, DOI: 10.5194/essd-13-2097-2021
[2] Evaluation of the ERA5 reanalysis as a potential reference dataset for hydrological modelling, Tarek et al., Hydrology and Earth System Sciences, 2020, DOI: 10.5194/hess-24-2017-2020
[3] ERA5 hourly data on single levels from 1940 to present, Copernicus Climate Data Store, 2018, DOI: 10.24381/cds.adbb2d47