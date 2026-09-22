# 气象预报任务输入数据契约规范

## 适用范围
适用于所有earth域气象预报任务的输入数据预检，包括短期（24-72小时）、中期（3-15天）和季节性预报。覆盖数据来源验证、资料截止时间检查、数据时点规则执行和数据血缘追溯。

## 输入
- 数据来源：ERA5再分析数据、站点观测数据、其他再分析产品
- 数据格式：NetCDF、GRIB、CSV等标准气象数据格式
- 变量：温度、湿度、风速、气压等气象要素
- 时间范围：目标预报时段的历史观测数据

## 输出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告
- 数据血缘追溯记录

## 流程节点
1. 数据来源识别 → 2. 版本与覆盖范围验证 → 3. 资料截止时间检查 → 4. 数据时点规则执行 → 5. 血缘追溯记录

每步含：操作、参数、工具、质量门禁

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 资料截止时间 | 观测签发时点 | [论文1] | 观测数据可被预报系统使用的最早时间 |
| 数据时点规则 | 目标时刻之前 | [论文2] | 目标时刻之后形成的真实观测不得进入输入 |
| 血缘追溯 | 完整记录 | [论文3] | 每项输入需记录来源、版本、获取时间 |

## 边界与分流
- 数据来源不可用时：BLOCKED，不得使用模拟数据降级
- 资料截止时间不明确时：BLOCKED，需向数据提供方确认
- 数据时点规则违反时：BLOCKED，需重新获取合规数据

## 质量检查
- 验证每项必填输入的来源URL/路径、版本号、时间覆盖范围、变量清单和质量标志
- 检查数据时点是否早于资料截止时间
- 确认数据血缘追溯记录完整

## 回退策略
- 数据来源不可用：等待数据更新或寻找替代数据源
- 资料截止时间不明确：联系数据提供方获取签发时间
- 数据时点规则违反：重新获取合规时间范围内的数据

## 资源召回建议
当执行气象预报任务的数据预检步骤时召回本卡片，配套资源包括数据源配置、时间范围定义工具和血缘追溯模板。

## 证据来源
[1] Discussion on Quality Control Method of Environmental Meteorological Data, Hua Yang, International Journal of Energy, 2024, DOI: 10.54097/k8djwf68
[2] A Meteorological Data Quality Control Framework for Tea Plantations Using Association Rules Mined from ERA5 Reanalysis Data, Zhongqiu Zhang et al., Agriculture, 2026, DOI: 10.3390/agriculture16020226
[3] Challenging problems of quality assurance and quality control (QA/QC) of meteorological time series data, B. Faybishenko et al., Stochastic Environmental Research and Risk Assessment, 2021, DOI: 10.1007/s00477-021-02106-w