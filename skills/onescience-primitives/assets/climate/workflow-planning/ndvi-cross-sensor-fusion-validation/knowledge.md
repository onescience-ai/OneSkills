# NDVI跨传感器融合重建与验证通用方法论

## 适用范围
面向多传感器（如AVHRR、MODIS、Landsat、Sentinel等）NDVI时间序列数据，本卡提供融合重建与验证的通用方法论框架。适用于需要将不同传感器的NDVI产品整合为一致长期连续记录的场景，包括但不限于：创建跨传感器长期NDVI数据集、提高时间序列完整性、消除传感器间辐射差异、以及融合后的质量验证。不适用于单一传感器内部的时间序列平滑处理。

## 输入
- 多传感器NDVI原始数据或产品（需注明传感器类型、时间范围、空间分辨率）
- 数据质量标志（如云掩膜、气溶胶标志、传感器状态）
- 空间覆盖范围与时间重叠期信息
- 验证参考数据（可选，用于后期验证）

## 输出
- 融合后的连续NDVI时间序列数据集
- 数据质量报告（包含处理前后的对比）
- 验证指标报告（偏差、RMSE、相关系数、趋势保持度等）
- 处理日志与参数记录

## 流程节点
1. **数据预检与获取** → 检查输入数据完整性、格式、质量标志；从权威平台下载真实数据
2. **时空对齐** → 统一空间投影、分辨率、时间基准；识别传感器重叠期
3. **辐射校正与光谱归一化** → 消除传感器间辐射差异（如AVHRR与MODIS的光谱响应函数差异）
4. **融合算法选择与配置** → 根据数据特点选择适当的融合方法
5. **融合执行** → 生成跨传感器一致的NDVI记录
6. **独立验证** → 使用未参与融合的数据进行精度评估
7. **验收判定** → 对照预设门限判断融合质量

## 关键参数

### 通用判据
| 参数 | 判据 | 来源 | 说明 |
|------|------|------|------|
| 时间重叠期 | ≥2年 | [1] | 用于建立传感器间转换关系的必要条件 |
| 空间分辨率匹配 | 相邻传感器差异≤2倍 | [2] | 过大的分辨率差异需先进行空间降尺度 |
| 质量标志使用 | 必须使用原始质量标志 | [3] | 云、雪、气溶胶等标志直接影响NDVI值 |
| 融合方法类型 | 物理模型/统计模型/机器学习 | [1][5] | 根据数据量和计算资源选择 |
| 验证数据独立性 | 不参与融合参数训练 | [6] | 确保验证结果可信 |

### 校准数值（来自具体研究）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| AVHRR NDVI范围 | [-1, 1]，通常有效范围[0, 1] | [4] | 超出范围值需进行质量检查 |
| MODIS NDVI产品 | MOD13A2 (16天合成)、MOD13Q1 (250m) | [3] | 常用产品及其时空特性 |
| 典型融合精度 | RMSE <0.1，相关系数>0.9 | [6][7] | 优秀融合结果的参考阈值 |
| 趋势保持要求 | 融合后年际趋势与原始数据一致 | [4] | 避免融合引入虚假趋势 |

## 边界与分流
- **无重叠期数据**：无法直接建立传感器转换关系，需采用间接方法（如参考已有融合产品进行交叉校准）
- **空间分辨率差异过大**（>4倍）：需先进行空间降尺度，或分区域融合
- **数据缺失率过高**（>50%时间无有效观测）：需评估融合可行性，可能需引入辅助数据
- **NDVI异常值（超出[-1, 1]）**：需在预处理阶段识别并处理，不能直接用于融合
- **计算资源有限**：优先选择计算复杂度低的统计方法，但需说明精度损失

## 质量检查
- 输入数据NDVI值范围检查：应为[-1, 1]，有效值通常在[0, 1]
- 质量标志覆盖率检查：确认云/气溶胶标志可用性
- 重叠期数据分布检查：确保重叠期有足够的观测样本建立转换关系
- 融合后统计检查：NDVI均值、方差、极值是否在合理范围
- 时间连续性检查：是否存在时间断点或突变
- 空间一致性检查：相邻像元融合结果是否平滑

## 回退策略
- 融合方法失败时：尝试简化方法（如从复杂机器学习退化到线性回归）
- 验证数据不可用时：使用交叉验证或留出验证作为替代
- 精度不达标时：返回检查数据预处理步骤，调整质量标志阈值
- 计算超时：降低分辨率或时间范围进行测试，再扩展到全区域

## 资源召回建议
- 当任务涉及多传感器NDVI数据融合时召回本卡
- 当需要NDVI数据验证方法论时召回本卡
- 当处理AVHRR-MODIS长期序列时召回本卡
- 配套资源：遥感数据获取平台知识、NDVI异常值处理知识、遥感验证标准知识

## 证据来源
[1] Li S, Xu L, Jing Y. High-quality vegetation index product generation: A review of NDVI time series reconstruction techniques. International Journal of Applied Earth Observation and Geoinformation, 2021.
[2] Kandasamy S, Baret F, Verger A. A comparison of methods for smoothing and gap filling time series of remote sensing observations. Biogeosciences, 2013.
[3] Cai Z, Jönsson P, Jin H. Performance of Smoothing Methods for Reconstructing NDVI Time-Series and Estimating Vegetation Phenology from MODIS Data. Remote Sensing, 2017.
[4] Sajadi P, Sang Y, Gholamnia M. Performance Evaluation of Long NDVI Timeseries from AVHRR, MODIS and Landsat Sensors. Remote Sensing, 2021.
[5] Jeong S, Ryu Y, Gentine P. Persistent global greening over the last four decades using novel long-term vegetation index data. Remote Sensing of Environment, 2024.
[6] Sun M, Gong A, Zhao X. Reconstruction of a Monthly 1 km NDVI Time Series Product in China Using Random Forest Methodology. Remote Sensing, 2023.
[7] Franch B, Vermote E, Roger J. A 30+ Year AVHRR Land Surface Reflectance Climate Data Record and Its Application to Wheat Yield Monitoring. Remote Sensing, 2017.
[8] Yang W, Tan B, Huang D. MODIS leaf area index products: from validation to algorithm improvement. IEEE Transactions on Geoscience and Remote Sensing, 2006.