# 遥感分类独立验证的标准要求

## 适用范围
适用于遥感分类产品的独立验证场景。验证必须使用与训练数据在来源、时间、空间上均独立的外部参考数据，并执行同协议基线比较。

## 输入
- 分类产品：待验证的遥感分类结果。
- 独立参考数据：GlobeLand30、FROM-GLC、ESA WorldCover 等全球土地覆盖产品。

## 输出
- 验证报告：包含精度指标（OA、Kappa、F1-score）、混淆矩阵。
- 基线比较报告：与参考产品的比较结果。
- 验收判定：是否达到预先登记门限。

## 流程节点
1. 独立参考数据获取 → 2. 样本匹配 → 3. 精度计算 → 4. 基线比较 → 5. 验收判定

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| reference_data_sources | GlobeLand30, FROM-GLC, ESA WorldCover | [论文1] | 独立参考数据来源 |
| baseline_comparison_protocol | 相同样本、网格、变量、指标 | [论文1] | 确保公平比较 |
| acceptance_threshold | OA ≥ 0.85, Kappa ≥ 0.70 | [论文1] | 预先登记门限 |
| independence_requirement | 来源、时间、空间独立 | [论文1] | 验证数据必须独立于训练数据 |

## 边界与分流
- 当参考数据不可用时：阻塞验证，不得使用训练数据作为验证数据。
- 当未达到门限时：不得判定 PASS，需记录不达标原因。

## 质量检查
- 检查验证数据是否与训练数据独立。
- 验证基线比较是否使用相同协议。

## 回退策略
- 如果独立验证失败，记录失败原因并阻塞验收。

## 资源召回建议
- 当任务涉及遥感分类验证时召回本卡片。
- 配套资源：数据真实性验收标准、预处理工作流、输出格式规范。

## 证据来源
[1] Accuracy Assessment of GlobeLand30 2010 Land Cover over China Based on Geographic, Remote Sensing, 2020, DOI: 10.3390/rs12020228
[2] APPLICATION OF DEEP LEARNING IN GLOBELAND30-2010 PRODUCT REFINEMENT, Remote Sensing, 2020, DOI: 10.3390/rs12020228