# 静止气象卫星源观测资料验证

## 适用范围
面向静止气象卫星驱动的对流初生（CI）检测任务，在执行CI检测前必须验证源观测资料的真实性、完整性和可追溯性。适用于FY-4A/AGRI、Himawari-8/AHI、GOES-R/ABI等静止卫星数据源。不适用于已确认数据可用的常规业务流程。

## 输入
- 卫星数据源标识（FY-4A/AGRI、Himawari-8/AHI等）
- 目标区域和时段
- 目标诊断量（亮温、反射率、云顶温度等）
- 数据截止时间要求

## 输出
- 数据验证报告：包含数据源、时间覆盖、空间覆盖、通道完整性、质量标志状态
- 验证通过/失败决策及阻塞原因说明

## 流程节点
1. **数据源识别** → 确认卫星型号、传感器载荷、数据级别（L1/L2/L3）
2. **格式验证** → 检查文件格式（NetCDF4/HDF5/GRIB）、元数据完整性
3. **时间覆盖验证** → 确认数据时间范围满足任务需求，时间分辨率符合要求
4. **空间覆盖验证** → 确认目标区域在数据覆盖范围内
5. **通道完整性验证** → 确认所需光谱通道数据完整
6. **质量标志检查** → 读取质量标志字段，排除无效/可疑数据
7. **验证报告生成** → 输出验证结果和决策

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| FY-4A/AGRI时间分辨率 | 15分钟 | [1] | 全圆盘观测间隔 |
| FY-4A/AGRI空间分辨率 | 4km（红外）/ 1km（可见光） | [1] | 不同通道分辨率不同 |
| Himawari-8/AHI时间分辨率 | 10分钟（全圆盘）/ 2.5分钟（日本区域） | [4] | 快速扫描模式 |
| 数据格式 | NetCDF4/HDF5 | [3] | 标准气象数据格式 |
| 光谱通道数 | AGRI: 14通道 / AHI: 16通道 | [1][4] | 多光谱观测 |
| 云顶温度（CTT）范围 | 200K-320K | [2] | 对流云顶典型范围 |

## 边界与分流
- **数据缺失**：若源观测资料不存在或不可读，必须标记BLOCKED并请求用户提供，不得自行生成模拟数据
- **格式不匹配**：若数据格式不符合预期，需确认数据级别或进行格式转换
- **时间不覆盖**：若数据时间范围不满足任务需求，需扩展检索或请求补充数据
- **质量标志异常**：若质量标志显示大量无效数据，需评估是否可用或请求替代数据源

## 质量检查
- 验证报告必须包含：数据源标识、时间范围、空间范围、通道完整性、质量标志统计
- 若任一验证项失败，必须输出明确的阻塞原因
- 验证结果必须可追溯到具体的数据文件和时间戳

## 回退策略
- 数据不可用时：标记BLOCKED，请求用户提供真实数据
- 格式不兼容时：尝试使用标准气象库（如xarray、netCDF4）解析
- 质量标志缺失时：记录为不确定性来源，降级处理

## 资源召回建议
- 当任务涉及卫星数据输入时召回本卡片
- 配套资源：climate-satellite-ci-source-data-validation（本卡）、climate-ci-threshold-selection

## 证据来源
[1] Radiometric Performance Evaluation of FY-4A/AGRI Based on Aqua/MODIS, Sensors, 2021, DOI: 10.3390/s21072472
[2] Validation of FY-4A AGRI layer precipitable water products using radiosonde data, Atmospheric Research, 2021, DOI: 10.1016/j.atmosres.2021.105832
[3] CACM-Net: Daytime Cloud Mask for AGRI Onboard the FY-4A Satellite, Remote Sensing, 2024, DOI: 10.3390/rs16142660
[4] Retrieval of cloud fraction using machine learning algorithms based on FY-4A AGRI, Atmospheric Measurement Techniques, 2024, DOI: 10.5194/amt-17-1-2024
[5] Impact of assimilating atmospheric motion vectors from Himawari-8, Atmospheric Research, 2023, DOI: 10.1016/j.atmosres.2022.106550
