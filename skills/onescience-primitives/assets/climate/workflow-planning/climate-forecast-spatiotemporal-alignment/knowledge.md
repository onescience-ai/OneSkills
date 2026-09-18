# 气象预报任务数据时空对齐规范

## 适用范围
适用于多源气象数据在进入预报模型前的标准化预处理环节。覆盖多站点温湿风联合预报、网格化数值预报、统计降尺度预报等场景。当任务涉及来自不同站点、不同时区、不同坐标系统或不同单位体系的气象数据时，本卡片提供时空维度上的对齐标准和处理流程。

## 输入
- 多源气象数据（站点观测、再分析产品、卫星反演）
- 站点元信息（经纬度、海拔、时区）
- 数据质量标志

## 输出
- 对齐后的标准输入数据（统一时间轴、坐标系、单位）
- 掩膜与样本索引
- 预处理转换记录（处理方法、参数、影响范围）

## 流程节点
1. **时间轴UTC对齐** → 将所有输入数据统一转换为UTC时间基准，消除时区差异
2. **空间坐标统一** → 将站点经纬度统一为WGS84坐标系，验证空间覆盖
3. **单位标准化** → 将气象变量转换为标准单位（温度°C、湿度%RH、风速m/s）
4. **质量标志关联** → 为每条数据关联质量标志编码，记录数据来源质量
5. **缺测处理** → 根据缺测比例和分布选择处理策略（前后插值、空间插值、标记不插值）
6. **信息泄漏检查** → 验证训练数据中未包含目标时刻之后的信息

每步含：操作、参数、工具、质量门禁

## 关键参数
### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 时间基准 | UTC | [CIMO Guide, WMO-No. 8] | 唯一允许的时间基准 |
| 坐标系统 | WGS84 | [CIMO Guide, WMO-No. 8] | 所有站点坐标统一到此坐标系 |
| 温度单位 | °C | [MERRA-2, 2017] | 标准气象温度单位 |
| 湿度单位 | %RH | [MERRA-2, 2017] | 相对湿度百分比 |
| 风速单位 | m/s | [MERRA-2, 2017] | 10m高度风速 |
| 缺测阈值 | <20%时插值 | [CRU TS, 2020] | 缺测比例超过20%的变量标记而不插值 |

### 校准数值
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 异常值检测 | 3σ原则 | [MERRA-2, 2017] | 以下数值来自ERA5/MERRA-2体系，供量级校准；其他体系需以自身证据重新锚定 |
| 插值方法 | 线性插值 | [CRU TS, 2020] | 一维时间序列缺测处理 |
| 标准化方法 | StandardScaler | [FLUXNET, 2020] | 训练集拟合，验证/测试集复用 |

## 边界与分流
- 当时间轴无法统一为UTC时：报告时区转换错误，BLOCKED
- 当坐标系统不一致时：执行坐标转换并记录转换参数
- 当缺测比例超过阈值时：标记该变量不可用，建议补充数据
- 当信息泄漏检查失败时：BLOCKED，重新划分数据集

## 质量检查
- 输出数据时间轴必须为UTC
- 输出坐标必须为WGS84
- 单位必须符合气象标准
- 必须生成预处理转换记录
- 信息泄漏检查必须通过

## 回退策略
- 时间对齐失败时：检查原始数据时间戳格式，修复转换逻辑
- 坐标转换失败时：验证源坐标系定义，使用标准转换库
- 缺测处理不当时：调整插值策略或标记为不可用

## 资源召回建议
- 当任务涉及气象数据预处理和标准化时召回本卡片
- 配套资源：climate-forecast-input-data-contract（输入契约）、climate-forecast-acceptance-quality（验收标准）

## 补充证据
[D1] WMO Guide to Meteorological Instruments and Methods of Observation (CIMO Guide), WMO-No. 8, WMO（accessed_at 2026-09-18，交叉验证）

## 证据来源
[1] The Modern-Era Retrospective Analysis for Research and Applications, Version 2 (MERRA-2), Gelaro et al., Journal of Climate, 2017, DOI: 10.1175/jcli-d-16-0758.1
[2] Climatologies at high resolution for the earth's land surface areas, Karger et al., Scientific Data, 2017, DOI: 10.1038/sdata.2017.122
[3] The FLUXNET2015 dataset and the ONEFlux processing pipeline for eddy covariance data, Pastorello et al., Scientific Data, 2020, DOI: 10.1038/s41597-020-0534-3