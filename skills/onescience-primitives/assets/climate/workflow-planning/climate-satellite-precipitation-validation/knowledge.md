# 卫星降水产品验证与性能评估

## 适用范围
适用于卫星降水产品的独立验证和性能评估。触发条件：用户需要验证卫星降水产品的精度和性能。

## 输入
- 卫星降水产品：IMERG、GSMaP、CMORPH、MSWEP等
- 独立验证资料：地面雨量站、雷达数据、其他卫星产品
- 验证区域和时段：目标区域和时段的降水数据

## 输出
- 验证指标：RMSE、MAE、相关系数、POD、FAR、CSI等
- 分层验证结果：按海陆、强度、天气型和传感器分层
- 性能评估报告
- 误差分析结果

## 流程节点
1. **验证资料选择**：选择独立于算法开发数据的验证资料
2. **数据匹配**：将卫星产品与验证资料在时间和空间上匹配
3. **指标计算**：计算各种验证指标
4. **分层分析**：按海陆、强度、天气型和传感器进行分层验证
5. **误差分解**：分析误差来源和组成
6. **性能评估**：与业务门限比较，评估算法性能

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 相关系数门限 | ≥0.75 | [报告] | 算法有效的最低要求 |
| RMSE门限 | ≤2.5 mm/h | [报告] | 降水估计精度要求 |
| 总体精度门限 | ≥70% | [报告] | 业务应用要求 |
| 验证维度 | 海陆、强度、天气型、传感器 | [论文5,6] | 分层验证的维度 |
| 误差分解成分 | 命中、漏报、虚报、偏差 | [论文6] | 误差的四个组成部分 |

## 边界与分流
- **验证资料独立性**：验证资料必须独立于算法开发数据
- **分层验证**：必须覆盖所有要求的分层维度
- **指标全面性**：需要计算所有规定的验证指标
- **性能不足处理**：当性能指标未达到门限时，必须进行深入的误差分析和诊断

## 质量检查
- 验证资料是否独立于算法开发数据
- 分层验证是否覆盖了所有要求的分层维度
- 验证指标计算是否正确
- 性能评估是否与业务门限比较

## 回退策略
- 如果无法获取独立验证资料，应报告验证缺失并寻求确认
- 如果性能指标未达到门限，进行误差分析和诊断
- 如果验证资料不完整，考虑使用其他验证资料或融合数据

## 资源召回建议
- 当需要验证卫星降水产品精度时召回本卡片
- 配套资源：被动微波卫星降水反演算法知识、数据预处理流程知识

## 证据来源
[1] Tang, G., Clark, M., & Papalexiou, S. M. (2020). Have satellite precipitation products improved over last two decades? A comprehensive comparison of GPM IMERG with nine satellite and reanalysis datasets. Remote Sensing of Environment, 240, 111697. DOI: 10.1016/j.rse.2020.111697
[2] Beck, H. E., Wood, E. F., & Pan, M. (2018). MSWEP V2 Global 3-Hourly 0.1° Precipitation: Methodology and Quantitative Assessment. Bulletin of the American Meteorological Society, 100(3), 473-500. DOI: 10.1175/bams-d-17-0138.1
[3] Xie, P., Joyce, R. J., & Wu, S. (2017). Reprocessed, Bias-Corrected CMORPH Global High-Resolution Precipitation Estimates from 1998. Journal of Hydrometeorology, 18(5), 1355-1373. DOI: 10.1175/jhm-d-16-0168.1
[4] Ryu, J., You, Y., & Kubota, T. (2025). Evaluation of Precipitation Retrieval Performance from 13 Passive Microwave Radiometers Relative to Spaceborne Radar Estimate. Journal of Hydrometeorology, 26(2), 123-135. DOI: 10.1175/jhm-d-25-0036.1
[5] Fernando, B., You, Y., & Ryu, J. (2025). Global Precipitation Estimate Error Decomposition Analysis for 14 Passive Microwave Sensors. Geophysical Research Letters, 52(5), e2024GL113631. DOI: 10.1029/2024GL113631
