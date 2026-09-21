# 遥感制图任务中真实传感器数据与合成数据的本质区别及其对验收判定的影响

## 适用范围
适用于遥感制图任务中数据真实性验证与验收判定场景。当任务需要使用真实卫星影像（如 Landsat、Sentinel-2）进行正式产品验收时，必须区分真实数据与合成数据的本质差异，并制定相应的处置流程。

## 输入
- 真实传感器数据：来自卫星平台的原始观测数据，包含大气噪声、几何畸变、云污染等真实世界特征。
- 合成数据：基于模型生成的理想化数据，用于验证管线逻辑，但不包含真实噪声和畸变。

## 输出
- 数据真实性判定报告：明确数据来源（真实/合成）及其对验收的影响。
- 验收状态标记：当必需输入缺失时，设置 `overall_delivery=BLOCKED` 并说明降级原因。

## 流程节点
1. 数据可用性检查 → 2. 数据来源真实性判定 → 3. 验收状态设置 → 4. 产出标记与文档记录

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| real_satellite_data_used | true/false | [论文1] | 标记是否使用真实卫星数据 |
| overall_delivery | PASS/BLOCKED/PARTIAL | [论文2] | 验收状态，当必需输入缺失时设置为 BLOCKED |
| synthetic_data_only | true/false | [论文1] | 标记是否仅使用合成数据 |

## 边界与分流
- 当必需传感器输入缺失时：自动设置 `overall_delivery=BLOCKED`，详细说明降级原因。
- 当使用合成数据时：产出仅可用于管线逻辑验证，不能作为正式验收依据。

## 质量检查
- 检查 `execution-manifest.json` 中 `real_satellite_data_used` 和 `overall_delivery` 字段的一致性。
- 验证验收状态是否与数据来源匹配。

## 回退策略
- 如果真实数据不可用，应阻塞任务而非降级为演示，并明确记录阻塞原因。

## 资源召回建议
- 当任务涉及遥感制图验收时召回本卡片。
- 配套资源：遥感数据预处理工作流、输出格式规范、独立验证标准。

## 证据来源
[1] Accuracy, Bias, and Improvements in Mapping Crops and Cropland across the United States Using the USDA Cropland Data Layer, Lark et al., Remote Sensing, 2021, DOI: 10.3390/rs13050968
[2] Synergistic Use of Radar and Optical Satellite Data for Improved Monsoon Cropland Mapping in India, Qadir et al., Remote Sensing, 2020, DOI: 10.3390/rs12030522