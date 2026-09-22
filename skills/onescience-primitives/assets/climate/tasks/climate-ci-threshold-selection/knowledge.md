# 对流初生概率阈值选择

## 适用范围
面向对流初生（CI）检测任务中概率输出的阈值选择，确保检测阈值与数据分布匹配，避免零检测或过度检测。适用于基于卫星亮温、云顶特性或ML模型输出的CI概率产品。

## 输入
- CI概率分布（来自ML模型或阈值加权算法）
- 训练数据中的正负样本分布
- 业务需求（POD/FAR权衡要求）

## 输出
- 最优检测阈值及选择依据
- 阈值敏感性分析结果
- ROC曲线或F1-score最优化报告

## 流程节点
1. **概率分布统计** → 分析模型输出概率的均值、方差、分位数
2. **正负样本分离** → 按CI发生/未发生分离概率分布
3. **ROC曲线绘制** → 计算不同阈值下的TPR和FPR
4. **最优阈值确定** → 基于Youden指数（TPR-FPR最大化）或F1-score最大化
5. **敏感性分析** → 评估阈值微调对POD/FAR/CSI的影响
6. **阈值校准** → 若概率未经校准，应用Platt scaling或 isotonic regression

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| CI概率典型范围 | 0.1-0.8 | [1][3] | 取决于区域和季节 |
| 推荐阈值选择方法 | ROC曲线 + Youden指数 | [3][4] | 平衡POD和FAR |
| 替代方法 | F1-score最大化 | [4] | 适用于不平衡样本 |
| 自适应阈值窗口 | 100-500像元 | [4] | 空间自适应阈值 |
| 概率校准方法 | Platt scaling / Isotonic regression | [1] | 将模型输出校准为真实概率 |

## 边界与分流
- **固定阈值失败**：若设置固定阈值（如0.5）导致零检测，必须改用数据驱动的阈值选择
- **概率未校准**：若模型输出概率未经校准，先执行概率校准再选择阈值
- **样本极度不平衡**：若正样本比例<5%，优先使用F1-score而非Accuracy作为优化目标
- **区域差异大**：不同区域CI概率分布差异显著，需按区域独立校准阈值

## 质量检查
- 阈值选择必须基于验证数据集（非训练集）
- 必须报告阈值对应的POD、FAR、CSI指标
- 阈值敏感性分析必须覆盖±10%范围
- 若使用固定阈值，必须说明选择依据

## 回退策略
- 若无法获取验证数据：使用交叉验证估计最优阈值
- 若ROC曲线无明显拐点：使用概率分布中位数作为初始阈值
- 若样本量不足：采用bootstrap重采样估计阈值置信区间

## 资源召回建议
- 当CI检测输出零检测或POD=0时召回本卡片
- 配套资源：climate-ci-ml-detection-methods、climate-ci-validation-protocol

## 证据来源
[1] Non-Gaussian Probability Densities of Convection Initiation and Development Investigated Using a Particle Filter, Monthly Weather Review, 2019, DOI: 10.1175/MWR-D-18-0313.1
[2] Convection Initiation over the Eastern Arabian Peninsula, Meteorologische Zeitschrift, 2020, DOI: 10.1127/metz/2020/0965
[3] Probabilistic Convective Initiation Nowcasting with Reduced Satellite-NWP Prediction Error, Asia-Pacific Journal of Atmospheric Sciences, 2018, DOI: 10.1007/s13143-018-0009-z
[4] Backward Adaptive Brightness Temperature Threshold Technique (BAB3T), Remote Sensing, 2020, DOI: 10.3390/rs12203363
[5] A New Convective Initiation Definition and Its Characteristics, Remote Sensing, 2025, DOI: 10.3390/rs17092106
