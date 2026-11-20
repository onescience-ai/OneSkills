# 30米农田范围与面积制图数据预处理任务

## 适用范围

**适用场景**：
- 需要将原始Landsat数据转换为可用于分类的地表反射率产品
- 需要执行完整的遥感数据预处理流程
- 当使用合成数据时需要记录预处理配置或说明跳过原因

**不适用场景**：
- 不需要预处理的简单分析任务
- 已完成缩放、质量掩膜、几何和时序准备的地表反射率数据

## 输入契约

**Landsat 8 C2 L2 数据**：`/public/share/sugonhpcapp01/onestore/rsi/onedatasets/landsat-8-c2-l2-044033-2021-sacramento-30m-window/` 包含 2021-05-08 和 2021-08-28 两个 Sacramento 场景。各目录内 `SR_B2-B7.tif` 为六波段反射率 DN，`QA_PIXEL-QA_RADSAT.tif` 为两个 QA 波段，`stac-item.json` 提供场景身份、时间、波段定标和来源信息。窗口为 EPSG:5070、30 m、256×256 像元。

**标签资料**：`/public/share/sugonhpcapp01/onestore/rsi/onedatasets/usda-cdl-2021-sacramento-30m-training-window/cropland-2021.tif` 为同网格 USDA NASS CDL 2021 分类数据，完整类别说明位于同目录 `stac-item.json`。其覆盖地域为 Sacramento，资料年份为 2021。

**必需输入**：
- Landsat Level-1T 原始影像或 Collection 2 Level-2 地表反射率产品
- 与产品处理级别对应的辐射定标配置或缩放参数
- 几何配准配置文件
- 质量掩膜配置

**可选输入**：
- 辅助分类数据（DEM、夜间灯光等）
- 参考标签资料

## 操作步骤

### 步骤1：辐射定标

**C2 L2 分支**：上述地表反射率 DN 的缩放系数为 0.0000275，偏移量为 −0.2，反射率为 `DN × 0.0000275 − 0.2`。无效像元、云/阴影/雪和饱和状态由 QA 波段共同描述；质量标志先于有效特征的统计定义。该缩放关系属于所列 C2 L2 产品，与 Level-1 的 TOA 定标公式适用对象不同。
将传感器原始计数值（DN）转换为表观辐亮度（TOA Radiance）和表观反射率（TOA Reflectance）。

**公式**：
- TOA Radiance = DN × ML + AL （ML和AL为定标系数）
- TOA Reflectance = (π × L × d²) / (ESUN × cos(θ)) （L为辐亮度，d为日地距离，ESUN为太阳辐照度，θ为太阳天顶角）

**工具**：ArcGIS、ENVI、GEE

### 步骤2：大气校正

**处理级别差异**：Level-1T 的流程包含大气校正；已经完成 LaSRC 处理的 Landsat 8 C2 L2 地表反射率使用已有校正结果，后续准备包括产品缩放、质量掩膜、网格一致性和时序处理。
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

**软件与计算资源**：栅格处理使用 rasterio/GDAL，数组及掩膜计算使用 NumPy。256×256、两季、14 维 float32 特征数组为 3.5 MiB；包含这一步的 CPU 随机森林端到端工作负载观测到单线程峰值主存 289.41 MiB，小窗口初始配置可采用 1 CPU 核、1 GiB 主存、0 GPU、0 显存。单独预处理的峰值未单独测量；大窗口主存由块尺寸、波段/时相数量、数据类型和并发数共同决定。

- 当需要执行Landsat数据预处理时召回本卡片
- 当需要记录预处理配置时召回本卡片
- 当需要判定数据质量时召回本卡片

## 证据来源

**来源资料信息**：

```json
{
  "harvested": true,
  "harvest_source": "onescience-knowledge-harvester",
  "harvest_query": "遥感数据预处理工作流中辐射定标、几何配准和质量掩膜的具体作用与必要性；当使用替代数据源时如何保持工作流步骤完整性；Landsat数据预处理标准流程",
  "evidence_papers": [
    {
      "title": "30 m 5-yearly land cover maps of Qilian Mountain Area (QMA_LC30) from 1990 to 2020",
      "doi": "10.1038/s41597-024-03976-9",
      "year": 2024
    },
    {
      "title": "Aeolian sand migration induced land degradation and desertification hotspots identification in the semi-arid rain shadow regions of Anantapur, India",
      "doi": "10.1038/s41598-025-31610-0",
      "year": 2025
    }
  ]
}
```

Landsat 和标签来源分别为 [Planetary Computer landsat-c2-l2](https://planetarycomputer.microsoft.com/api/stac/v1/collections/landsat-c2-l2) 与 [usda-cdl](https://planetarycomputer.microsoft.com/api/stac/v1/collections/usda-cdl)；场景身份、定标与分类说明来自数据同目录 STAC 元数据。

[1] Yang A, Zhong B, Wang X, et al. 30 m 5-yearly land cover maps of Qilian Mountain Area (QMA_LC30) from 1990 to 2020. Sci Data. 2024;11(1):1339. DOI: 10.1038/s41597-024-03976-9
[2] Badapalli PK, Nakkala AB, et al. Aeolian sand migration induced land degradation and desertification hotspots identification in the semi-arid rain shadow regions of Anantapur, India. Sci Rep. 2025;16(1):1875. DOI: 10.1038/s41598-025-31610-0
