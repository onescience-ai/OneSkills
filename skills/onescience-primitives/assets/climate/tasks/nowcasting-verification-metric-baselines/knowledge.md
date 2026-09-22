# 临近预报检验指标业务基准与合成数据局限性

## 适用范围

临近预报（0-2小时）模型效果评估场景，特别是冰雹概率预报的检验指标解读。本卡提供真实业务场景中各类检验指标的典型值域基准，以及合成数据上指标虚高的原因分析。核心区分：合成数据上的高指标仅验证算法数学正确性，不反映业务性能。

## 输入

- 预报产品的检验指标（CSI、FSS、Brier Score、ROC-AUC 等）
- 数据来源说明（真实观测 vs 合成数据）
- 事件稀有度信息（base rate）

## 输出

- 指标与业务基准的对比评估
- 合成数据局限性说明
- 业务可信度判定

## 流程节点

1. 指标值域判定 → 2. 基准对比 → 3. 数据来源影响分析 → 4. 业务可信度输出

### 步骤1：指标值域判定

各检验指标的定义与合理值域：

| 指标 | 定义 | 合理值域（业务） | 极端值含义 |
|------|------|------------------|-----------|
| CSI (Critical Success Index) | hits / (hits + misses + false_alarms) | 0.2 - 0.6 | >0.7 通常不现实 |
| FSS (Fractions Skill Score) | 邻域分数技能评分 | 0.5 - 0.8 | >0.95 暗示过拟合或数据问题 |
| Brier Score | 均方概率误差 | 0.1 - 0.3 | <0.05 通常不现实 |
| ROC-AUC | 受试者工作特征曲线下面积 | 0.7 - 0.9 | >0.95 在稀有事件中需警惕 |
| POD (Probability of Detection) | hits / (hits + misses) | 0.3 - 0.8 | 依赖于命中率-虚报率权衡 |
| FAR (False Alarm Ratio) | false_alarms / (hits + false_alarms) | 0.2 - 0.6 | 业务可接受范围 |

[1][3]

### 步骤2：基准对比

将实际指标与上述基准对比：
- **落在合理范围**：指标可信，可作为业务性能参考
- **显著高于基准**：需检查数据来源（合成数据？信息泄漏？）
- **显著低于基准**：可能存在模型缺陷或数据质量问题

### 步骤3：合成数据影响分析

合成数据导致指标虚高的原因：
1. **信号已知**：合成数据中冰雹位置由算法生成，预报模型可能间接"学到"了生成规律
2. **噪声可控**：合成噪声分布规则，真实观测噪声复杂（地物杂波、衰减、遮挡）
3. **无观测误差**：真实雷达存在标定误差、波束展宽、距离折叠等问题
4. **空间相关性简化**：合成数据的空间相关结构通常比真实天气简单
5. **稀有事件被均匀化**：合成数据可能未反映冰雹事件的真实时空聚集性

[2]

### 步骤4：业务可信度输出

判定规则：
- 真实观测 + 指标在合理范围 → **可信**
- 真实观测 + 指标显著偏高 → **需人工审查**
- 合成数据 + 任何指标 → **仅验证数学正确性，不具业务参考价值**
- verification_results 中必须包含"数据来源"和"业务基准对比"字段

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 冰雹预报 CSI（业务） | 0.2 - 0.5 | [1][2] | 真实冰雹预报的最佳表现 |
| 冰雹预报 CSI（合成数据） | 0.8 - 1.0 | [报告] | 仅验证算法正确性 |
| FSS 合理范围（业务） | 0.5 - 0.8 | [3] | 邻域方法的典型技能 |
| Brier Score 合理范围 | 0.1 - 0.3 | [4] | 概率预报校准程度 |
| ROC-AUC 合理范围 | 0.7 - 0.9 | [1] | 区分能力 |
| 基率（冰雹） | 0.1% - 1% | [2] | 极端稀有事件 |

## 边界与分流

- **无法获取真实观测**：在 verification_results 中明确标注"基于合成数据"，并在 conclusion 中将最终判定设为 PARTIAL
- **指标与业务基准差异巨大**：当 CSI > 0.7 时，自动触发数据来源审查
- **稀有事件检验**：冰雹 base rate < 1% 时，准确率（accuracy）无参考价值，应使用 CSI、FSS、HSS 等稀有事件友好指标

## 质量检查

- verification_metrics.json 中是否包含"数据来源"字段
- 是否包含与业务基准的对比信息
- 当指标显著偏高时，是否有合成数据局限性说明

## 回退策略

- 业务基准不确定时：引用权威文献值域，标注为参考级
- 合成数据验证：在报告中单独列出"合成数据验证结果"小节，与业务基准区分呈现

## 资源召回建议

- 临近预报效果评估阶段应召回本卡
- 配套召回 `nowcasting-verification-independence`（验证独立性）和 `radar-data-acquisition-for-hail-nowcasting`（数据来源）

## 证据来源

[1] Verification of weather-radar-based hail metrics with crowdsourced observations, Atmospheric Measurement Techniques, 2024, DOI: 10.5194/amt-2024-31
[2] An Hourly Climatology of Operational MRMS MESH-Diagnosed Severe and Significant Hail, Weather and Forecasting, 2021, DOI: 10.1175/WAF-D-20-0191.1
[3] Verification of Probabilistic SPC Convective Outlooks from 2002 to 2023, Weather and Forecasting, 2026, DOI: 10.1175/WAF-D-25-0093.1
[4] Evaluating the impact of prevalence on the scaled Brier score, Matthews correlation coefficient and F1 score, Discover Data, 2026, DOI: 10.1007/s42979-026-00801-z
