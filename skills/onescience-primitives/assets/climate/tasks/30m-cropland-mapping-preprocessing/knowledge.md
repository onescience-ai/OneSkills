# 30米农田范围与面积制图数据预处理任务

## 适用范围

**适用场景**：
- 需要将原始Landsat数据转换为可用于分类的地表反射率产品
- 需要执行完整的遥感数据预处理流程
- 当使用合成数据时需要记录预处理配置或说明跳过原因

**不适用场景**：
- 不需要预处理的简单分析任务
- 已经是地表反射率产品的数据

## 输入契约

**必需输入**：
- 原始Landsat影像数据（Level-1T产品）
- 辐射定标配置文件
- 几何配准配置文件
- 质量掩膜配置

**可选输入**：
- 辅助分类数据（DEM、夜间灯光等）
- 参考标签资料

## 操作步骤

### 步骤1：辐射定标
将传感器原始计数值（DN）转换为表观辐亮度（TOA Radiance）和表观反射率（TOA Reflectance）。

**公式**：
- TOA Radiance = DN × ML + AL （ML和AL为定标系数）
- TOA Reflectance = (π × L × d²) / (ESUN × cos(θ)) （L为辐亮度，d为日地距离，ESUN为太阳辐照度，θ为太阳天顶角）

**工具**：ArcGIS、ENVI、GEE

### 步骤2：大气校正
将表观反射率转换为地表反射率（Surface Reflectance），消除大气散射和吸收影响。

**常用工具**：
- Sen2Cor（Sentinel-2数据）
- LaSRC（Landsat数据）
- CFMask（云掩膜）

**质量门禁**：
- 大气校正后反射率值应在合理范围内（通常0-1）
- 不存在明显的条带或噪声

### 步骤3：几何配准
确保多时相影像在空间上对齐，消除几何畸变。

**方法**：
- 基于地面控制点（GCP）的配准
- 基于自动特征匹配的配准

**质量门禁**：
- 配准误差应小于0.5个像素
- 多时相影像空间一致性良好

### 步骤4：云掩膜
排除受云污染的像元，确保数据质量。

**方法**：
- 使用QA_PIXEL波段（Landsat Collection 2）
- 使用CFMask算法

**质量门禁**：
- 云掩膜应准确识别云、云阴影、雪等
- 掩膜后有效像元比例应合理

## 输出产物

**主要输出**：
- 地表反射率产品（Surface Reflectance）
- 预处理转换记录
- 质量掩膜

**元数据要求**：
- 处理参数和版本
- 预处理时间
- 数据来源和版本

## 质量门禁

- 预处理后的时间轴、坐标、单位和形状可检查
- 每项插值、归一化、掩膜和缺测处理均有记录
- 辐射定标、几何配准和质量掩膜均有记录
- 不存在由验证资料或未来资料造成的信息泄漏

## 回退策略

- 当原始数据不可用时：记录数据缺失情况，标记任务为BLOCKED
- 当预处理步骤无法执行时：记录跳过原因，生成preprocessing_skip_record.json
- 当使用合成数据时：在日志中记录合成数据使用情况和预处理配置跳过原因

## 资源召回建议

- 当需要执行Landsat数据预处理时召回本卡片
- 当需要记录预处理配置时召回本卡片
- 当需要判定数据质量时召回本卡片

## 证据来源

[1] Yang A, Zhong B, Wang X, et al. 30 m 5-yearly land cover maps of Qilian Mountain Area (QMA_LC30) from 1990 to 2020. Sci Data. 2024;11(1):1339. DOI: 10.1038/s41597-024-03976-9
[2] Badapalli PK, Nakkala AB, et al. Aeolian sand migration induced land degradation and desertification hotspots identification in the semi-arid rain shadow regions of Anantapur, India. Sci Rep. 2025;16(1):1875. DOI: 10.1038/s41598-025-31610-0
