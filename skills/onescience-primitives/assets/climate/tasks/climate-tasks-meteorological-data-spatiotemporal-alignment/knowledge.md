# 气象数据时空对齐标准化流程规范

## 适用范围
适用于earth域多站点时序预报任务的气象数据预处理，包括时间轴UTC对齐、空间坐标统一、单位标准化、质量标志编码和缺测处理。覆盖站点数据与格点数据的对齐差异。

## 输入
- 多站点历史温湿风数据
- 站点位置信息（经纬度、海拔）
- 时间特征（观测时间戳、时区信息）
- 质量标志（观测质量、插值标记、异常标记）

## 输出
- 对齐后的标准输入数据
- 掩膜与样本索引
- 预处理转换记录
- 时空对齐检查报告

## 流程节点
1. 时间轴统一（UTC对齐、时区转换） → 2. 空间坐标统一（WGS84投影） → 3. 单位标准化（气象标准单位） → 4. 质量标志关联 → 5. 缺测处理策略配置 → 6. 信息泄漏检查

每步含：操作、参数、工具、质量门禁

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 时间基准 | UTC | [论文1] | 唯一时间基准，所有时间戳统一为UTC |
| 坐标系统 | WGS84 | [论文2] | 空间坐标统一为WGS84投影 |
| 温度单位 | °C | [论文3] | 气象标准温度单位 |
| 湿度单位 | %RH | [论文3] | 气象标准相对湿度单位 |
| 风速单位 | m/s | [论文3] | 气象标准风速单位 |
| 缺测处理 | 前后插值/标记但不插值 | [论文1] | 根据缺测类型选择处理策略 |

## 边界与分流
- 时区信息缺失时：默认使用UTC，但需在元数据中标注
- 坐标系统不一致时：转换为WGS84，记录转换参数
- 单位不标准时：执行单位转换，记录转换公式
- 缺测率过高时（>30%）：标记数据质量低，考虑降级使用

## 质量检查
- 验证时间轴为UTC、坐标为WGS84、单位符合气象标准
- 检查信息泄漏检查结果
- 确认预处理转换记录完整

## 回退策略
- 时间轴对齐失败：检查原始数据时间戳格式，尝试时间解析修复
- 坐标系统转换失败：记录转换失败原因，标记数据为不可用
- 单位转换失败：记录转换失败原因，标记变量为不可用

## 资源召回建议
当执行气象数据预处理步骤时召回本卡片，配套资源包括时间解析工具、坐标转换工具和单位转换工具。

## 证据来源
[1] Quality control and gap‐filling methods applied to hourly temperature observations over central Italy, Paolina B. Cerlini et al., Meteorological Applications, 2020, DOI: 10.1002/met.1913
[2] Challenging problems of quality assurance and quality control (QA/QC) of meteorological time series data, B. Faybishenko et al., Stochastic Environmental Research and Risk Assessment, 2021, DOI: 10.1007/s00477-021-02106-w
[3] On the Importance of Data Quality Assessment of Crowdsourced Meteorological Data, Milena Vuckovic et al., Sustainability, 2023, DOI: 10.3390/su15086941