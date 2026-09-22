# 气象时序预报模型性能评估标准

## 适用范围
适用于earth域气象预报任务的模型性能评估，覆盖短期（24-72小时）、中期（3-15天）预报。提供R2、Skill Score、RMSE等指标的合理范围和诊断方法。

## 输入
- 模型预测结果
- 实际观测数据
- 基线模型预测结果（如持续性预报、气候平均值）
- 性能评估指标配置

## 输出
- 性能评估报告（包含R2、Skill Score、RMSE、MAE等指标）
- 负R2诊断报告
- 性能门禁检查结果
- 改进建议

## 流程节点
1. 指标计算 → 2. 性能门禁检查 → 3. 负R2诊断 → 4. 模型选择决策 → 5. 回退策略执行

每步含：操作、参数、工具、质量门禁

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| R2基本要求 | >0 | [论文1] | 低于0表示模型不如均值预测 |
| Skill Score基本要求 | >0 | [论文2] | 低于0表示模型不如基线预报 |
| 温度RMSE合理范围 | <3°C（短期）<5°C（中期） | [论文3] | 根据预报时效调整 |
| 湿度RMSE合理范围 | <15% | [论文3] | 相对湿度均方根误差 |
| 风速RMSE合理范围 | <2m/s | [论文3] | 风速均方根误差 |

## 边界与分流
- R2<0时：标记为REJECT，触发模型回退或参数调整
- Skill Score<0时：检查基线模型选择是否合理
- RMSE超限时：检查数据质量、模型配置或特征工程
- 性能门禁失败时：执行诊断并返回改进方案

## 质量检查
- 验证性能门禁检查结果
- 检查负R2诊断报告
- 确认改进建议可执行

## 回退策略
- R2<0：回退到更简单的模型（如线性回归、ARIMA）或调整超参数
- Skill Score<0：更换基线模型或调整评估方法
- RMSE超限：检查数据质量、增加训练数据或调整模型复杂度

## 资源召回建议
当执行气象预报模型性能评估时召回本卡片，配套资源包括指标计算工具、门禁检查脚本和诊断分析模板。

## 证据来源
[1] A method to improve binary forecast skill verification, Thitithep Sitthiyot et al., MethodsX, 2024, DOI: 10.1016/j.mex.2024.103010
[2] How to Derive Skill from the Fractions Skill Score, Bobby Antonio et al., Monthly Weather Review, 2025, DOI: 10.1175/mwr-d-24-0120.1
[3] The fractions skill score for ensemble forecast verification, Tobias Necker et al., Quarterly Journal of the Royal Meteorological Society, 2024, DOI: 10.1002/qj.4824