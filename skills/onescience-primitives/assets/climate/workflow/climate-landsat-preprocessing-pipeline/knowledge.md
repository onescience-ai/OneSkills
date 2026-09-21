# Landsat数据预处理标准流程

## 适用范围
适用于 Landsat Level-1T 数据的预处理工作流。数据需经过辐射定标→大气校正→地形校正→云掩膜才能用于植被指数计算。

## 输入
- Landsat Level-1T 数据：包含辐射定标系数、地理坐标、质量标记。
- 辅助数据：数字高程模型（DEM）用于地形校正。

## 输出
- 地表反射率产品：经过大气校正和地形校正的反射率数据。
- 云掩膜：排除受云污染像元。
- 预处理参数记录：每步的处理参数和版本。

## 流程节点
1. 辐射定标 → 2. 大气校正 → 3. 地形校正 → 4. 云掩膜 → 5. 参数记录

每步含：操作、参数、工具、质量门禁

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| radiometric_calibration | DN→TOAReflectance | [论文1] | 使用 Landsat 元数据中的增益和偏移 |
| atmospheric_correction | LaSRC 或 Sen2Cor | [论文1] | 获取地表反射率 |
| terrain_correction | C校正或经验模型 | [论文2] | 消除地形阴影 |
| cloud_mask | CFMask 算法 | [论文1] | 排除云、阴影、雪像元 |
| preprocessing_config | JSON配置文件 | [论文1] | 记录每步参数和版本 |

## 边界与分流
- 当使用合成数据时：在日志中记录预处理配置或说明跳过原因，生成 `preprocessing_config.json`。
- 当真实数据可用时：执行完整预处理流程，记录每步参数。

## 质量检查
- 检查 `processing_log.txt` 中是否包含预处理步骤的配置或跳过记录。
- 验证预处理参数文件是否完整。

## 回退策略
- 如果预处理步骤失败，记录失败原因并标记产出为 PARTIAL。

## 资源召回建议
- 当任务涉及 Landsat 数据预处理时召回本卡片。
- 配套资源：数据真实性验收标准、输出格式规范、独立验证标准。

## 证据来源
[1] Atmospheric Correction of Landsat Image, Journal of Environmental and Geographical Sciences, 2023, DOI: 10.58425/jegs.v2i1.120
[2] Assessment of uncertainties in the computation of atmospheric correction parameters, Science World Journal, 2026, DOI: 10.58425/jegs.v2i1.120