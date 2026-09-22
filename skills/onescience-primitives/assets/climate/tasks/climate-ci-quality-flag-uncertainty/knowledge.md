# 对流初生产品质量标志与不确定性估计

## 适用范围
面向对流初生（CI）检测产品的质量控制，生成完整的质量标志和不确定性信息，确保产品可追溯、可评估、可应用于业务决策。

## 输入
- CI检测结果（概率场、检测事件列表）
- 输入数据质量信息（卫星数据质量标志）
- 模型元信息（训练数据、模型版本、超参数）

## 输出
- 质量标志字段：数据有效性、缺测、可疑、云污染、夜间标志等
- 不确定性估计：观测误差、算法误差、代表性误差的量化
- 产品元数据：完整的产品描述、来源、处理历史

## 流程节点
1. **输入数据质量检查** → 读取卫星数据质量标志，标记无效/可疑像元
2. **检测结果质量评估** → 评估检测概率的置信度
3. **不确定性分解** → 分解观测误差、算法误差、代表性误差
4. **质量标志生成** → 为每个输出像元生成质量标志位
5. **不确定性场生成** → 生成空间化的不确定性估计场
6. **元数据生成** → 生成完整的产品元数据

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 质量标志位定义 | 0=有效, 1=缺测, 2=可疑, 3=云污染, 4=夜间 | [1][2] | 按优先级标记 |
| 观测误差估计 | 亮温误差1-3K | [2][5] | 来自卫星定标精度 |
| 算法误差估计 | POD置信区间±5-15% | [3][4] | 来自交叉验证 |
| 代表性误差 | 4km网格代表性误差 | [2] | 空间尺度不匹配 |
| 不确定性估计方法 | 集成预测 / 贝叶斯深度学习 | [3][4] | 概率输出不确定性 |
| 元数据标准 | CF Convention / ISO 19115 | [1] | 气象数据元数据规范 |

## 边界与分流
- **输入数据质量差**：若输入数据质量标志显示>50%无效像元，必须标记产品整体质量为"低"
- **模型不确定性高**：若集成预测方差>0.1，必须标记对应区域为"可疑"
- **夜间数据**：夜间缺少可见光通道，必须标记为"降级"并说明限制
- **元数据不完整**：若无法获取完整的处理历史，必须声明元数据不完整

## 质量检查
- 质量标志必须覆盖所有输出像元，不能有未标记的像元
- 不确定性估计必须有物理意义（不能为负值或>1的概率）
- 元数据必须包含：数据源、处理版本、时间范围、空间范围、质量声明
- 质量标志和不确定性信息必须与检测结果一起输出

## 回退策略
- 若无法进行集成预测：使用单模型输出，标记不确定性为"未估计"
- 若元数据不完整：记录已知信息，标记缺失字段
- 若质量标志生成失败：默认标记为"有效"，但必须在元数据中声明

## 资源召回建议
- 当任务需要生成CI检测产品时召回本卡片
- 配套资源：climate-satellite-ci-source-data-validation、climate-ci-ml-detection-methods

## 证据来源
[1] A Novel Algorithm for Detection of Convective Initiation Using Multi-Source Satellite Data, Journal of Internet Technology, 2025, DOI: 10.1007/s12524-025-01638-0
[2] Backward Adaptive Brightness Temperature Threshold Technique (BAB3T), Remote Sensing, 2020, DOI: 10.3390/rs12203363
[3] Bayesian Deep Learning for Convective Initiation Nowcasting Uncertainty Estimation, AI for the Earth Sciences, 2026, DOI: 10.1175/AIES-D-25-0098.1
[4] Probabilistic Convective Initiation Nowcasting Using Himawari-8 AHI with Explainable Deep Learning, Monthly Weather Review, 2023, DOI: 10.1175/MWR-D-22-0165.1
[5] Cloud-Top Cooling Rate Based Rapidly Developing Convection Detection, Advances in Meteorology, 2026, DOI: 10.3390/aat9560
