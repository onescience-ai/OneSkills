# 气象时序预报模型性能评估

## 适用范围
适用于earth域所有预报任务（温度、湿度、风速、降水等）的性能评估，涵盖确定性预报和概率预报评估。

## 输入
- 预报结果（预测值序列）
- 参考真值（ERA5或独立观测）
- 基线预报（持续性预报或气候态）

## 输出
- 性能评估报告（含各指标值）
- 负R2诊断结果
- 性能门禁检查结果

## 流程节点

### 1. 确定性指标计算
- 操作：计算RMSE、MAE、R2、ACC
- 参数：纬度加权、气候态基准
- 质量门禁：R2<0 → 自动REJECT

### 2. 概率指标计算（如适用）
- 操作：计算CRPS、Spread-Skill Ratio
- 参数：集合成员数、置信水平
- 质量门禁：SSR远离1.0 → 校准问题

### 3. Skill Score计算
- 操作：与持续性预报基线比较
- 参数：基线选择（持续性或气候态）
- 质量门禁：Skill Score<0 → 低于基线

### 4. 负R2诊断
- 操作：分析负R2原因
- 参数：过拟合检查、特征工程检查
- 质量门禁：识别根本原因

## 关键参数

| 参数 | 合理范围 | 来源 | 说明 |
|------|----------|------|------|
| R2 | >0（基本），>0.5（良好） | [1] | R2<0不如均值预测 |
| Skill Score | >0 | [1] | >0优于持续性基线 |
| ACC | >0.6（短期），>0.5（中期） | [1] | 异常相关系数 |
| CRPS | 越低越好 | [2] | 概率预报技巧 |
| SSR | ≈1.0 | [2] | 完美校准为1.0 |
| 温度RMSE | <3°C(短期)，<5°C(中期) | [1] | 地面2m温度 |
| 风速RMSE | <2m/s(短期)，<3m/s(中期) | [1] | 10m风速 |

## 边界与分流
- R2<0 → 检查过拟合、数据质量、特征工程
- Skill Score<0 → 模型不如持续性预报，需诊断
- SSR<0.8 → 集合过自信，需增加扰动
- SSR>1.2 → 集合欠自信，需减少扰动

## 质量检查
- 验证R2和Skill Score符号
- 检查各指标是否在合理范围
- 确认负值已诊断原因

## 回退策略
- R2为负时：检查数据归一化→调整模型复杂度→更换架构
- Skill Score为负时：检查基线选择→调整模型配置

## 资源召回建议
- 需召回：climate-forecast-acceptance-criteria-scenario（验收门限）
- 配套任务：climate-forecast-model-validation

## 证据来源
[1] Bi K, Xie L, Zhang H, et al. Accurate medium-range global weather forecasting with 3D neural networks. Nature, 2023, 619: 533-538. DOI: 10.1038/s41586-023-06185-3
[2] Price I, Sanchez-Gonzalez A, Alet F, et al. Probabilistic weather forecasting with machine learning. Nature, 2025, 637: 84-90. DOI: 10.1038/s41586-024-08252-9
