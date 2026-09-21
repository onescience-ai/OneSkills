# 气象多要素数据时空对齐标准流程

## 适用范围
适用于气象科研任务中需要将多个气象要素（温度、湿度、风场、气压等）数据进行时空对齐的场景，确保多要素数据在同一时空网格上严格对齐，为后续分析提供一致的数据基础。

## 输入
- 多个气象要素的NetCDF文件
- 每个文件的变量名、单位、坐标维度信息
- 数据质量标志（如有）

## 输出
- 对齐后的标准输入数据
- 掩膜与样本索引
- 预处理转换记录，包含：
  - 时间轴一致性检查结果
  - 空间网格对齐结果
  - 单位标准化记录
  - 质量标志和缺测处理记录

## 流程节点
1. **时间轴一致性检查** → 检查time coordinate是否完全匹配
2. **空间网格对齐** → 检查lat/lon坐标是否逐点一致
3. **单位标准化** → 统一到ERA5标准单位
4. **质量标志编码** → 处理质量标志和缺测值
5. **对齐验证** → 验证对齐结果的正确性

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 温度单位 | K | [1] | ERA5标准单位 |
| 湿度单位 | kg/kg | [1] | 比湿标准单位 |
| 气压单位 | Pa | [1] | 帕斯卡标准单位 |
| 风场单位 | m/s | [1] | 米每秒标准单位 |
| 空间分辨率 | 0.25° | [2] | ERA5标准分辨率 |
| 时间分辨率 | 小时 | [2] | ERA5逐小时数据 |
| 缺测值标记 | _FillValue/NaN | [3] | NetCDF标准缺测标记 |

## 边界与分流
- 当数据维度名称不一致时（如lat/latitude），需要进行维度重命名
- 当坐标精度不一致时，需要进行插值或重采样
- 当单位不一致时，需要进行单位转换
- 当缺测值处理失败时，记录失败原因并标记相关数据为无效

## 质量检查
- 验证对齐后各变量的shape、dims、units和time坐标是否一致
- 检查对齐记录中每个变量的shape、dims、units和time坐标是否一致
- 确认对齐后数据的物理范围是否合理

## 回退策略
- 当对齐失败时，记录失败原因并标记相关交付项为PARTIAL
- 当单位转换失败时，保留原始单位并在元数据中说明

## 资源召回建议
- 当任务需要将多个气象要素数据进行时空对齐时召回本卡片
- 配套使用ERA5数据源核验流程卡片
- 配套使用气象产品质控规范卡片

## 证据来源
[1] Evaluation of spatial-temporal variation performance of ERA5 precipitation data in China, Chen et al., Scientific Reports, 2021, DOI: 10.1038/s41598-021-84674-6
[2] Comparison of Reanalysis and Observational Precipitation Datasets Including ERA5, Sun et al., Atmosphere, 2021, DOI: 10.3390/atmos12091167
[3] ERA5-Land: a state-of-the-art global reanalysis dataset for land applications, Muñoz-Sabater et al., Earth System Science Data, 2021, DOI: 10.5194/essd-13-2097-2021