# 气象预报产品质量标志编码规范

## 适用范围
适用于earth域预报产品的质量标志编码，覆盖观测质量、插值质量和预报质量。支持WMO标准和业务系统标准的质量标志编码体系。

## 输入
- 预报结果数据
- 质量评估指标（RMSE、R2、Skill Score等）
- 不确定性估计（置信区间、预测区间）
- 产品元数据（坐标系统、时间基准、单位）

## 输出
- 质量标志文件（quality_flags.csv）
- 产品元数据文件（forecast_metadata.json）
- 质量标志分布统计
- 不确定性信息

## 流程节点
1. 质量标志等级定义 → 2. 编码体系选择 → 3. 质量标志生成 → 4. 不确定性关联 → 5. 元数据生成

每步含：操作、参数、工具、质量门禁

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 质量标志等级 | good/fair/poor | [论文1] | 三等级分类 |
| good阈值 | RMSE<1σ | [论文2] | 低于标准差1倍 |
| fair阈值 | 1σ≤RMSE<2σ | [论文2] | 1-2倍标准差 |
| poor阈值 | RMSE≥2σ | [论文2] | 高于2倍标准差 |
| 时间基准 | UTC | [论文3] | 所有时间戳统一为UTC |
| 坐标系统 | WGS84 | [论文3] | 空间坐标统一 |

## 边界与分流
- 质量标志分布不合理时：检查阈值设置是否合理
- 不确定性信息缺失时：标记为低质量或使用默认不确定性
- 元数据不完整时：补充缺失字段或标记为不完整

## 质量检查
- 验证质量标志编码符合标准
- 检查质量标志分布合理性
- 确认产品元数据完整

## 回退策略
- 编码体系不兼容：转换为标准编码体系
- 质量标志分布异常：调整阈值或重新评估
- 元数据缺失：补充缺失字段或使用默认值

## 资源召回建议
当执行气象预报产品质量标志生成时召回本卡片，配套资源包括编码转换工具、元数据生成模板和质量检查脚本。

## 证据来源
[1] Discussion on Quality Control Method of Environmental Meteorological Data, Hua Yang, International Journal of Energy, 2024, DOI: 10.54097/k8djwf68
[2] A Meteorological Data Quality Control Framework for Tea Plantations Using Association Rules Mined from ERA5 Reanalysis Data, Zhongqiu Zhang et al., Agriculture, 2026, DOI: 10.3390/agriculture16020226
[3] Data Quality Control and Calibration for Mini-Radiosonde System "Storm Tracker" in Taiwan, Hung-Chi KUO et al., Journal of the Meteorological Society of Japan, 2025, DOI: 10.2151/jmsj.2025-029