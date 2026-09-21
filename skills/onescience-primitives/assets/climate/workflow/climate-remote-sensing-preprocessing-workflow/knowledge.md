# 遥感数据预处理工作流中辐射定标、几何配准和质量掩膜的具体作用与必要性

## 适用范围
适用于遥感数据预处理工作流，特别是针对 Landsat、Sentinel 等光学卫星数据的预处理。当使用替代数据源（如合成数据）时，需保持工作流步骤完整性以记录跳过原因。

## 输入
- 原始卫星影像：包含辐射计数值、几何坐标、质量标记。
- 替代数据源：合成数据或模拟数据，用于验证管线逻辑。

## 输出
- 预处理后的影像：辐射定标后的反射率、几何配准后的空间对齐、质量掩膜后的清洁像元。
- 预处理记录：配置参数、跳过原因、替代方案说明。

## 流程节点
1. 辐射定标 → 2. 几何配准 → 3. 质量掩膜 → 4. 预处理记录生成

每步含：操作、参数、工具、质量门禁

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| radiometric_calibration | DN→TOAReflectance | [论文1] | 将传感器原始计数值转换为大气顶层反射率 |
| geometric_registration | 空间对齐至参考影像 | [论文2] | 确保多时相影像空间一致性 |
| quality_mask | 云掩膜、阴影掩膜 | [论文1] | 排除受污染像元 |
| preprocessing_config | JSON配置文件 | [论文2] | 记录预处理参数，即使跳过也需生成 |

## 边界与分流
- 当使用替代数据源时：在日志中记录预处理配置或说明跳过原因，生成 `preprocessing_skip_record.json`。
- 当真实数据可用时：执行完整预处理流程，记录每步参数。

## 质量检查
- 检查 `processing_log.txt` 中是否包含 s02 步骤的执行或跳过记录。
- 验证预处理配置文件是否完整。

## 回退策略
- 如果预处理步骤失败，记录失败原因并标记产出为 PARTIAL。

## 资源召回建议
- 当任务涉及遥感数据预处理时召回本卡片。
- 配套资源：数据真实性验收标准、输出格式规范、独立验证标准。

## 证据来源
[1] Atmospheric Correction of Landsat Image, Journal of Environmental and Geographical Sciences, 2023, DOI: 10.58425/jegs.v2i1.120
[2] MAETEC: AN OPTIMIZED MATLAB-BASED APPROACH FOR ACCURATE AND EFFICIENT TERRAIN CORRECTION, Remote Sensing, 2023, DOI: 10.3390/rs15030195