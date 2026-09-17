# 被动微波卫星降水反演算法与数据规范

## 适用范围
适用于被动微波卫星降水反演任务，包括GPM GMI、AMSR2、TMI等传感器的亮温数据处理和降水率反演。触发条件：用户需要从被动微波卫星数据反演瞬时降水率。

## 输入
- 传感器亮温数据：GPM GMI、AMSR2、TMI等传感器的多通道亮温数据
- 扫描几何数据：经纬度、扫描角、天顶角等
- 环境辅助量：地表类型、海拔、云水路径等
- 数据来源：真实卫星传感器数据，不能使用模拟数据

## 输出
- 瞬时降水率反演结果
- 降水类型识别结果
- 质量标志和不确定性信息
- 产品元数据和文件清单

## 流程节点
1. **s01任务边界预检**：核验传感器观测、辅助资料、目标区域时段的输入数据
2. **s02时空对齐与样本构造**：统一多通道亮温、扫描几何和环境辅助量的时间、空间、单位、质量标志
3. **s03方法配置与输入输出契约验证**：冻结方法配置，验证输入输出契约
4. **s04核心计算**：先识别降水再反演雨雪率
5. **s05输出生成**：生成瞬时降水类别及地表降水率及必要的质量标志
6. **s06独立验证**：按海陆、强度、天气型和传感器独立验证

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| GPM GMI通道数 | 13 | [论文1] | 包括10.65、18.7、23.8、36.64、89.0、166.0、183.31 GHz等频率 |
| AMSR2通道数 | 14 | [论文1] | 包括6.9、7.3、10.65、18.7、23.8、36.5、89.0 GHz等频率 |
| 空间分辨率 | 5-25 km | [论文1] | 取决于传感器和频率 |
| 时间分辨率 | 2-3小时 | [论文1] | 卫星重访周期 |
| 降水识别特征 | 亮温梯度、极化差、频率差 | [论文4] | 多通道特征提取 |
| 反演算法 | 物理反演、统计反演、机器学习反演 | [论文4,5,6,7] | 根据任务需求选择 |

## 边界与分流
- **海陆差异**：海洋和陆地采用不同的反演策略
- **降水类型**：降雨和降雪需要不同的处理方法
- **数据质量**：低质量数据需要质量控制和掩膜处理
- **传感器差异**：不同传感器的通道配置和分辨率需要适配

## 质量检查
- 验证数据来源和版本可追溯
- 检查时空覆盖是否满足目标区域和时段要求
- 验证反演结果的物理合理性
- 检查相关系数是否为正值且≥0.75
- 验证总体精度是否≥70%

## 回退策略
- 如果无法获取真实卫星数据，应报告数据缺失并寻求确认
- 如果算法性能不足，进行误差分析和诊断
- 如果传感器数据不完整，考虑使用其他传感器或融合数据

## 资源召回建议
- 当需要从被动微波卫星数据反演降水率时召回本卡片
- 配套资源：卫星降水产品验证知识、数据预处理流程知识

## 证据来源
[1] Skofronick-Jackson, G., Petersen, W. A., & Berg, W. (2016). The Global Precipitation Measurement (GPM) Mission for Science and Society. Bulletin of the American Meteorological Society, 98(8), 1545-1566. DOI: 10.1175/bams-d-15-00306.1
[2] Sun, Q., Miao, C., & Duan, Q. (2017). A Review of Global Precipitation Data Sets: Data Sources, Estimation, and Intercomparisons. Reviews of Geophysics, 55(3), 619-659. DOI: 10.1002/2017RG000574
[3] Guilloteau, C., Foufoula-Georgiou, E., & Kummerow, C. D. (2017). Global Multiscale Evaluation of Satellite Passive Microwave Retrieval of Precipitation during the TRMM and GPM Eras. Journal of Hydrometeorology, 18(5), 1355-1373. DOI: 10.1175/jhm-d-17-0087.1
[4] Sanò, P., Panegrossi, G., & Casella, D. (2018). The Passive Microwave Neural Network Precipitation Retrieval (PNPR) Algorithm for the CONICAL Scanning Global Microwave Imager (GMI) Radiometer. Remote Sensing, 10(7), 1122. DOI: 10.3390/rs10071122
[5] Ryu, J., You, Y., & Kubota, T. (2025). Evaluation of Precipitation Retrieval Performance from 13 Passive Microwave Radiometers Relative to Spaceborne Radar Estimate. Journal of Hydrometeorology, 26(2), 123-135. DOI: 10.1175/jhm-d-25-0036.1
[6] Fernando, B., You, Y., & Ryu, J. (2025). Global Precipitation Estimate Error Decomposition Analysis for 14 Passive Microwave Sensors. Geophysical Research Letters, 52(5), e2024GL113631. DOI: 10.1029/2024GL113631
[7] Xu, J., Ma, Z., & Hu, H. (2025). A One‐Dimensional Variational Precipitation Retrieval Algorithm Considering Cloud Types for Western North Pacific Tropical Cyclones. Journal of Geophysical Research Atmospheres, 130(10), e2025JD044523. DOI: 10.1029/2025JD044523
