# 对流初生检测验证协议

## 适用范围
面向对流初生（CI）检测结果的独立验证，确保验证协议满足"独立验证资料"要求，验证指标（POD/FAR/CSI）计算正确，验证报告完整可靠。

## 输入
- CI检测结果（检测到的CI事件列表、概率场）
- 独立验证资料（雷达回波、不同传感器观测、人工标注）
- 验证时间窗口和空间匹配容差

## 输出
- 验证指标报告：POD、FAR、CSI、HSS等
- 验证资料独立性说明
- 验证结论和局限性声明

## 流程节点
1. **验证资料选择** → 选择独立于训练数据的验证资料
2. **时空匹配** → 将检测结果与验证资料在时间和空间上匹配
3. **混淆矩阵计算** → 计算TP、FP、FN、TN
4. **指标计算** → 计算POD、FAR、CSI、HSS等
5. **显著性检验** → 评估指标的统计显著性
6. **验证报告生成** → 输出完整验证报告

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| POD（检测概率） | TP/(TP+FN) | [1][3] | 正确检测的CI事件比例 |
| FAR（虚警率） | FP/(TP+FP) | [1][3] | 误报的CI事件比例 |
| CSI（关键成功指数） | TP/(TP+FP+FN) | [3][5] | 综合性能指标 |
| HSS（Heidke技能得分） | 2(TP*TN-FP*FN)/((TP+FN)(FN+TN)+(TP+FP)(FP+TN)) | [3] | 相对于随机预测的改进 |
| 时间匹配窗口 | ±15-30分钟 | [1][4] | CI事件的时间容差 |
| 空间匹配窗口 | 10-30km | [1][4] | CI事件的空间容差 |

## 边界与分流
- **验证资料不独立**：若验证资料来自同一传感器或同一时段，必须明确声明限制，不得声明性能PASS
- **验证样本量不足**（<20 CI事件）：使用bootstrap重采样估计指标置信区间
- **正样本极度不平衡**：CSI比POD/FAR更能反映真实性能，优先使用CSI
- **无独立验证资料**：必须明确说明无法进行独立验证，不声明算法性能

## 质量检查
- 验证资料必须独立于训练数据（不同传感器、不同时段、或不同区域）
- 必须报告POD、FAR、CSI三个指标，不能只选择性报告有利指标
- 必须说明时间匹配窗口和空间匹配窗口的选择依据
- 必须声明验证的局限性和不确定性来源

## 回退策略
- 若无雷达数据：使用其他卫星传感器（如极轨卫星）作为替代验证源
- 若无独立验证资料：使用交叉验证，但必须明确说明限制
- 若验证样本量小：使用bootstrap或jackknife方法估计置信区间

## 资源召回建议
- 当任务需要验证CI检测结果时召回本卡片
- 配套资源：climate-ci-ml-detection-methods、climate-ci-threshold-selection

## 证据来源
[1] Observing the pre-convective environment and convection initiation with Doppler lidar and radar, Meteorologische Zeitschrift, 2022, DOI: 10.1127/metz/2021-0061
[2] Convection Initiation over the Eastern Arabian Peninsula, Meteorologische Zeitschrift, 2020, DOI: 10.1127/metz/2020/0965
[3] Evaluating Convective Initiation in High-Resolution Numerical Weather Prediction Models, Monthly Weather Review, 2021, DOI: 10.1175/MWR-D-20-0384.1
[4] Simultaneous Assimilation of Planetary Boundary Layer Observations from Radar and Satellite, Monthly Weather Review, 2023, DOI: 10.1175/MWR-D-22-0290.1
[5] A Novel Framework of Detecting Convective Initiation Combining Automated Sampling and Machine Learning, Remote Sensing, 2019, DOI: 10.3390/rs11172057
