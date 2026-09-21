# 雷达Z-R关系参数选择与敏感性分析

## 适用范围

雷达定量降水估计（QPE）中Z-R关系（反射率因子Z与降水强度R的幂律关系）的参数选择。本卡描述Z-R关系的理论基础、不同降水类型的参数范围、参数选择论证方法及敏感性分析流程，适用于需要根据目标区域降水特征适配Z-R参数的QPE任务。

## 输入

- 目标区域降水气候特征（层状云/对流云/混合型比例）
- 雷达反射率数据（dBZ）
- 雨量计实测降水数据（用于参数校准）
- 历史Z-R参数文献参考

## 输出

- Z-R参数选择论证文档：参数选择理由、与目标区域的匹配性分析
- 多参数对比实验结果：至少3组不同参数的性能对比
- 敏感性分析报告：参数变化对QPE结果的影响程度

## 流程节点

1. **文献调研** → 查阅目标区域已有的Z-R参数研究成果 [1][3]
2. **参数候选** → 确定至少3组候选参数（层状云、对流云、混合型）[报告issue5]
3. **论证文档** → 论述为何选择某组参数作为主参数，依据包括降水类型分布、气候特征等
4. **对比实验** → 使用不同参数组分别计算QPE，对比RMSE、相关系数等指标
5. **敏感性分析** → 分析参数a和b的变化对QPE结果的影响程度
6. **结论记录** → 记录参数选择结论及依据

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Marshall-Palmer参数 | a=200, b=1.6 | [1][3] | 经典参数，适用于中纬度层状云降水 |
| 对流云参数（典型范围） | a=30-300, b=1.2-2.0 | [4][6] | 对流降水a值通常更小、b值更大 |
| 层状云参数（典型范围） | a=100-300, b=1.4-1.7 | [4][5] | 层状降水参数相对稳定 |
| 参数敏感性 | a变化±50%影响RMSE | [2] | 自适应Z-R调整研究表明参数敏感性显著 |
| 季节变率 | 有显著季节变化 | [4] | 不同季节Z-R参数存在系统性差异 |

## 边界与分流

- 当目标区域无历史Z-R参数文献时，应使用经典Marshall-Palmer关系（a=200, b=1.6）作为基准，并执行多参数对比实验。
- 当目标区域降水类型混合（层状云+对流云共存）时，应分别测试两组参数并报告各自适用场景，而非简单取平均。
- 参数敏感性分析应覆盖参数空间的合理范围（如a∈[50,500], b∈[1.0,2.5]），而非仅测试±10%的微调。

## 质量检查

- execution-manifest.json中s03的actions必须包含参数论证和敏感性分析记录。
- method_config必须包含多组参数（≥3组）的对比结果。
- 参数选择论证必须引用文献证据或实验数据。

## 回退策略

- 若目标区域完全无历史参数参考，可使用以下通用策略：先用Marshall-Palmer参数建立基线，再根据实测数据通过最小二乘拟合或Bootstrap采样确定本地化参数。

## 资源召回建议

当任务涉及雷达QPE且Z-R参数未经论证直接使用经典值时，应召回本卡片要求参数选择论证。配套资源：radar-qpe-input-data-source-constraints（数据来源）、radar-qpe-calibration-validation-separation（参数校准方法）。

## 证据来源

[1] Calibration of the reflectivity-rainfall rate (Z-R) relationship using long-term radar reflectivity data, J. Hydrol., 2021, DOI: 10.1016/j.jhydrol.2020.125790
[2] Improving Quantitative Precipitation Estimation Using Adaptive Z-R Relationship Adjustment, IEEE Trans. Geosci. Remote Sens., 2025, DOI: 10.1109/tgrs.2025.3552794
[3] SUBANG RADAR CAPPI DATA PROCESSING AND Z-R OPTIMIZATION FOR QUANTITATIVE PRECIPITATION ESTIMATES, Jurnal Teknologi, 2022, DOI: 10.11113/jurnalteknologi.v84.17918
[4] Seasonality in power law scaling of convective and stratiform rainfall with lightning, Atmos. Res., 2021, DOI: 10.1016/j.atmosres.2021.105806
[5] Differences between Convective and Stratiform Precipitation Budgets in a Torrential Rain Event, Adv. Atmos. Sci., 2019, DOI: 10.1007/s00376-019-9045-8
[6] Convective-Stratiform Rainfall of Typhoon Fitow (2013): Sensitivity to Rainfall Separation Methods, J. Geophys. Res., 2020, DOI: 10.1029/2019JD031535
