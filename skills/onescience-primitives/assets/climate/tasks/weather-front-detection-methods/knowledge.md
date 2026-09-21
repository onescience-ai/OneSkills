# 天气锋面检测方法学对比知识

## 适用范围
适用于气象科研任务中需要选择天气锋面检测方法的场景，包括CNN监督学习方法和传统阈值方法的适用条件、输入要求、输出精度差异。

## 输入
- 多要素分析场数据（温度、湿度、风场、气压等）
- 人工标注的锋面位置数据（如有）
- 任务精度要求

## 输出
- 方法选择论证报告，包含：
  - CNN方法与传统方法的适用性对比
  - 方法选择理由和预期精度
  - 替代方案评估

## 流程节点
1. **方法特性分析** → 分析CNN方法和传统方法的特性
2. **适用条件评估** → 评估当前任务是否满足方法适用条件
3. **精度需求匹配** → 匹配任务精度需求与方法输出精度
4. **选择论证** → 论证方法选择理由
5. **替代方案记录** → 记录替代方案和降级策略

## 关键参数
| 参数 | CNN方法 | 传统阈值方法 | 来源 | 说明 |
|------|---------|-------------|------|------|
| 输入要求 | 多要素网格数据+标注数据 | 多要素网格数据 | [1] | CNN需要训练数据 |
| 输出能力 | 冷锋、暖锋、准静止锋、锢囚锋 | 主要检测锋面位置 | [2] | CNN类型识别能力强 |
| 计算资源 | GPU加速 | CPU即可 | [1] | CNN计算成本高 |
| 精度水平 | 较高（依赖训练数据质量） | 中等 | [2] | CNN精度受数据影响 |
| 适用场景 | 有大量标注数据的场景 | 快速原型或数据不足 | [3] | 根据资源选择 |

## 边界与分流
- 当缺乏人工标注数据时，优先考虑传统阈值方法
- 当计算资源有限时，优先考虑传统阈值方法
- 当需要高精度类型识别时，优先考虑CNN方法
- 当任务为快速原型验证时，优先考虑传统阈值方法

## 质量检查
- 验证方法选择理由是否充分
- 检查替代方案是否已评估
- 确认方法与任务需求匹配

## 回退策略
- 当CNN方法无法实现时，降级为传统阈值方法并说明精度损失
- 当传统方法精度不足时，标记相关交付项为PARTIAL

## 资源召回建议
- 当任务需要选择锋面检测方法时召回本卡片
- 配套使用锋面类型识别判据卡片
- 配套使用气象产品质控规范卡片

## 证据来源
[1] Deep Learning for Spatially Explicit Prediction of Synoptic-Scale Fronts, Lagerquist et al., Weather and Forecasting, 2019, DOI: 10.1175/waf-d-18-0100.1
[2] Climatology and Variability of Warm and Cold Fronts over North America from 1979 to 2018, Lagerquist et al., Journal of Climate, 2020, DOI: 10.1175/jcli-d-19-0651.1
[3] Machine Learning-Based Detection of Weather Fronts and Associated Extreme Precipitation in Historical and Future Climates, Bai et al., Geophysical Research Letters, 2021, DOI: 10.1029/2021gl095418