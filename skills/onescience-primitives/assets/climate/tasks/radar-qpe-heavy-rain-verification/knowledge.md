# 雷达QPE强降水检验方法

## 适用范围

雷达定量降水估计（QPE）任务中对强降水事件估计能力的专项检验。本卡描述强降水事件的阈值定义、检验指标体系、样本量要求和计算方法，适用于需要评估QPE方法在强降水场景下性能的业务验收与研究对比场景。

## 输入

- QPE估算降水场与雨量计实测降水的配对数据
- 强降水阈值定义（根据业务需求和地区气候特征确定）
- 足够数量的强降水事件样本

## 输出

- 强降水检验指标表：检测率（POD）、虚警率（FAR）、临界成功指数（CSI）、命中数、虚警数、漏报数
- 样本量报告：强降水事件总数、时间分布、空间分布
- 验收判定：基于预登记门限的PASS/REJECT判定

## 流程节点

1. **阈值确定** → 根据业务需求选择强降水阈值（如≥10 mm/h、≥25 mm/h）[1]
2. **样本筛选** → 从QPE和雨量计数据中按阈值筛选强降水事件
3. **列联表构建** → 统计命中（Hits）、虚警（False Alarms）、漏报（Misses）
4. **指标计算** → 计算POD、FAR、CSI等指标
5. **样本量检查** → 确认强降水样本数≥最低要求（通常≥5-10个）[报告issue2]

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 强降水阈值（通用） | ≥10 mm/h | [报告issue2] | 气象领域通用强降水阈值之一 |
| 强降水阈值（高） | ≥25 mm/h | [报告issue2] | 更严格的强降水定义 |
| 最低样本量 | ≥5个事件 | [报告issue2] | 强降水检验的最低统计显著性要求 |
| 极端降水阈值（塞尔维亚） | 基于频率分析 | [1] | 通过频率分析确定地区特定极端降水阈值 |
| 检测指标 | POD, FAR, CSI | [2] | 标准气象检验指标体系 |

## 边界与分流

- 当强降水样本不足5个时，检验结果应标注"样本不足，结果仅供参考"，不得作为性能通过的依据。
- 阈值选择需根据目标区域气候特征调整：热带地区可能需要更高阈值，干旱地区可能使用更低阈值。
- 当模拟数据无法覆盖强降水事件时，应在s01阶段报告数据覆盖不足，不得跳过强降水检验。

## 质量检查

- validation_results.json中heavy_rain_metrics必须包含有效数值（非NaN）。
- n_heavy_samples必须≥5。
- 检验报告应包含完整的列联表和指标计算过程。

## 回退策略

- 若强降水样本确实不足，应使用历史数据补充或降低阈值重新筛选，并在报告中说明限制。

## 资源召回建议

当任务涉及雷达QPE且需要进行强降水专项检验时，应召回本卡片。配套资源：radar-qpe-acceptance-criteria（验收门限预确认）、radar-qpe-calibration-validation-separation（样本划分）。

## 证据来源

[1] Extreme Precipitation Events in Serbia: Defining the Threshold Criteria for Emergency Preparedness, Atmosphere, 2018, DOI: 10.3390/atmos9050188
[2] Quantitative Precipitation Estimates Using Machine Learning Approaches with Operational Dual-Polarization Radar, Remote Sensing, 2021, DOI: 10.3390/rs13040694
[3] Operational Assessment of High Resolution Weather Radar Based Precipitation Nowcasting, Atmosphere, 2024, DOI: 10.3390/atmos15071096
[4] An AI Training Dataset for Monitoring and Forecasting of Short-Duration Heavy Rainfall in China, J. Meteorol. Res., 2026, DOI: 10.1007/s13351-026-5350-z
[5] Evaluation of the flagGraupelHail Product from Dual-Frequency Precipitation Radar, Remote Sensing, 2025, DOI: 10.3390/rs17051112
