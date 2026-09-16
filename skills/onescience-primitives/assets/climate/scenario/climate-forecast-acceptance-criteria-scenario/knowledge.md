# 气象预报验收门限规范

## 适用范围
适用于earth域所有气象预报任务（温度、湿度、风速、降水等）的交付验收判定。包括短期预报（0-72h）、中期预报（3-10天）和延伸期预报（10-30天）。

## 输入
- 预报结果文件（含各变量的预测值）
- 参考真值（ERA5再分析数据或独立观测）
- 任务定义文件（明确预报变量、时效、站点范围）

## 输出
- 验收门限清单（经场景确认）
- 性能门禁检查结果（PASS/REJECT）
- 分层验收报告（按时效、变量、站点）

## 流程节点

### 1. 验收门限制定
- 操作：根据任务类型和变量特性制定门限
- 参数：RMSE、MAE、R2、Skill Score
- 质量门禁：门限需经场景确认，未确认前不得声明PASS

### 2. 性能门禁检查
- 操作：逐项检查各指标是否达到门限
- 质量门禁：R2<0自动REJECT，Skill Score<0表示低于基线

### 3. 分层验收
- 操作：按时效（24h/48h/72h）、变量（温度/湿度/风速）、站点分别验收
- 质量门禁：任一层未通过则整体标记PARTIAL

## 关键参数

| 参数 | 短期(0-72h) | 中期(3-10天) | 来源 | 说明 |
|------|-------------|--------------|------|------|
| 温度RMSE | <3°C | <5°C | [1] | 地面2m温度 |
| 湿度RMSE | <15% | <20% | [1] | 相对湿度 |
| 风速RMSE | <2m/s | <3m/s | [1] | 10m风速 |
| R2最低要求 | >0 | >0 | [2] | R2<0表示不如均值预测 |
| Skill Score | >0 | >0 | [2] | >0表示优于持续性基线 |
| ACC | >0.6 | >0.5 | [1] | 异常相关系数 |

## 边界与分流
- R2<0 → 自动REJECT，触发模型回退或参数调整
- Skill Score<0 → 标记低于基线，需诊断原因
- 门限未确认 → 所有交付项标记BLOCKED

## 质量检查
- 验证门限是否经场景确认
- 检查R2和Skill Score符号
- 确认分层验收覆盖所有维度

## 回退策略
- 性能不达标时：检查数据质量→调整模型参数→更换模型架构
- 门限不合理时：与场景协商调整门限

## 资源召回建议
- 需召回：climate-forecast-data-validation-workflow（数据验证流程）
- 需召回：climate-forecast-performance-evaluation（性能评估任务）

## 证据来源
[1] Bi K, Xie L, Zhang H, et al. Accurate medium-range global weather forecasting with 3D neural networks. Nature, 2023, 619: 533-538. DOI: 10.1038/s41586-023-06185-3
[2] Price I, Sanchez-Gonzalez A, Alet F, et al. Probabilistic weather forecasting with machine learning. Nature, 2025, 637: 84-90. DOI: 10.1038/s41586-024-08252-9
[3] Ravuri S, Lenc K, Willson M, et al. Skilful precipitation nowcasting using deep generative models of radar. Nature, 2021, 597: 672-677. DOI: 10.1038/s41586-021-03854-z
