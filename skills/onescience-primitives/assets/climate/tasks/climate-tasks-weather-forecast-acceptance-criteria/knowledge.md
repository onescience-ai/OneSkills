# 气象预报任务验收门限规范

## 适用范围
适用于earth域气象预报任务的验收标准，覆盖业务预报和研究预报的不同门限要求。支持按时效、站点、变量分别设定门限。

## 输入
- 模型预测结果
- 实际观测数据
- 验收门限配置（按时效、变量、站点分层）
- 业务预报或研究预报类型标识

## 输出
- 验收门限清单（经场景确认）
- 性能门禁检查结果
- 验收判定报告（PASS/BLOCKED/REJECT）

## 流程节点
1. 验收门限确认 → 2. 性能指标计算 → 3. 门禁检查 → 4. 验收判定 → 5. 交付状态更新

每步含：操作、参数、工具、质量门禁

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 温度RMSE（短期） | <3°C | [论文1] | 24-72小时预报 |
| 温度RMSE（中期） | <5°C | [论文1] | 3-15天预报 |
| 湿度RMSE | <15% | [论文2] | 相对湿度均方根误差 |
| 风速RMSE | <2m/s | [论文2] | 风速均方根误差 |
| R2基本要求 | >0 | [论文3] | 低于0表示模型不如均值预测 |
| R2良好要求 | >0.5 | [论文3] | 表示模型解释力较好 |
| Skill Score基本要求 | >0 | [论文3] | 低于0表示模型不如基线预报 |

## 边界与分流
- 验收门限未确认时：标记为BLOCKED，不得声明性能PASS
- 性能指标超限时：标记为REJECT，触发模型回退或参数调整
- 门限冲突时：以更严格的门限为准

## 质量检查
- 验证验收门限清单是否经场景确认
- 检查性能门禁检查结果
- 确认验收判定报告完整

## 回退策略
- 门限未确认：向场景确认门限后重新执行验收
- 性能不达标：执行诊断并返回改进方案
- 门限冲突：协商确定最终门限

## 资源召回建议
当执行气象预报任务验收时召回本卡片，配套资源包括门限配置模板、验收检查工具和判定报告生成器。

## 证据来源
[1] Verification of medium range weather forecast for the Kandi region of Punjab, NAVNEET KAUR et al., MAUSAM, 2021, DOI: 10.54302/mausam.v70i4.274
[2] DISTRICT LEVEL WEATHER FORECAST VERIFICATION IN CHHATTISGARH, M. RAJAVEL et al., MAUSAM, 2021, DOI: 10.54302/mausam.v70i4.281
[3] Exploring the Use of Public Weather Station Data for Operational Weather Forecast Verification, Christopher James Steele et al., Meteorological Applications, 2025, DOI: 10.1002/met.70086