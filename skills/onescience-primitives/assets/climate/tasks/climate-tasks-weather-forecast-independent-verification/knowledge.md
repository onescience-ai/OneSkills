# 气象预报独立验证规范

## 适用范围
适用于earth域气象预报任务的独立验证，确保验证结果可信。区分测试集（用于模型选择）和独立验证资料（用于性能验收）。

## 输入
- 独立验证资料（ERA5再分析数据、独立站点观测、历史回放数据）
- 预报结果数据
- 验证指标配置（RMSE、R2、Skill Score等）
- 同协议要求（变量、网格、指标协议与训练数据一致）

## 输出
- 独立验证报告
- 独立性确认记录
- 性能验收判定
- 适用范围说明

## 流程节点
1. 独立验证资料获取 → 2. 独立性确认 → 3. 同协议验证 → 4. 性能指标计算 → 5. 验收判定

每步含：操作、参数、工具、质量门禁

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 独立性要求 | 未参与训练/调参/阈值选择 | [论文1] | 验证资料必须独立于训练过程 |
| 时间覆盖 | 覆盖预报时效 | [论文2] | 验证资料时间范围必须覆盖预报时段 |
| 空间覆盖 | 覆盖目标站点 | [论文2] | 验证资料空间范围必须覆盖目标站点 |
| 同协议要求 | 变量/网格/指标一致 | [论文3] | 验证资料与训练资料采用相同协议 |

## 边界与分流
- 独立验证资料不可用时：BLOCKED，不得使用测试集替代
- 独立性确认失败时：BLOCKED，需重新获取独立验证资料
- 同协议不满足时：调整协议或寻找替代验证资料

## 质量检查
- 验证独立验证资料来源
- 确认独立性记录
- 检查同协议要求满足

## 回退策略
- 独立验证资料不可用：等待数据更新或寻找替代数据源
- 独立性确认失败：重新获取独立验证资料
- 同协议不满足：调整协议或使用替代验证方法

## 资源召回建议
当执行气象预报独立验证时召回本卡片，配套资源包括独立验证资料获取工具、独立性检查脚本和同协议验证模板。

## 证据来源
[1] Exploring the Use of Public Weather Station Data for Operational Weather Forecast Verification, Christopher James Steele et al., Meteorological Applications, 2025, DOI: 10.1002/met.70086
[2] Seasonal Forecast Skill of ENSO Teleconnection Maps, Nathan J. L. Lenssen et al., Weather and Forecasting, 2020, DOI: 10.1175/waf-d-19-0235.1
[3] Verification of the NOAA Space Weather Prediction Center Solar Flare Forecast (1998–2024), Enrico Camporeale et al., Space Weather, 2025, DOI: 10.1029/2025sw004546