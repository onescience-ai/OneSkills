# 雷达QPE校准与验证样本独立分离

## 适用范围

雷达定量降水估计（QPE）任务中，校准阶段使用的雨量计数据与验证阶段使用的雨量计数据必须严格分离，以避免信息泄漏导致验证结果失真。本卡描述样本划分的标准方法和原则，适用于任何使用雨量计数据进行Z-R关系校准和QPE性能验证的场景。

## 输入

- 雨量计站点列表及其实测降水时间序列
- 雷达QPE估算降水场
- 站点空间坐标信息
- 样本划分比例参数（如70%校准/30%验证）

## 输出

- 样本划分方案：校准组站点列表与验证组站点列表
- 划分规则文档：划分方法、比例、随机种子（如适用）
- 校准统计（基于校准组）和验证指标（基于验证组）分别独立计算

## 流程节点

1. **划分方案设计** → 选择划分方法（时间/空间/传感器）[1][3]
2. **站点分组** → 将雨量计站点分为校准组和验证组
3. **数据提取** → 分别提取校准组和验证组的雷达-雨量计配对数据
4. **校准执行** → 仅使用校准组数据拟合Z-R关系或其他校准参数
5. **验证执行** → 仅使用验证组数据计算QPE性能指标
6. **一致性检查** → 确认校准组和验证组无重叠

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 划分比例（典型） | 70%校准 / 30%验证 | [报告issue3] | 留出法的标准比例 |
| 最低验证样本量 | ≥5个站点 | [报告issue2] | 统计显著性最低要求 |
| 空间划分原则 | 按站点地理位置分组 | [1][3] | 相邻站点不跨组 |
| 时间划分原则 | 不同时段分离 | [报告issue3] | 校准期和验证期不重叠 |
| 传感器划分原则 | 不同设备分离 | [报告issue3] | 校准和验证使用不同雨量计 |

## 边界与分流

- 当站点数量过少（如<10个）不足以同时满足校准和验证的最低样本量时，应采用k折交叉验证（k≥3）替代留出法。
- 当数据存在明显的时空非平稳性时（如山区与平原混合），空间划分应确保各组覆盖相似的地形特征。
- 校准组和验证组的样本量差异不应超过2倍，否则应调整划分比例。

## 质量检查

- execution-manifest.json中s05的calibration_stats.n_valid_samples与s06的overall_metrics.n_valid_samples必须不同（表明使用了不同样本集）。
- radar_qpe_pipeline.py中必须包含样本划分逻辑代码。
- 校准组和验证组的站点列表交集必须为空。

## 回退策略

- 若站点数量不足以进行独立划分，可采用留一法交叉验证（Leave-One-Out CV），每次留出一个站点作为验证，其余作为校准。

## 资源召回建议

当任务涉及雷达QPE且校准与验证使用相同样本时，应召回本卡片纠正数据划分。配套资源：radar-qpe-input-data-source-constraints（数据来源）、radar-z-r-parameter-selection（Z-R参数校准）。

## 证据来源

[1] Merging radar and rain gauge data by using spatial-temporal local weighted linear regression kriging, J. Hydrol., 2021, DOI: 10.1016/J.JHYDROL.2021.126612
[2] Evaluation of the Radar QPE and Rain Gauge Data Merging Methods in Northern China, Remote Sensing, 2020, DOI: 10.3390/rs12030363
[3] Evaluating Geostatistical and Statistical Merging Methods for Radar-Gauge Rainfall Integration, Remote Sensing, 2025, DOI: 10.3390/rs17152622
[4] Calibration of the reflectivity-rainfall rate (Z-R) relationship using long-term radar reflectivity data, J. Hydrol., 2021, DOI: 10.1016/j.jhydrol.2020.125790
[5] Radar-Rain Gauge Merging for High-Spatiotemporal-Resolution Rainfall Estimation Using RBF, Remote Sensing, 2025, DOI: 10.3390/rs17030530
