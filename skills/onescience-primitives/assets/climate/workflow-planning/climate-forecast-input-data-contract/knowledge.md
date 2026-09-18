# 气象预报输入数据契约规范

## 适用范围
适用于所有气象预报任务（earth域），包括温度、湿度、风速等多变量联合时序预报。当任务涉及使用ERA5再分析数据、站点观测数据或其他气象数据源时，必须遵循本规范。

## 输入
- 数据来源：ERA5再分析数据、站点观测数据、再分析产品
- 数据类型：时间序列数据、空间网格数据
- 数据格式：CSV、NetCDF、GRIB等标准气象数据格式

## 输出
- 输入数据与版本清单：每项必填输入的来源URL/路径、版本号、时间覆盖范围、变量清单和质量标志
- 输入完整性预检报告：数据源验证结果、时空覆盖检查、变量单位检查
- 任务范围和资料截止时间表：明确各数据源的资料截止时间

## 流程节点
1. 数据源识别 → 2. 数据版本验证 → 3. 时空覆盖检查 → 4. 变量单位检查 → 5. 质量标志验证 → 6. 资料截止时间验证 → 7. 数据血缘追溯

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 数据源版本 | 最新稳定版本 | [论文38] | 确保数据一致性 |
| 时间覆盖 | 任务所需时间范围 | [论文33] | 包含训练期和验证期 |
| 空间覆盖 | 目标站点位置 | [论文33] | 确保站点在数据覆盖范围内 |
| 变量清单 | 温度、湿度、风速等 | [论文39] | 符合气象标准单位 |
| 质量标志 | WMO标准编码 | [论文38] | 标记数据质量等级 |

## 边界与分流
- 当数据源不可用时，必须BLOCKED，不得使用模拟数据降级
- 当资料截止时间违反时，必须BLOCKED，不得使用未来数据
- 当数据版本不一致时，必须BLOCKED，不得混合不同版本数据

## 质量检查
- 验证每条输入数据的观测时间是否早于资料截止时间
- 验证数据源版本是否与任务要求一致
- 验证变量单位是否符合气象标准（温度°C、湿度%RH、风速m/s）

## 回退策略
- 数据源不可用时：寻找替代数据源或BLOCKED任务
- 资料截止时间违反时：调整任务时间范围或BLOCKED任务
- 数据质量不足时：执行质量控制或BLOCKED任务

## 资源召回建议
当任务涉及以下情况时应召回本卡片：
- 使用ERA5、站点观测等气象数据源
- 需要验证数据可用性和质量
- 需要确保数据时点规则合规
- 需要生成数据血缘追溯记录

## 证据来源
[1] Quality control and gap-filling methods applied to hourly temperature observations over central Italy, Bongioannini Cerlini et al., Meteorological Applications, 2020, DOI: 10.1002/met.1913
[2] Programme for Monitoring of the Greenland Ice Sheet (PROMICE) automatic weather station data, Fausto et al., Earth system science data, 2021, DOI: 10.5194/essd-13-3819-2021
[3] The CMIP6 Data Request (DREQ, version 01.00.31), Juckes et al., Geoscientific model development, 2020, DOI: 10.5194/gmd-13-201-2020