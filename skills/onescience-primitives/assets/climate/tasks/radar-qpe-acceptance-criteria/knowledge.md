# 雷达QPE产品验收标准与门限管理

## 适用范围

雷达定量降水估计（QPE）产品在业务部署前的性能验收。本卡描述验收标准体系的构建方法、指标门限值的确定原则、预登记门限的管理规范及验收判定流程，适用于水文预报、城市内涝预警、气象业务等应用场景的QPE产品验收。

## 输入

- QPE验证指标计算结果（RMSE、相关系数、偏差、POD、FAR、CSI等）
- 预登记验收门限（在任务执行前确认的性能阈值）
- 应用场景需求文档（确定门限值的依据）

## 输出

- 验收判定报告：PASS/REJECT/PARTIAL
- 指标对比表：实测值 vs 门限值
- 验收结论与限制说明

## 流程节点

1. **门限预登记** → 在s01阶段向场景确认验收门限参数，记录到task_state.json [报告issue4]
2. **指标计算** → 在s06阶段计算所有验收指标
3. **门限比对** → 将实测指标与预登记门限逐项对比
4. **综合判定** → 所有核心指标达标→PASS；任一核心指标不达标→REJECT；部分指标缺失→PARTIAL
5. **报告生成** → 输出验收报告，包含指标表、门限表和判定理由

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 时间采样要求 | ≥5 min间隔 | [1] | 2026年研究建议的最低时间采样率 |
| 质量指数（QI） | 0-1连续值 | [2] | 用于雷达降水合成的质量评估 |
| 产品空间分辨率 | ~1 km²网格 | [3] | 荷兰QPE产品的标准分辨率 |
| 产品时间分辨率 | 5 min累积 | [3] | 荷兰QPE产品的标准时间分辨率 |
| 质量控制等级 | QC1-QC4 | [5] | RADVOL-QC系统的质量控制分级 |

## 边界与分流

- 若任务prompt中未提供验收门限，必须在s01阶段主动向场景请求确认，不得跳过直接进入执行 [报告issue4]。
- 若门限信息在执行前未确认，最终quality_flags应标记为PARTIAL而非PASS。
- 门限值需根据应用场景调整：水文预报可能更关注RMSE，城市内涝预警可能更关注强降水检测率。

## 质量检查

- execution-manifest.json必须包含pre_registered_thresholds字段。
- quality_flags的validation_quality必须基于预登记门限给出明确判定（PASS/REJECT/PARTIAL）。
- 未达到预先登记门限时不得判定性能通过。

## 回退策略

- 若门限确实无法获取，应在报告中明确说明"未提供预确认验收门限，不声明性能PASS"，并建议用户补充门限后重新判定。

## 资源召回建议

当任务涉及雷达QPE产品验收且缺少预登记门限时，应召回本卡片。配套资源：radar-qpe-heavy-rain-verification（强降水专项检验）、radar-qpe-calibration-validation-separation（验证样本独立性）。

## 证据来源

[1] Required Time Steps for Weather Radar Quantitative Precipitation Estimation, J. Hydrometeorol., 2026, DOI: 10.1175/jhm-d-25-0151.1
[2] Quality-based compositing of weather radar derived precipitation, Meteorol. Appl., 2019, DOI: 10.1002/met.1812
[3] The Dutch real-time gauge-adjusted radar precipitation product, Earth Syst. Sci. Data, 2025, DOI: 10.5194/essd-17-4715-2025
[4] Comparison between precipitation estimates of ground-based weather radar composites and GPM's DPR radar, Meteorol. Zeitschr., 2020, DOI: 10.1127/metz/2020/1039
[5] Improvement in algorithms for quality control of weather radar data (RADVOL-QC system), Atmos. Meas. Tech., 2022, DOI: 10.5194/amt-15-261-2022
